"""Tests for trajectory simulation module.

Reference: abc-assessment-spec Section 11.7 (trajectory types)
"""

import numpy as np

from src.psychometric.trajectory_simulation import (
    simulate_burnout_trajectories,
    simulate_vulnerable_to_distressed_cascade,
)


class TestSimulateBurnoutTrajectories:
    """Tests for longitudinal trajectory generation."""

    def test_output_shape(self):
        """Returns (n_persons, n_timepoints) score matrix."""
        result = simulate_burnout_trajectories(n_persons=100, n_timepoints=10, seed=42)
        assert result["scores"].shape == (100, 10)

    def test_returns_trajectory_labels(self):
        """Each person has a trajectory type label."""
        result = simulate_burnout_trajectories(n_persons=100, n_timepoints=10, seed=42)
        assert "labels" in result
        assert len(result["labels"]) == 100

    def test_trajectory_type_distribution(self):
        """Trajectory types follow approximate target distribution.

        Reference: abc-assessment-spec Section 11.7
        Stable 40%, Gradual Decline 20%, Gradual Rise 20%, Acute 10%, Volatile 10%
        """
        result = simulate_burnout_trajectories(n_persons=1000, n_timepoints=10, seed=42)
        labels = result["labels"]
        counts = {}
        for label in labels:
            counts[label] = counts.get(label, 0) + 1
        # Check all 5 types present
        assert len(counts) == 5
        # Stable should be most common
        assert counts["stable"] >= counts["gradual_decline"]

    def test_decline_trajectories_decrease(self):
        """Gradual decline trajectories show decreasing mean over time."""
        result = simulate_burnout_trajectories(n_persons=500, n_timepoints=10, seed=42)
        decline_mask = np.array(result["labels"]) == "gradual_decline"
        if np.sum(decline_mask) > 10:
            decline_scores = result["scores"][decline_mask]
            early_mean = np.mean(decline_scores[:, :3])
            late_mean = np.mean(decline_scores[:, 7:])
            assert late_mean < early_mean

    def test_rise_trajectories_increase(self):
        """Gradual rise trajectories show increasing mean over time."""
        result = simulate_burnout_trajectories(n_persons=500, n_timepoints=10, seed=42)
        rise_mask = np.array(result["labels"]) == "gradual_rise"
        if np.sum(rise_mask) > 10:
            rise_scores = result["scores"][rise_mask]
            early_mean = np.mean(rise_scores[:, :3])
            late_mean = np.mean(rise_scores[:, 7:])
            assert late_mean > early_mean

    def test_returns_burnout_events(self):
        """Output includes burnout transition events."""
        result = simulate_burnout_trajectories(n_persons=100, n_timepoints=10, seed=42)
        assert "burnout_onset" in result
        assert len(result["burnout_onset"]) == 100
        # -1 means no burnout, otherwise timepoint index
        assert np.all(np.array(result["burnout_onset"]) >= -1)

    def test_decline_has_more_burnout_than_stable(self):
        """Declining trajectories should have more burnout events than stable."""
        result = simulate_burnout_trajectories(n_persons=1000, n_timepoints=10, seed=42)
        labels = np.array(result["labels"])
        onsets = np.array(result["burnout_onset"])
        decline_burnout = np.mean(onsets[labels == "gradual_decline"] >= 0)
        stable_burnout = np.mean(onsets[labels == "stable"] >= 0)
        assert decline_burnout > stable_burnout

    def test_reproducibility(self):
        """Same seed produces identical output."""
        r1 = simulate_burnout_trajectories(n_persons=50, n_timepoints=8, seed=42)
        r2 = simulate_burnout_trajectories(n_persons=50, n_timepoints=8, seed=42)
        np.testing.assert_array_equal(r1["scores"], r2["scores"])


class TestSimulateVulnerableToDistressedCascade:
    """Tests for the Vulnerable-to-Distressed cascade model."""

    def test_output_shape(self):
        """Returns satisfaction and frustration trajectories."""
        result = simulate_vulnerable_to_distressed_cascade(n_persons=50, n_timepoints=10, seed=42)
        assert result["satisfaction"].shape == (50, 10)
        assert result["frustration"].shape == (50, 10)

    def test_satisfaction_declines(self):
        """Satisfaction should decline over the cascade."""
        result = simulate_vulnerable_to_distressed_cascade(n_persons=200, n_timepoints=10, seed=42)
        early_sat = np.mean(result["satisfaction"][:, :3])
        late_sat = np.mean(result["satisfaction"][:, 7:])
        assert late_sat < early_sat

    def test_frustration_increases(self):
        """Frustration should increase over the cascade."""
        result = simulate_vulnerable_to_distressed_cascade(n_persons=200, n_timepoints=10, seed=42)
        early_frust = np.mean(result["frustration"][:, :3])
        late_frust = np.mean(result["frustration"][:, 7:])
        assert late_frust > early_frust

    def test_starts_in_vulnerable_territory(self):
        """Initial scores should be in Vulnerable range (high sat + high frust)."""
        result = simulate_vulnerable_to_distressed_cascade(n_persons=200, n_timepoints=10, seed=42)
        mean_sat_t0 = np.mean(result["satisfaction"][:, 0])
        mean_frust_t0 = np.mean(result["frustration"][:, 0])
        # Should start with high satisfaction and moderate-high frustration
        assert mean_sat_t0 > 5.0
        assert mean_frust_t0 > 3.0

    def test_returns_cascade_lag(self):
        """Output includes the lag between frustration rise and satisfaction drop."""
        result = simulate_vulnerable_to_distressed_cascade(n_persons=50, n_timepoints=10, seed=42)
        assert "cascade_lag" in result
        assert len(result["cascade_lag"]) == 50

    def test_configurable_lag(self):
        """Different lag parameters produce different cascade timing."""
        r_short = simulate_vulnerable_to_distressed_cascade(
            n_persons=100, n_timepoints=10, mean_lag=1, seed=42
        )
        r_long = simulate_vulnerable_to_distressed_cascade(
            n_persons=100, n_timepoints=10, mean_lag=4, seed=42
        )
        assert np.mean(r_long["cascade_lag"]) > np.mean(r_short["cascade_lag"])
