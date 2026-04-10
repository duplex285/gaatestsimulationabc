"""Complete ABC Assessment scoring pipeline.

Reference: abc-assessment-spec Section 2.1 (full pipeline)

Pipeline:
  Raw responses (1-7)
    -> Reverse-score items (8 - r)
    -> Subscale means (1.0 - 7.0)
    -> Normalize to 0-10
    -> Domain state classification
    -> Big Five inference
    -> 10-type motivational derivation
    -> Frustration signature detection
    -> Belbin role inference
    -> Context gap analysis (when team scores provided)

Enhanced pipeline (personalization engine layer):
    -> Bayesian posterior updating (across measurements)
    -> Base rate adjustment (demographic priors)
    -> Narrative generation (language for athletes and coaches)
    -> Transition tracking (archetype development over time)
"""

from src.python_scoring.base_rate_engine import BaseRateEngine
from src.python_scoring.bayesian_scorer import ABCBayesianProfile
from src.python_scoring.belbin_inference import infer_belbin_roles
from src.python_scoring.big_five_inference import compute_big_five
from src.python_scoring.context_gap import compute_context_gaps
from src.python_scoring.domain_classification import classify_all_domains
from src.python_scoring.frustration_signatures import detect_signatures
from src.python_scoring.narrative_engine import NarrativeEngine
from src.python_scoring.reverse_scoring import apply_reverse_scoring
from src.python_scoring.subscale_computation import compute_all_subscales
from src.python_scoring.transition_engine import TransitionTracker
from src.python_scoring.type_derivation import derive_type

REQUIRED_ITEMS = frozenset(
    [
        "AS1",
        "AS2",
        "AS3",
        "AS4",
        "AS5",
        "AS6",
        "AF1",
        "AF2",
        "AF3",
        "AF4",
        "AF5",
        "AF6",
        "BS1",
        "BS2",
        "BS3",
        "BS4",
        "BS5",
        "BS6",
        "BF1",
        "BF2",
        "BF3",
        "BF4",
        "BF5",
        "BF6",
        "CS1",
        "CS2",
        "CS3",
        "CS4",
        "CS5",
        "CS6",
        "CF1",
        "CF2",
        "CF3",
        "CF4",
        "CF5",
        "CF6",
    ]
)


class ABCScorer:
    """Orchestrates the full ABC scoring pipeline.

    Reference: abc-assessment-spec Section 2.1
    """

    def score(
        self,
        responses: dict[str, int],
        team_scores: dict[str, float] | None = None,
    ) -> dict:
        """Score a complete set of 36 item responses.

        Reference: abc-assessment-spec Section 2.1

        Args:
            responses: Dict mapping item codes (AS1, AF1, etc.) to
                responses on 1-7 Likert scale.
            team_scores: Optional dict of team-level subscale scores (0-10)
                for context gap analysis. Keys: a_sat, a_frust, etc.

        Returns:
            Dict with subscales, domain_states, big_five, type_name,
            type_domain, frustration_signatures, belbin_roles, context_gaps.
        """
        self._validate_responses(responses)

        # Step 1: Reverse score items
        # Reference: abc-assessment-spec Section 2.1
        scored = apply_reverse_scoring(responses)

        # Step 2-3: Compute subscale means and normalize to 0-10
        # Reference: abc-assessment-spec Section 2.1, Section 13.2
        subscales = compute_all_subscales(scored)

        # Step 4: Domain state classification
        # Reference: abc-assessment-spec Section 2.2
        domain_states = classify_all_domains(subscales)

        # Step 5: Big Five inference
        # Reference: abc-assessment-spec Section 2.3
        big_five = compute_big_five(subscales)

        # Step 6: Motivational type derivation (from subscale profile shape)
        # Reference: abc-assessment-spec Section 2.4
        type_result = derive_type(subscales)

        # Step 7: Frustration signature detection
        # Reference: abc-assessment-spec Section 2.5
        frustration_signatures = detect_signatures(subscales)

        # Step 8: Belbin role inference
        # Reference: abc-assessment-spec Section 2.6
        belbin_roles = infer_belbin_roles(subscales, big_five)

        # Step 9: Context gap analysis
        # Reference: abc-assessment-spec Section 2.7
        context_gaps = compute_context_gaps(subscales, team_scores)

        return {
            "subscales": subscales,
            "domain_states": domain_states,
            "big_five": big_five,
            "type_name": type_result["type_name"],
            "type_domain": type_result["type_domain"],
            "profile": type_result["profile"],
            "frustration_signatures": frustration_signatures,
            "belbin_roles": belbin_roles,
            "context_gaps": context_gaps,
        }

    def _validate_responses(self, responses: dict[str, int]) -> None:
        """Validate that all 36 required items are present and in range.

        Reference: abc-assessment-spec Section 1.1
        """
        missing = REQUIRED_ITEMS - set(responses.keys())
        if missing:
            raise ValueError(f"Missing required items: {sorted(missing)}")

        for item, value in responses.items():
            if item not in REQUIRED_ITEMS:
                continue
            if not isinstance(value, int):
                raise ValueError(f"Response for {item} must be int, got {type(value).__name__}")
            if value < 1 or value > 7:
                raise ValueError(f"Response for {item} must be 1-7, got {value}")


class EnhancedABCScorer:
    """Personalization engine layer on top of ABCScorer.

    Adds Bayesian posterior updating, demographic base rate adjustment,
    narrative generation, and transition tracking. The core scoring
    pipeline is unchanged.

    Usage:
        scorer = EnhancedABCScorer(demographics={"gender": "female"})
        result = scorer.score(responses, audience="athlete")
        # ... athlete takes assessment again two weeks later ...
        result2 = scorer.score(responses2, audience="athlete")
        # result2 now includes updated posteriors, transition info, etc.

    Reference: improvement-plan-personalization-engine.md
    """

    def __init__(
        self,
        demographics: dict | None = None,
        base_rate_config_path: str | None = None,
    ):
        """Initialize the enhanced scorer.

        Reference: abc-assessment-spec Section 4

        Args:
            demographics: Athlete demographic info for base rate
                stratification. Keys: gender, sexual_orientation,
                race_ethnicity, financial_stress, division, sport_type.
            base_rate_config_path: Path to base_rates.yaml. Defaults
                to config/base_rates.yaml.
        """
        self._core_scorer = ABCScorer()
        self._narrative = NarrativeEngine()
        self._tracker = TransitionTracker()

        self._base_rate_engine = BaseRateEngine(base_rate_config_path)
        self._demographics = demographics or {}
        self._prior = self._base_rate_engine.get_prior(self._demographics)

        self._bayesian_profile = ABCBayesianProfile()
        self._measurement_count = 0

    def score(
        self,
        responses: dict[str, int],
        team_scores: dict[str, float] | None = None,
        audience: str = "athlete",
        weeks_since_last: int = 2,
    ) -> dict:
        """Score responses with full personalization layer.

        Reference: abc-assessment-spec Section 4

        Args:
            responses: Dict mapping item codes to 1-7 responses.
            team_scores: Optional team-level subscale scores (0-10).
            audience: "athlete" or "coach" for narrative framing.
            weeks_since_last: Weeks since previous measurement.

        Returns:
            Dict with all core scoring outputs plus:
            - bayesian: posterior distributions per subscale
            - narratives: personalized text for athlete or coach
            - transition: archetype change classification
            - base_rate: demographic prior information
            - measurement_disclosure: confidence framing text
        """
        # Core pipeline (unchanged)
        core = self._core_scorer.score(responses, team_scores)

        # Bayesian update
        self._measurement_count += 1
        bayesian = self._bayesian_profile.update_all(core["subscales"])

        # Archetype probabilities from posterior
        archetype_probs = self._bayesian_profile.get_archetype_probabilities()

        # Get posterior confidence for the classified type
        type_confidence = archetype_probs.get(core["type_name"], 0.0)

        # Transition tracking
        transition = self._tracker.record(
            type_name=core["type_name"],
            posterior_confidence=type_confidence,
            weeks_since_last=weeks_since_last,
        )

        # Base rate adjustment per domain
        adjusted_states = {}
        for domain in ["ambition", "belonging", "craft"]:
            adjusted = self._base_rate_engine.adjust_classification(
                raw_state=core["domain_states"][domain],
                subscale_scores=core["subscales"],
                prior=self._prior["distressed_vulnerable_prior"],
            )
            adjusted_states[domain] = adjusted

        # Narratives
        archetype_narrative = self._narrative.generate_archetype_narrative(
            core["type_name"], audience
        )

        domain_narratives = {}
        for domain in ["ambition", "belonging", "craft"]:
            state = core["domain_states"][domain]
            sat_key = f"{domain[0]}_sat"
            confidence = adjusted_states[domain].get("confidence", None)
            # Map confidence string to float for narrative
            conf_map = {"high": 0.85, "moderate": 0.65, "low": 0.45}
            conf_float = conf_map.get(confidence)

            domain_narratives[domain] = self._narrative.generate_domain_state_narrative(
                domain,
                state,
                core["subscales"][sat_key],
                audience,
                conf_float,
            )

        signature_narratives = [
            self._narrative.generate_signature_narrative(sig, audience)
            for sig in core["frustration_signatures"]
        ]

        transition_narrative = None
        if transition.get("transition") is not None:
            t = transition["transition"]
            transition_narrative = self._narrative.generate_transition_narrative(
                t["from"],
                t["to"],
                t["type"],
                audience,
            )

        disclosure = self._narrative.generate_measurement_disclosure(
            self._measurement_count, audience
        )

        # Assemble result
        result = dict(core)
        result.update(
            {
                "bayesian": {
                    "subscales": bayesian["subscales"],
                    "domain_states": bayesian["domain_states"],
                    "archetype_probabilities": archetype_probs,
                    "measurement_count": self._measurement_count,
                },
                "adjusted_domain_states": adjusted_states,
                "narratives": {
                    "archetype": archetype_narrative,
                    "domains": domain_narratives,
                    "signatures": signature_narratives,
                    "transition": transition_narrative,
                    "measurement_disclosure": disclosure,
                },
                "transition": transition,
                "base_rate": self._prior,
                "trajectory": self._tracker.get_summary(),
            }
        )

        return result

    @property
    def measurement_count(self) -> int:
        """Number of measurements processed.

        Reference: abc-assessment-spec Section 4
        """
        return self._measurement_count

    def get_trajectory_summary(self) -> dict:
        """Return the athlete's full trajectory summary.

        Reference: abc-assessment-spec Section 4
        """
        return self._tracker.get_summary()
