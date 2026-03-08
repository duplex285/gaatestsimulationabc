"""Tests for subscale computation module.

Reference: abc-assessment-spec Section 2.1 (subscale means, normalization)
Reference: abc-assessment-spec Section 13.2 (subscale scoring formulas)

Subscale mean = mean of 4 items (after reverse coding), on 1-7 scale.
Normalized = ((mean - 1) / 6) * 10, yielding 0-10 scale.
"""

import pytest

from src.python_scoring.subscale_computation import (
    compute_all_subscales,
    compute_subscale_mean,
    normalize_to_10,
)
from tests.python_tests.conftest import ALL_ITEMS


class TestSubscaleMean:
    """Test raw subscale mean computation (1-7 scale)."""

    def test_all_sevens(self):
        assert compute_subscale_mean([7, 7, 7, 7]) == 7.0

    def test_all_ones(self):
        assert compute_subscale_mean([1, 1, 1, 1]) == 1.0

    def test_all_fours(self):
        assert compute_subscale_mean([4, 4, 4, 4]) == 4.0

    def test_mixed_values(self):
        assert compute_subscale_mean([1, 3, 5, 7]) == 4.0

    def test_known_mean(self):
        assert compute_subscale_mean([6, 7, 5, 6]) == 6.0

    def test_requires_four_items(self):
        """Subscales have exactly 4 items."""
        with pytest.raises((ValueError, AssertionError)):
            compute_subscale_mean([7, 7, 7])

    def test_rejects_out_of_range(self):
        with pytest.raises((ValueError, AssertionError)):
            compute_subscale_mean([0, 7, 7, 7])


class TestNormalization:
    """Test normalization from 1-7 to 0-10 scale.

    Formula: ((mean - 1) / 6) * 10
    Reference: abc-assessment-spec Section 2.1
    """

    def test_max_7_becomes_10(self):
        assert normalize_to_10(7.0) == pytest.approx(10.0)

    def test_min_1_becomes_0(self):
        assert normalize_to_10(1.0) == pytest.approx(0.0)

    def test_midpoint_4_becomes_5(self):
        assert normalize_to_10(4.0) == pytest.approx(5.0)

    def test_5point5_on_likert(self):
        """5.5 on 1-7 scale = 7.5 on 0-10 scale."""
        expected = ((5.5 - 1) / 6) * 10  # 7.5
        assert normalize_to_10(5.5) == pytest.approx(expected)

    def test_boundary_values(self):
        """Test key boundary values."""
        # 4.3 on 1-7 -> 5.5 on 0-10 (the domain state threshold)
        assert normalize_to_10(4.3) == pytest.approx(5.5, abs=0.01)


class TestComputeAllSubscales:
    """Test computing all 6 subscale scores from scored responses."""

    def test_all_sevens_gives_10(self):
        """All items at 7 (after reverse scoring) -> all subscales at 10.0."""
        scored = dict.fromkeys(ALL_ITEMS, 7)
        result = compute_all_subscales(scored)
        for subscale in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            assert result[subscale] == pytest.approx(10.0), f"{subscale} should be 10.0"

    def test_all_ones_gives_0(self):
        scored = dict.fromkeys(ALL_ITEMS, 1)
        result = compute_all_subscales(scored)
        for subscale in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            assert result[subscale] == pytest.approx(0.0), f"{subscale} should be 0.0"

    def test_all_fours_gives_5(self):
        scored = dict.fromkeys(ALL_ITEMS, 4)
        result = compute_all_subscales(scored)
        for subscale in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            assert result[subscale] == pytest.approx(5.0), f"{subscale} should be 5.0"

    def test_returns_six_subscales(self):
        scored = dict.fromkeys(ALL_ITEMS, 4)
        result = compute_all_subscales(scored)
        expected_keys = {"a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"}
        assert set(result.keys()) == expected_keys

    def test_scores_in_valid_range(self):
        """All scores must be between 0.0 and 10.0."""
        import random

        random.seed(42)
        scored = {}
        for item in ALL_ITEMS:
            scored[item] = random.randint(1, 7)
        result = compute_all_subscales(scored)
        for subscale, score in result.items():
            assert 0.0 <= score <= 10.0, f"{subscale}={score} out of range"
