"""Tests for norming simulation module.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
"""

import numpy as np

from src.psychometric.norming_simulation import simulate_stratified_population


class TestSimulateStratifiedPopulation:
    """Tests for stratified synthetic population generation."""

    def test_output_has_required_columns(self):
        """Output contains score columns and stratification variable."""
        result = simulate_stratified_population(seed=42)
        assert "a_sat" in result
        assert "level" in result

    def test_total_n_matches_spec(self):
        """Total respondents matches sum of per-stratum counts."""
        strata = {
            "elite": {"mean_shift": 0.5, "n": 200},
            "club": {"mean_shift": 0.0, "n": 300},
        }
        result = simulate_stratified_population(strata=strata, seed=42)
        assert len(result["a_sat"]) == 500

    def test_strata_labels_present(self):
        """All stratum labels appear in the output."""
        strata = {
            "elite": {"mean_shift": 0.5, "n": 100},
            "club": {"mean_shift": 0.0, "n": 100},
            "youth": {"mean_shift": -0.3, "n": 100},
        }
        result = simulate_stratified_population(strata=strata, seed=42)
        labels = set(result["level"])
        assert labels == {"elite", "club", "youth"}

    def test_mean_shift_applied(self):
        """Positive mean_shift produces higher scores than negative."""
        strata = {
            "high": {"mean_shift": 1.0, "n": 500},
            "low": {"mean_shift": -1.0, "n": 500},
        }
        result = simulate_stratified_population(strata=strata, seed=42)
        high_mask = np.array(result["level"]) == "high"
        low_mask = np.array(result["level"]) == "low"
        high_mean = np.mean(np.array(result["a_sat"])[high_mask])
        low_mean = np.mean(np.array(result["a_sat"])[low_mask])
        assert high_mean > low_mean

    def test_all_six_subscales_present(self):
        """Output includes all 6 ABC subscale scores."""
        result = simulate_stratified_population(seed=42)
        expected = {"a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"}
        assert expected.issubset(set(result.keys()))

    def test_scores_in_plausible_range(self):
        """Scores are in [0, 10] range (clipped)."""
        result = simulate_stratified_population(seed=42)
        for key in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            arr = np.array(result[key])
            assert np.all(arr >= 0), f"{key} has values below 0"
            assert np.all(arr <= 10), f"{key} has values above 10"

    def test_reproducibility(self):
        """Same seed produces identical output.

        Reference: CLAUDE_RULES.md Rule 7
        """
        r1 = simulate_stratified_population(seed=42)
        r2 = simulate_stratified_population(seed=42)
        np.testing.assert_array_equal(r1["a_sat"], r2["a_sat"])

    def test_default_strata(self):
        """Default strata produce a reasonable population."""
        result = simulate_stratified_population(seed=42)
        # Default should have at least 100 respondents
        assert len(result["a_sat"]) >= 100
