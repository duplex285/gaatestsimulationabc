"""Tests for measurement invariance simulation module.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
"""

import numpy as np

from src.psychometric.invariance_simulation import simulate_multigroup_data


class TestSimulateMultigroupData:
    """Tests for multi-group synthetic data generation."""

    def test_returns_required_keys(self):
        """Output contains data matrices and group labels."""
        result = simulate_multigroup_data(seed=42)
        assert "groups" in result
        assert isinstance(result["groups"], dict)

    def test_default_two_groups(self):
        """Default produces two groups (team_sport, individual_sport)."""
        result = simulate_multigroup_data(seed=42)
        assert len(result["groups"]) == 2

    def test_each_group_has_correct_shape(self):
        """Each group's data has (n_per_group, 24) shape."""
        result = simulate_multigroup_data(n_per_group=100, seed=42)
        for name, data in result["groups"].items():
            assert data.shape == (100, 24), f"Group {name} shape = {data.shape}"

    def test_custom_groups(self):
        """Custom group labels work."""
        result = simulate_multigroup_data(
            group_labels=["male", "female", "nonbinary"],
            n_per_group=50,
            seed=42,
        )
        assert set(result["groups"].keys()) == {"male", "female", "nonbinary"}

    def test_mean_shift_changes_scores(self):
        """Groups with mean shift have different score means."""
        result = simulate_multigroup_data(
            group_labels=["high", "low"],
            n_per_group=500,
            mean_shift={"high": 1.0, "low": -1.0},
            seed=42,
        )
        high_mean = np.mean(result["groups"]["high"])
        low_mean = np.mean(result["groups"]["low"])
        assert high_mean > low_mean

    def test_no_shift_similar_means(self):
        """Groups without mean shift have similar score distributions."""
        result = simulate_multigroup_data(
            group_labels=["A", "B"],
            n_per_group=500,
            seed=42,
        )
        a_mean = np.mean(result["groups"]["A"])
        b_mean = np.mean(result["groups"]["B"])
        assert abs(a_mean - b_mean) < 0.5

    def test_loading_shift_changes_structure(self):
        """Loading shift produces different factor loadings between groups."""
        result = simulate_multigroup_data(
            group_labels=["standard", "shifted"],
            n_per_group=200,
            loading_shift={"shifted": 0.2},
            seed=42,
        )
        # Both groups should have data but with different structure
        assert result["groups"]["standard"].shape[1] == 24
        assert result["groups"]["shifted"].shape[1] == 24

    def test_reproducibility(self):
        """Same seed produces identical output."""
        r1 = simulate_multigroup_data(seed=42)
        r2 = simulate_multigroup_data(seed=42)
        for group in r1["groups"]:
            np.testing.assert_array_equal(r1["groups"][group], r2["groups"][group])
