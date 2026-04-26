"""Tests for forward/reverse-keying diagnostic.

Reference: Kam, Meyer & Sun (2021), logical response perspective
Reference: howard-2024-implementation-plan.md V2-B WI-13
"""

import numpy as np
import pytest

from src.psychometric.keying_diagnostic import (
    forward_reverse_correlation,
    method_factor_diagnostic,
)


@pytest.fixture
def unidimensional_subscale():
    """Generate a clean unidimensional 6-item subscale.

    4 forward items + 2 reverse items, all loading on the same latent trait.
    Reverse items are stored already reverse-keyed in raw form (low values
    on the original Likert when trait is high), so the recoded mean should
    correlate highly with the forward mean.
    """
    rng = np.random.default_rng(42)
    n = 600
    likert_max = 7
    theta = rng.standard_normal(n)
    forward = np.zeros((n, 4))
    for j in range(4):
        # Map theta to Likert via cumulative thresholds
        raw = theta + 0.4 * rng.standard_normal(n)
        forward[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)
    reverse = np.zeros((n, 2))
    for j in range(2):
        raw = -theta + 0.4 * rng.standard_normal(n)  # reverse-keyed
        reverse[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)
    items = np.column_stack([forward, reverse])
    return items, [0, 1, 2, 3], [4, 5], theta


@pytest.fixture
def artifact_subscale():
    """Reverse items behave as a separate dimension (logical-response artifact).

    Forward items load on theta_a; reverse items load on a different latent
    factor uncorrelated with theta_a. After sign-recoding, correlation
    between forward-mean and reverse-mean should be low.
    """
    rng = np.random.default_rng(42)
    n = 600
    likert_max = 7
    theta_a = rng.standard_normal(n)
    theta_b = rng.standard_normal(n)  # uncorrelated method factor

    forward = np.zeros((n, 4))
    for j in range(4):
        raw = theta_a + 0.3 * rng.standard_normal(n)
        forward[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)

    reverse = np.zeros((n, 2))
    for j in range(2):
        # Reverse items keyed off an independent dimension
        raw = -theta_b + 0.3 * rng.standard_normal(n)
        reverse[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)

    items = np.column_stack([forward, reverse])
    return items, [0, 1, 2, 3], [4, 5]


@pytest.fixture
def quadratic_artifact_data():
    """Data where method-factor variance follows quadratic theta pattern.

    Per Kam (2021): high-trait and low-trait respondents agree with both
    forward and reverse items (logical-response error), producing a U-shaped
    method-factor profile across theta.
    """
    rng = np.random.default_rng(42)
    n = 800
    likert_max = 7
    theta = rng.standard_normal(n)

    forward = np.zeros((n, 4))
    for j in range(4):
        raw = theta + 0.3 * rng.standard_normal(n)
        forward[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)

    # Reverse items: nominally -theta, but with a quadratic shift that
    # raises both the very-low-theta and very-high-theta groups (logical
    # response). After recoding (likert_max + 1 - x), the reverse mean
    # ends up below the forward mean for extreme theta and roughly equal
    # for mid theta -> method factor (rev_recoded - fwd) shows a downward U.
    reverse = np.zeros((n, 2))
    for j in range(2):
        # raw response on original (un-recoded) Likert
        raw = -theta + 0.5 * (theta**2 - 1.0) + 0.2 * rng.standard_normal(n)
        reverse[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)

    items = np.column_stack([forward, reverse])
    return items, [0, 1, 2, 3], [4, 5], theta


@pytest.fixture
def clean_data_for_method_test():
    """Strictly unidimensional data: no quadratic artifact expected."""
    rng = np.random.default_rng(42)
    n = 800
    likert_max = 7
    theta = rng.standard_normal(n)
    forward = np.zeros((n, 4))
    for j in range(4):
        raw = theta + 0.3 * rng.standard_normal(n)
        forward[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)
    reverse = np.zeros((n, 2))
    for j in range(2):
        raw = -theta + 0.3 * rng.standard_normal(n)
        reverse[:, j] = np.clip(np.round(4 + raw * 1.2), 1, likert_max)
    items = np.column_stack([forward, reverse])
    return items, [0, 1, 2, 3], [4, 5], theta


class TestForwardReverseCorrelation:
    """Tests for forward_reverse_correlation."""

    def test_forward_reverse_correlation_high_for_unidimensional(self, unidimensional_subscale):
        """Unidimensional synthetic data: correlation > 0.7, flag=False."""
        items, fwd_idx, rev_idx, _ = unidimensional_subscale
        result = forward_reverse_correlation(items, fwd_idx, rev_idx, likert_max=7)
        assert result["correlation"] > 0.70, f"r = {result['correlation']:.3f}"
        assert result["flag"] is False

    def test_forward_reverse_correlation_low_for_artifact(self, artifact_subscale):
        """Data with injected artifact: correlation < 0.6, flag=True."""
        items, fwd_idx, rev_idx = artifact_subscale
        result = forward_reverse_correlation(items, fwd_idx, rev_idx, likert_max=7)
        assert result["correlation"] < 0.60, f"r = {result['correlation']:.3f}"
        assert result["flag"] is True

    def test_listwise_deletion(self, unidimensional_subscale):
        """Data with NaN: n_used reflects listwise drop."""
        items, fwd_idx, rev_idx, _ = unidimensional_subscale
        items_nan = items.astype(float).copy()
        items_nan[0:25, 0] = np.nan
        result = forward_reverse_correlation(items_nan, fwd_idx, rev_idx, likert_max=7)
        assert result["n_used"] == items.shape[0] - 25


class TestMethodFactorDiagnostic:
    """Tests for method_factor_diagnostic."""

    def test_method_factor_quadratic_detected_when_present(self, quadratic_artifact_data):
        """Data with injected quadratic logical-response: artifact_detected=True."""
        items, fwd_idx, rev_idx, theta = quadratic_artifact_data
        result = method_factor_diagnostic(items, fwd_idx, rev_idx, theta, likert_max=7)
        assert result["artifact_detected"] is True, result

    def test_method_factor_no_artifact_when_clean(self, clean_data_for_method_test):
        """Clean data: artifact_detected=False."""
        items, fwd_idx, rev_idx, theta = clean_data_for_method_test
        result = method_factor_diagnostic(items, fwd_idx, rev_idx, theta, likert_max=7)
        assert result["artifact_detected"] is False, result

    def test_method_factor_returns_required_keys(self, clean_data_for_method_test):
        """Required keys present in output."""
        items, fwd_idx, rev_idx, theta = clean_data_for_method_test
        result = method_factor_diagnostic(items, fwd_idx, rev_idx, theta, likert_max=7)
        for key in (
            "method_factor",
            "theta_coefficient",
            "theta_squared_coefficient",
            "theta_squared_p_value",
            "artifact_detected",
        ):
            assert key in result

    def test_method_factor_listwise_with_nan(self, unidimensional_subscale):
        """method_factor length matches retained rows after listwise deletion."""
        items, fwd_idx, rev_idx, theta = unidimensional_subscale
        items_nan = items.astype(float).copy()
        items_nan[0:10, 0] = np.nan
        result = method_factor_diagnostic(items_nan, fwd_idx, rev_idx, theta, likert_max=7)
        assert len(result["method_factor"]) == items.shape[0] - 10
