"""Johnson (2000) relative weight analysis for ABC subscale predictors.

Decomposes R^2 across correlated predictors via an SVD-based orthogonal
transformation. Returns raw weights (sum to R^2) and rescaled weights
(sum to 1.0), with bootstrap confidence intervals.

Use case for ABC: the six subscales (a_sat, a_frust, b_sat, b_frust,
c_sat, c_frust) are highly inter-correlated. OLS coefficients are
unstable and uninterpretable as importance. Relative weights are stable
under collinearity and have a clear additive interpretation.

Reference: Johnson (2000), Multivariate Behavioral Research, 35(1), 1-19
Reference: Tonidandel & LeBreton (2011, 2015), Organizational Research Methods
Reference: howard-2024-implementation-plan.md V2-B WI-6
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy.stats import bootstrap


def _drop_nan_rows(predictors: np.ndarray, criterion: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Listwise deletion of rows with any NaN in predictors or criterion."""
    mask = ~np.isnan(predictors).any(axis=1) & ~np.isnan(criterion)
    return predictors[mask], criterion[mask]


def _zscore(matrix: np.ndarray) -> np.ndarray:
    """Z-score columns (population SD, ddof=0) used because RWA operates on correlations."""
    mean = matrix.mean(axis=0)
    sd = matrix.std(axis=0, ddof=0)
    sd = np.where(sd == 0, 1.0, sd)
    return (matrix - mean) / sd


def _compute_raw_weights(predictors: np.ndarray, criterion: np.ndarray) -> tuple[np.ndarray, float]:
    """Five-step Johnson (2000) computation of raw relative weights and R^2.

    Reference: Johnson (2000) eqs. 5-8
    """
    # Step 1: standardize. Listwise deletion already done by caller.
    x_std = _zscore(predictors)
    y_std = _zscore(criterion.reshape(-1, 1)).ravel()
    n = x_std.shape[0]

    # Step 2: correlation matrices.
    # Reference: Johnson (2000) eq. 5 (R_xx, R_xy)
    r_xx = (x_std.T @ x_std) / n
    r_xy = (x_std.T @ y_std) / n

    # Step 3: eigendecomposition of R_xx (R_xx is symmetric positive semi-definite).
    # Reference: Johnson (2000) eq. 6 (PCA of predictor correlation matrix)
    eigvals, eigvecs = np.linalg.eigh(r_xx)
    # Order does not matter for the final weights; we just need numerical stability.
    if eigvals.size > 0 and eigvals[0] > 0:
        condition = float(eigvals[-1] / eigvals[0]) if eigvals[0] > 0 else float("inf")
    else:
        condition = float("inf")
    if condition > 1e6:
        warnings.warn(
            f"Predictor correlation matrix is near-singular "
            f"(condition number = {condition:.2e}); results may reflect collinearity.",
            stacklevel=3,
        )
    eigvals_clipped = np.clip(eigvals, 1e-10, None)

    # Step 4: orthogonal transformation matrix Lambda* and standardized betas.
    # Reference: Johnson (2000) eqs. 6-7
    sqrt_lambda = np.sqrt(eigvals_clipped)
    inv_sqrt_lambda = 1.0 / sqrt_lambda
    lambda_star = eigvecs @ np.diag(sqrt_lambda) @ eigvecs.T
    # beta = (Q diag(1/sqrt(L)) Q^T) R_xy: regression of y on the orthogonal components,
    # rotated back into the predictor space.
    beta = (eigvecs @ np.diag(inv_sqrt_lambda) @ eigvecs.T) @ r_xy

    # Step 5: epsilon_j = sum_k Lambda*[j,k]^2 * beta[k]^2
    # Reference: Johnson (2000) eq. 8
    raw_weights = (lambda_star**2) @ (beta**2)

    # R^2 from standardized regression: beta_ols^T R_xy.
    # Reference: standard multivariate regression identity for standardized variables.
    beta_ols = np.linalg.lstsq(r_xx, r_xy, rcond=None)[0]
    r_squared = float(beta_ols @ r_xy)
    r_squared = float(np.clip(r_squared, 0.0, 1.0))
    return raw_weights, r_squared


def _bootstrap_ci(
    predictors: np.ndarray,
    criterion: np.ndarray,
    n_bootstrap: int,
    alpha: float,
    ci_method: str,
    random_seed: int | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Bootstrap CIs for raw and rescaled weights via paired resampling of rows.

    Uses scipy.stats.bootstrap with paired=True so the same row indices are drawn
    from predictors and criterion.

    Reference: Tonidandel & LeBreton (2011) bootstrap CI procedure for RWA
    """
    method_map = {"bca": "BCa", "percentile": "percentile"}
    if ci_method not in method_map:
        raise ValueError(f"ci_method must be 'bca' or 'percentile', got {ci_method!r}")
    scipy_method = method_map[ci_method]

    p = predictors.shape[1]
    indices = np.arange(predictors.shape[0])

    def stat_raw(idx: np.ndarray, axis: int = -1) -> np.ndarray:  # noqa: ARG001
        # scipy bootstrap calls with axis=-1 and shape (n_resamples, n_samples) when vectorized.
        # We supply vectorized=False so axis is ignored; idx is a 1D array of indices.
        idx = np.asarray(idx, dtype=int)
        x_b = predictors[idx]
        y_b = criterion[idx]
        with warnings.catch_warnings():
            # Bootstrap resamples may amplify near-collinearity; warnings suppressed
            # to avoid 1000s of identical warnings during resampling.
            warnings.simplefilter("ignore")
            raw_b, _ = _compute_raw_weights(x_b, y_b)
        return raw_b

    def stat_rescaled(idx: np.ndarray, axis: int = -1) -> np.ndarray:  # noqa: ARG001
        idx = np.asarray(idx, dtype=int)
        x_b = predictors[idx]
        y_b = criterion[idx]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            raw_b, _ = _compute_raw_weights(x_b, y_b)
        total = raw_b.sum()
        if total <= 0:
            return np.full(p, np.nan)
        return raw_b / total

    rng = np.random.default_rng(random_seed)
    confidence_level = 1.0 - alpha

    # scipy.stats.bootstrap returns one CI per output element when statistic returns a vector.
    # Vectorized=False because our statistic is not vectorizable across resamples.
    res_raw = bootstrap(
        (indices,),
        stat_raw,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        method=scipy_method,
        vectorized=False,
        rng=rng,
    )
    res_rescaled = bootstrap(
        (indices,),
        stat_rescaled,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        method=scipy_method,
        vectorized=False,
        rng=np.random.default_rng(random_seed),
    )

    ci_raw = np.column_stack([res_raw.confidence_interval.low, res_raw.confidence_interval.high])
    ci_rescaled = np.column_stack(
        [res_rescaled.confidence_interval.low, res_rescaled.confidence_interval.high]
    )
    return ci_raw, ci_rescaled


def relative_weights(
    predictors: np.ndarray,
    criterion: np.ndarray,
    n_bootstrap: int = 10000,
    alpha: float = 0.05,
    ci_method: str = "bca",
    random_seed: int | None = 42,
) -> dict:
    """Johnson (2000) relative weight analysis.

    Decomposes R^2 across correlated predictors via an SVD-based orthogonal
    transformation. Returns raw weights (sum to R^2), rescaled weights
    (sum to 1.0), and bootstrap CIs.

    Reference: Johnson (2000); Tonidandel & LeBreton (2011, 2015)
    Reference: howard-2024-implementation-plan.md V2-B WI-6

    Args:
        predictors: (n, p) predictor matrix
        criterion: (n,) criterion vector
        n_bootstrap: number of bootstrap resamples (default 10000)
        alpha: 1 - confidence level (default 0.05 -> 95% CI)
        ci_method: "bca" or "percentile"
        random_seed: seed for the bootstrap RNG

    Returns:
        dict with keys:
            r_squared: float
            raw_weights: np.ndarray (p,)         # sums to r_squared
            rescaled_weights: np.ndarray (p,)    # sums to 1.0
            ci_raw: np.ndarray (p, 2)            # [lower, upper] for raw weights
            ci_rescaled: np.ndarray (p, 2)       # for rescaled weights
    """
    predictors = np.asarray(predictors, dtype=float)
    criterion = np.asarray(criterion, dtype=float).ravel()
    if predictors.ndim != 2:
        raise ValueError(f"predictors must be 2D, got shape {predictors.shape}")
    if predictors.shape[0] != criterion.shape[0]:
        raise ValueError(
            f"row mismatch: predictors {predictors.shape[0]} vs criterion {criterion.shape[0]}"
        )

    predictors, criterion = _drop_nan_rows(predictors, criterion)
    if predictors.shape[0] < predictors.shape[1] + 2:
        raise ValueError(
            f"after listwise deletion, n={predictors.shape[0]} is too small "
            f"for p={predictors.shape[1]} predictors"
        )

    raw_weights, r_squared = _compute_raw_weights(predictors, criterion)
    total = raw_weights.sum()
    rescaled_weights = raw_weights / total if total > 0 else np.full_like(raw_weights, np.nan)

    ci_raw, ci_rescaled = _bootstrap_ci(
        predictors, criterion, n_bootstrap, alpha, ci_method, random_seed
    )

    return {
        "r_squared": r_squared,
        "raw_weights": raw_weights,
        "rescaled_weights": rescaled_weights,
        "ci_raw": ci_raw,
        "ci_rescaled": ci_rescaled,
    }
