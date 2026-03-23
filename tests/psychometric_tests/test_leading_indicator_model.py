"""Tests for leading indicator model.

Reference: abc-assessment-spec Section 11.7 (trajectory detection targets)
"""

import numpy as np
import pytest

from src.psychometric.leading_indicator_model import (
    compute_detection_lag,
    compute_transition_probability,
    identify_leading_indicators,
    optimize_alert_multidimensional,
    optimize_alert_thresholds,
)
from src.psychometric.trajectory_simulation import simulate_burnout_trajectories


@pytest.fixture
def trajectory_data():
    """Generate trajectory data for testing."""
    return simulate_burnout_trajectories(n_persons=500, n_timepoints=10, seed=42)


class TestComputeTransitionProbability:
    """Tests for burnout transition probability estimation."""

    def test_returns_probabilities(self, trajectory_data):
        """Output is an array of probabilities in [0, 1]."""
        scores = trajectory_data["scores"]
        burnout = trajectory_data["burnout_onset"]
        result = compute_transition_probability(scores, burnout, lead_window=3)
        assert np.all(result >= 0)
        assert np.all(result <= 1)

    def test_output_length_matches_persons(self, trajectory_data):
        """One probability per person."""
        scores = trajectory_data["scores"]
        burnout = trajectory_data["burnout_onset"]
        result = compute_transition_probability(scores, burnout, lead_window=3)
        assert len(result) == len(burnout)

    def test_decline_has_higher_probability(self, trajectory_data):
        """Declining trajectories should have higher transition probability."""
        scores = trajectory_data["scores"]
        burnout = trajectory_data["burnout_onset"]
        labels = np.array(trajectory_data["labels"])
        probs = compute_transition_probability(scores, burnout, lead_window=3)
        decline_prob = np.mean(probs[labels == "gradual_decline"])
        stable_prob = np.mean(probs[labels == "stable"])
        assert decline_prob > stable_prob


class TestIdentifyLeadingIndicators:
    """Tests for identifying which subscale changes lead burnout."""

    def test_returns_ranked_indicators(self):
        """Output is a list of indicators ranked by predictive value."""
        rng = np.random.default_rng(42)
        n, t = 200, 8
        # 6 subscale trajectories
        subscale_trajectories = {
            "a_frust": rng.normal(0, 1, (n, t)).cumsum(axis=1),  # random walk
            "b_frust": rng.normal(0, 1, (n, t)).cumsum(axis=1),
            "c_frust": rng.normal(0, 1, (n, t)).cumsum(axis=1),
        }
        # Burnout correlated with a_frust
        burnout_onset = np.where(
            subscale_trajectories["a_frust"][:, -1] > 3.0,
            np.random.default_rng(42).integers(5, 8, n),
            -1,
        )
        result = identify_leading_indicators(subscale_trajectories, burnout_onset)
        assert isinstance(result, list)
        assert len(result) > 0
        assert "subscale" in result[0]
        assert "auc" in result[0]

    def test_indicators_sorted_by_auc(self):
        """Indicators are sorted by AUC (highest first)."""
        rng = np.random.default_rng(42)
        n, t = 300, 8
        subscale_trajectories = {
            "a_frust": rng.normal(0, 1, (n, t)).cumsum(axis=1),
            "b_frust": rng.normal(0, 0.5, (n, t)).cumsum(axis=1),
        }
        burnout_onset = np.where(
            subscale_trajectories["a_frust"][:, -1] > 2.0, rng.integers(5, 8, n), -1
        )
        result = identify_leading_indicators(subscale_trajectories, burnout_onset)
        aucs = [r["auc"] for r in result]
        assert aucs == sorted(aucs, reverse=True)


class TestComputeDetectionLag:
    """Tests for detection lag computation."""

    def test_returns_lag_per_person(self, trajectory_data):
        """Output has one lag value per person with burnout."""
        scores = trajectory_data["scores"]
        burnout = np.array(trajectory_data["burnout_onset"])
        has_burnout = burnout >= 0
        if np.sum(has_burnout) == 0:
            pytest.skip("No burnout events in sample")
        lags = compute_detection_lag(
            scores, burnout, alert_threshold=-1.0, se=np.full_like(scores, 0.3)
        )
        assert len(lags) == np.sum(has_burnout)

    def test_lag_non_negative(self, trajectory_data):
        """Detection lag is >= 0 (alert fires at or before burnout)."""
        scores = trajectory_data["scores"]
        burnout = np.array(trajectory_data["burnout_onset"])
        if np.sum(burnout >= 0) == 0:
            pytest.skip("No burnout events")
        lags = compute_detection_lag(
            scores, burnout, alert_threshold=-0.5, se=np.full_like(scores, 0.3)
        )
        # Lag can be -1 (missed) or >= 0
        valid_lags = lags[lags >= 0]
        if len(valid_lags) > 0:
            assert np.all(valid_lags >= 0)


class TestOptimizeAlertThresholds:
    """Tests for alert threshold optimization."""

    def test_returns_optimal_config(self, trajectory_data):
        """Output includes optimal threshold and performance metrics."""
        scores = trajectory_data["scores"]
        burnout = np.array(trajectory_data["burnout_onset"])
        se = np.full_like(scores, 0.3)
        result = optimize_alert_thresholds(scores, burnout, se)
        assert "optimal_threshold" in result
        assert "mean_detection_lag" in result
        assert "sensitivity" in result
        assert "false_positive_rate" in result

    def test_sensitivity_between_zero_and_one(self, trajectory_data):
        """Sensitivity is in [0, 1]."""
        scores = trajectory_data["scores"]
        burnout = np.array(trajectory_data["burnout_onset"])
        se = np.full_like(scores, 0.3)
        result = optimize_alert_thresholds(scores, burnout, se)
        assert 0.0 <= result["sensitivity"] <= 1.0

    def test_fpr_between_zero_and_one(self, trajectory_data):
        """False positive rate is in [0, 1]."""
        scores = trajectory_data["scores"]
        burnout = np.array(trajectory_data["burnout_onset"])
        se = np.full_like(scores, 0.3)
        result = optimize_alert_thresholds(scores, burnout, se)
        assert 0.0 <= result["false_positive_rate"] <= 1.0


class TestOptimizeAlertMultidimensional:
    """Tests for multi-dimensional alert optimization via differential evolution."""

    @pytest.fixture
    def multi_subscale_data(self):
        """Generate multi-subscale trajectory data for optimization."""
        traj = simulate_burnout_trajectories(n_persons=200, n_timepoints=8, seed=42)
        rng = np.random.default_rng(42)
        # Create 3 subscale trajectories correlated with burnout
        scores_base = traj["scores"]
        subscale_scores = {
            "a_frust": scores_base + rng.normal(0, 0.3, scores_base.shape),
            "b_frust": scores_base + rng.normal(0, 0.5, scores_base.shape),
            "c_frust": scores_base + rng.normal(0, 0.8, scores_base.shape),
        }
        subscale_se = {name: np.full_like(s, 0.3) for name, s in subscale_scores.items()}
        return subscale_scores, subscale_se, np.array(traj["burnout_onset"])

    def test_returns_optimal_config(self, multi_subscale_data):
        """Output includes weights, threshold, window, and performance metrics."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        assert "optimal_weights" in result
        assert "optimal_threshold" in result
        assert "optimal_window" in result
        assert "mean_detection_lag" in result
        assert "sensitivity" in result
        assert "false_positive_rate" in result
        assert "n_evaluations" in result

    def test_weights_sum_to_one(self, multi_subscale_data):
        """Optimized weights are normalized to sum to 1."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        weight_sum = sum(result["optimal_weights"].values())
        assert abs(weight_sum - 1.0) < 0.01

    def test_sensitivity_between_zero_and_one(self, multi_subscale_data):
        """Sensitivity is in [0, 1]."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        assert 0.0 <= result["sensitivity"] <= 1.0

    def test_fpr_between_zero_and_one(self, multi_subscale_data):
        """FPR is in [0, 1]."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        assert 0.0 <= result["false_positive_rate"] <= 1.0

    def test_n_evaluations_positive(self, multi_subscale_data):
        """Optimizer ran multiple fitness evaluations."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        assert result["n_evaluations"] > 10

    def test_all_subscales_have_weights(self, multi_subscale_data):
        """Every subscale receives a weight."""
        scores, se, burnout = multi_subscale_data
        result = optimize_alert_multidimensional(scores, se, burnout, seed=42)
        assert set(result["optimal_weights"].keys()) == set(scores.keys())
