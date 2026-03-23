"""Tests for trajectory engine module.

Reference: abc-assessment-spec Section 11.7 (trajectory detection)
Reference: Jacobson & Truax (1991), Reliable Change Index
"""

import numpy as np

from src.psychometric.trajectory_engine import (
    classify_trajectory_pattern,
    compute_individual_trajectory,
    detect_reliable_change,
    detect_trend,
)


class TestDetectReliableChange:
    """Tests for Jacobson-Truax RCI on consecutive measurement pairs."""

    def test_no_change_returns_no_flags(self):
        """Flat scores produce no reliable change flags."""
        scores = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_reliable_change(scores, se)
        assert not np.any(result["improved"])
        assert not np.any(result["deteriorated"])

    def test_large_drop_flagged_as_deterioration(self):
        """A drop exceeding RCI threshold is flagged."""
        scores = np.array([7.0, 7.0, 7.0, 3.0, 3.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_reliable_change(scores, se)
        assert np.any(result["deteriorated"])

    def test_large_rise_flagged_as_improvement(self):
        """A rise exceeding RCI threshold is flagged."""
        scores = np.array([3.0, 3.0, 3.0, 7.0, 7.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_reliable_change(scores, se)
        assert np.any(result["improved"])

    def test_output_length(self):
        """Result arrays have n_timepoints - 1 elements (consecutive pairs)."""
        scores = np.array([5.0, 5.5, 6.0, 5.8, 5.2])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_reliable_change(scores, se)
        assert len(result["rci_values"]) == 4
        assert len(result["improved"]) == 4
        assert len(result["deteriorated"]) == 4

    def test_larger_se_reduces_sensitivity(self):
        """Larger standard errors make the same change non-significant."""
        scores = np.array([5.0, 5.0, 5.0, 3.5, 3.5])
        se_tight = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        se_wide = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        r_tight = detect_reliable_change(scores, se_tight)
        r_wide = detect_reliable_change(scores, se_wide)
        assert np.sum(r_tight["deteriorated"]) >= np.sum(r_wide["deteriorated"])


class TestDetectTrend:
    """Tests for linear trend detection over sliding window."""

    def test_flat_scores_no_trend(self):
        """Flat scores produce no significant trend."""
        scores = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_trend(scores, se, window_size=3)
        assert result["direction"] == "stable"

    def test_declining_scores_negative_trend(self):
        """Steadily declining scores produce a negative trend."""
        scores = np.array([8.0, 7.0, 6.0, 5.0, 4.0, 3.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_trend(scores, se, window_size=4)
        assert result["direction"] == "declining"
        assert result["slope"] < 0

    def test_rising_scores_positive_trend(self):
        """Steadily rising scores produce a positive trend."""
        scores = np.array([3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3, 0.3])
        result = detect_trend(scores, se, window_size=4)
        assert result["direction"] == "rising"
        assert result["slope"] > 0

    def test_returns_slope_and_significance(self):
        """Output includes slope, direction, and significance flag."""
        scores = np.array([5.0, 5.5, 6.0, 6.5])
        se = np.array([0.3, 0.3, 0.3, 0.3])
        result = detect_trend(scores, se, window_size=4)
        assert "slope" in result
        assert "direction" in result
        assert "significant" in result


class TestClassifyTrajectoryPattern:
    """Tests for trajectory pattern classification."""

    def test_stable_pattern(self):
        """Flat scores classify as stable."""
        scores = np.array([5.0, 5.1, 4.9, 5.0, 5.1, 4.9, 5.0, 5.0])
        se = np.full(8, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result == "stable"

    def test_gradual_decline_pattern(self):
        """Steadily declining scores classify as gradual_decline."""
        scores = np.array([8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5])
        se = np.full(8, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result == "gradual_decline"

    def test_gradual_rise_pattern(self):
        """Steadily rising scores classify as gradual_rise."""
        scores = np.array([3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5])
        se = np.full(8, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result == "gradual_rise"

    def test_acute_event_pattern(self):
        """Sudden large drop classifies as acute_event."""
        scores = np.array([7.0, 7.0, 7.0, 7.0, 3.0, 3.0, 3.0, 3.0])
        se = np.full(8, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result == "acute_event"

    def test_volatile_pattern(self):
        """Large fluctuations classify as volatile."""
        scores = np.array([3.0, 7.0, 3.0, 7.0, 3.0, 7.0, 3.0, 7.0])
        se = np.full(8, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result == "volatile"

    def test_returns_string(self):
        """Result is one of the 5 trajectory types."""
        scores = np.array([5.0, 5.0, 5.0, 5.0])
        se = np.full(4, 0.3)
        result = classify_trajectory_pattern(scores, se)
        assert result in {"stable", "gradual_decline", "gradual_rise", "acute_event", "volatile"}


class TestComputeIndividualTrajectory:
    """Tests for individual trajectory computation."""

    def test_returns_all_components(self):
        """Output includes scores, SEs, reliable changes, trend, and pattern."""
        scores = np.array([5.0, 5.5, 6.0, 5.8, 5.2])
        se = np.array([0.3, 0.3, 0.3, 0.3, 0.3])
        result = compute_individual_trajectory(scores, se)
        assert "scores" in result
        assert "standard_errors" in result
        assert "reliable_changes" in result
        assert "trend" in result
        assert "pattern" in result

    def test_scores_preserved(self):
        """Input scores are preserved in output."""
        scores = np.array([5.0, 5.5, 6.0])
        se = np.array([0.3, 0.3, 0.3])
        result = compute_individual_trajectory(scores, se)
        np.testing.assert_array_equal(result["scores"], scores)
