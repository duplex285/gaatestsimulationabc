"""Population norming for ABC Assessment.

Converts raw subscale scores to T-scores, percentile ranks, and severity
bands using a reference population distribution. Replaces the fixed 0-10
scale with empirically normed scores that are interpretable relative to
the athlete population.

Reference: McCall (1922), How to Measure in Education
Reference: PROMIS scoring manual (T-score: mean=50, SD=10)
Reference: Lovibond & Lovibond (1995), DASS-21 severity bands
Reference: Crawford & Garthwaite (2006), Norms and Comparison Methods
"""

import numpy as np


def compute_t_scores(
    raw_scores: np.ndarray,
    reference_mean: float,
    reference_sd: float,
) -> np.ndarray:
    """Convert raw scores to T-scores using a reference population.

    Reference: McCall (1922); PROMIS scoring manual

    Formula: T = 50 + 10 * (raw - reference_mean) / reference_sd

    T-scores have mean=50 and SD=10 in the reference population.
    A T-score of 60 means "one SD above the population mean."

    Args:
        raw_scores: array of raw scores to convert
        reference_mean: mean of the reference population
        reference_sd: SD of the reference population

    Returns:
        Array of T-scores (same shape as input)
    """
    if reference_sd <= 0:
        return np.full_like(raw_scores, 50.0, dtype=float)

    return 50.0 + 10.0 * (raw_scores - reference_mean) / reference_sd


def compute_percentile_ranks(
    scores: np.ndarray,
    reference_distribution: np.ndarray,
) -> np.ndarray:
    """Compute percentile ranks against a reference distribution.

    Reference: Angoff (1984), Scales, Norms, and Equivalent Scores

    For each score, computes the percentage of the reference distribution
    at or below that score.

    Args:
        scores: array of scores to rank
        reference_distribution: array of reference population scores

    Returns:
        Array of percentile ranks (0-100)
    """
    sorted_ref = np.sort(reference_distribution)
    n_ref = len(sorted_ref)

    percentiles = np.zeros(len(scores))
    for i, score in enumerate(scores):
        count_at_or_below = np.sum(sorted_ref <= score)
        percentiles[i] = (count_at_or_below / n_ref) * 100.0

    return percentiles


def assign_severity_bands(
    t_scores: np.ndarray,
    bands: list[dict] | None = None,
) -> list[str]:
    """Assign severity band labels from T-scores.

    Reference: Lovibond & Lovibond (1995), DASS-21 severity structure

    Default bands (for frustration/distress-direction scores):
        Normal:           T < 55
        Mild:             55 <= T < 60
        Moderate:         60 <= T < 65
        Severe:           65 <= T < 70
        Extremely Severe: T >= 70

    Args:
        t_scores: array of T-scores
        bands: optional list of dicts with "label" and "t_max" keys,
               ordered from lowest to highest. Default uses DASS-style bands.

    Returns:
        List of severity band labels (same length as input)
    """
    if bands is None:
        bands = [
            {"label": "Normal", "t_max": 55},
            {"label": "Mild", "t_max": 60},
            {"label": "Moderate", "t_max": 65},
            {"label": "Severe", "t_max": 70},
            {"label": "Extremely Severe", "t_max": float("inf")},
        ]

    result = []
    for t in t_scores:
        assigned = bands[-1]["label"]  # default to last band
        for band in bands:
            if t < band["t_max"]:
                assigned = band["label"]
                break
        result.append(assigned)

    return result


def build_stratified_norms(
    data: dict[str, np.ndarray],
    stratification_var: str,
    score_columns: list[str],
) -> dict:
    """Build norm tables stratified by a demographic variable.

    Reference: Crawford & Garthwaite (2006)

    Computes mean, SD, and n for each score column within each stratum,
    plus overall (unstratified) norms.

    Args:
        data: dict mapping column names to arrays. Must include
              stratification_var and all score_columns.
        stratification_var: name of the grouping variable
        score_columns: list of score column names to norm

    Returns:
        Nested dict: {stratum: {score_column: {mean, sd, n}}}
        Includes an "overall" key for unstratified norms.
    """
    groups = np.array(data[stratification_var])
    unique_groups = sorted(set(groups))

    result = {}

    # Overall norms
    overall = {}
    for col in score_columns:
        scores = np.array(data[col])
        overall[col] = {
            "mean": float(np.mean(scores)),
            "sd": float(np.std(scores)),
            "n": len(scores),
        }
    result["overall"] = overall

    # Per-stratum norms
    for group in unique_groups:
        mask = groups == group
        stratum = {}
        for col in score_columns:
            scores = np.array(data[col])[mask]
            stratum[col] = {
                "mean": float(np.mean(scores)),
                "sd": float(np.std(scores)),
                "n": int(np.sum(mask)),
            }
        result[group] = stratum

    return result
