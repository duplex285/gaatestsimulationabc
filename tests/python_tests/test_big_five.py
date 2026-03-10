"""Tests for Big Five inference module.

Reference: abc-assessment-spec Section 2.3 (Big Five inference)
Reference: abc-assessment-spec Section 13.2 (weight matrix, centering, percentile)

Steps:
1. Centre each subscale: (score - 5) / 5
2. Dot product with weight row
3. Convert to percentile: 50 + z * 30, clamped to [1, 99]

Weight matrix v4 (covariance-aware optimised, domain-anchored):
| Trait           | A-sat | A-frust | B-sat | B-frust | C-sat | C-frust |
|-----------------|-------|---------|-------|---------|-------|---------|
| Openness        | 0.12  |  0.16   | -0.36 | -0.35   | 0.52  |  0.33   |
| Conscientiousness| 0.03 |  0.13   |  0.20 |  0.30   | 0.18  | -0.45   |
| Extraversion    | 0.47  |  0.02   |  0.27 |  0.19   |-0.12  |  0.11   |
| Agreeableness   |-0.23  |  0.19   |  0.43 | -0.13   | 0.08  |  0.18   |
| Neuroticism     | 0.00  |  0.24   |  0.05 |  0.41   |-0.03  |  0.05   |
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

    def test_low_craft_frust_raises_conscientiousness(self):
        """Low C-frust should produce above-average Conscientiousness.

        C anchors on c_frust (-0.45): discipline = low craft friction.
        """
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 7.0,
            "c_frust": 1.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["conscientiousness"] > 50

    def test_high_b_frust_raises_neuroticism(self):
        """High belonging frustration should produce above-average Neuroticism.

        N anchors on b_frust (+0.41) and a_frust (+0.24).
        """
        subscales = {
            "a_sat": 5.0,
            "a_frust": 7.0,
            "b_sat": 5.0,
            "b_frust": 9.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["neuroticism"] > 50

    def test_high_a_sat_raises_extraversion(self):
        """High A-sat should boost Extraversion. E anchors on a_sat (+0.47)."""
        subscales = {
            "a_sat": 9.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["extraversion"] > 50

    def test_high_b_sat_raises_agreeableness(self):
        """High B-sat should boost Agreeableness. A anchors on b_sat (+0.43)."""
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 9.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["agreeableness"] > 50

    def test_high_c_sat_raises_openness(self):
        """High C-sat should boost Openness. O anchors on c_sat (+0.52)."""
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 9.0,
            "c_frust": 5.0,
        }
        big_five = compute_big_five(subscales)
        assert big_five["openness"] > 50

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
