"""Tests for population norming module.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
Reference: McCall (1922), T-score transformation
Reference: PROMIS scoring manual (T-score convention: mean=50, SD=10)
Reference: Lovibond & Lovibond (1995), DASS severity bands
"""

import numpy as np

from src.psychometric.norming import (
    assign_severity_bands,
    build_stratified_norms,
    compute_percentile_ranks,
    compute_t_scores,
)


class TestComputeTScores:
    """Tests for T-score conversion."""

    def test_mean_maps_to_50(self):
        """Population mean maps to T=50.

        Reference: PROMIS convention
        """
        scores = np.array([5.0, 5.0, 5.0])
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=1.5)
        np.testing.assert_almost_equal(result, [50.0, 50.0, 50.0])

    def test_one_sd_above_maps_to_60(self):
        """One SD above the mean maps to T=60."""
        scores = np.array([6.5])
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=1.5)
        np.testing.assert_almost_equal(result, [60.0])

    def test_one_sd_below_maps_to_40(self):
        """One SD below the mean maps to T=40."""
        scores = np.array([3.5])
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=1.5)
        np.testing.assert_almost_equal(result, [40.0])

    def test_output_shape_matches_input(self):
        """Output has same shape as input."""
        scores = np.random.default_rng(42).normal(5.0, 1.5, 100)
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=1.5)
        assert result.shape == scores.shape

    def test_t_score_formula(self):
        """T = 50 + 10 * (raw - mean) / SD.

        Reference: McCall (1922)
        """
        scores = np.array([3.0, 5.0, 7.0])
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=2.0)
        expected = np.array([40.0, 50.0, 60.0])
        np.testing.assert_almost_equal(result, expected)

    def test_preserves_rank_order(self):
        """T-scores preserve the rank order of raw scores."""
        rng = np.random.default_rng(42)
        scores = rng.normal(5.0, 1.5, 50)
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=1.5)
        raw_order = np.argsort(scores)
        t_order = np.argsort(result)
        np.testing.assert_array_equal(raw_order, t_order)

    def test_zero_sd_returns_50(self):
        """Zero reference SD returns T=50 for all scores (degenerate case)."""
        scores = np.array([3.0, 5.0, 7.0])
        result = compute_t_scores(scores, reference_mean=5.0, reference_sd=0.0)
        np.testing.assert_almost_equal(result, [50.0, 50.0, 50.0])


class TestComputePercentileRanks:
    """Tests for percentile rank computation."""

    def test_output_shape(self):
        """Output matches input shape."""
        scores = np.array([3.0, 5.0, 7.0])
        reference = np.random.default_rng(42).normal(5.0, 1.5, 1000)
        result = compute_percentile_ranks(scores, reference)
        assert result.shape == (3,)

    def test_percentiles_between_0_and_100(self):
        """Percentile ranks are in [0, 100]."""
        rng = np.random.default_rng(42)
        scores = rng.normal(5.0, 2.0, 50)
        reference = rng.normal(5.0, 1.5, 1000)
        result = compute_percentile_ranks(scores, reference)
        assert np.all(result >= 0)
        assert np.all(result <= 100)

    def test_median_near_50th_percentile(self):
        """A score at the reference median should be near the 50th percentile."""
        reference = np.random.default_rng(42).normal(5.0, 1.5, 10000)
        median_score = np.array([np.median(reference)])
        result = compute_percentile_ranks(median_score, reference)
        assert 45 < result[0] < 55

    def test_extreme_high_near_100(self):
        """Score far above the reference should be near 100th percentile."""
        reference = np.random.default_rng(42).normal(5.0, 1.5, 1000)
        result = compute_percentile_ranks(np.array([20.0]), reference)
        assert result[0] > 95

    def test_extreme_low_near_0(self):
        """Score far below the reference should be near 0th percentile."""
        reference = np.random.default_rng(42).normal(5.0, 1.5, 1000)
        result = compute_percentile_ranks(np.array([-10.0]), reference)
        assert result[0] < 5

    def test_preserves_rank_order(self):
        """Higher raw scores produce higher percentile ranks."""
        reference = np.random.default_rng(42).normal(5.0, 1.5, 1000)
        scores = np.array([2.0, 4.0, 6.0, 8.0])
        result = compute_percentile_ranks(scores, reference)
        assert np.all(np.diff(result) > 0)


class TestAssignSeverityBands:
    """Tests for severity band assignment from T-scores."""

    def test_normal_band(self):
        """T < 55 is Normal."""
        result = assign_severity_bands(np.array([45.0, 50.0, 54.9]))
        assert all(r == "Normal" for r in result)

    def test_mild_band(self):
        """55 <= T < 60 is Mild."""
        result = assign_severity_bands(np.array([55.0, 57.5, 59.9]))
        assert all(r == "Mild" for r in result)

    def test_moderate_band(self):
        """60 <= T < 65 is Moderate."""
        result = assign_severity_bands(np.array([60.0, 62.5, 64.9]))
        assert all(r == "Moderate" for r in result)

    def test_severe_band(self):
        """65 <= T < 70 is Severe."""
        result = assign_severity_bands(np.array([65.0, 67.5, 69.9]))
        assert all(r == "Severe" for r in result)

    def test_extremely_severe_band(self):
        """T >= 70 is Extremely Severe."""
        result = assign_severity_bands(np.array([70.0, 80.0, 100.0]))
        assert all(r == "Extremely Severe" for r in result)

    def test_output_shape(self):
        """Output length matches input length."""
        t_scores = np.array([40.0, 55.0, 65.0, 75.0])
        result = assign_severity_bands(t_scores)
        assert len(result) == 4

    def test_custom_bands(self):
        """Custom band thresholds work."""
        custom = [
            {"label": "Low", "t_max": 45},
            {"label": "Medium", "t_max": 55},
            {"label": "High", "t_max": 999},
        ]
        result = assign_severity_bands(np.array([40.0, 50.0, 60.0]), bands=custom)
        assert result[0] == "Low"
        assert result[1] == "Medium"
        assert result[2] == "High"


class TestBuildStratifiedNorms:
    """Tests for stratified norm table construction."""

    def test_returns_norms_per_stratum(self):
        """Output contains norm data for each stratum."""
        rng = np.random.default_rng(42)
        n = 300
        data = {
            "a_sat": rng.normal(5.0, 1.5, n),
            "level": np.array(["elite"] * 100 + ["club"] * 100 + ["youth"] * 100),
        }
        result = build_stratified_norms(data, stratification_var="level", score_columns=["a_sat"])
        assert "elite" in result
        assert "club" in result
        assert "youth" in result

    def test_each_stratum_has_mean_and_sd(self):
        """Each stratum reports mean, SD, and n."""
        rng = np.random.default_rng(42)
        n = 200
        data = {
            "a_sat": rng.normal(5.0, 1.5, n),
            "group": np.array(["A"] * 100 + ["B"] * 100),
        }
        result = build_stratified_norms(data, stratification_var="group", score_columns=["a_sat"])
        for stratum in result:
            assert "a_sat" in result[stratum]
            assert "mean" in result[stratum]["a_sat"]
            assert "sd" in result[stratum]["a_sat"]
            assert "n" in result[stratum]["a_sat"]

    def test_overall_norms_included(self):
        """Output includes overall (unstratified) norms."""
        rng = np.random.default_rng(42)
        data = {
            "a_sat": rng.normal(5.0, 1.5, 200),
            "group": np.array(["A"] * 100 + ["B"] * 100),
        }
        result = build_stratified_norms(data, stratification_var="group", score_columns=["a_sat"])
        assert "overall" in result

    def test_multiple_score_columns(self):
        """Works with multiple score columns."""
        rng = np.random.default_rng(42)
        n = 200
        data = {
            "a_sat": rng.normal(5.0, 1.5, n),
            "a_frust": rng.normal(4.0, 1.5, n),
            "group": np.array(["A"] * 100 + ["B"] * 100),
        }
        result = build_stratified_norms(
            data, stratification_var="group", score_columns=["a_sat", "a_frust"]
        )
        assert "a_sat" in result["A"]
        assert "a_frust" in result["A"]
