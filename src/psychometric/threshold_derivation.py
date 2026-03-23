"""Empirical threshold derivation for ABC Assessment.

Replaces fixed thresholds (6.46, 4.38) with data-derived cutoffs using
ROC analysis, Youden's J statistic, bootstrap confidence intervals, and
the Jacobson-Truax Reliable Change Index.

Reference: Swets (1988), Measuring the Accuracy of Diagnostic Systems, Science
Reference: Youden (1950), Index for Rating Diagnostic Tests, Cancer
Reference: Jacobson & Truax (1991), Clinical Significance, JCCP
Reference: Efron & Tibshirani (1993), An Introduction to the Bootstrap
"""

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def compute_roc_curve(
    scores: np.ndarray,
    criterion: np.ndarray,
) -> dict:
    """Compute ROC curve for scores against a binary criterion.

    Reference: Swets (1988)

    Higher scores are assumed to indicate the positive class (burnout).
    Uses sklearn.metrics.roc_curve internally.

    Args:
        scores: continuous predictor scores, shape (n,)
        criterion: binary criterion (0 = non-burnout, 1 = burnout), shape (n,)

    Returns:
        dict with keys:
            fpr: false positive rates at each threshold
            tpr: true positive rates at each threshold
            thresholds: score values at each operating point
            auc: area under the ROC curve
    """
    fpr, tpr, thresholds = roc_curve(criterion, scores)
    auc = roc_auc_score(criterion, scores)

    return {
        "fpr": fpr,
        "tpr": tpr,
        "thresholds": thresholds,
        "auc": auc,
    }


def youden_index_optimal_cutoff(
    fpr: np.ndarray,
    tpr: np.ndarray,
    thresholds: np.ndarray,
) -> dict:
    """Find the optimal cutoff via Youden's J statistic.

    Reference: Youden (1950)

    J = sensitivity + specificity - 1 = TPR - FPR

    The cutoff maximising J balances sensitivity and specificity equally.

    Args:
        fpr: false positive rates from ROC curve
        tpr: true positive rates from ROC curve
        thresholds: score values at each operating point

    Returns:
        dict with keys:
            optimal_threshold: score value at the optimal operating point
            sensitivity: TPR at optimal point
            specificity: 1 - FPR at optimal point
            youden_j: value of J at optimal point
    """
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)

    sensitivity = tpr[optimal_idx]
    specificity = 1.0 - fpr[optimal_idx]

    return {
        "optimal_threshold": float(thresholds[optimal_idx]),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "youden_j": float(j_scores[optimal_idx]),
    }


def bootstrap_threshold_ci(
    scores: np.ndarray,
    criterion: np.ndarray,
    n_bootstrap: int = 2000,
    ci_level: float = 0.95,
    seed: int = 42,
) -> dict:
    """Bootstrap confidence interval for the optimal ROC threshold.

    Reference: Efron & Tibshirani (1993)

    Resamples the data with replacement, computes the Youden-optimal
    threshold for each resample, and returns the percentile CI.

    Args:
        scores: continuous predictor scores, shape (n,)
        criterion: binary criterion (0/1), shape (n,)
        n_bootstrap: number of bootstrap resamples
        ci_level: confidence level (default 0.95 for 95% CI)
        seed: random seed for reproducibility

    Returns:
        dict with keys:
            point_estimate: Youden-optimal threshold on full data
            ci_lower: lower bound of CI
            ci_upper: upper bound of CI
            bootstrap_thresholds: array of bootstrap threshold estimates
    """
    rng = np.random.default_rng(seed)
    n = len(scores)

    # Point estimate on full data
    roc = compute_roc_curve(scores, criterion)
    point = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])

    # Bootstrap
    bootstrap_thresholds = np.zeros(n_bootstrap)
    for b in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        b_scores = scores[idx]
        b_criterion = criterion[idx]

        # Skip resamples with only one class
        if len(np.unique(b_criterion)) < 2:
            bootstrap_thresholds[b] = point["optimal_threshold"]
            continue

        b_roc = compute_roc_curve(b_scores, b_criterion)
        b_opt = youden_index_optimal_cutoff(b_roc["fpr"], b_roc["tpr"], b_roc["thresholds"])
        bootstrap_thresholds[b] = b_opt["optimal_threshold"]

    alpha = 1.0 - ci_level
    ci_lower = float(np.percentile(bootstrap_thresholds, 100 * alpha / 2))
    ci_upper = float(np.percentile(bootstrap_thresholds, 100 * (1 - alpha / 2)))

    return {
        "point_estimate": point["optimal_threshold"],
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "bootstrap_thresholds": bootstrap_thresholds,
    }


def jacobson_truax_rci(
    pre_scores: np.ndarray,
    post_scores: np.ndarray,
    reliability: float,
    sd_pre: float,
) -> dict:
    """Compute the Jacobson-Truax Reliable Change Index.

    Reference: Jacobson & Truax (1991), Clinical Significance: A Statistical
               Approach to Defining Meaningful Change, JCCP

    The standard error of the difference is:
        SE_diff = sqrt(2) * SD_pre * sqrt(1 - reliability)

    The RCI for each person is:
        RCI = (post - pre) / SE_diff

    Change is reliable if |RCI| > 1.96 (95% confidence level).

    Args:
        pre_scores: baseline scores, shape (n,)
        post_scores: follow-up scores, shape (n,)
        reliability: test-retest or internal consistency reliability coefficient
        sd_pre: standard deviation of the pre-test scores in the reference population

    Returns:
        dict with keys:
            rci_values: RCI per person, shape (n,)
            se_diff: standard error of the difference (scalar)
            threshold_1_96: the change magnitude exceeding 1.96 * SE_diff
            reliably_improved: boolean array, True if RCI > 1.96
            reliably_deteriorated: boolean array, True if RCI < -1.96
            unchanged: boolean array, True if |RCI| <= 1.96
    """
    se_diff = np.sqrt(2) * sd_pre * np.sqrt(1 - reliability)
    change = post_scores - pre_scores
    rci_values = change / se_diff

    reliably_improved = rci_values > 1.96
    reliably_deteriorated = rci_values < -1.96
    unchanged = ~reliably_improved & ~reliably_deteriorated

    return {
        "rci_values": rci_values,
        "se_diff": float(se_diff),
        "threshold_1_96": float(1.96 * se_diff),
        "reliably_improved": reliably_improved,
        "reliably_deteriorated": reliably_deteriorated,
        "unchanged": unchanged,
    }
