"""Edwards (2001) polynomial regression and response surface analysis.

Replaces the legacy difference-score approach (`src/python_scoring/context_gap.py`)
with a polynomial regression of the criterion on Personal, Team, their
product, and their squared terms. Tests the difference-score constraints
as a nested model comparison and reports response-surface features
(line-of-agreement slope, line-of-disagreement slope, curvatures, surface peak).

Reference: Edwards (2001), Ten Difference Score Myths,
    Organizational Research Methods, 4, 265-287
Reference: Shanock et al. (2010), Polynomial Regression with Response Surface Analysis
Reference: howard-2024-implementation-plan.md V2-B WI-9
"""

from __future__ import annotations

import numpy as np
from scipy.stats import f as f_dist


def _design_matrix(personal: np.ndarray, team: np.ndarray) -> np.ndarray:
    """Build the polynomial regression design matrix.

    Columns: [1, P, T, P^2, P*T, T^2]

    Reference: Edwards (2001) eq. 4
    """
    p = np.asarray(personal, dtype=float).ravel()
    t = np.asarray(team, dtype=float).ravel()
    intercept = np.ones_like(p)
    return np.column_stack([intercept, p, t, p**2, p * t, t**2])


def _ols_fit(design: np.ndarray, outcome: np.ndarray) -> dict:
    """OLS fit returning coefficients, residuals, and standard errors.

    Reference: standard OLS via numpy.linalg.lstsq + (X'X)^{-1} sigma^2 for SE
    """
    n, k = design.shape
    coef, _residual_ss, _rank, _sv = np.linalg.lstsq(design, outcome, rcond=None)
    residuals = outcome - design @ coef
    rss = float(residuals @ residuals)
    df_resid = n - k
    sigma2 = rss / df_resid if df_resid > 0 else float("nan")

    # Variance-covariance matrix (X'X)^{-1} * sigma^2 with pseudo-inverse for safety.
    xtx_inv = np.linalg.pinv(design.T @ design)
    cov_beta = xtx_inv * sigma2
    se = np.sqrt(np.clip(np.diag(cov_beta), 0, None))

    tss = float(np.sum((outcome - outcome.mean()) ** 2))
    r_squared = 1.0 - rss / tss if tss > 0 else 0.0

    return {
        "coef": coef,
        "se": se,
        "rss": rss,
        "df_resid": df_resid,
        "r_squared": float(r_squared),
        "n": n,
        "k": k,
    }


def _surface_features(coef: np.ndarray) -> dict:
    """Compute response-surface features from polynomial coefficients.

    Reference: Edwards (2001) Table 1; Shanock et al. (2010) eqs. 1-4
    """
    b0, b1, b2, b3, b4, b5 = coef.tolist()

    # Surface peak: solve gradient = 0.
    # dY/dP = b1 + 2*b3*P + b4*T = 0
    # dY/dT = b2 + b4*P + 2*b5*T = 0
    # Reference: Edwards (2001) p. 277 (stationary point of quadratic surface)
    hessian = np.array([[2 * b3, b4], [b4, 2 * b5]])
    grad_const = -np.array([b1, b2])
    peak_personal: float | None
    peak_team: float | None
    peak_outcome: float | None
    det_h = float(np.linalg.det(hessian))
    if abs(det_h) < 1e-12:
        # Saddle / degenerate
        peak_personal = None
        peak_team = None
        peak_outcome = None
    else:
        try:
            peak = np.linalg.solve(hessian, grad_const)
            peak_personal = float(peak[0])
            peak_team = float(peak[1])
            peak_outcome = float(
                b0
                + b1 * peak_personal
                + b2 * peak_team
                + b3 * peak_personal**2
                + b4 * peak_personal * peak_team
                + b5 * peak_team**2
            )
        except np.linalg.LinAlgError:
            peak_personal = peak_team = peak_outcome = None

    return {
        # Slope along line of agreement (P = T): dY/dP|P=T = b1 + b2 (linear part)
        # Reference: Shanock et al. (2010) eq. 1
        "line_of_agreement_slope": float(b1 + b2),
        # Slope along line of disagreement (P = -T): dY/dP|T=-P = b1 - b2
        # Reference: Shanock et al. (2010) eq. 3
        "line_of_disagreement_slope": float(b1 - b2),
        # Curvature along agreement: b3 + b4 + b5
        # Reference: Shanock et al. (2010) eq. 2
        "curvature_along_agreement": float(b3 + b4 + b5),
        # Curvature along disagreement: b3 - b4 + b5
        # Reference: Shanock et al. (2010) eq. 4
        "curvature_along_disagreement": float(b3 - b4 + b5),
        "peak_personal": peak_personal,
        "peak_team": peak_team,
        "peak_outcome": peak_outcome,
    }


def fit_response_surface(
    personal: np.ndarray,
    team: np.ndarray,
    outcome: np.ndarray,
) -> dict:
    """Fit polynomial regression: Outcome = b0 + b1*P + b2*T + b3*P^2 + b4*P*T + b5*T^2 + e.

    Reference: Edwards (2001), polynomial regression as alternative to difference scores
    Reference: howard-2024-implementation-plan.md V2-B WI-9

    Args:
        personal: (n,) personal scores
        team: (n,) team scores
        outcome: (n,) outcome variable

    Returns:
        dict with keys:
            coefficients: dict {b0, b1, b2, b3, b4, b5} -> float
            r_squared: float
            coefficient_se: dict mapping each b to standard error
            surface_features: dict with peak coordinates, slopes, curvatures
    """
    p = np.asarray(personal, dtype=float).ravel()
    t = np.asarray(team, dtype=float).ravel()
    y = np.asarray(outcome, dtype=float).ravel()
    if not (p.shape == t.shape == y.shape):
        raise ValueError(f"shape mismatch: personal {p.shape}, team {t.shape}, outcome {y.shape}")

    # Listwise deletion
    mask = np.isfinite(p) & np.isfinite(t) & np.isfinite(y)
    p, t, y = p[mask], t[mask], y[mask]

    design = _design_matrix(p, t)
    fit = _ols_fit(design, y)

    coef_names = ["b0", "b1", "b2", "b3", "b4", "b5"]
    coefficients = {name: float(fit["coef"][i]) for i, name in enumerate(coef_names)}
    coefficient_se = {name: float(fit["se"][i]) for i, name in enumerate(coef_names)}

    return {
        "coefficients": coefficients,
        "r_squared": fit["r_squared"],
        "coefficient_se": coefficient_se,
        "surface_features": _surface_features(fit["coef"]),
    }


def test_difference_score_constraints(
    personal: np.ndarray,
    team: np.ndarray,
    outcome: np.ndarray,
) -> dict:
    """Test the constraints implied by a difference-score model.

    Difference-score hypothesis: Outcome ~ k * (Personal - Team), which implies
    b1 = -b2 AND b3 = b4 = b5 = 0 in the full polynomial.
    Tested as a nested F-test: full (6 params) vs constrained (intercept + (P - T)).

    Reference: Edwards (2001) Myth 1 (constraint implications)
    Reference: howard-2024-implementation-plan.md V2-B WI-9

    Returns:
        dict with keys:
            f_statistic: float
            p_value: float
            df_constraint: int (= 4)
            df_residual: int
            reject_difference_hypothesis: bool (True if p < 0.05)
            effect_size_r_squared_change: float (R^2 lost by imposing constraints)
    """
    p = np.asarray(personal, dtype=float).ravel()
    t = np.asarray(team, dtype=float).ravel()
    y = np.asarray(outcome, dtype=float).ravel()
    mask = np.isfinite(p) & np.isfinite(t) & np.isfinite(y)
    p, t, y = p[mask], t[mask], y[mask]

    full_design = _design_matrix(p, t)
    full_fit = _ols_fit(full_design, y)

    # Constrained model: Y = a0 + a1 * (P - T)
    # Reference: Edwards (2001) eq. 2 (difference-score implied model)
    constrained_design = np.column_stack([np.ones_like(p), p - t])
    constrained_fit = _ols_fit(constrained_design, y)

    df_constraint = 4  # 6 free params vs 2 free params
    df_residual = full_fit["df_resid"]
    rss_full = full_fit["rss"]
    rss_constrained = constrained_fit["rss"]

    # Nested F-test: F = ((RSS_c - RSS_f) / q) / (RSS_f / df_resid_f)
    # Reference: Edwards (2001) p. 269 (nested model comparison)
    if rss_full <= 0 or df_residual <= 0:
        f_statistic = float("inf")
        p_value = 0.0
    else:
        numerator = (rss_constrained - rss_full) / df_constraint
        denominator = rss_full / df_residual
        f_statistic = float(numerator / denominator) if denominator > 0 else float("inf")
        p_value = float(f_dist.sf(f_statistic, df_constraint, df_residual))

    return {
        "f_statistic": f_statistic,
        "p_value": p_value,
        "df_constraint": df_constraint,
        "df_residual": int(df_residual),
        "reject_difference_hypothesis": bool(p_value < 0.05),
        "effect_size_r_squared_change": float(full_fit["r_squared"] - constrained_fit["r_squared"]),
    }


# Prevent pytest from collecting this function as a test (the name is mandated
# by the WI-9 API contract; the leading "test_" refers to a hypothesis test).
test_difference_score_constraints.__test__ = False


def calibrated_concern_probability(
    personal: float,
    team: float,
    surface: dict,
    criterion_threshold: float = 0.5,
) -> float:
    """Probability that the (personal, team) combination predicts a criterion event.

    Replaces the hard -1.5 difference threshold from `context_gap.py`.

    Strategy: predict outcome from the fitted polynomial surface, transform with a
    logistic centered at criterion_threshold. Slope is calibrated so that a one-unit
    deviation from the threshold corresponds to a probability shift of about 0.27.

    Reference: howard-2024-implementation-plan.md V2-B WI-9 (calibrated probability
        of concern based on the fitted surface)

    Args:
        personal: P value for the focal athlete
        team: T value for the focal athlete or context
        surface: output dict from `fit_response_surface`
        criterion_threshold: predicted outcome value at which P(concern) = 0.5

    Returns:
        Probability in [0, 1].
    """
    coef = surface["coefficients"]
    b0 = coef["b0"]
    b1 = coef["b1"]
    b2 = coef["b2"]
    b3 = coef["b3"]
    b4 = coef["b4"]
    b5 = coef["b5"]
    predicted = (
        b0 + b1 * personal + b2 * team + b3 * personal**2 + b4 * personal * team + b5 * team**2
    )
    # Logistic with slope 1: P(concern) = sigmoid(predicted - threshold).
    # Reference: standard logistic transform; threshold at predicted == criterion_threshold
    z = predicted - criterion_threshold
    # Numerically stable sigmoid
    if z >= 0:
        ez = float(np.exp(-z))
        return float(1.0 / (1.0 + ez))
    ez = float(np.exp(z))
    return float(ez / (1.0 + ez))
