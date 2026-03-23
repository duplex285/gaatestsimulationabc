"""Norming simulation for ABC Assessment.

Generates stratified synthetic athlete populations for norming demonstration.
Each stratum (e.g., elite, club, youth) has a configurable mean shift,
producing populations where elite athletes score higher on satisfaction
and lower on frustration than youth athletes.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)

Status: SYNTHETIC. All norms derived from this data must be replaced
with empirical population data before clinical use.
"""

import numpy as np

SUBSCALES = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]

# Default population parameters (on the 0-10 normalized scale)
DEFAULT_MEANS = {
    "a_sat": 5.5,
    "a_frust": 4.0,
    "b_sat": 5.8,
    "b_frust": 3.8,
    "c_sat": 5.3,
    "c_frust": 4.2,
}
DEFAULT_SD = 1.8

DEFAULT_STRATA = {
    "elite": {"mean_shift": 0.5, "n": 200},
    "club": {"mean_shift": 0.0, "n": 500},
    "youth": {"mean_shift": -0.3, "n": 300},
}


def simulate_stratified_population(
    strata: dict[str, dict] | None = None,
    base_means: dict[str, float] | None = None,
    base_sd: float = DEFAULT_SD,
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Generate a stratified synthetic athlete population.

    Reference: abc-assessment-spec Section 11.1

    For each stratum, generates scores from a normal distribution centered
    at base_mean + mean_shift, with the specified SD. Satisfaction subscales
    shift positively with mean_shift; frustration subscales shift negatively
    (higher-level athletes have more satisfaction, less frustration).

    Scores are clipped to [0, 10].

    Args:
        strata: dict mapping stratum name to {"mean_shift": float, "n": int}.
                Default uses elite/club/youth with shifts of +0.5/0.0/-0.3.
        base_means: dict mapping subscale name to population mean. Default
                    uses typical athlete values.
        base_sd: population SD for all subscales (default 1.8).
        seed: random seed for reproducibility.

    Returns:
        dict with keys: all 6 subscale names + "level" (stratum labels).
        Each value is a numpy array of length sum(n across strata).
    """
    if strata is None:
        strata = DEFAULT_STRATA
    if base_means is None:
        base_means = DEFAULT_MEANS

    rng = np.random.default_rng(seed)

    total_n = sum(s["n"] for s in strata.values())

    result = {sub: np.zeros(total_n) for sub in SUBSCALES}
    result["level"] = np.empty(total_n, dtype=object)

    idx = 0
    for stratum_name, spec in strata.items():
        n = spec["n"]
        shift = spec["mean_shift"]

        for sub in SUBSCALES:
            is_frustration = "frust" in sub
            # Frustration shifts opposite to satisfaction:
            # higher-level athletes have less frustration
            effective_shift = -shift if is_frustration else shift
            mean = base_means[sub] + effective_shift

            scores = rng.normal(mean, base_sd, n)
            scores = np.clip(scores, 0.0, 10.0)
            result[sub][idx : idx + n] = scores

        result["level"][idx : idx + n] = stratum_name
        idx += n

    return result
