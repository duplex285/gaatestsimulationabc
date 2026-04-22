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
from src.python_scoring.bayesian_scorer import (
    DOMAIN_PAIRS,
    ABCBayesianProfile,
    classify_with_uncertainty,
)
from src.python_scoring.belbin_inference import infer_belbin_roles
from src.python_scoring.big_five_inference import compute_big_five
from src.python_scoring.causality_orientations import score_causality_orientations
from src.python_scoring.context_gap import compute_context_gaps
from src.python_scoring.context_manager import DomainContextManager
from src.python_scoring.domain_classification import classify_all_domains
from src.python_scoring.frustration_signatures import detect_signatures
from src.python_scoring.group_conscious import score_group_conscious
from src.python_scoring.narrative_engine import NarrativeEngine
from src.python_scoring.overinvestment_trigger import DailySignals, evaluate_overinvestment
from src.python_scoring.passion_quality import score_passion_quality
from src.python_scoring.regulatory_style import score_regulatory_style
from src.python_scoring.reverse_scoring import apply_reverse_scoring
from src.python_scoring.self_concordance import score_self_concordance
from src.python_scoring.self_concordance_trajectory import GoalTrajectoryTracker
from src.python_scoring.subscale_computation import compute_all_subscales
from src.python_scoring.transition_engine import (
    TransitionTracker,
    classify_fatigue_timescale,
)
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
        context: str = "sport",
        context_config_path: str | None = None,
    ):
        """Initialize the enhanced scorer.

        Reference: abc-assessment-spec Section 4, Section 7

        Args:
            demographics: Athlete demographic info for base rate
                stratification. Keys: gender, sexual_orientation,
                race_ethnicity, financial_stress, division, sport_type.
            base_rate_config_path: Path to base_rates.yaml. Defaults
                to config/base_rates.yaml.
            context: Domain context name (sport, professional, military,
                healthcare, transition). Determines domain labels and
                narrative framing.
            context_config_path: Path to domain_contexts.yaml. Defaults
                to config/domain_contexts.yaml.
        """
        self._core_scorer = ABCScorer()
        self._narrative = NarrativeEngine()
        self._tracker = TransitionTracker()
        self._goal_trajectory_tracker = GoalTrajectoryTracker()

        self._base_rate_engine = BaseRateEngine(base_rate_config_path)
        self._demographics = demographics or {}
        self._prior = self._base_rate_engine.get_prior(self._demographics)

        self._bayesian_profile = ABCBayesianProfile()
        self._measurement_count = 0

        # Task 2: Fatigue timescale history per domain
        # Reference: abc-assessment-spec Section 12.1
        self._frustration_history: dict[str, list[float]] = {
            "ambition": [],
            "belonging": [],
            "craft": [],
        }

        # Task 3: Cross-domain context switching
        # Reference: abc-assessment-spec Section 7
        self._context_manager = DomainContextManager(
            context=context, config_path=context_config_path
        )
        self._context = context
        self._domain_labels = self._context_manager.get_labels()

    def score(
        self,
        responses: dict[str, int],
        team_scores: dict[str, float] | None = None,
        audience: str = "athlete",
        weeks_since_last: int = 2,
        passion_responses: dict[str, int] | None = None,
        regulatory_responses: dict[str, int] | None = None,
        daily_signals: DailySignals | None = None,
        group_conscious_responses: dict[str, int] | None = None,
        causality_responses: dict[str, int] | None = None,
        self_concordance_responses: dict[str, int] | None = None,
        self_concordance_goal_text: str | None = None,
        self_concordance_goal_id: str | None = None,
    ) -> dict:
        """Score responses with full personalization layer.

        Reference: abc-assessment-spec Section 4
        Reference: improvement-plan-personalization-engine.md Sections 16.1, 16.2

        Args:
            responses: Dict mapping core item codes (36 items) to 1-7 responses.
            team_scores: Optional team-level subscale scores (0-10).
            audience: "athlete" or "coach" for narrative framing.
            weeks_since_last: Weeks since previous measurement.
            passion_responses: Optional dict of passion-quality items
                (HP1-HP3, OP1-OP3). Quarterly cadence. When provided,
                passion leaning and the overinvestment trigger are
                attached to the result.
            regulatory_responses: Optional dict of regulatory-style
                items (AR1-AR2, BR1-BR2, CR1-CR2). Biweekly cadence.
                When provided, per-domain regulation results and any
                erosion events are attached to the result and fed into
                `TransitionTracker` for cross-measurement detection.
            daily_signals: Optional DailySignals from the cognitive
                signal engine. Refines overinvestment routing.
            group_conscious_responses: Optional dict of group-conscious
                items (AG1, BG1, CG1, TI1, TI2). Biweekly cadence.
                When provided, per-domain perceived collective
                satisfaction, team identification, and any empathic-
                risk flags are attached to the result.
            causality_responses: Optional dict of causality-orientation
                items (AO1-AO4, CO1-CO4, IO1-IO4). Annual cadence.
                When provided, three orientation scores and the
                dominant-orientation classification are attached to
                the result along with the orientation narrative.
            self_concordance_responses: Optional dict of self-concordance
                items (SC1-SC4) for one current goal. Biweekly cadence.
                When provided, the autonomous and controlled composites,
                signed self-concordance score, and three-band leaning
                are attached to the result along with the narrative.
            self_concordance_goal_text: Optional free-text goal the
                athlete rated. Stored on the result for product display
                but does not affect scoring or narrative selection.
            self_concordance_goal_id: Optional stable goal identifier.
                When supplied alongside self_concordance_responses, the
                scorer records the point into a per-goal trajectory
                tracker and surfaces the current trajectory on the
                result dict once three or more computable points exist
                for the goal.

        Returns:
            Dict with all core scoring outputs plus:
            - bayesian: posterior distributions per subscale
            - narratives: personalized text for athlete or coach
            - transition: archetype change classification plus erosion
            - base_rate: demographic prior information
            - measurement_disclosure: confidence framing text
            - passion: passion-quality result when provided
            - regulatory: per-domain regulatory result when provided
            - overinvestment: trigger routing when passion provided
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

        # Optional regulatory-style scoring (Section 16.1)
        regulatory_profile = None
        if regulatory_responses is not None:
            regulatory_profile = score_regulatory_style(regulatory_responses)

        # Transition tracking, now fed the regulatory profile for erosion
        transition = self._tracker.record(
            type_name=core["type_name"],
            posterior_confidence=type_confidence,
            weeks_since_last=weeks_since_last,
            regulatory_profile=regulatory_profile,
        )

        # Task 1: Personalized thresholds (after 6+ measurements)
        # Reference: abc-assessment-spec Section 8
        personalized_thresholds = {}
        personalized_domain_states = {}
        if self._measurement_count >= 6:
            for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
                sat_scorer = self._bayesian_profile.scorers[sat_key]
                frust_scorer = self._bayesian_profile.scorers[frust_key]
                p_sat_thresh = sat_scorer.get_personalized_threshold(k=1.5, floor=3.0)
                p_frust_thresh = frust_scorer.get_personalized_threshold(k=1.5, floor=3.0)
                if p_sat_thresh is not None and p_frust_thresh is not None:
                    personalized_thresholds[domain] = {
                        "satisfaction": p_sat_thresh,
                        "frustration": p_frust_thresh,
                    }
                    personalized_domain_states[domain] = classify_with_uncertainty(
                        sat_scorer,
                        frust_scorer,
                        sat_threshold=p_sat_thresh,
                        frust_threshold=p_frust_thresh,
                    )

        # Task 2: Fatigue timescale classification
        # Reference: abc-assessment-spec Section 12.1
        fatigue_timescales = {}
        for domain, (_, frust_key) in DOMAIN_PAIRS.items():
            self._frustration_history[domain].append(core["subscales"][frust_key])
            if len(self._frustration_history[domain]) >= 3:
                ts = classify_fatigue_timescale(self._frustration_history[domain])
                fatigue_timescales[domain] = ts.value

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

        # Optional passion quality (Section 16.2)
        passion_result = None
        overinvestment_result = None
        passion_narrative = None
        overinvestment_narrative = None
        if passion_responses is not None:
            passion_result = score_passion_quality(passion_responses)
            passion_narrative = self._narrative.generate_passion_narrative(
                passion_result.leaning, audience
            )
            overinvestment_result = evaluate_overinvestment(
                core["subscales"], passion_result, daily_signals
            )
            overinvestment_narrative = self._narrative.generate_overinvestment_narrative(
                overinvestment_result.path, audience
            )

        # Optional regulatory narratives (Section 16.1)
        regulatory_narratives: dict[str, str] = {}
        if regulatory_profile is not None:
            for domain_name, dom_reg in regulatory_profile.domains.items():
                regulatory_narratives[domain_name] = self._narrative.generate_regulatory_narrative(
                    domain_name, dom_reg.style, audience
                )

        # Erosion narratives from the transition entry (if any)
        erosion_narratives: dict[str, str] = {}
        for domain_name in transition.get("regulation_erosion_events", []):
            erosion_narratives[domain_name] = self._narrative.generate_erosion_narrative(
                domain_name, audience
            )

        # Optional group-conscious layer (Section 16.5)
        group_conscious_profile = None
        group_conscious_narratives: dict[str, object] = {}
        if group_conscious_responses is not None:
            group_conscious_profile = score_group_conscious(group_conscious_responses)

            collective_narratives: dict[str, str] = {}
            for domain_name, cs in group_conscious_profile.collective.items():
                collective_narratives[domain_name] = (
                    self._narrative.generate_collective_satisfaction_narrative(
                        domain_name, cs.level, audience
                    )
                )
            group_conscious_narratives["collective"] = collective_narratives

            group_conscious_narratives["team_identification"] = (
                self._narrative.generate_team_identification_narrative(
                    group_conscious_profile.team_identification.level, audience
                )
            )

            if group_conscious_profile.empathic_risk_domains:
                group_conscious_narratives["empathic_risk"] = (
                    self._narrative.generate_empathic_risk_narrative(audience)
                )
                group_conscious_narratives["empathic_risk_domains"] = list(
                    group_conscious_profile.empathic_risk_domains
                )

        # Optional causality orientations layer (Section 16.6)
        causality_profile = None
        causality_narrative = None
        if causality_responses is not None:
            causality_profile = score_causality_orientations(causality_responses)
            causality_narrative = self._narrative.generate_causality_narrative(
                causality_profile.dominant, audience
            )

        # Optional self-concordance layer (Section 16.7)
        self_concordance_profile = None
        self_concordance_narrative = None
        self_concordance_trajectory = None
        self_concordance_trajectory_narrative = None
        if self_concordance_responses is not None:
            self_concordance_profile = score_self_concordance(
                self_concordance_responses,
                goal_text=self_concordance_goal_text,
            )
            self_concordance_narrative = self._narrative.generate_self_concordance_narrative(
                self_concordance_profile.leaning, audience
            )

            # When the caller supplies a stable goal_id, record the point
            # into the per-goal trajectory tracker and surface the current
            # trajectory (plus narrative) for that goal. The cycle_index
            # uses the measurement_count as a stable monotonic axis.
            if self_concordance_goal_id is not None:
                self._goal_trajectory_tracker.record(
                    goal_id=self_concordance_goal_id,
                    cycle_index=self._measurement_count,
                    profile=self_concordance_profile,
                )
                self_concordance_trajectory = self._goal_trajectory_tracker.get_trajectory(
                    self_concordance_goal_id
                )
                if (
                    self_concordance_trajectory is not None
                    and self_concordance_trajectory.label != "insufficient_data"
                ):
                    self_concordance_trajectory_narrative = (
                        self._narrative.generate_self_concordance_trajectory_narrative(
                            self_concordance_trajectory.label, audience
                        )
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
                    "passion": passion_narrative,
                    "overinvestment": overinvestment_narrative,
                    "regulatory": regulatory_narratives,
                    "erosion": erosion_narratives,
                    "group_conscious": group_conscious_narratives,
                    "causality": causality_narrative,
                    "self_concordance": self_concordance_narrative,
                    "self_concordance_trajectory": self_concordance_trajectory_narrative,
                },
                "passion": passion_result,
                "regulatory": regulatory_profile,
                "overinvestment": overinvestment_result,
                "group_conscious": group_conscious_profile,
                "causality": causality_profile,
                "self_concordance": self_concordance_profile,
                "self_concordance_trajectory": self_concordance_trajectory,
                "transition": transition,
                "base_rate": self._prior,
                "trajectory": self._tracker.get_summary(),
                # Task 1: Personalized thresholds
                # Reference: abc-assessment-spec Section 8
                "personalized_thresholds": personalized_thresholds
                if personalized_thresholds
                else None,
                "personalized_domain_states": personalized_domain_states
                if personalized_domain_states
                else None,
                # Task 2: Fatigue timescales
                # Reference: abc-assessment-spec Section 12.1
                "fatigue_timescales": fatigue_timescales if fatigue_timescales else None,
                # Task 3: Context switching
                # Reference: abc-assessment-spec Section 7
                "context": self._context,
                "domain_labels": self._domain_labels,
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
