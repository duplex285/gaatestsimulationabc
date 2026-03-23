"""Integrated psychometric scoring pipeline for ABC Assessment.

Wraps all psychometric modules into a single ABCPsychometricScorer class
that produces IRT-scored subscales, T-scores, severity bands, trajectory
analysis, and risk assessments with tier-aware output suppression.

Runs alongside the existing ABCScorer in src/python_scoring/. Migration
from CTT to IRT happens only after empirical data validates the new methods.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
Reference: Phase 2b (decision consistency: confidence bands required)
Reference: Phase 5b (tier reliability: suppress unsupported outputs)
Reference: Phase 6 (leading indicators: continuous RCI, not state transitions)
"""

import numpy as np

from src.psychometric.irt_estimation import score_theta_eap
from src.psychometric.irt_subscale_scoring import FACTOR_ITEM_INDICES, theta_to_subscale_score
from src.psychometric.norming import assign_severity_bands, compute_t_scores
from src.psychometric.tier_reliability import (
    determine_supportable_interpretations,
)
from src.psychometric.trajectory_engine import (
    compute_individual_trajectory,
)

# Default reference norms (synthetic, from Phase 5)
DEFAULT_NORMS = {
    "a_sat": {"mean": 5.5, "sd": 1.8},
    "a_frust": {"mean": 4.0, "sd": 1.8},
    "b_sat": {"mean": 5.8, "sd": 1.8},
    "b_frust": {"mean": 3.8, "sd": 1.8},
    "c_sat": {"mean": 5.3, "sd": 1.8},
    "c_frust": {"mean": 4.2, "sd": 1.8},
}

# Tier mapping by item count
TIER_BY_COUNT = {6: "6_item", 18: "18_item", 36: "36_item"}


class ABCPsychometricScorer:
    """Integrated psychometric scoring pipeline.

    Wraps the existing ABCScorer and adds:
    - IRT theta scoring with per-person standard errors (Phase 1)
    - T-scores and severity bands (Phase 5)
    - Tier-aware output suppression (Phase 5b)
    - Trajectory analysis with reliable change detection (Phase 6)
    - Confidence/precision reporting (Phase 2b)

    Args:
        discrimination: IRT discrimination parameters, shape (36,)
        difficulty: IRT difficulty parameters, shape (36, K-1)
        reference_norms: dict mapping subscale name to {mean, sd} for T-score conversion
    """

    def __init__(
        self,
        discrimination: np.ndarray,
        difficulty: np.ndarray,
        reference_norms: dict | None = None,
    ):
        self.discrimination = discrimination
        self.difficulty = difficulty
        self.norms = reference_norms or DEFAULT_NORMS

        # Pre-compute supportable interpretations per tier
        self._tier_support = determine_supportable_interpretations(discrimination, difficulty)

    def _detect_tier(self, n_items: int) -> str:
        """Determine measurement tier from item count."""
        if n_items <= 6:
            return "6_item"
        elif n_items <= 18:
            return "18_item"
        else:
            return "36_item"

    def _score_subscales(self, responses: np.ndarray) -> dict:
        """Score all 6 subscales using IRT EAP estimation.

        Returns dict with scores, theta, and standard_errors per factor.
        """
        n_items = len(responses)
        response_matrix = responses.reshape(1, -1)

        scores = {}
        thetas = {}
        ses = {}

        for factor, indices in FACTOR_ITEM_INDICES.items():
            # Only use indices that exist in the response array
            valid_indices = [i for i in indices if i < n_items]
            if not valid_indices:
                continue

            factor_responses = response_matrix[:, valid_indices]
            factor_disc = self.discrimination[valid_indices]
            factor_diff = self.difficulty[valid_indices]

            theta_hat, se_hat = score_theta_eap(factor_responses, factor_disc, factor_diff)

            thetas[factor] = float(theta_hat[0])
            ses[factor] = float(se_hat[0])
            scores[factor] = theta_to_subscale_score(theta_hat[0])

        return {"scores": scores, "theta": thetas, "standard_errors": ses}

    def _compute_t_scores(self, subscale_scores: dict[str, float]) -> dict[str, float]:
        """Convert subscale scores to T-scores using reference norms."""
        t_scores = {}
        for factor, score in subscale_scores.items():
            if factor in self.norms:
                ref = self.norms[factor]
                t = compute_t_scores(np.array([score]), ref["mean"], ref["sd"])
                t_scores[factor] = float(t[0])
        return t_scores

    def _compute_severity_bands(self, t_scores: dict[str, float]) -> dict[str, str]:
        """Assign severity bands from T-scores."""
        bands = {}
        for factor, t in t_scores.items():
            band_list = assign_severity_bands(np.array([t]))
            bands[factor] = band_list[0]
        return bands

    def _compute_confidence(self, ses: dict[str, float], tier: str) -> dict:
        """Compute confidence/precision information.

        Reference: Phase 2b (misclassification risk)
        """
        supported = self._tier_support.get(tier, {}).get("supported", [])
        not_supported = self._tier_support.get(tier, {}).get("not_supported", [])

        mean_se = float(np.mean(list(ses.values()))) if ses else 1.0

        if mean_se < 0.25:
            precision_label = "high"
        elif mean_se < 0.40:
            precision_label = "moderate"
        else:
            precision_label = "low"

        return {
            "mean_se": mean_se,
            "precision": precision_label,
            "supported_interpretations": supported,
            "not_supported_interpretations": not_supported,
        }

    def score(
        self,
        responses: np.ndarray,
        n_items: int | None = None,
    ) -> dict:
        """Score a single administration.

        Args:
            responses: item responses, shape (n_items,), values in [1, 7]
            n_items: override item count for tier detection (default: len(responses))

        Returns:
            dict with: subscales, theta, standard_errors, t_scores,
            severity_bands, tier, confidence, scoring_method,
            and optionally domain_states and type_name if tier supports them
        """
        if n_items is None:
            n_items = len(responses)

        tier = self._detect_tier(n_items)

        # IRT scoring
        irt_result = self._score_subscales(responses)
        subscales = irt_result["scores"]
        thetas = irt_result["theta"]
        ses = irt_result["standard_errors"]

        # T-scores and severity bands
        t_scores = self._compute_t_scores(subscales)
        severity_bands = self._compute_severity_bands(t_scores)

        # Confidence
        confidence = self._compute_confidence(ses, tier)

        result = {
            "subscales": subscales,
            "theta": thetas,
            "standard_errors": ses,
            "t_scores": t_scores,
            "severity_bands": severity_bands,
            "tier": tier,
            "confidence": confidence,
            "scoring_method": "irt_eap",
        }

        # Tier-aware output: only include domain states and types if supported
        supported = confidence["supported_interpretations"]

        # Only classify if all 6 subscales were scored (requires enough items)
        all_subscales_present = len(subscales) == 6

        if "domain_state_classification" in supported and all_subscales_present:
            from src.python_scoring.domain_classification import classify_all_domains

            result["domain_states"] = classify_all_domains(subscales)
        else:
            result["domain_states"] = None

        if "24_type_classification" in supported and all_subscales_present:
            from src.python_scoring.type_derivation import derive_type

            type_result = derive_type(subscales)
            result["type_name"] = type_result.get("type_name")
        else:
            result["type_name"] = None

        return result

    def score_trajectory(
        self,
        timepoint_responses: list[np.ndarray],
    ) -> dict:
        """Score a trajectory across multiple administrations.

        Uses continuous theta scores with RCI-based change detection
        per Phase 2b's finding that state classifications are too unstable.

        Args:
            timepoint_responses: list of response arrays, one per timepoint

        Returns:
            dict with: timepoint_scores, pattern, reliable_changes,
            trend, risk_assessment
        """
        len(timepoint_responses)

        # Score each timepoint
        timepoint_scores = []
        all_thetas = []  # Use first factor's theta as primary signal
        all_ses = []

        for responses in timepoint_responses:
            tp_result = self.score(responses)
            timepoint_scores.append(tp_result)

            # Use mean theta across factors as composite signal
            theta_vals = list(tp_result["theta"].values())
            se_vals = list(tp_result["standard_errors"].values())
            all_thetas.append(float(np.mean(theta_vals)))
            all_ses.append(float(np.mean(se_vals)))

        scores_array = np.array(all_thetas)
        se_array = np.array(all_ses)

        # Trajectory analysis
        trajectory = compute_individual_trajectory(scores_array, se_array)

        # Risk assessment based on trajectory
        n_deteriorations = int(np.sum(trajectory["reliable_changes"]["deteriorated"]))
        trend_dir = trajectory["trend"]["direction"]

        if n_deteriorations >= 2 or trend_dir == "declining":
            alert_level = "elevated"
        elif n_deteriorations >= 1:
            alert_level = "watch"
        else:
            alert_level = "normal"

        return {
            "timepoint_scores": timepoint_scores,
            "pattern": trajectory["pattern"],
            "reliable_changes": {
                "improved": trajectory["reliable_changes"]["improved"].tolist(),
                "deteriorated": trajectory["reliable_changes"]["deteriorated"].tolist(),
                "rci_values": trajectory["reliable_changes"]["rci_values"].tolist(),
            },
            "trend": {
                "direction": trajectory["trend"]["direction"],
                "slope": trajectory["trend"]["slope"],
                "significant": trajectory["trend"]["significant"],
            },
            "risk_assessment": {
                "alert_level": alert_level,
                "n_reliable_deteriorations": n_deteriorations,
                "trend_direction": trend_dir,
            },
        }
