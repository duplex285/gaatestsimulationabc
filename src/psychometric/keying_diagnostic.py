"""Forward-only vs reverse-only keying diagnostic.

Implements two complementary tests for whether the satisfaction/frustration
distinction in ABC subscales is substantive or a logical-response artifact
of item-keying direction.

Reference: Kam, Meyer & Sun (2021), Item Keying and Logical Response Errors
Reference: howard-2024-implementation-plan.md V2-B WI-13

Test 1 (forward_reverse_correlation). For each subscale, compute the
correlation between the forward-only mean and the sign-recoded reverse-only
mean. r >= 0.60 indicates the subscale is unidimensional in the direction
the construct theory predicts; r < 0.60 indicates either a logical-response
artifact or genuine bidimensionality.

Test 2 (method_factor_diagnostic). Define a method factor as
(reverse_recoded_mean - forward_mean) and regress it on theta and theta**2.
Per Kam (2021) the logical-response artifact predicts a significant
quadratic term: respondents at both trait extremes endorse forward and
reverse items inconsistently relative to mid-trait respondents.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def _recode_reverse(x: np.ndarray, likert_max: int) -> np.ndarray:
    """Sign-recode reverse-keyed Likert responses.

    Reference: Kam, Meyer & Sun (2021); standard psychometric recoding.

    For a 1..likert_max scale, recoded = likert_max + 1 - x.
    """
    return (likert_max + 1) - x


def forward_reverse_correlation(
    items: np.ndarray,
    forward_indices: list[int],
    reverse_indices: list[int],
    likert_max: int = 7,
) -> dict:
    """Forward-only vs reverse-only subscale-mean correlation.

    Reference: Kam, Meyer & Sun (2021)
    Reference: howard-2024-implementation-plan.md V2-B WI-13

    Args:
        items: (n, n_items) raw Likert responses.
        forward_indices: column indices of positively-keyed items.
        reverse_indices: column indices of negatively-keyed items.
        likert_max: maximum point on the Likert scale (default 7).

    Returns:
        dict with forward_mean (n,), reverse_mean_recoded (n,), correlation,
        n_used (after listwise deletion), flag (True if r < 0.60),
        interpretation.
    """
    if not forward_indices or not reverse_indices:
        raise ValueError("Both forward_indices and reverse_indices must be non-empty.")

    items = np.asarray(items, dtype=float)
    used_cols = forward_indices + reverse_indices
    sub = items[:, used_cols]
    keep = ~np.isnan(sub).any(axis=1)
    n_used = int(keep.sum())
    if n_used < 3:
        raise ValueError(f"Too few complete cases after listwise deletion (n_used={n_used}).")

    fwd = items[keep][:, forward_indices].mean(axis=1)
    rev_raw = items[keep][:, reverse_indices]
    rev_recoded = _recode_reverse(rev_raw, likert_max).mean(axis=1)

    # Correlation: scipy.stats.pearsonr per Rule 1 (use established libraries)
    r, _p = stats.pearsonr(fwd, rev_recoded)
    flag = bool(r < 0.60)
    if r >= 0.60:
        interp = "Subscale appears unidimensional in the direction theory predicts (r >= 0.60)."
    else:
        interp = (
            "Forward and reverse halves diverge (r < 0.60): possible "
            "logical-response artifact or genuine bidimensionality."
        )

    return {
        "forward_mean": fwd,
        "reverse_mean_recoded": rev_recoded,
        "correlation": float(r),
        "n_used": n_used,
        "flag": flag,
        "interpretation": interp,
    }


def method_factor_diagnostic(
    items: np.ndarray,
    forward_indices: list[int],
    reverse_indices: list[int],
    theta: np.ndarray,
    likert_max: int = 7,
) -> dict:
    """Test the Kam (2021) quadratic trait-by-method interaction.

    Reference: Kam, Meyer & Sun (2021)
    Reference: howard-2024-implementation-plan.md V2-B WI-13

    method_factor[i] = reverse_recoded_mean[i] - forward_mean[i]
    Regress method_factor on theta and theta**2.
    If the quadratic coefficient is significant (p < 0.05) and large in
    magnitude (>= 0.10), the logical-response artifact is confirmed.

    Args:
        items: (n, n_items) raw Likert responses.
        forward_indices: column indices of positively-keyed items.
        reverse_indices: column indices of negatively-keyed items.
        theta: (n,) latent trait estimates (e.g., from IRT).
        likert_max: maximum point on the Likert scale (default 7).

    Returns:
        dict with method_factor (n,), theta_coefficient,
        theta_squared_coefficient, theta_squared_p_value, artifact_detected.
    """
    items = np.asarray(items, dtype=float)
    theta = np.asarray(theta, dtype=float)
    if theta.shape[0] != items.shape[0]:
        raise ValueError("theta length must match items rows.")

    used_cols = forward_indices + reverse_indices
    sub = items[:, used_cols]
    keep = ~np.isnan(sub).any(axis=1)
    if not np.all(np.isfinite(theta[keep])):
        keep = keep & np.isfinite(theta)

    n_used = int(keep.sum())
    if n_used < 10:
        raise ValueError(f"Too few complete cases (n_used={n_used}).")

    fwd = items[keep][:, forward_indices].mean(axis=1)
    rev_recoded = _recode_reverse(items[keep][:, reverse_indices], likert_max).mean(axis=1)
    method_factor = rev_recoded - fwd

    th = theta[keep]
    th_sq = th**2

    # OLS via numpy.linalg.lstsq with intercept; Wald-style p-value for the
    # quadratic coefficient using residual variance.
    X = np.column_stack([np.ones(n_used), th, th_sq])
    beta, _resid, _rank, _sv = np.linalg.lstsq(X, method_factor, rcond=None)
    y_hat = X @ beta
    residuals = method_factor - y_hat
    dof = n_used - X.shape[1]
    sigma2 = float(np.sum(residuals**2) / dof) if dof > 0 else np.nan
    # Var(beta) = sigma2 * (X'X)^{-1}
    xtx_inv = np.linalg.inv(X.T @ X)
    var_beta = sigma2 * xtx_inv
    se_quad = float(np.sqrt(var_beta[2, 2]))
    t_quad = float(beta[2] / se_quad) if se_quad > 0 else 0.0
    # Two-sided p-value from t distribution
    p_quad = float(2.0 * (1.0 - stats.t.cdf(abs(t_quad), df=dof)))

    artifact_detected = bool((p_quad < 0.05) and (abs(beta[2]) >= 0.10))

    return {
        "method_factor": method_factor,
        "theta_coefficient": float(beta[1]),
        "theta_squared_coefficient": float(beta[2]),
        "theta_squared_p_value": p_quad,
        "artifact_detected": artifact_detected,
        "n_used": n_used,
    }
