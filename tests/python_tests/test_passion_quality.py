"""Tests for the passion quality scoring module.

Reference: improvement-plan-personalization-engine.md Section 16.2
Reference: src/python_scoring/passion_quality.py
Reference: docs/passion-items-draft.md (item content and scoring model)

Coverage:
- Subscale means and 0-10 normalization
- Balance score computation
- Leaning classification: harmonious, obsessive, mixed, uninvested,
  insufficient_signal
- Display gate and recommendation gate behavior
- Partial response handling
- Input validation
"""

from __future__ import annotations

import pytest

from src.python_scoring.passion_quality import (
    BALANCE_LEANING_THRESHOLD,
    PassionQualityResult,
    score_passion_quality,
)


def _responses(
    hp1: int = 4,
    hp2: int = 4,
    hp3: int = 4,
    op1: int = 4,
    op2: int = 4,
    op3: int = 4,
) -> dict[str, int]:
    return {
        "HP1": hp1,
        "HP2": hp2,
        "HP3": hp3,
        "OP1": op1,
        "OP2": op2,
        "OP3": op3,
    }


class TestScoring:
    """Raw scoring math."""

    def test_midpoint_responses_score_5(self):
        result = score_passion_quality(_responses())
        assert result.hp_score == pytest.approx(5.0)
        assert result.op_score == pytest.approx(5.0)
        assert result.balance == pytest.approx(0.0)

    def test_maximum_harmonious_minimum_obsessive(self):
        result = score_passion_quality(_responses(hp1=7, hp2=7, hp3=7, op1=1, op2=1, op3=1))
        assert result.hp_score == pytest.approx(10.0)
        assert result.op_score == pytest.approx(0.0)
        assert result.balance == pytest.approx(10.0)
        assert result.leaning == "harmonious"

    def test_maximum_obsessive_minimum_harmonious(self):
        result = score_passion_quality(_responses(hp1=1, hp2=1, hp3=1, op1=7, op2=7, op3=7))
        assert result.hp_score == pytest.approx(0.0)
        assert result.op_score == pytest.approx(10.0)
        assert result.balance == pytest.approx(-10.0)
        assert result.leaning == "obsessive"

    def test_balance_is_hp_minus_op(self):
        result = score_passion_quality(_responses(hp1=6, hp2=6, hp3=6, op1=3, op2=3, op3=3))
        assert result.balance == pytest.approx(result.hp_score - result.op_score)


class TestLeaningClassification:
    """Leaning labels per docs/passion-items-draft.md Section 4."""

    def test_harmonious_when_hp_elevated_and_balance_positive(self):
        result = score_passion_quality(_responses(hp1=6, hp2=6, hp3=6, op1=3, op2=3, op3=3))
        assert result.leaning == "harmonious"
        assert result.recommendation_gate_passed is True

    def test_obsessive_when_op_elevated_and_balance_negative(self):
        result = score_passion_quality(_responses(hp1=3, hp2=3, hp3=3, op1=6, op2=6, op3=6))
        assert result.leaning == "obsessive"
        assert result.recommendation_gate_passed is True

    def test_mixed_when_both_elevated(self):
        """Mixed is non-directional but decisive: rec gate passes because
        both subscales are elevated and the coach action is specific
        (check for underlying conflict)."""
        result = score_passion_quality(_responses(hp1=6, hp2=6, hp3=6, op1=6, op2=6, op3=6))
        assert result.leaning == "mixed"
        assert result.recommendation_gate_passed is True

    def test_uninvested_when_both_low(self):
        """Uninvested is also decisive: rec gate passes because the
        coach action is specific (look elsewhere for drive)."""
        result = score_passion_quality(_responses(hp1=2, hp2=2, hp3=2, op1=2, op2=2, op3=2))
        assert result.leaning == "uninvested"
        assert result.recommendation_gate_passed is True

    def test_insufficient_signal_when_balance_small_and_one_elevated(self):
        """HP elevated, OP not, but balance too small to declare harmonious.

        hp responses (5,5,4) -> mean 4.667 -> 0-10 score 6.11 (elevated).
        op responses (3,4,4) -> mean 3.667 -> 0-10 score 4.44 (not elevated).
        balance = 1.67, under the 2.0 leaning threshold.
        """
        result = score_passion_quality(_responses(hp1=5, hp2=5, hp3=4, op1=3, op2=4, op3=4))
        assert result.leaning == "insufficient_signal"
        assert result.recommendation_gate_passed is False


class TestGates:
    """Display and recommendation gate behavior."""

    def test_all_six_items_display_gate_passes(self):
        result = score_passion_quality(_responses())
        assert result.display_gate_passed is True

    def test_four_items_display_gate_passes_rec_fails(self):
        responses = {"HP1": 6, "HP2": 6, "OP1": 3, "OP2": 3}
        result = score_passion_quality(responses)
        assert result.display_gate_passed is True
        assert result.recommendation_gate_passed is False
        assert "6 items" in result.gate_reason

    def test_three_items_display_gate_fails(self):
        responses = {"HP1": 6, "HP2": 6, "OP1": 3}
        result = score_passion_quality(responses)
        assert result.display_gate_passed is False
        assert result.recommendation_gate_passed is False
        assert result.leaning == "not_computed"
        assert result.hp_score is None
        assert result.op_score is None

    def test_no_items_display_gate_fails(self):
        result = score_passion_quality({})
        assert result.display_gate_passed is False
        assert result.leaning == "not_computed"

    def test_empty_subscale_fails_display_gate(self):
        """Four HP items answered but no OP items: display gate fails."""
        responses = {"HP1": 6, "HP2": 6, "HP3": 6}
        responses["HP1"] = 6
        result = score_passion_quality(responses)
        assert result.display_gate_passed is False

    def test_balance_close_to_zero_fails_recommendation(self):
        """Insufficient-signal leaning with balance < 1.0 hits the
        pattern-still-forming branch.

        hp=(4,4,4) -> score 5.0 (elevated). op=(4,4,3) -> score 4.44
        (not elevated). Balance 0.56. Leaning is insufficient_signal
        because balance is under the 2.0 leaning threshold.
        """
        result = score_passion_quality(_responses(hp1=4, hp2=4, hp3=4, op1=4, op2=4, op3=3))
        assert result.display_gate_passed is True
        assert result.leaning == "insufficient_signal"
        assert result.recommendation_gate_passed is False
        assert "pattern still forming" in result.gate_reason

    def test_strong_leaning_passes_recommendation_gate(self):
        result = score_passion_quality(_responses(hp1=7, hp2=7, hp3=7, op1=1, op2=1, op3=1))
        assert result.recommendation_gate_passed is True
        assert result.balance >= BALANCE_LEANING_THRESHOLD


class TestValidation:
    """Input validation."""

    def test_rejects_non_integer_response(self):
        with pytest.raises(TypeError):
            score_passion_quality({"HP1": 4.5, "HP2": 4, "HP3": 4, "OP1": 4, "OP2": 4, "OP3": 4})

    def test_rejects_out_of_range_low(self):
        with pytest.raises(ValueError):
            score_passion_quality({"HP1": 0, "HP2": 4, "HP3": 4, "OP1": 4, "OP2": 4, "OP3": 4})

    def test_rejects_out_of_range_high(self):
        with pytest.raises(ValueError):
            score_passion_quality({"HP1": 8, "HP2": 4, "HP3": 4, "OP1": 4, "OP2": 4, "OP3": 4})

    def test_ignores_unknown_items(self):
        """Items outside HP/OP are silently ignored."""
        responses = _responses()
        responses["AS1"] = 7  # Not a passion item
        result = score_passion_quality(responses)
        assert result.items_answered == 6
        assert result.display_gate_passed is True


class TestStructure:
    """PassionQualityResult shape."""

    def test_result_is_dataclass_instance(self):
        result = score_passion_quality(_responses())
        assert isinstance(result, PassionQualityResult)

    def test_result_exposes_gate_reason(self):
        result = score_passion_quality({})
        assert isinstance(result.gate_reason, str)
        assert len(result.gate_reason) > 0
