"""Tests for BayesianScorer, ABCBayesianProfile, and classification utilities.

Covers conjugate normal updating, posterior convergence, credible intervals,
domain state classification, and personalized thresholds.
"""

import math

from src.python_scoring.bayesian_scorer import (
    DOMAIN_PAIRS,
    SUBSCALE_NAMES,
    ABCBayesianProfile,
    BayesianScorer,
    classify_with_uncertainty,
)

# ---------------------------------------------------------------------------
# BayesianScorer: initialization
# ---------------------------------------------------------------------------


class TestBayesianScorerInit:
    def test_default_prior(self):
        scorer = BayesianScorer()
        assert scorer.prior_mean == 5.0
        assert scorer.prior_sd == 2.0
        assert scorer.posterior_mean == 5.0
        assert scorer.posterior_sd == 2.0
        assert scorer.measurements_incorporated == 0

    def test_custom_prior(self):
        scorer = BayesianScorer(prior_mean=7.0, prior_sd=1.5)
        assert scorer.prior_mean == 7.0
        assert scorer.prior_sd == 1.5
        assert scorer.posterior_mean == 7.0
        assert scorer.posterior_sd == 1.5


# ---------------------------------------------------------------------------
# Single update: hand-calculated verification
# ---------------------------------------------------------------------------


class TestSingleUpdate:
    def test_single_update_posterior_mean(self):
        """Verify posterior mean by hand calculation.

        Prior: N(5.0, 2.0^2)  =>  precision_prior = 1/4 = 0.25
        Observation: x=8.0, SE=0.8  =>  precision_data = 1/0.64 = 1.5625
        Post precision = 0.25 + 1.5625 = 1.8125
        Post mean = (5.0*0.25 + 8.0*1.5625) / 1.8125
                  = (1.25 + 12.5) / 1.8125
                  = 13.75 / 1.8125
                  = 7.5862...
        Post SD = sqrt(1/1.8125) = sqrt(0.5517...) = 0.7428...
        """
        scorer = BayesianScorer(prior_mean=5.0, prior_sd=2.0)
        result = scorer.update(8.0, measurement_se=0.8)

        expected_mean = 13.75 / 1.8125
        expected_sd = math.sqrt(1.0 / 1.8125)

        assert abs(result["posterior_mean"] - expected_mean) < 1e-6
        assert abs(result["posterior_sd"] - expected_sd) < 1e-6
        assert result["measurements_incorporated"] == 1

    def test_single_update_weights(self):
        """Prior weight and data weight sum to 1.0."""
        scorer = BayesianScorer()
        result = scorer.update(7.0)
        assert abs(result["prior_weight"] + result["data_weight"] - 1.0) < 1e-10

    def test_data_dominates_with_wide_prior(self):
        """Wide prior (sd=10) means data dominates after one observation."""
        scorer = BayesianScorer(prior_mean=5.0, prior_sd=10.0)
        result = scorer.update(8.0, measurement_se=0.8)
        assert result["data_weight"] > 0.99


# ---------------------------------------------------------------------------
# Multiple updates: posterior SD always decreases
# ---------------------------------------------------------------------------


class TestMultipleUpdates:
    def test_posterior_sd_decreases(self):
        """Each update should reduce the posterior SD."""
        scorer = BayesianScorer()
        prev_sd = scorer.posterior_sd
        for score in [6.0, 7.0, 5.5, 6.5, 7.0]:
            result = scorer.update(score)
            assert result["posterior_sd"] < prev_sd
            prev_sd = result["posterior_sd"]

    def test_prior_weight_decreases_monotonically(self):
        """Cumulative original-prior weight should decrease with each measurement.

        Each update reports prior_weight as the fraction of the *current*
        posterior precision attributable to the incoming prior (which is the
        previous posterior). The cumulative weight of the *original* prior
        is the product of all per-step prior weights.
        """
        scorer = BayesianScorer()
        cumulative = 1.0
        prev_cumulative = 1.0
        for score in [6.0, 6.5, 7.0, 5.5, 6.0, 7.5, 6.0]:
            result = scorer.update(score)
            cumulative *= result["prior_weight"]
            assert cumulative < prev_cumulative
            prev_cumulative = cumulative

    def test_posterior_converges_toward_data(self):
        """Repeated high scores should push posterior mean toward the data."""
        scorer = BayesianScorer(prior_mean=5.0, prior_sd=2.0)
        for _ in range(20):
            scorer.update(9.0, measurement_se=0.8)
        assert scorer.posterior_mean > 8.5


# ---------------------------------------------------------------------------
# Credible interval contains posterior mean
# ---------------------------------------------------------------------------


class TestCredibleInterval:
    def test_ci_contains_mean(self):
        scorer = BayesianScorer()
        result = scorer.update(7.0)
        ci_low, ci_high = result["credible_interval_90"]
        assert ci_low < result["posterior_mean"] < ci_high

    def test_ci_shrinks_with_more_data(self):
        scorer = BayesianScorer()
        result1 = scorer.update(6.0)
        width1 = result1["credible_interval_90"][1] - result1["credible_interval_90"][0]
        result2 = scorer.update(6.5)
        width2 = result2["credible_interval_90"][1] - result2["credible_interval_90"][0]
        assert width2 < width1


# ---------------------------------------------------------------------------
# ABCBayesianProfile: update_all returns all 6 subscales
# ---------------------------------------------------------------------------


def _make_subscale_scores(sat=6.0, frust=4.0):
    """Helper: build a subscale dict with uniform sat/frust values."""
    scores = {}
    for name in SUBSCALE_NAMES:
        if name.endswith("_sat"):
            scores[name] = sat
        else:
            scores[name] = frust
    return scores


class TestABCBayesianProfile:
    def test_update_all_returns_all_subscales(self):
        profile = ABCBayesianProfile()
        scores = _make_subscale_scores()
        result = profile.update_all(scores)
        assert set(result["subscales"].keys()) == set(SUBSCALE_NAMES)

    def test_update_all_returns_all_domains(self):
        profile = ABCBayesianProfile()
        scores = _make_subscale_scores()
        result = profile.update_all(scores)
        assert set(result["domain_states"].keys()) == set(DOMAIN_PAIRS.keys())

    def test_custom_base_rate_prior(self):
        """Custom base rate priors override default N(5,2)."""
        prior = {"a_sat": {"mean": 7.0, "sd": 1.0}}
        profile = ABCBayesianProfile(base_rate_prior=prior)
        assert profile.scorers["a_sat"].prior_mean == 7.0
        assert profile.scorers["a_sat"].prior_sd == 1.0
        # Others should remain at defaults
        assert profile.scorers["b_sat"].prior_mean == 5.0

    def test_scalar_base_rate_prior(self):
        """Scalar prior value uses default SD."""
        prior = {"a_sat": 8.0}
        profile = ABCBayesianProfile(base_rate_prior=prior)
        assert profile.scorers["a_sat"].prior_mean == 8.0
        assert profile.scorers["a_sat"].prior_sd == 2.0


# ---------------------------------------------------------------------------
# Domain state probabilities sum to 1.0 per domain
# ---------------------------------------------------------------------------


class TestDomainStateProbabilities:
    def test_state_probs_sum_to_one(self):
        profile = ABCBayesianProfile()
        scores = _make_subscale_scores()
        result = profile.update_all(scores)

        for domain, states in result["domain_states"].items():
            total = (
                states["posterior_thriving"]
                + states["posterior_vulnerable"]
                + states["posterior_mild"]
                + states["posterior_distressed"]
            )
            assert abs(total - 1.0) < 1e-6, f"Domain '{domain}' state probabilities sum to {total}"

    def test_state_probs_sum_after_multiple_updates(self):
        profile = ABCBayesianProfile()
        for _ in range(5):
            scores = _make_subscale_scores(sat=7.0, frust=3.0)
            result = profile.update_all(scores)

        for _domain, states in result["domain_states"].items():
            total = (
                states["posterior_thriving"]
                + states["posterior_vulnerable"]
                + states["posterior_mild"]
                + states["posterior_distressed"]
            )
            assert abs(total - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# classify_with_uncertainty: correct state identification
# ---------------------------------------------------------------------------


class TestClassifyWithUncertainty:
    def test_high_sat_low_frust_is_thriving(self):
        """High satisfaction, low frustration should classify as Thriving."""
        sat = BayesianScorer(prior_mean=8.0, prior_sd=0.5)
        frust = BayesianScorer(prior_mean=2.0, prior_sd=0.5)
        result = classify_with_uncertainty(sat, frust)
        assert result["most_likely_state"] == "Thriving"
        assert result["confidence"] > 0.5

    def test_low_sat_high_frust_is_distressed(self):
        """Low satisfaction, high frustration should classify as Distressed."""
        sat = BayesianScorer(prior_mean=3.0, prior_sd=0.5)
        frust = BayesianScorer(prior_mean=7.0, prior_sd=0.5)
        result = classify_with_uncertainty(sat, frust)
        assert result["most_likely_state"] == "Distressed"

    def test_high_sat_high_frust_is_vulnerable(self):
        """High satisfaction, high frustration should classify as Vulnerable."""
        sat = BayesianScorer(prior_mean=8.0, prior_sd=0.5)
        frust = BayesianScorer(prior_mean=7.0, prior_sd=0.5)
        result = classify_with_uncertainty(sat, frust)
        assert result["most_likely_state"] == "Vulnerable"

    def test_low_sat_low_frust_is_mild(self):
        """Low satisfaction, low frustration should classify as Mild."""
        sat = BayesianScorer(prior_mean=3.0, prior_sd=0.5)
        frust = BayesianScorer(prior_mean=2.0, prior_sd=0.5)
        result = classify_with_uncertainty(sat, frust)
        assert result["most_likely_state"] == "Mild"

    def test_wide_uncertainty_lowers_confidence(self):
        """Wide posteriors should produce lower max probability."""
        # Tight posteriors
        sat_tight = BayesianScorer(prior_mean=8.0, prior_sd=0.3)
        frust_tight = BayesianScorer(prior_mean=2.0, prior_sd=0.3)
        result_tight = classify_with_uncertainty(sat_tight, frust_tight)

        # Wide posteriors
        sat_wide = BayesianScorer(prior_mean=8.0, prior_sd=3.0)
        frust_wide = BayesianScorer(prior_mean=2.0, prior_sd=3.0)
        result_wide = classify_with_uncertainty(sat_wide, frust_wide)

        assert result_tight["confidence"] > result_wide["confidence"]

    def test_probabilities_sum_to_one(self):
        sat = BayesianScorer(prior_mean=6.0, prior_sd=1.5)
        frust = BayesianScorer(prior_mean=4.0, prior_sd=1.5)
        result = classify_with_uncertainty(sat, frust)
        total = (
            result["posterior_thriving"]
            + result["posterior_vulnerable"]
            + result["posterior_mild"]
            + result["posterior_distressed"]
        )
        assert abs(total - 1.0) < 1e-6


# ---------------------------------------------------------------------------
# get_personalized_threshold: returns None before 6 measurements
# ---------------------------------------------------------------------------


class TestPersonalizedThreshold:
    def test_returns_none_before_six(self):
        scorer = BayesianScorer()
        for score in [6.0, 7.0, 5.5, 6.5, 7.0]:
            scorer.update(score)
        assert scorer.measurements_incorporated == 5
        assert scorer.get_personalized_threshold() is None

    def test_returns_value_after_six(self):
        scorer = BayesianScorer()
        for score in [6.0, 7.0, 5.5, 6.5, 7.0, 6.0]:
            scorer.update(score)
        assert scorer.measurements_incorporated == 6
        threshold = scorer.get_personalized_threshold()
        assert threshold is not None
        assert isinstance(threshold, float)

    def test_never_below_floor(self):
        """Threshold should never go below the floor value."""
        scorer = BayesianScorer(prior_mean=2.0, prior_sd=1.0)
        # Feed very low scores to push posterior mean down
        for _ in range(10):
            scorer.update(1.0, measurement_se=0.5)
        threshold = scorer.get_personalized_threshold(floor=3.0)
        assert threshold >= 3.0

    def test_custom_floor(self):
        scorer = BayesianScorer(prior_mean=2.0, prior_sd=1.0)
        for _ in range(10):
            scorer.update(1.0, measurement_se=0.5)
        threshold = scorer.get_personalized_threshold(floor=2.0)
        assert threshold >= 2.0

    def test_custom_k(self):
        """Larger k produces a lower threshold (further below the mean)."""
        scorer = BayesianScorer(prior_mean=7.0, prior_sd=1.0)
        for _ in range(8):
            scorer.update(7.0, measurement_se=0.8)
        t_small_k = scorer.get_personalized_threshold(k=1.0, floor=0.0)
        t_large_k = scorer.get_personalized_threshold(k=2.0, floor=0.0)
        assert t_small_k > t_large_k

    def test_threshold_formula(self):
        """Verify threshold = max(mean - k*sd, floor)."""
        scorer = BayesianScorer(prior_mean=7.0, prior_sd=1.0)
        for _ in range(8):
            scorer.update(7.0, measurement_se=0.8)
        k = 1.5
        floor = 3.0
        expected = max(scorer.posterior_mean - k * scorer.posterior_sd, floor)
        assert scorer.get_personalized_threshold(k=k, floor=floor) == expected
