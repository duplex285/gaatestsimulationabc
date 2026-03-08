"""Tests for reverse scoring module.

Reference: abc-assessment-spec Section 2.1 (reverse formula: 8 - response)
Reference: abc-assessment-spec Section 1.2 (item 4 of each subscale is reversed)
"""

import pytest

from src.python_scoring.reverse_scoring import apply_reverse_scoring, reverse_score
from tests.python_tests.conftest import ALL_ITEMS


class TestReverseScoreFunction:
    """Test the core reverse_score() function."""

    def test_reverse_7_becomes_1(self):
        assert reverse_score(7) == 1

    def test_reverse_1_becomes_7(self):
        assert reverse_score(1) == 7

    def test_reverse_4_stays_4(self):
        """Midpoint is invariant under reversal."""
        assert reverse_score(4) == 4

    def test_reverse_2_becomes_6(self):
        assert reverse_score(2) == 6

    def test_reverse_3_becomes_5(self):
        assert reverse_score(3) == 5

    def test_reverse_5_becomes_3(self):
        assert reverse_score(5) == 3

    def test_reverse_6_becomes_2(self):
        assert reverse_score(6) == 2

    def test_all_valid_values(self):
        """Every value 1-7 reverses correctly: 8 - x."""
        for x in range(1, 8):
            assert reverse_score(x) == 8 - x

    def test_double_reverse_is_identity(self):
        """Reversing twice returns original value."""
        for x in range(1, 8):
            assert reverse_score(reverse_score(x)) == x

    def test_invalid_zero_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            reverse_score(0)

    def test_invalid_eight_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            reverse_score(8)

    def test_invalid_negative_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            reverse_score(-1)

    def test_invalid_float_raises(self):
        with pytest.raises((ValueError, TypeError, AssertionError)):
            reverse_score(3.5)


class TestApplyReverseScoring:
    """Test applying reverse scoring to a full response dict."""

    def test_reverse_items_are_reversed(self):
        """Item 4 of each subscale should be reversed."""
        responses = {
            "AS1": 7,
            "AS2": 7,
            "AS3": 7,
            "AS4": 1,
            "AF1": 1,
            "AF2": 1,
            "AF3": 1,
            "AF4": 7,
            "BS1": 7,
            "BS2": 7,
            "BS3": 7,
            "BS4": 1,
            "BF1": 1,
            "BF2": 1,
            "BF3": 1,
            "BF4": 7,
            "CS1": 7,
            "CS2": 7,
            "CS3": 7,
            "CS4": 1,
            "CF1": 1,
            "CF2": 1,
            "CF3": 1,
            "CF4": 7,
        }
        scored = apply_reverse_scoring(responses)
        # Reverse items should be flipped
        assert scored["AS4"] == 7  # was 1, reversed to 7
        assert scored["AF4"] == 1  # was 7, reversed to 1
        assert scored["BS4"] == 7
        assert scored["BF4"] == 1
        assert scored["CS4"] == 7
        assert scored["CF4"] == 1

    def test_forward_items_unchanged(self):
        """Non-reverse items should pass through unchanged."""
        responses = dict.fromkeys(ALL_ITEMS, 5)
        scored = apply_reverse_scoring(responses)
        assert scored["AS1"] == 5
        assert scored["AF1"] == 5
        assert scored["BS1"] == 5

    def test_midpoint_all_fours(self):
        """All 4s: reverse items also stay 4."""
        responses = dict.fromkeys(ALL_ITEMS, 4)
        scored = apply_reverse_scoring(responses)
        for item, val in scored.items():
            assert val == 4, f"{item} should be 4, got {val}"

    def test_returns_all_24_items(self):
        responses = dict.fromkeys(ALL_ITEMS, 4)
        scored = apply_reverse_scoring(responses)
        assert len(scored) == 24
