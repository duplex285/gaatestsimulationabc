"""Tests for causality-orientations scoring.

Reference: improvement-plan-personalization-engine.md Section 16.6
Reference: src/python_scoring/causality_orientations.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.causality_orientations import (
    ALL_ITEMS,
    DOMINANT_MARGIN,
    CausalityProfile,
    score_causality_orientations,
)


def _uniform(value: int) -> dict[str, int]:
    return dict.fromkeys(ALL_ITEMS, value)


def _orientation_skewed(
    autonomy: int = 4, controlled: int = 4, impersonal: int = 4
) -> dict[str, int]:
    responses: dict[str, int] = {}
    for i in range(1, 5):
        responses[f"AO{i}"] = autonomy
        responses[f"CO{i}"] = controlled
        responses[f"IO{i}"] = impersonal
    return responses


class TestScoring:
    def test_midpoint_responses_score_5(self):
        p = score_causality_orientations(_uniform(4))
        assert p.autonomy_score == pytest.approx(5.0)
        assert p.controlled_score == pytest.approx(5.0)
        assert p.impersonal_score == pytest.approx(5.0)

    def test_max_responses_score_10(self):
        p = score_causality_orientations(_uniform(7))
        assert p.autonomy_score == pytest.approx(10.0)

    def test_min_responses_score_0(self):
        p = score_causality_orientations(_uniform(1))
        assert p.autonomy_score == pytest.approx(0.0)


class TestDominantClassification:
    def test_autonomy_dominant(self):
        p = score_causality_orientations(
            _orientation_skewed(autonomy=7, controlled=2, impersonal=2)
        )
        assert p.dominant == "autonomy"
        assert p.recommendation_gate_passed is True

    def test_controlled_dominant(self):
        p = score_causality_orientations(
            _orientation_skewed(autonomy=2, controlled=7, impersonal=2)
        )
        assert p.dominant == "controlled"
        assert p.recommendation_gate_passed is True

    def test_impersonal_dominant(self):
        p = score_causality_orientations(
            _orientation_skewed(autonomy=2, controlled=2, impersonal=7)
        )
        assert p.dominant == "impersonal"
        assert p.recommendation_gate_passed is True

    def test_mixed_when_two_close(self):
        """autonomy ~8.3, controlled ~8.3, impersonal ~3.3 -> mixed."""
        p = score_causality_orientations(
            _orientation_skewed(autonomy=6, controlled=6, impersonal=3)
        )
        assert p.dominant == "mixed"
        assert p.recommendation_gate_passed is False

    def test_emergent_when_all_low(self):
        """All subscales under 4.0 -> emergent."""
        p = score_causality_orientations(
            _orientation_skewed(autonomy=2, controlled=2, impersonal=2)
        )
        assert p.dominant == "emergent"

    def test_margin_rule_holds(self):
        """Margin less than 1.5 with top above threshold -> mixed, not dominant."""
        # autonomy ~6.7 (raw 5), controlled ~5.5 (raw 4.3); margin ~1.2 < 1.5
        p = score_causality_orientations(
            {
                "AO1": 5,
                "AO2": 5,
                "AO3": 5,
                "AO4": 5,
                "CO1": 4,
                "CO2": 5,
                "CO3": 4,
                "CO4": 4,
                "IO1": 1,
                "IO2": 1,
                "IO3": 1,
                "IO4": 1,
            }
        )
        assert p.dominant == "mixed"


class TestGates:
    def test_full_screen_passes_both_gates(self):
        p = score_causality_orientations(
            _orientation_skewed(autonomy=7, controlled=1, impersonal=1)
        )
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is True

    def test_partial_screen_fails_display_when_too_few(self):
        """Fewer than 8 items total -> display fails."""
        p = score_causality_orientations({"AO1": 7, "AO2": 7, "CO1": 1, "IO1": 1})
        assert p.display_gate_passed is False
        assert p.dominant == "not_computed"
        assert p.autonomy_score is None

    def test_missing_subscale_fails_display(self):
        """8+ items but one subscale has fewer than 2 -> display fails."""
        responses = {
            "AO1": 7,
            "AO2": 7,
            "AO3": 7,
            "AO4": 7,
            "CO1": 1,
            "CO2": 1,
            "CO3": 1,
            "CO4": 1,
            "IO1": 1,  # only 1 impersonal item
        }
        p = score_causality_orientations(responses)
        assert p.display_gate_passed is False

    def test_partial_full_coverage_passes_display_fails_recommendation(self):
        """10 of 12 items, 2+ per subscale: display passes, rec fails."""
        responses = _uniform(4)
        del responses["AO4"]
        del responses["CO4"]
        p = score_causality_orientations(responses)
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is False
        assert "12" in p.gate_reason

    def test_all_items_but_no_clear_dominant_fails_rec(self):
        p = score_causality_orientations(_uniform(4))
        assert p.display_gate_passed is True
        assert p.recommendation_gate_passed is False


class TestValidation:
    def test_rejects_non_integer(self):
        responses = _uniform(4)
        responses["AO1"] = 4.5
        with pytest.raises(TypeError):
            score_causality_orientations(responses)

    def test_rejects_out_of_range(self):
        responses = _uniform(4)
        responses["AO1"] = 0
        with pytest.raises(ValueError):
            score_causality_orientations(responses)

    def test_ignores_unknown_items(self):
        responses = _uniform(4)
        responses["AS1"] = 7
        p = score_causality_orientations(responses)
        assert p.items_answered == 12


class TestStructure:
    def test_returns_dataclass(self):
        p = score_causality_orientations(_uniform(4))
        assert isinstance(p, CausalityProfile)

    def test_empty_returns_not_computed(self):
        p = score_causality_orientations({})
        assert p.dominant == "not_computed"
        assert p.display_gate_passed is False

    def test_dominant_margin_constant(self):
        assert DOMINANT_MARGIN == 1.5
