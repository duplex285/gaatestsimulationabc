"""Tests for the integrated ABCPsychometricScorer pipeline.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
"""

import numpy as np
import pytest

from src.psychometric.irt_simulation import (
    generate_synthetic_grm_parameters,
    simulate_grm_responses,
)
from src.psychometric.psychometric_pipeline import ABCPsychometricScorer


@pytest.fixture
def scorer():
    """Create a scorer with synthetic IRT parameters."""
    params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
    return ABCPsychometricScorer(
        discrimination=params["discrimination"],
        difficulty=params["difficulty"],
    )


@pytest.fixture
def sample_responses():
    """Generate sample 36-item responses for one person."""
    params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
    rng = np.random.default_rng(42)
    theta = rng.standard_normal(1)
    responses = simulate_grm_responses(
        theta, params["discrimination"], params["difficulty"], seed=42
    )
    return responses[0]  # single person


@pytest.fixture
def sample_response_dict(sample_responses):
    """Convert array responses to the dict format the existing pipeline uses."""
    item_codes = [
        "AS1",
        "AS2",
        "AS3",
        "AS4",
        "AS5",
        "AS6",
        "AF1",
        "AF2",
        "AF3",
        "AF4",
        "AF5",
        "AF6",
        "BS1",
        "BS2",
        "BS3",
        "BS4",
        "BS5",
        "BS6",
        "BF1",
        "BF2",
        "BF3",
        "BF4",
        "BF5",
        "BF6",
        "CS1",
        "CS2",
        "CS3",
        "CS4",
        "CS5",
        "CS6",
        "CF1",
        "CF2",
        "CF3",
        "CF4",
        "CF5",
        "CF6",
    ]
    return {code: int(val) for code, val in zip(item_codes, sample_responses, strict=False)}


@pytest.fixture
def trajectory_responses():
    """Generate 5 timepoints of responses for trajectory analysis."""
    params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
    np.random.default_rng(42)
    # Simulate declining theta: 1.0, 0.5, 0.0, -0.5, -1.0
    thetas = [1.0, 0.5, 0.0, -0.5, -1.0]
    all_responses = []
    for i, theta in enumerate(thetas):
        responses = simulate_grm_responses(
            np.array([theta]), params["discrimination"], params["difficulty"], seed=42 + i
        )
        all_responses.append(responses[0])
    return all_responses


class TestABCPsychometricScorerSingleAdmin:
    """Tests for single-administration scoring."""

    def test_score_returns_required_keys(self, scorer, sample_responses):
        """Output includes all expected sections."""
        result = scorer.score(sample_responses)
        assert "subscales" in result
        assert "theta" in result
        assert "standard_errors" in result
        assert "t_scores" in result
        assert "severity_bands" in result
        assert "tier" in result
        assert "scoring_method" in result

    def test_subscales_in_zero_to_ten(self, scorer, sample_responses):
        """All subscale scores are in [0, 10]."""
        result = scorer.score(sample_responses)
        for name, score in result["subscales"].items():
            assert 0.0 <= score <= 10.0, f"{name} = {score}"

    def test_theta_estimates_present(self, scorer, sample_responses):
        """Theta estimates present for all 6 factors."""
        result = scorer.score(sample_responses)
        assert len(result["theta"]) == 6

    def test_standard_errors_positive(self, scorer, sample_responses):
        """All standard errors are positive."""
        result = scorer.score(sample_responses)
        for name, se in result["standard_errors"].items():
            assert se > 0, f"SE for {name} = {se}"

    def test_t_scores_centered_near_50(self, scorer):
        """T-scores for a midpoint response should be near 50."""
        mid_responses = np.full(36, 4, dtype=int)
        result = scorer.score(mid_responses)
        t_values = list(result["t_scores"].values())
        mean_t = np.mean(t_values)
        assert 30 < mean_t < 70

    def test_severity_bands_are_strings(self, scorer, sample_responses):
        """Severity bands are string labels."""
        result = scorer.score(sample_responses)
        valid_bands = {"Normal", "Mild", "Moderate", "Severe", "Extremely Severe"}
        for name, band in result["severity_bands"].items():
            assert band in valid_bands, f"{name} band = {band}"

    def test_tier_detection(self, scorer):
        """Tier is correctly identified based on item count."""
        r6 = scorer.score(np.full(6, 4, dtype=int), n_items=6)
        r36 = scorer.score(np.full(36, 4, dtype=int), n_items=36)
        assert r6["tier"] == "6_item"
        assert r36["tier"] == "36_item"
        # 18-item tier: pass full 36-item array but override n_items for tier detection
        r18 = scorer.score(np.full(36, 4, dtype=int), n_items=18)
        assert r18["tier"] == "18_item"

    def test_unsupported_outputs_suppressed_at_6_item(self, scorer):
        """At 6-item tier, domain states and types are not reported.

        Reference: Phase 5b finding
        """
        result = scorer.score(np.full(6, 4, dtype=int), n_items=6)
        assert result.get("domain_states") is None
        assert result.get("type_name") is None

    def test_confidence_included(self, scorer, sample_responses):
        """Output includes confidence/precision information."""
        result = scorer.score(sample_responses)
        assert "confidence" in result


class TestABCPsychometricScorerTrajectory:
    """Tests for trajectory analysis across multiple administrations."""

    def test_trajectory_returns_pattern(self, scorer, trajectory_responses):
        """Trajectory analysis returns a pattern classification."""
        result = scorer.score_trajectory(trajectory_responses)
        assert "pattern" in result
        assert result["pattern"] in {
            "stable",
            "gradual_decline",
            "gradual_rise",
            "acute_event",
            "volatile",
        }

    def test_trajectory_returns_reliable_changes(self, scorer, trajectory_responses):
        """Trajectory includes reliable change flags."""
        result = scorer.score_trajectory(trajectory_responses)
        assert "reliable_changes" in result

    def test_trajectory_returns_trend(self, scorer, trajectory_responses):
        """Trajectory includes trend analysis."""
        result = scorer.score_trajectory(trajectory_responses)
        assert "trend" in result
        assert "direction" in result["trend"]

    def test_declining_trajectory_detected(self, scorer, trajectory_responses):
        """A declining trajectory should be classified as decline or detected as negative trend."""
        result = scorer.score_trajectory(trajectory_responses)
        # Either pattern is decline or trend direction is declining
        is_decline = result["pattern"] == "gradual_decline"
        is_neg_trend = result["trend"]["direction"] == "declining"
        assert is_decline or is_neg_trend

    def test_trajectory_returns_risk_assessment(self, scorer, trajectory_responses):
        """Trajectory includes risk assessment with alert level."""
        result = scorer.score_trajectory(trajectory_responses)
        assert "risk_assessment" in result
        assert "alert_level" in result["risk_assessment"]

    def test_trajectory_returns_per_timepoint_scores(self, scorer, trajectory_responses):
        """Trajectory includes scores at each timepoint."""
        result = scorer.score_trajectory(trajectory_responses)
        assert "timepoint_scores" in result
        assert len(result["timepoint_scores"]) == len(trajectory_responses)
