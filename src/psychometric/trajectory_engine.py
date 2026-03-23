"""Trajectory engine for ABC Assessment.

Processes longitudinal score data to detect reliable change, trends,
and trajectory patterns. Uses continuous theta scores with IRT standard
errors rather than categorical domain state transitions, per Phase 2b's
finding that state classifications flip on ~33% of readministrations.

Reference: abc-assessment-spec Section 11.7 (trajectory detection)
Reference: Jacobson & Truax (1991), Reliable Change Index
"""

import numpy as np


def detect_reliable_change(
    scores: np.ndarray,
    standard_errors: np.ndarray,
) -> dict:
    """Detect reliable change between consecutive measurement pairs.

    Reference: Jacobson & Truax (1991)

    For each consecutive pair (t, t+1), computes the RCI:
        RCI = (score_{t+1} - score_t) / SE_diff
    where SE_diff = sqrt(SE_t^2 + SE_{t+1}^2)

    Change is reliable if |RCI| > 1.96 (95% confidence).

    Args:
        scores: time series of scores for one person, shape (n_timepoints,)
        standard_errors: SE at each timepoint, shape (n_timepoints,)

    Returns:
        dict with keys (each shape n_timepoints - 1):
            rci_values: RCI for each consecutive pair
            improved: boolean, True if RCI > 1.96
            deteriorated: boolean, True if RCI < -1.96
    """
    n = len(scores)
    rci_values = np.zeros(n - 1)
    improved = np.zeros(n - 1, dtype=bool)
    deteriorated = np.zeros(n - 1, dtype=bool)

    for t in range(n - 1):
        change = scores[t + 1] - scores[t]
        se_diff = np.sqrt(standard_errors[t] ** 2 + standard_errors[t + 1] ** 2)

        rci = change / se_diff if se_diff > 0 else 0.0

        rci_values[t] = rci
        improved[t] = rci > 1.96
        deteriorated[t] = rci < -1.96

    return {
        "rci_values": rci_values,
        "improved": improved,
        "deteriorated": deteriorated,
    }


def detect_trend(
    scores: np.ndarray,
    standard_errors: np.ndarray,
    window_size: int = 4,
) -> dict:
    """Detect linear trend over the most recent window of scores.

    Fits a least-squares line to the last `window_size` scores and
    tests whether the slope exceeds what measurement error alone
    could produce.

    The slope is significant if |slope| > 1.96 * SE_slope, where
    SE_slope accounts for both measurement error and sampling variability.

    Args:
        scores: time series of scores, shape (n_timepoints,)
        standard_errors: SE at each timepoint, shape (n_timepoints,)
        window_size: number of recent timepoints to include

    Returns:
        dict with keys:
            slope: estimated slope per timepoint
            direction: "rising", "declining", or "stable"
            significant: boolean, whether slope exceeds error threshold
            se_slope: standard error of the slope estimate
    """
    n = len(scores)
    w = min(window_size, n)
    window_scores = scores[-w:]
    window_se = standard_errors[-w:]

    # Fit linear regression: score = a + b * time
    time = np.arange(w, dtype=float)
    time_centered = time - np.mean(time)

    slope = (
        np.sum(time_centered * window_scores) / np.sum(time_centered**2)
        if np.sum(time_centered**2) > 0
        else 0.0
    )

    # SE of slope incorporates measurement error
    mean_se = np.mean(window_se)
    residuals = window_scores - (np.mean(window_scores) + slope * time_centered)
    residual_sd = max(np.std(residuals), mean_se)
    sum_sq_time = np.sum(time_centered**2)
    se_slope = residual_sd / np.sqrt(sum_sq_time) if sum_sq_time > 0 else float("inf")

    significant = abs(slope) > 1.96 * se_slope if se_slope < float("inf") else False

    if significant and slope < 0:
        direction = "declining"
    elif significant and slope > 0:
        direction = "rising"
    else:
        direction = "stable"

    return {
        "slope": float(slope),
        "direction": direction,
        "significant": significant,
        "se_slope": float(se_slope),
    }


def classify_trajectory_pattern(
    scores: np.ndarray,
    standard_errors: np.ndarray,
) -> str:
    """Classify a score trajectory into one of five patterns.

    Reference: abc-assessment-spec Section 11.7

    Patterns:
    - stable: no significant trend, low variability
    - gradual_decline: significant negative trend
    - gradual_rise: significant positive trend
    - acute_event: single large reliable drop between consecutive points
    - volatile: high variability without consistent trend

    Args:
        scores: time series for one person, shape (n_timepoints,)
        standard_errors: SE at each timepoint, shape (n_timepoints,)

    Returns:
        One of: "stable", "gradual_decline", "gradual_rise", "acute_event", "volatile"
    """
    n = len(scores)
    if n < 3:
        return "stable"

    # Check for high volatility FIRST (many direction changes override
    # large single drops, since volatility implies repeated swings)
    score_range = np.max(scores) - np.min(scores)
    mean_se = np.mean(standard_errors)
    diffs = np.diff(scores)
    sign_changes = np.sum(np.abs(np.diff(np.sign(diffs))) > 0)
    if sign_changes >= n * 0.6 and score_range > 4 * mean_se:
        return "volatile"

    # Check for acute event: single large drop
    rci_result = detect_reliable_change(scores, standard_errors)
    max_drop = np.min(rci_result["rci_values"])
    if max_drop < -3.0:  # very large single-point drop
        return "acute_event"

    # Check for trend
    trend = detect_trend(scores, standard_errors, window_size=min(n, 6))
    if trend["significant"]:
        if trend["direction"] == "declining":
            return "gradual_decline"
        elif trend["direction"] == "rising":
            return "gradual_rise"

    return "stable"


def compute_individual_trajectory(
    scores: np.ndarray,
    standard_errors: np.ndarray,
) -> dict:
    """Compute all trajectory components for a single person.

    Aggregates reliable change detection, trend analysis, and pattern
    classification into a single result dict.

    Args:
        scores: time series for one person, shape (n_timepoints,)
        standard_errors: SE at each timepoint, shape (n_timepoints,)

    Returns:
        dict with keys:
            scores: input scores (preserved)
            standard_errors: input SEs (preserved)
            reliable_changes: output of detect_reliable_change()
            trend: output of detect_trend()
            pattern: trajectory pattern classification string
    """
    return {
        "scores": scores,
        "standard_errors": standard_errors,
        "reliable_changes": detect_reliable_change(scores, standard_errors),
        "trend": detect_trend(scores, standard_errors),
        "pattern": classify_trajectory_pattern(scores, standard_errors),
    }
