"""Base rate engine for Bayesian adjustment of ABC domain classifications.

Loads demographic-stratified population priors from config/base_rates.yaml
and applies Bayes' Theorem to adjust raw ABC classifications against
epidemiological base rates.

References:
  - NCAA Student-Athlete Health and Wellness Study (SAHWS), 2022-23 (N=23,272)
  - ACHA-NCHA, 2018-19 (N=9,057 student-athletes)
  - Madigan et al. (2022), meta-analysis of athlete burnout (k=91, N=21,012)

The core idea: a raw "Distressed" classification from ABC items alone
may be a false positive if the respondent's demographic group has a low
base rate of exhaustion. Conversely, a "Mild" classification may mask
true distress in a high-prevalence group. Bayesian adjustment recalibrates
these classifications using sensitivity and specificity estimates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Ordered from most specific to least specific for stratum selection
_STRATUM_PRIORITY = [
    "financial_stress",
    "sexual_orientation",
    "gender",
    "race_ethnicity",
    "division",
]

# Maps demographic keys to YAML sub-key prefixes
_DEMO_KEY_TO_YAML = {
    "gender": "by_gender",
    "sexual_orientation": "by_sexual_orientation",
    "race_ethnicity": "by_race_ethnicity",
    "financial_stress": "by_financial_stress",
    "division": "by_division",
}

_POSITIVE_STATES = {"Distressed", "Vulnerable"}
_NEGATIVE_STATES = {"Mild", "Thriving"}
_ALL_STATES = ("Thriving", "Vulnerable", "Mild", "Distressed")


class BaseRateEngine:
    """Loads population base rates and adjusts ABC classifications via Bayes' Theorem.

    The engine treats ABC classification as a binary diagnostic test:
      - Positive = Distressed or Vulnerable
      - Negative = Mild or Thriving

    Sensitivity = P(ABC flags distressed | truly distressed)
    Specificity = P(ABC flags not distressed | truly not distressed)

    The base rate (prior) is the population prevalence of near-constant
    mental exhaustion for the respondent's demographic stratum.
    """

    def __init__(self, config_path: str | None = None) -> None:
        """Load base_rates.yaml configuration.

        Reference: abc-assessment-spec Section 2

        Args:
            config_path: Absolute or relative path to the YAML config.
                Defaults to config/base_rates.yaml relative to the
                project root (two directories above this file).
        """
        if config_path is None:
            project_root = Path(__file__).resolve().parent.parent.parent
            config_path = str(project_root / "config" / "base_rates.yaml")

        with open(config_path) as f:
            self._config: dict[str, Any] = yaml.safe_load(f)

        self._exhaustion = self._config["near_constant_exhaustion"]
        self._mapping = self._config["domain_state_mapping"]
        self._calibration = self._config.get("classification_calibration", {})

    def get_prior(self, demographics: dict[str, str]) -> dict[str, Any]:
        """Return the stratified base rate for a respondent's demographics.

        Reference: abc-assessment-spec Section 2

        Selects the single most informative stratum rather than combining
        rates multiplicatively, because the source studies report marginal
        prevalence (not conditional) and multiplicative combination would
        overstate joint risk without validated interaction data.

        Stratum priority (most to least specific):
          financial_stress > sexual_orientation > gender >
          race_ethnicity > division

        Args:
            demographics: Dict with optional keys: gender,
                sexual_orientation, race_ethnicity, financial_stress,
                division, sport_type, career_phase. Values should match
                the categories in base_rates.yaml (e.g., "male", "female",
                "lgbtq_plus", "high", "d1").

        Returns:
            Dict with keys:
              - distressed_vulnerable_prior (float): base rate for the
                Distressed/Vulnerable group
              - any_exhaustion_prior (float): broader threshold rate
              - source (str): description of which stratum was used
        """
        selected_rate = None
        source_description = "overall (no matching demographic provided)"

        for stratum_key in _STRATUM_PRIORITY:
            if stratum_key not in demographics:
                continue
            demo_value = demographics[stratum_key]
            yaml_key = _DEMO_KEY_TO_YAML[stratum_key]
            stratum_data = self._exhaustion.get(yaml_key, {})

            if demo_value in stratum_data:
                selected_rate = stratum_data[demo_value]
                source_description = f"{yaml_key}.{demo_value}"
                break

        if selected_rate is None:
            selected_rate = self._exhaustion["overall"]

        # Compute broader threshold rate
        multiplier = self._mapping["any_recent_exhaustion"]["multiplier"]
        cap = self._mapping["any_recent_exhaustion"]["cap"]
        any_exhaustion_rate = min(selected_rate * multiplier, cap)

        return {
            "distressed_vulnerable_prior": selected_rate,
            "any_exhaustion_prior": round(any_exhaustion_rate, 4),
            "source": source_description,
        }

    def adjust_classification(
        self,
        raw_state: str,
        subscale_scores: dict[str, float],
        prior: float,
        sensitivity: float = 0.81,
        specificity: float = 0.84,
    ) -> dict[str, Any]:
        """Apply Bayes' Theorem to adjust a raw ABC domain classification.

        Reference: abc-assessment-spec Section 2

        Models the ABC as a binary diagnostic test:
          - Positive condition: truly Distressed or Vulnerable
          - Negative condition: truly Mild or Thriving

        Bayes' Theorem:
          P(truly D/V | ABC says D/V) =
            sensitivity * prior / P(ABC says D/V)

          P(ABC says D/V) =
            sensitivity * prior + (1 - specificity) * (1 - prior)

        For a negative test result (ABC says M/T):
          P(truly D/V | ABC says M/T) =
            (1 - sensitivity) * prior / P(ABC says M/T)

          P(ABC says M/T) =
            (1 - sensitivity) * prior + specificity * (1 - prior)

        The posterior is then distributed across the four states using
        the raw classification as a weighting signal.

        Args:
            raw_state: One of "Thriving", "Vulnerable", "Mild", "Distressed".
            subscale_scores: Dict with satisfaction and frustration scores
                (e.g., {"satisfaction": 7.2, "frustration": 3.1}). Used to
                weight posterior distribution within the positive/negative
                group.
            prior: Base rate for the Distressed/Vulnerable group (from
                get_prior).
            sensitivity: P(ABC flags distressed | truly distressed).
                Default 0.81.
            specificity: P(ABC flags not distressed | truly not distressed).
                Default 0.84.

        Returns:
            Dict with keys:
              - posteriors: dict mapping each state to its posterior probability
              - raw_state: the original classification
              - adjusted_state: the state with highest posterior
              - base_rate_used: the prior value
              - confidence: "low", "moderate", or "high" based on posterior
                spread
        """
        if raw_state not in _ALL_STATES:
            raise ValueError(f"raw_state must be one of {_ALL_STATES}, got '{raw_state}'")

        abc_positive = raw_state in _POSITIVE_STATES

        if abc_positive:
            # P(truly D/V | ABC says D/V)
            p_test_positive = sensitivity * prior + (1 - specificity) * (1 - prior)
            posterior_positive = (sensitivity * prior) / p_test_positive
            posterior_negative = 1.0 - posterior_positive
        else:
            # P(truly D/V | ABC says M/T)
            p_test_negative = (1 - sensitivity) * prior + specificity * (1 - prior)
            posterior_positive = ((1 - sensitivity) * prior) / p_test_negative
            posterior_negative = 1.0 - posterior_positive

        # Distribute posterior across the four states.
        # Within the positive group (D/V), weight by frustration intensity.
        # Within the negative group (M/T), weight by satisfaction level.
        sat = subscale_scores.get("satisfaction", 5.0)
        frust = subscale_scores.get("frustration", 5.0)

        posteriors = _distribute_posteriors(
            posterior_positive, posterior_negative, raw_state, sat, frust
        )

        # Determine adjusted state
        adjusted_state = max(posteriors, key=posteriors.get)

        # Confidence from posterior spread: high if top posterior is dominant
        sorted_probs = sorted(posteriors.values(), reverse=True)
        gap = sorted_probs[0] - sorted_probs[1]

        if gap >= 0.30:
            confidence = "high"
        elif gap >= 0.15:
            confidence = "moderate"
        else:
            confidence = "low"

        return {
            "posteriors": {k: round(v, 4) for k, v in posteriors.items()},
            "raw_state": raw_state,
            "adjusted_state": adjusted_state,
            "base_rate_used": prior,
            "confidence": confidence,
        }


def _distribute_posteriors(
    p_positive: float,
    p_negative: float,
    raw_state: str,
    satisfaction: float,
    frustration: float,
) -> dict[str, float]:
    """Split posterior mass across four states using subscale scores.

    Reference: abc-assessment-spec Section 2

    Within the Distressed/Vulnerable group, higher frustration shifts
    weight toward Distressed. Within the Mild/Thriving group, higher
    satisfaction shifts weight toward Thriving.

    The raw state receives a loyalty bonus (0.6 of its group's mass)
    to reflect the ABC's item-level information beyond the binary test.

    Args:
        p_positive: Posterior probability of truly Distressed/Vulnerable.
        p_negative: Posterior probability of truly Mild/Thriving.
        raw_state: The original ABC classification.
        satisfaction: Satisfaction subscale score (0-10 scale).
        frustration: Frustration subscale score (0-10 scale).

    Returns:
        Dict mapping each state to its posterior probability. Sums to 1.0.
    """
    loyalty = 0.6  # share given to the raw state within its group

    # Positive group: Distressed vs Vulnerable
    frust_ratio = min(max(frustration / 10.0, 0.1), 0.9)
    if raw_state == "Distressed":
        p_distressed = p_positive * loyalty + p_positive * (1 - loyalty) * frust_ratio
        p_vulnerable = p_positive - p_distressed
    elif raw_state == "Vulnerable":
        p_vulnerable = p_positive * loyalty + p_positive * (1 - loyalty) * (1 - frust_ratio)
        p_distressed = p_positive - p_vulnerable
    else:
        # Raw state is negative; split by frustration ratio alone
        p_distressed = p_positive * frust_ratio
        p_vulnerable = p_positive * (1 - frust_ratio)

    # Negative group: Thriving vs Mild
    sat_ratio = min(max(satisfaction / 10.0, 0.1), 0.9)
    if raw_state == "Thriving":
        p_thriving = p_negative * loyalty + p_negative * (1 - loyalty) * sat_ratio
        p_mild = p_negative - p_thriving
    elif raw_state == "Mild":
        p_mild = p_negative * loyalty + p_negative * (1 - loyalty) * (1 - sat_ratio)
        p_thriving = p_negative - p_mild
    else:
        # Raw state is positive; split by satisfaction ratio alone
        p_thriving = p_negative * sat_ratio
        p_mild = p_negative * (1 - sat_ratio)

    return {
        "Thriving": p_thriving,
        "Vulnerable": p_vulnerable,
        "Mild": p_mild,
        "Distressed": p_distressed,
    }
