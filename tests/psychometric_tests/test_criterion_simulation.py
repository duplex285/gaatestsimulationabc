"""Tests for criterion simulation module.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
Reference: abc-assessment-spec Section 11.7 (trajectory types)
"""

import numpy as np
from scipy.stats import pearsonr

from src.psychometric.criterion_simulation import (
    simulate_criterion_scores,
    simulate_criterion_trajectories,
)


class TestSimulateCriterionScores:
    """Tests for cross-sectional criterion score generation."""

    def test_output_shape(self):
        """Returns array matching input length."""
        abc_scores = np.random.default_rng(42).standard_normal(200)
        criterion = simulate_criterion_scores(abc_scores, target_correlation=0.6, seed=42)
        assert criterion.shape == (200,)

    def test_achieves_target_correlation(self):
        """Generated criterion correlates with ABC scores near the target.

        Reference: SDT literature, ABQ-ABC correlation ~0.55-0.65
        """
        rng = np.random.default_rng(42)
        abc_scores = rng.standard_normal(1000)
        criterion = simulate_criterion_scores(abc_scores, target_correlation=0.60, seed=42)
        r, _ = pearsonr(abc_scores, criterion)
        assert abs(r - 0.60) < 0.08, f"Achieved r={r:.3f}, target was 0.60"

    def test_different_target_correlations(self):
        """Different target correlations produce different actual correlations."""
        rng = np.random.default_rng(42)
        abc_scores = rng.standard_normal(500)
        c_low = simulate_criterion_scores(abc_scores, target_correlation=0.30, seed=42)
        c_high = simulate_criterion_scores(abc_scores, target_correlation=0.80, seed=42)
        r_low, _ = pearsonr(abc_scores, c_low)
        r_high, _ = pearsonr(abc_scores, c_high)
        assert r_high > r_low

    def test_custom_mean_and_sd(self):
        """Generated scores respect target mean and SD."""
        rng = np.random.default_rng(42)
        abc_scores = rng.standard_normal(1000)
        criterion = simulate_criterion_scores(
            abc_scores,
            target_correlation=0.5,
            criterion_mean=25.0,
            criterion_sd=5.0,
            seed=42,
        )
        assert abs(np.mean(criterion) - 25.0) < 2.0
        assert abs(np.std(criterion) - 5.0) < 1.5

    def test_reproducibility(self):
        """Same seed produces identical output.

        Reference: CLAUDE_RULES.md Rule 7
        """
        abc_scores = np.random.default_rng(42).standard_normal(100)
        c1 = simulate_criterion_scores(abc_scores, target_correlation=0.5, seed=99)
        c2 = simulate_criterion_scores(abc_scores, target_correlation=0.5, seed=99)
        np.testing.assert_array_equal(c1, c2)


class TestSimulateCriterionTrajectories:
    """Tests for longitudinal criterion trajectory generation."""

    def test_output_shape(self):
        """Returns (n_persons, n_timepoints) matrix."""
        rng = np.random.default_rng(42)
        abc_trajectories = rng.standard_normal((100, 8))
        result = simulate_criterion_trajectories(abc_trajectories, target_correlation=0.5, seed=42)
        assert result["criterion"].shape == (100, 8)

    def test_contains_transition_events(self):
        """Output includes boolean transition event markers."""
        rng = np.random.default_rng(42)
        abc_trajectories = rng.standard_normal((100, 8))
        result = simulate_criterion_trajectories(abc_trajectories, target_correlation=0.5, seed=42)
        assert "transitions" in result
        assert result["transitions"].shape == (100, 8)
        assert result["transitions"].dtype == bool

    def test_transition_threshold_respected(self):
        """Transitions only fire when criterion >= threshold."""
        rng = np.random.default_rng(42)
        abc_trajectories = rng.standard_normal((100, 8))
        threshold = 1.5
        result = simulate_criterion_trajectories(
            abc_trajectories,
            target_correlation=0.5,
            transition_threshold=threshold,
            seed=42,
        )
        # Every transition marker should correspond to criterion >= threshold
        for p in range(100):
            for t in range(8):
                if result["transitions"][p, t]:
                    assert result["criterion"][p, t] >= threshold
                else:
                    assert result["criterion"][p, t] < threshold

    def test_contains_transition_timepoint(self):
        """Output includes the first transition timepoint per person (-1 if none)."""
        rng = np.random.default_rng(42)
        abc_trajectories = rng.standard_normal((50, 8))
        result = simulate_criterion_trajectories(abc_trajectories, target_correlation=0.5, seed=42)
        assert "first_transition" in result
        assert result["first_transition"].shape == (50,)
        # Values should be -1 (no transition) or 0..7 (timepoint index)
        assert np.all(result["first_transition"] >= -1)
        assert np.all(result["first_transition"] < 8)

    def test_reproducibility(self):
        """Same seed produces identical trajectories.

        Reference: CLAUDE_RULES.md Rule 7
        """
        rng = np.random.default_rng(42)
        abc = rng.standard_normal((50, 8))
        r1 = simulate_criterion_trajectories(abc, target_correlation=0.5, seed=99)
        r2 = simulate_criterion_trajectories(abc, target_correlation=0.5, seed=99)
        np.testing.assert_array_equal(r1["criterion"], r2["criterion"])
        np.testing.assert_array_equal(r1["transitions"], r2["transitions"])
