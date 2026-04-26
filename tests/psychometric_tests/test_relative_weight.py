"""Tests for Johnson (2000) relative weight analysis.

Reference: Johnson (2000), A Heuristic Method for Estimating the Relative
    Weight of Predictor Variables in Multiple Regression
Reference: Tonidandel & LeBreton (2011, 2015), Relative Importance Analysis
Reference: howard-2024-implementation-plan.md V2-B WI-6
"""

import warnings

import numpy as np
import pytest

from src.psychometric.relative_weight import relative_weights


@pytest.fixture
def rng():
    """Seeded RNG.

    Reference: CLAUDE_RULES.md Rule 7 (reproducibility non-negotiable)
    """
    return np.random.default_rng(42)


def _make_correlated_predictors(
    n: int, p: int, mean_r: float, rng: np.random.Generator
) -> np.ndarray:
    """Generate p predictors with approximate average pairwise correlation mean_r."""
    cov = np.full((p, p), mean_r)
    np.fill_diagonal(cov, 1.0)
    # Cholesky on a positive-definite correlation matrix
    chol = np.linalg.cholesky(cov)
    z = rng.standard_normal((n, p))
    return z @ chol.T


class TestRelativeWeights:
    """Behavioral tests for the Johnson (2000) RWA implementation."""

    def test_weights_sum_to_r_squared(self, rng):
        """Sum of raw weights should equal model R^2.

        Reference: Johnson (2000) eq. 8 (epsilon_j sum to R^2)
        """
        n, p = 400, 4
        x = _make_correlated_predictors(n, p, 0.3, rng)
        beta = np.array([0.4, 0.2, 0.3, 0.1])
        y = x @ beta + rng.standard_normal(n) * 0.6

        # Use small bootstrap for speed
        result = relative_weights(x, y, n_bootstrap=200, ci_method="percentile")
        assert np.isclose(result["raw_weights"].sum(), result["r_squared"], atol=1e-6), (
            f"sum(raw)={result['raw_weights'].sum()}, R^2={result['r_squared']}"
        )

    def test_uncorrelated_predictors_give_squared_betas(self, rng):
        """Orthogonal predictors: raw weights approx squared standardized betas.

        Reference: Johnson (2000) p. 4 (orthogonal special case)
        """
        n, p = 1000, 4
        x = rng.standard_normal((n, p))
        # Orthogonalize to ensure near-zero inter-predictor correlation
        q, _ = np.linalg.qr(x)
        x = q * np.sqrt(n)  # rescale so columns have variance ~ 1
        beta = np.array([0.5, 0.3, 0.2, 0.1])
        y = x @ beta + rng.standard_normal(n) * 0.5

        result = relative_weights(x, y, n_bootstrap=100, ci_method="percentile")
        # Standardized betas in the orthogonal case == correlations
        x_std = (x - x.mean(0)) / x.std(0, ddof=0)
        y_std = (y - y.mean()) / y.std(ddof=0)
        std_beta = (x_std.T @ y_std) / n
        squared_betas = std_beta**2
        assert np.allclose(result["raw_weights"], squared_betas, atol=1e-3)

    def test_rescaled_weights_sum_to_one(self, rng):
        """Rescaled weights always sum to 1.0."""
        n, p = 300, 5
        x = _make_correlated_predictors(n, p, 0.4, rng)
        y = x[:, 0] + 0.5 * x[:, 1] + rng.standard_normal(n)
        result = relative_weights(x, y, n_bootstrap=100, ci_method="percentile")
        assert np.isclose(result["rescaled_weights"].sum(), 1.0, atol=1e-8)

    def test_dominant_predictor_gets_highest_weight(self, rng):
        """One strong + 5 noise: dominant predictor wins.

        Reference: Johnson (2000) example simulations
        """
        n = 500
        x = rng.standard_normal((n, 6))
        y = 2.0 * x[:, 0] + 0.05 * rng.standard_normal(n)
        result = relative_weights(x, y, n_bootstrap=100, ci_method="percentile")
        assert int(np.argmax(result["raw_weights"])) == 0

    def test_handles_six_correlated_subscales(self, rng):
        """Six ABC-like subscales, mean r approx 0.4: returns 6 finite weights."""
        n = 500
        x = _make_correlated_predictors(n, 6, 0.4, rng)
        y = (
            0.3 * x[:, 0]
            + 0.2 * x[:, 1]
            + 0.25 * x[:, 2]
            + 0.1 * x[:, 3]
            + 0.05 * x[:, 4]
            + 0.15 * x[:, 5]
            + rng.standard_normal(n) * 0.5
        )
        result = relative_weights(x, y, n_bootstrap=100, ci_method="percentile")
        assert result["raw_weights"].shape == (6,)
        assert np.all(np.isfinite(result["raw_weights"]))
        assert np.all(result["raw_weights"] >= 0)

    def test_bootstrap_ci_bounds_sensible(self, rng):
        """Bootstrap CI lower < point estimate < upper for the dominant predictor."""
        n = 400
        x = rng.standard_normal((n, 3))
        y = 1.0 * x[:, 0] + 0.5 * x[:, 1] + rng.standard_normal(n) * 0.5
        result = relative_weights(x, y, n_bootstrap=300, ci_method="percentile")
        ci = result["ci_raw"]
        for j in range(3):
            assert ci[j, 0] <= result["raw_weights"][j] + 1e-6
            assert ci[j, 1] >= result["raw_weights"][j] - 1e-6

    def test_perfect_collinearity_raises_warning(self, rng):
        """Duplicate column triggers a warning, does not crash."""
        n = 200
        x_base = rng.standard_normal((n, 3))
        x = np.column_stack([x_base, x_base[:, 0]])  # duplicate first column
        y = x_base[:, 0] + rng.standard_normal(n) * 0.3
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = relative_weights(x, y, n_bootstrap=50, ci_method="percentile")
            assert any(
                "condition" in str(item.message).lower()
                or "collinear" in str(item.message).lower()
                or "singular" in str(item.message).lower()
                for item in w
            ), "Expected a collinearity-related warning"
        assert result["raw_weights"].shape == (4,)
        assert np.all(np.isfinite(result["raw_weights"]))
