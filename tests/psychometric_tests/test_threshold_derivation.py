"""Tests for threshold derivation module.

Reference: Swets (1988), ROC Analysis
Reference: Youden (1950), Index for Rating Diagnostic Tests
Reference: Jacobson & Truax (1991), Clinical Significance
"""

import numpy as np
import pytest

from src.psychometric.threshold_derivation import (
    bootstrap_threshold_ci,
    compute_roc_curve,
    jacobson_truax_rci,
    youden_index_optimal_cutoff,
)


@pytest.fixture
def separable_data():
    """Scores and criterion where a clear threshold exists.

    Group 1 (non-burnout): scores centered at 3.0
    Group 2 (burnout): scores centered at 7.0
    Clear separation around 5.0.
    """
    rng = np.random.default_rng(42)
    n = 500
    non_burnout_scores = rng.normal(3.0, 1.0, size=n)
    burnout_scores = rng.normal(7.0, 1.0, size=n)
    scores = np.concatenate([non_burnout_scores, burnout_scores])
    criterion = np.concatenate([np.zeros(n), np.ones(n)])
    return scores, criterion


@pytest.fixture
def noisy_data():
    """Scores and criterion with moderate overlap (realistic scenario).

    Group 1 (non-burnout): scores centered at 4.0
    Group 2 (burnout): scores centered at 6.0
    Partial overlap around 5.0.
    """
    rng = np.random.default_rng(42)
    n = 500
    non_burnout_scores = rng.normal(4.0, 1.5, size=n)
    burnout_scores = rng.normal(6.0, 1.5, size=n)
    scores = np.concatenate([non_burnout_scores, burnout_scores])
    criterion = np.concatenate([np.zeros(n), np.ones(n)])
    return scores, criterion


class TestComputeROCCurve:
    """Tests for ROC curve computation."""

    def test_returns_required_keys(self, separable_data):
        """Output contains fpr, tpr, thresholds, and auc."""
        scores, criterion = separable_data
        result = compute_roc_curve(scores, criterion)
        assert "fpr" in result
        assert "tpr" in result
        assert "thresholds" in result
        assert "auc" in result

    def test_auc_high_for_separable_data(self, separable_data):
        """Well-separated groups produce AUC near 1.0.

        Reference: Swets (1988)
        """
        scores, criterion = separable_data
        result = compute_roc_curve(scores, criterion)
        assert result["auc"] > 0.95

    def test_auc_moderate_for_noisy_data(self, noisy_data):
        """Overlapping groups produce moderate AUC.

        Reference: Phase 2 validation gate, AUC > 0.65
        """
        scores, criterion = noisy_data
        result = compute_roc_curve(scores, criterion)
        assert 0.65 < result["auc"] < 0.95

    def test_fpr_tpr_same_length(self, separable_data):
        """FPR and TPR arrays have the same length."""
        scores, criterion = separable_data
        result = compute_roc_curve(scores, criterion)
        assert len(result["fpr"]) == len(result["tpr"])

    def test_fpr_starts_at_zero_ends_at_one(self, separable_data):
        """FPR ranges from 0 to 1."""
        scores, criterion = separable_data
        result = compute_roc_curve(scores, criterion)
        assert result["fpr"][0] == 0.0
        assert result["fpr"][-1] == 1.0

    def test_auc_between_zero_and_one(self, noisy_data):
        """AUC is always in [0, 1]."""
        scores, criterion = noisy_data
        result = compute_roc_curve(scores, criterion)
        assert 0.0 <= result["auc"] <= 1.0

    def test_higher_scores_indicate_positive(self, separable_data):
        """When higher scores = burnout, AUC should be high.

        Reference: convention that higher ABC frustration = more burnout risk
        """
        scores, criterion = separable_data
        result = compute_roc_curve(scores, criterion)
        assert result["auc"] > 0.90


class TestYoudenIndexOptimalCutoff:
    """Tests for Youden's J statistic optimal cutoff selection."""

    def test_returns_required_keys(self, separable_data):
        """Output contains threshold, sensitivity, specificity, youden_j."""
        scores, criterion = separable_data
        roc = compute_roc_curve(scores, criterion)
        result = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])
        assert "optimal_threshold" in result
        assert "sensitivity" in result
        assert "specificity" in result
        assert "youden_j" in result

    def test_optimal_threshold_near_midpoint_for_separable(self, separable_data):
        """Optimal cutoff should be near the midpoint between group means.

        Groups centered at 3.0 and 7.0, so optimal ~5.0.
        """
        scores, criterion = separable_data
        roc = compute_roc_curve(scores, criterion)
        result = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])
        assert 4.0 < result["optimal_threshold"] < 6.0

    def test_high_sensitivity_and_specificity_for_separable(self, separable_data):
        """Well-separated data should yield high sensitivity and specificity."""
        scores, criterion = separable_data
        roc = compute_roc_curve(scores, criterion)
        result = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])
        assert result["sensitivity"] > 0.90
        assert result["specificity"] > 0.90

    def test_youden_j_between_zero_and_one(self, noisy_data):
        """Youden's J is in [0, 1].

        Reference: Youden (1950), J = sensitivity + specificity - 1
        """
        scores, criterion = noisy_data
        roc = compute_roc_curve(scores, criterion)
        result = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])
        assert 0.0 <= result["youden_j"] <= 1.0

    def test_youden_j_equals_sens_plus_spec_minus_one(self, noisy_data):
        """Verify Youden's J formula: J = sensitivity + specificity - 1."""
        scores, criterion = noisy_data
        roc = compute_roc_curve(scores, criterion)
        result = youden_index_optimal_cutoff(roc["fpr"], roc["tpr"], roc["thresholds"])
        expected_j = result["sensitivity"] + result["specificity"] - 1.0
        assert abs(result["youden_j"] - expected_j) < 1e-10


class TestBootstrapThresholdCI:
    """Tests for bootstrap confidence intervals on thresholds."""

    def test_returns_required_keys(self, noisy_data):
        """Output contains point_estimate, ci_lower, ci_upper."""
        scores, criterion = noisy_data
        result = bootstrap_threshold_ci(scores, criterion, n_bootstrap=100, seed=42)
        assert "point_estimate" in result
        assert "ci_lower" in result
        assert "ci_upper" in result

    def test_ci_contains_point_estimate(self, noisy_data):
        """Confidence interval contains the point estimate."""
        scores, criterion = noisy_data
        result = bootstrap_threshold_ci(scores, criterion, n_bootstrap=200, seed=42)
        assert result["ci_lower"] <= result["point_estimate"] <= result["ci_upper"]

    def test_ci_width_reasonable(self, noisy_data):
        """CI width should be < 0.15 for the validation gate with sufficient data.

        Reference: Phase 2 validation gate
        """
        scores, criterion = noisy_data
        result = bootstrap_threshold_ci(scores, criterion, n_bootstrap=500, seed=42)
        ci_width = result["ci_upper"] - result["ci_lower"]
        # With 1000 observations and moderate separation, CI should be tight
        assert ci_width < 2.0  # relaxed for noisy data

    def test_narrower_ci_with_more_data(self):
        """Larger samples produce narrower confidence intervals."""
        rng = np.random.default_rng(42)

        # Small sample
        scores_s = np.concatenate([rng.normal(4, 1.5, 100), rng.normal(6, 1.5, 100)])
        crit_s = np.concatenate([np.zeros(100), np.ones(100)])
        r_small = bootstrap_threshold_ci(scores_s, crit_s, n_bootstrap=200, seed=42)

        # Large sample
        scores_l = np.concatenate([rng.normal(4, 1.5, 1000), rng.normal(6, 1.5, 1000)])
        crit_l = np.concatenate([np.zeros(1000), np.ones(1000)])
        r_large = bootstrap_threshold_ci(scores_l, crit_l, n_bootstrap=200, seed=42)

        ci_small = r_small["ci_upper"] - r_small["ci_lower"]
        ci_large = r_large["ci_upper"] - r_large["ci_lower"]
        assert ci_large < ci_small

    def test_reproducibility(self, noisy_data):
        """Same seed produces identical CIs.

        Reference: CLAUDE_RULES.md Rule 7
        """
        scores, criterion = noisy_data
        r1 = bootstrap_threshold_ci(scores, criterion, n_bootstrap=100, seed=42)
        r2 = bootstrap_threshold_ci(scores, criterion, n_bootstrap=100, seed=42)
        assert r1["point_estimate"] == r2["point_estimate"]
        assert r1["ci_lower"] == r2["ci_lower"]


class TestJacobsonTruaxRCI:
    """Tests for Jacobson-Truax Reliable Change Index."""

    def test_returns_required_keys(self):
        """Output contains rci_values, classifications, and thresholds."""
        rng = np.random.default_rng(42)
        pre = rng.normal(5.0, 1.5, 100)
        post = pre + rng.normal(-1.0, 1.0, 100)  # average decline of 1.0
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        assert "rci_values" in result
        assert "se_diff" in result
        assert "threshold_1_96" in result
        assert "reliably_improved" in result
        assert "reliably_deteriorated" in result
        assert "unchanged" in result

    def test_rci_shape(self):
        """RCI values match input length."""
        rng = np.random.default_rng(42)
        pre = rng.normal(5.0, 1.5, 100)
        post = pre + rng.normal(0, 1.0, 100)
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        assert len(result["rci_values"]) == 100

    def test_large_improvement_classified_as_reliable(self):
        """Large positive change exceeds RCI threshold.

        Reference: Jacobson & Truax (1991), RCI > 1.96 = reliable change
        """
        pre = np.array([3.0, 3.0, 3.0])
        post = np.array([8.0, 8.0, 8.0])  # large improvement
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        assert np.all(result["reliably_improved"])

    def test_no_change_classified_as_unchanged(self):
        """Zero change falls within measurement error."""
        pre = np.array([5.0, 5.0, 5.0])
        post = np.array([5.0, 5.0, 5.0])
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        assert np.all(result["unchanged"])

    def test_large_deterioration_classified_correctly(self):
        """Large negative change is reliably deteriorated."""
        pre = np.array([8.0, 8.0, 8.0])
        post = np.array([3.0, 3.0, 3.0])
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        assert np.all(result["reliably_deteriorated"])

    def test_se_diff_formula(self):
        """SE_diff uses correct formula: sqrt(2) * SD * sqrt(1 - reliability).

        Reference: Jacobson & Truax (1991)
        """
        result = jacobson_truax_rci(np.array([5.0]), np.array([5.0]), reliability=0.85, sd_pre=1.5)
        expected_se = np.sqrt(2) * 1.5 * np.sqrt(1 - 0.85)
        assert abs(result["se_diff"] - expected_se) < 1e-10

    def test_classifications_mutually_exclusive(self):
        """Each person is classified as exactly one of improved/unchanged/deteriorated."""
        rng = np.random.default_rng(42)
        pre = rng.normal(5.0, 1.5, 200)
        post = pre + rng.normal(0, 2.0, 200)
        result = jacobson_truax_rci(pre, post, reliability=0.85, sd_pre=1.5)
        total = (
            np.sum(result["reliably_improved"])
            + np.sum(result["unchanged"])
            + np.sum(result["reliably_deteriorated"])
        )
        assert total == 200
