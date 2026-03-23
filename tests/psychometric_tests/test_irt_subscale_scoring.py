"""Tests for IRT subscale scoring bridge.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
Reference: abc-assessment-spec Section 1.2 (subscale map)
"""

import numpy as np
import pytest

from src.psychometric.irt_subscale_scoring import (
    FACTOR_ITEM_INDICES,
    score_subscales_irt,
    theta_to_subscale_score,
)


class TestThetaToSubscaleScore:
    """Tests for theta-to-0-10 conversion."""

    def test_zero_theta_maps_to_five(self):
        """Theta=0 (population mean) maps to 5.0 on 0-10 scale.

        Reference: abc-assessment-spec Section 2.1
        """
        score = theta_to_subscale_score(0.0)
        assert score == 5.0

    def test_positive_theta_above_five(self):
        """Positive theta maps above 5.0."""
        score = theta_to_subscale_score(1.0)
        assert score > 5.0

    def test_negative_theta_below_five(self):
        """Negative theta maps below 5.0."""
        score = theta_to_subscale_score(-1.0)
        assert score < 5.0

    def test_clamped_at_zero(self):
        """Extreme negative theta clamps to 0.0."""
        score = theta_to_subscale_score(-10.0)
        assert score == 0.0

    def test_clamped_at_ten(self):
        """Extreme positive theta clamps to 10.0."""
        score = theta_to_subscale_score(10.0)
        assert score == 10.0

    def test_linear_mapping(self):
        """Mapping is linear between clamping boundaries.

        Formula: score = 5.0 + theta * 2.5, clamped to [0, 10]
        """
        assert theta_to_subscale_score(1.0) == pytest.approx(7.5)
        assert theta_to_subscale_score(-1.0) == pytest.approx(2.5)
        assert theta_to_subscale_score(2.0) == pytest.approx(10.0)
        assert theta_to_subscale_score(-2.0) == pytest.approx(0.0)

    def test_custom_center_and_scale(self):
        """Custom center and scale parameters work correctly."""
        # Center at 50, scale by 10 (T-score-like)
        score = theta_to_subscale_score(0.0, center=50.0, scale=10.0, clamp_min=0, clamp_max=100)
        assert score == 50.0


class TestFactorItemIndices:
    """Tests for the factor-to-item index mapping."""

    def test_six_factors(self):
        """Mapping contains all 6 ABC factors."""
        assert len(FACTOR_ITEM_INDICES) == 6

    def test_six_items_per_factor(self):
        """Each factor maps to exactly 6 item indices."""
        for factor, indices in FACTOR_ITEM_INDICES.items():
            assert len(indices) == 6, f"Factor {factor} has {len(indices)} items, expected 6"

    def test_indices_span_0_to_35(self):
        """All item indices fall within [0, 35] for 36 items."""
        all_indices = []
        for indices in FACTOR_ITEM_INDICES.values():
            all_indices.extend(indices)
        assert min(all_indices) == 0
        assert max(all_indices) == 35
        assert len(set(all_indices)) == 36  # no duplicates

    def test_factor_names_match_spec(self):
        """Factor names match abc-assessment-spec Section 1.2."""
        expected = {"a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"}
        assert set(FACTOR_ITEM_INDICES.keys()) == expected


class TestScoreSubscalesIRT:
    """Tests for full IRT subscale scoring pipeline."""

    @pytest.fixture
    def mock_irt_setup(self):
        """Create a minimal IRT setup for testing the bridge function."""
        from src.psychometric.irt_simulation import (
            generate_synthetic_grm_parameters,
            simulate_grm_responses,
        )

        params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
        rng = np.random.default_rng(42)
        theta = rng.standard_normal(50)
        responses = simulate_grm_responses(
            theta, params["discrimination"], params["difficulty"], seed=42
        )
        return {
            "responses": responses,
            "discrimination": params["discrimination"],
            "difficulty": params["difficulty"],
            "true_theta": theta,
        }

    def test_returns_all_six_subscales(self, mock_irt_setup):
        """Output dict has all 6 subscale scores."""
        result = score_subscales_irt(
            mock_irt_setup["responses"],
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        expected_keys = {"a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"}
        assert set(result["scores"].keys()) == expected_keys

    def test_returns_standard_errors(self, mock_irt_setup):
        """Output includes SE for each subscale."""
        result = score_subscales_irt(
            mock_irt_setup["responses"],
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        assert "standard_errors" in result
        assert set(result["standard_errors"].keys()) == set(result["scores"].keys())

    def test_scores_in_zero_to_ten(self, mock_irt_setup):
        """All subscale scores fall within [0, 10]."""
        result = score_subscales_irt(
            mock_irt_setup["responses"],
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        for factor, scores in result["scores"].items():
            assert np.all(scores >= 0), f"{factor} has scores below 0"
            assert np.all(scores <= 10), f"{factor} has scores above 10"

    def test_ses_positive(self, mock_irt_setup):
        """All standard errors are positive."""
        result = score_subscales_irt(
            mock_irt_setup["responses"],
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        for factor, ses in result["standard_errors"].items():
            assert np.all(ses > 0), f"{factor} has non-positive SEs"

    def test_returns_theta_estimates(self, mock_irt_setup):
        """Output includes raw theta estimates per factor."""
        result = score_subscales_irt(
            mock_irt_setup["responses"],
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        assert "theta" in result
        assert set(result["theta"].keys()) == set(result["scores"].keys())

    def test_single_person_scoring(self, mock_irt_setup):
        """Can score a single person (1-row response matrix)."""
        single = mock_irt_setup["responses"][:1]
        result = score_subscales_irt(
            single,
            mock_irt_setup["discrimination"],
            mock_irt_setup["difficulty"],
        )
        for factor in result["scores"]:
            assert len(result["scores"][factor]) == 1
