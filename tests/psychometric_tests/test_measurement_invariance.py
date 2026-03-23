"""Tests for measurement invariance module.

Reference: APA/AERA/NCME Standards (2014), Chapter 3 (Fairness)
Reference: Chen (2007), delta-CFI and delta-RMSEA criteria
Reference: Vandenberg & Lance (2000), Measurement Invariance Review
"""

import pytest

from src.psychometric.invariance_simulation import simulate_multigroup_data
from src.psychometric.measurement_invariance import (
    compute_invariance_summary,
    evaluate_configural_invariance,
    evaluate_metric_invariance,
    evaluate_scalar_invariance,
)


@pytest.fixture
def invariant_data():
    """Two groups with identical factor structure (invariance should hold)."""
    return simulate_multigroup_data(
        group_labels=["group_a", "group_b"],
        n_per_group=300,
        seed=42,
    )


@pytest.fixture
def noninvariant_data():
    """Two groups where one has shifted loadings (metric invariance may fail)."""
    return simulate_multigroup_data(
        group_labels=["standard", "shifted"],
        n_per_group=300,
        loading_shift={"shifted": 0.3},
        seed=42,
    )


@pytest.fixture
def factor_map():
    """Standard ABC factor mapping."""
    mapping = {}
    factors = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    for f_idx, factor in enumerate(factors):
        for i in range(4):
            mapping[f_idx * 4 + i] = factor
    return mapping


@pytest.fixture
def item_names():
    """Standard ABC item names."""
    return [f"{p}{i}" for p in ["AS", "AF", "BS", "BF", "CS", "CF"] for i in range(1, 5)]


class TestTestConfiguralInvariance:
    """Tests for configural invariance (same factor structure across groups)."""

    def test_returns_fit_indices(self, invariant_data, item_names, factor_map):
        """Output includes fit indices for the configural model."""
        result = evaluate_configural_invariance(invariant_data["groups"], item_names, factor_map)
        assert "cfi" in result
        assert "rmsea" in result
        assert "chi2" in result

    def test_acceptable_fit_for_invariant_data(self, invariant_data, item_names, factor_map):
        """Invariant data should produce acceptable configural fit."""
        result = evaluate_configural_invariance(invariant_data["groups"], item_names, factor_map)
        # With clean data, CFI should be reasonable
        if result["cfi"] is not None:
            assert result["cfi"] > 0.80

    def test_returns_per_group_fit(self, invariant_data, item_names, factor_map):
        """Output includes fit per group."""
        result = evaluate_configural_invariance(invariant_data["groups"], item_names, factor_map)
        assert "per_group" in result


class TestTestMetricInvariance:
    """Tests for metric invariance (equal factor loadings across groups)."""

    def test_returns_fit_indices(self, invariant_data, item_names, factor_map):
        """Output includes fit indices for the metric model."""
        result = evaluate_metric_invariance(invariant_data["groups"], item_names, factor_map)
        assert "cfi" in result
        assert "rmsea" in result

    def test_returns_delta_fit(self, invariant_data, item_names, factor_map):
        """Output includes delta-CFI and delta-RMSEA vs configural."""
        result = evaluate_metric_invariance(invariant_data["groups"], item_names, factor_map)
        assert "delta_cfi" in result
        assert "delta_rmsea" in result


class TestTestScalarInvariance:
    """Tests for scalar invariance (equal intercepts across groups)."""

    def test_returns_fit_indices(self, invariant_data, item_names, factor_map):
        """Output includes fit indices for the scalar model."""
        result = evaluate_scalar_invariance(invariant_data["groups"], item_names, factor_map)
        assert "cfi" in result
        assert "rmsea" in result

    def test_returns_delta_fit(self, invariant_data, item_names, factor_map):
        """Output includes delta-CFI and delta-RMSEA vs metric."""
        result = evaluate_scalar_invariance(invariant_data["groups"], item_names, factor_map)
        assert "delta_cfi" in result
        assert "delta_rmsea" in result


class TestComputeInvarianceSummary:
    """Tests for the full invariance summary."""

    def test_returns_all_levels(self, invariant_data, item_names, factor_map):
        """Summary includes configural, metric, and scalar results."""
        result = compute_invariance_summary(invariant_data["groups"], item_names, factor_map)
        assert "configural" in result
        assert "metric" in result
        assert "scalar" in result

    def test_includes_pass_fail(self, invariant_data, item_names, factor_map):
        """Summary includes pass/fail for each level.

        Reference: Chen (2007), delta-CFI < 0.01, delta-RMSEA < 0.015
        """
        result = compute_invariance_summary(invariant_data["groups"], item_names, factor_map)
        assert "metric_holds" in result
        assert "scalar_holds" in result
        assert isinstance(result["metric_holds"], bool)
        assert isinstance(result["scalar_holds"], bool)

    def test_invariant_data_passes(self, invariant_data, item_names, factor_map):
        """Data generated with identical structure should pass invariance."""
        result = compute_invariance_summary(invariant_data["groups"], item_names, factor_map)
        # With clean identical data, both should hold
        assert result["metric_holds"]
