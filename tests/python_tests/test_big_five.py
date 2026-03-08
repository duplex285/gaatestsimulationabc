"""Tests for Big Five inference module.

Reference: abc-assessment-spec Section 2.3 (Big Five inference)
Reference: abc-assessment-spec Section 13.2 (weight matrix, centering, percentile)

Steps:
1. Centre each subscale: (score - 5) / 5
2. Dot product with weight row
3. Convert to percentile: 50 + z * 30, clamped to [1, 99]

Weight matrix:
| Trait           | A-sat | A-frust | B-sat | B-frust | C-sat | C-frust |
|-----------------|-------|---------|-------|---------|-------|---------|
| Openness        | 0.25  | -0.10   | 0.15  | -0.05   | 0.35  | -0.15   |
| Conscientiousness| 0.40 | -0.25   | 0.10  | -0.10   | 0.55  | -0.30   |
| Extraversion    | 0.30  | -0.15   | 0.45  | -0.20   | 0.15  | -0.10   |
| Agreeableness   | 0.05  | -0.15   | 0.50  | -0.40   | 0.10  | -0.05   |
| Neuroticism     | -0.20 | 0.48    | -0.25 | 0.45    | -0.15 | 0.42    |
"""

import pytest

from src.python_scoring.big_five_inference import (
    centre_subscales,
    compute_big_five,
)


class TestCentreSubscales:
    """Test centering: (score - 5) / 5."""

    def test_midpoint_centres_to_zero(self):
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        centred = centre_subscales(subscales)
        for key, val in centred.items():
            assert val == pytest.approx(0.0), f"{key} should centre to 0.0"

    def test_max_centres_to_1(self):
        subscales = {
            "a_sat": 10.0,
            "a_frust": 10.0,
            "b_sat": 10.0,
            "b_frust": 10.0,
            "c_sat": 10.0,
            "c_frust": 10.0,
        }
        centred = centre_subscales(subscales)
        for key, val in centred.items():
            assert val == pytest.approx(1.0), f"{key} should centre to 1.0"

    def test_min_centres_to_neg1(self):
        subscales = {
            "a_sat": 0.0,
            "a_frust": 0.0,
            "b_sat": 0.0,
            "b_frust": 0.0,
            "c_sat": 0.0,
            "c_frust": 0.0,
        }
        centred = centre_subscales(subscales)
        for key, val in centred.items():
            assert val == pytest.approx(-1.0), f"{key} should centre to -1.0"


class TestComputeBigFive:
    """Test Big Five inference from subscale scores."""

    def test_midpoint_gives_50th_percentile(self):
        """All subscales at 5.0 -> centred to 0 -> dot product = 0 -> percentile = 50."""
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        for trait in [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]:
            assert big_five[trait] == pytest.approx(50.0), f"{trait} should be 50"

    def test_returns_five_traits(self):
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        expected = {"openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"}
        assert set(big_five.keys()) == expected

    def test_all_percentiles_clamped_to_1_99(self):
        """Extreme scores should still produce percentiles in [1, 99]."""
        # Max sat, min frust -> high positive weights dominate
        subscales = {
            "a_sat": 10.0,
            "a_frust": 0.0,
            "b_sat": 10.0,
            "b_frust": 0.0,
            "c_sat": 10.0,
            "c_frust": 0.0,
        }
        big_five = compute_big_five(subscales)
        for trait, val in big_five.items():
            assert 1 <= val <= 99, f"{trait}={val} out of [1, 99]"

    def test_extreme_low_clamped(self):
        """Min sat, max frust -> should clamp low end."""
        subscales = {
            "a_sat": 0.0,
            "a_frust": 10.0,
            "b_sat": 0.0,
            "b_frust": 10.0,
            "c_sat": 0.0,
            "c_frust": 10.0,
        }
        big_five = compute_big_five(subscales)
        for trait, val in big_five.items():
            assert 1 <= val <= 99, f"{trait}={val} out of [1, 99]"

    def test_high_sat_low_frust_raises_conscientiousness(self):
        """High sat + low frust should produce above-average Conscientiousness.

        C has strongest positive weights on A-sat(0.40), C-sat(0.55) and
        strongest negative weights on A-frust(-0.25), C-frust(-0.30).
        """
        subscales = {
            "a_sat": 9.0,
            "a_frust": 1.0,
            "b_sat": 9.0,
            "b_frust": 1.0,
            "c_sat": 9.0,
            "c_frust": 1.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["conscientiousness"] > 50

    def test_high_frust_raises_neuroticism(self):
        """High frustration should produce above-average Neuroticism.

        N has positive weights on all frust subscales (0.48, 0.45, 0.42).
        """
        subscales = {
            "a_sat": 2.0,
            "a_frust": 9.0,
            "b_sat": 2.0,
            "b_frust": 9.0,
            "c_sat": 2.0,
            "c_frust": 9.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["neuroticism"] > 50

    def test_high_b_sat_raises_extraversion_and_agreeableness(self):
        """High B-sat should boost Extraversion (0.45) and Agreeableness (0.50)."""
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 10.0,
            "b_frust": 0.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["extraversion"] > 50
        assert big_five["agreeableness"] > 50

    def test_differentiable_extreme_profiles(self):
        """All-high and all-low profiles should produce different Big Five estimates.

        Reference: abc-assessment-spec Section 11.5 (edge cases produce
        differentiable, non-degenerate estimates).
        """
        high = {
            "a_sat": 10.0,
            "a_frust": 0.0,
            "b_sat": 10.0,
            "b_frust": 0.0,
            "c_sat": 10.0,
            "c_frust": 0.0,
        }
        low = {
            "a_sat": 0.0,
            "a_frust": 10.0,
            "b_sat": 0.0,
            "b_frust": 10.0,
            "c_sat": 0.0,
            "c_frust": 10.0,
        }
        bf_high = compute_big_five(high)
        bf_low = compute_big_five(low)
        # Profiles should differ on every trait
        for trait in bf_high:
            assert bf_high[trait] != bf_low[trait], f"{trait} should differ"
