"""Tests for self-concordance scoring.

Reference: improvement-plan-personalization-engine.md Section 16.7
Reference: src/python_scoring/self_concordance.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.self_concordance import (
    LEANING_THRESHOLD,
    SelfConcordanceProfile,
    score_self_concordance,
)


def _responses(sc1: int = 4, sc2: int = 4, sc3: int = 4, sc4: int = 4) -> dict[str, int]:
    return {"SC1": sc1, "SC2": sc2, "SC3": sc3, "SC4": sc4}


class TestScoring:
    def test_midpoint_responses(self):
        p = score_self_concordance(_responses())
        assert p.autonomous_score == pytest.approx(5.0)
        assert p.controlled_score == pytest.approx(5.0)
        assert p.self_concordance == pytest.approx(0.0)

    def test_max_autonomous_min_controlled(self):
        p = score_self_concordance(_responses(sc1=1, sc2=1, sc3=7, sc4=7))
        assert p.autonomous_score == pytest.approx(10.0)
        assert p.controlled_score == pytest.approx(0.0)
        assert p.self_concordance == pytest.approx(10.0)
        assert p.leaning == "autonomous"

    def test_max_controlled_min_autonomous(self):
        p = score_self_concordance(_responses(sc1=7, sc2=7, sc3=1, sc4=1))
        assert p.self_concordance == pytest.approx(-10.0)
        assert p.leaning == "controlled"

    def test_signed_score_formula(self):
        p = score_self_concordance(_responses(sc1=2, sc2=2, sc3=6, sc4=6))
        assert p.self_concordance == pytest.approx(p.autonomous_score - p.controlled_score)


class TestLeaningClassification:
    def test_autonomous_clear(self):
        p = score_self_concordance(_responses(sc1=2, sc2=2, sc3=6, sc4=6))
        assert p.leaning == "autonomous"
        assert p.recommendation_gate_passed is True

    def test_controlled_clear(self):
        p = score_self_concordance(_responses(sc1=6, sc2=6, sc3=2, sc4=2))
        assert p.leaning == "controlled"
        assert p.recommendation_gate_passed is True

    def test_mixed_when_balanced(self):
        p = score_self_concordance(_responses())  # all 4s
        assert p.leaning == "mixed"
        assert p.recommendation_gate_passed is False

    def test_mixed_when_both_elevated_close(self):
        p = score_self_concordance(_responses(sc1=6, sc2=6, sc3=6, sc4=6))
        # autonomous 8.33, controlled 8.33, sc 0 -> mixed
        assert p.leaning == "mixed"

    def test_threshold_constant(self):
        assert LEANING_THRESHOLD == 3.0


class TestGates:
    def test_all_four_passes_both_gates(self):
        p = score_self_concordance(_responses(sc1=1, sc2=1, sc3=7, sc4=7))
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is True

    def test_three_items_passes_display_only(self):
        p = score_self_concordance({"SC1": 2, "SC3": 6, "SC4": 6})
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is False

    def test_one_subscale_empty_fails_display(self):
        """Three autonomous, no controlled -> display fails."""
        p = score_self_concordance({"SC3": 7, "SC4": 7})
        assert p.display_gate_passed is False
        assert p.leaning == "not_computed"
        assert p.autonomous_score is None

    def test_too_few_items_fails_display(self):
        p = score_self_concordance({"SC3": 7})
        assert p.display_gate_passed is False

    def test_mixed_fails_recommendation_gate(self):
        p = score_self_concordance(_responses())
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is False
        assert "no clear" in p.gate_reason


class TestValidation:
    def test_rejects_non_integer(self):
        with pytest.raises(TypeError):
            score_self_concordance({"SC1": 4.5, "SC2": 4, "SC3": 4, "SC4": 4})

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            score_self_concordance({"SC1": 0, "SC2": 4, "SC3": 4, "SC4": 4})

    def test_ignores_unknown_items(self):
        responses = _responses()
        responses["AS1"] = 7
        p = score_self_concordance(responses)
        assert p.items_answered == 4


class TestGoalText:
    def test_goal_text_stored(self):
        p = score_self_concordance(_responses(), goal_text="make varsity")
        assert p.goal_text == "make varsity"

    def test_goal_text_none_when_omitted(self):
        p = score_self_concordance(_responses())
        assert p.goal_text is None

    def test_goal_text_does_not_affect_score(self):
        with_text = score_self_concordance(_responses(), goal_text="anything")
        without = score_self_concordance(_responses())
        assert with_text.self_concordance == without.self_concordance
        assert with_text.leaning == without.leaning


class TestStructure:
    def test_returns_dataclass(self):
        p = score_self_concordance(_responses())
        assert isinstance(p, SelfConcordanceProfile)

    def test_empty_responses(self):
        p = score_self_concordance({})
        assert p.leaning == "not_computed"
        assert p.display_gate_passed is False
