"""Tests for the regulatory-style scoring module.

Reference: improvement-plan-personalization-engine.md Section 16.1
Reference: src/python_scoring/regulatory_style.py
Reference: docs/regulatory-style-items-draft.md
"""

from __future__ import annotations

import pytest

from src.python_scoring.regulatory_style import (
    DomainRegulation,
    RegulatoryProfile,
    score_regulatory_style,
)


def _all_responses(
    ar1: int = 4,
    ar2: int = 4,
    br1: int = 4,
    br2: int = 4,
    cr1: int = 4,
    cr2: int = 4,
) -> dict[str, int]:
    return {"AR1": ar1, "AR2": ar2, "BR1": br1, "BR2": br2, "CR1": cr1, "CR2": cr2}


class TestScoring:
    def test_midpoint_responses_score_5(self):
        profile = score_regulatory_style(_all_responses())
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].autonomous_score == pytest.approx(5.0)
            assert profile.domains[d].controlled_score == pytest.approx(5.0)
            assert profile.domains[d].rai == pytest.approx(0.0)

    def test_max_autonomous_min_controlled(self):
        profile = score_regulatory_style(_all_responses(ar1=7, ar2=1, br1=7, br2=1, cr1=7, cr2=1))
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].autonomous_score == pytest.approx(10.0)
            assert profile.domains[d].controlled_score == pytest.approx(0.0)
            assert profile.domains[d].rai == pytest.approx(10.0)
            assert profile.domains[d].style == "identified"

    def test_min_autonomous_max_controlled(self):
        profile = score_regulatory_style(_all_responses(ar1=1, ar2=7, br1=1, br2=7, cr1=1, cr2=7))
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].rai == pytest.approx(-10.0)
            assert profile.domains[d].style == "introjected"

    def test_per_domain_independence(self):
        """Different responses per domain produce different per-domain styles.

        Ambition: 7/1 -> identified. Belonging: 1/7 -> introjected.
        Craft: 3/3 -> scores 3.33/3.33, both below the 5.0 elevated
        threshold -> amotivated. Raw 4 would score 5.0 exactly, which
        counts as elevated.
        """
        profile = score_regulatory_style(
            {"AR1": 7, "AR2": 1, "BR1": 1, "BR2": 7, "CR1": 3, "CR2": 3}
        )
        assert profile.domains["ambition"].style == "identified"
        assert profile.domains["belonging"].style == "introjected"
        assert profile.domains["craft"].style == "amotivated"


class TestStyleClassification:
    def test_identified_when_auto_high_ctrl_low(self):
        profile = score_regulatory_style(_all_responses(ar1=6, ar2=2, br1=6, br2=2, cr1=6, cr2=2))
        assert profile.domains["ambition"].style == "identified"

    def test_conflicted_when_both_high(self):
        profile = score_regulatory_style(_all_responses(ar1=6, ar2=6, br1=6, br2=6, cr1=6, cr2=6))
        assert profile.domains["ambition"].style == "conflicted"

    def test_introjected_when_auto_low_ctrl_high(self):
        profile = score_regulatory_style(_all_responses(ar1=2, ar2=6, br1=2, br2=6, cr1=2, cr2=6))
        assert profile.domains["ambition"].style == "introjected"

    def test_amotivated_when_both_low(self):
        profile = score_regulatory_style(_all_responses(ar1=2, ar2=2, br1=2, br2=2, cr1=2, cr2=2))
        assert profile.domains["ambition"].style == "amotivated"


class TestGates:
    def test_both_items_passes_display_gate(self):
        profile = score_regulatory_style(_all_responses())
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].display_gate_passed is True

    def test_one_item_missing_fails_display_gate(self):
        responses = _all_responses()
        del responses["AR2"]
        profile = score_regulatory_style(responses)
        assert profile.domains["ambition"].display_gate_passed is False
        assert profile.domains["ambition"].style == "not_computed"
        assert profile.domains["ambition"].rai is None
        assert "AR2" in profile.domains["ambition"].gate_reason

    def test_other_domains_unaffected_when_one_missing(self):
        responses = _all_responses()
        del responses["AR2"]
        profile = score_regulatory_style(responses)
        assert profile.domains["belonging"].display_gate_passed is True
        assert profile.domains["craft"].display_gate_passed is True

    def test_clear_scores_pass_recommendation_gate(self):
        """Scores at least one ambiguous-margin away from threshold pass."""
        profile = score_regulatory_style(_all_responses(ar1=7, ar2=1, br1=7, br2=1, cr1=7, cr2=1))
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].recommendation_gate_passed is True

    def test_boundary_score_fails_recommendation_gate(self):
        """A score within 1.0 of the 5.0 threshold fails the rec gate."""
        # Scores 5.0 (exactly at threshold) and 5.0 -> conflicted, but
        # both within margin.
        profile = score_regulatory_style(_all_responses(ar1=4, ar2=4, br1=7, br2=1, cr1=7, cr2=1))
        # 1-7 raw 4 -> 0-10 score 5.0; both items at 4 land on the boundary
        assert profile.domains["ambition"].recommendation_gate_passed is False
        assert "boundary" in profile.domains["ambition"].gate_reason


class TestValidation:
    def test_rejects_non_integer(self):
        with pytest.raises(TypeError):
            score_regulatory_style({"AR1": 4.5, "AR2": 4, "BR1": 4, "BR2": 4, "CR1": 4, "CR2": 4})

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            score_regulatory_style({"AR1": 0, "AR2": 4, "BR1": 4, "BR2": 4, "CR1": 4, "CR2": 4})

    def test_ignores_unknown_items(self):
        responses = _all_responses()
        responses["AS1"] = 7
        profile = score_regulatory_style(responses)
        assert profile.items_answered == 6


class TestStructure:
    def test_profile_returns_three_domains(self):
        profile = score_regulatory_style(_all_responses())
        assert isinstance(profile, RegulatoryProfile)
        assert set(profile.domains.keys()) == {"ambition", "belonging", "craft"}
        for d in profile.domains.values():
            assert isinstance(d, DomainRegulation)

    def test_empty_responses_returns_three_not_computed(self):
        profile = score_regulatory_style({})
        for d in ("ambition", "belonging", "craft"):
            assert profile.domains[d].style == "not_computed"
            assert profile.domains[d].display_gate_passed is False
        assert profile.items_answered == 0
