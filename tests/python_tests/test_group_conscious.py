"""Tests for the group-conscious scoring module.

Reference: improvement-plan-personalization-engine.md Section 16.5
Reference: src/python_scoring/group_conscious.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.group_conscious import (
    DISPERSION_MIN_ATHLETES,
    compute_team_dispersion,
    score_group_conscious,
)


def _full_responses(
    ag1: int = 4,
    bg1: int = 4,
    cg1: int = 4,
    ti1: int = 4,
    ti2: int = 4,
) -> dict[str, int]:
    return {"AG1": ag1, "BG1": bg1, "CG1": cg1, "TI1": ti1, "TI2": ti2}


class TestScoring:
    def test_midpoint_responses(self):
        profile = score_group_conscious(_full_responses())
        for d in ("ambition", "belonging", "craft"):
            assert profile.collective[d].score == pytest.approx(5.0)
        assert profile.team_identification.score == pytest.approx(5.0)

    def test_max_responses(self):
        profile = score_group_conscious(_full_responses(ag1=7, bg1=7, cg1=7, ti1=7, ti2=7))
        for d in ("ambition", "belonging", "craft"):
            assert profile.collective[d].score == pytest.approx(10.0)
        assert profile.team_identification.score == pytest.approx(10.0)

    def test_min_responses(self):
        profile = score_group_conscious(_full_responses(ag1=1, bg1=1, cg1=1, ti1=1, ti2=1))
        for d in ("ambition", "belonging", "craft"):
            assert profile.collective[d].score == pytest.approx(0.0)


class TestLevels:
    def test_high_level(self):
        profile = score_group_conscious(_full_responses(ag1=6, bg1=6, cg1=6))
        assert profile.collective["ambition"].level == "high"

    def test_moderate_level(self):
        profile = score_group_conscious(_full_responses(ag1=4))  # score 5.0 -> moderate
        assert profile.collective["ambition"].level == "moderate"

    def test_low_level(self):
        profile = score_group_conscious(_full_responses(ag1=2))  # score 1.67 -> low
        assert profile.collective["ambition"].level == "low"


class TestEmpathicRisk:
    def test_fires_when_high_ti_and_low_collective(self):
        """TI 7/7 -> score 10 (>=6). AG1 2 -> score 1.67 (<4). Risk on ambition."""
        profile = score_group_conscious(_full_responses(ag1=2, bg1=6, cg1=6, ti1=7, ti2=7))
        assert "ambition" in profile.empathic_risk_domains
        assert "belonging" not in profile.empathic_risk_domains
        assert "craft" not in profile.empathic_risk_domains

    def test_no_fire_with_low_ti(self):
        """Low TI suppresses empathic risk regardless of collective."""
        profile = score_group_conscious(_full_responses(ag1=1, bg1=1, cg1=1, ti1=1, ti2=1))
        assert profile.empathic_risk_domains == []

    def test_multiple_domains_can_fire(self):
        profile = score_group_conscious(_full_responses(ag1=1, bg1=1, cg1=1, ti1=7, ti2=7))
        assert set(profile.empathic_risk_domains) == {"ambition", "belonging", "craft"}

    def test_suppressed_when_ti_missing(self):
        responses = {"AG1": 1, "BG1": 1, "CG1": 1}
        profile = score_group_conscious(responses)
        assert profile.empathic_risk_domains == []
        assert profile.team_identification.score is None


class TestGates:
    def test_both_ti_items_passes_recommendation_gate(self):
        profile = score_group_conscious(_full_responses())
        assert profile.team_identification.recommendation_gate_passed is True

    def test_one_ti_item_fails_recommendation_gate(self):
        profile = score_group_conscious({"AG1": 4, "BG1": 4, "CG1": 4, "TI1": 4})
        assert profile.team_identification.display_gate_passed is True
        assert profile.team_identification.recommendation_gate_passed is False

    def test_missing_collective_item_fails_display_for_that_domain(self):
        profile = score_group_conscious({"BG1": 4, "CG1": 4, "TI1": 4, "TI2": 4})
        assert profile.collective["ambition"].display_gate_passed is False
        assert profile.collective["ambition"].level == "not_computed"
        assert profile.collective["belonging"].display_gate_passed is True


class TestValidation:
    def test_rejects_non_integer(self):
        with pytest.raises(TypeError):
            score_group_conscious({"AG1": 4.5, "BG1": 4, "CG1": 4, "TI1": 4, "TI2": 4})

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            score_group_conscious({"AG1": 8, "BG1": 4, "CG1": 4, "TI1": 4, "TI2": 4})

    def test_ignores_unknown_items(self):
        responses = _full_responses()
        responses["AS1"] = 7
        profile = score_group_conscious(responses)
        assert profile.items_answered == 5


def _flat_athlete(value: float) -> dict[str, float]:
    return {
        "a_sat": value,
        "a_frust": value,
        "b_sat": value,
        "b_frust": value,
        "c_sat": value,
        "c_frust": value,
    }


class TestDispersion:
    def test_below_min_athletes_not_computed(self):
        teams = [_flat_athlete(5.0)]
        d = compute_team_dispersion(teams)
        assert d.computed is False
        assert d.team_size == 1

    def test_three_athletes_identical_tight(self):
        teams = [_flat_athlete(7.0), _flat_athlete(7.0), _flat_athlete(7.0)]
        d = compute_team_dispersion(teams)
        assert d.computed is True
        assert d.team_size == 3
        for key in d.subscale_sds:
            assert d.subscale_sds[key] == pytest.approx(0.0)
            assert d.subscale_bands[key] == "tight"
        assert d.high_dispersion_subscales == []

    def test_moderate_dispersion_band(self):
        """Three athletes at 3, 5, 7 on a_sat produce stdev 2.0 -> moderate."""
        teams = [_flat_athlete(3.0), _flat_athlete(5.0), _flat_athlete(7.0)]
        d = compute_team_dispersion(teams)
        assert d.computed is True
        assert d.subscale_bands["a_sat"] == "moderate"
        assert 1.5 <= d.subscale_sds["a_sat"] < 2.5

    def test_high_dispersion_fires(self):
        """Half thriving on belonging, half struggling."""
        high_belong = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 9.0,
            "b_frust": 1.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        low_belong = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 1.0,
            "b_frust": 9.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        teams = [high_belong, high_belong, low_belong, low_belong]
        d = compute_team_dispersion(teams)
        assert d.computed is True
        assert "b_sat" in d.high_dispersion_subscales
        assert "b_frust" in d.high_dispersion_subscales
        assert d.subscale_bands["a_sat"] == "tight"

    def test_missing_subscale_skipped(self):
        """Subscale missing from enough athletes is silently skipped."""
        teams = [
            {"a_sat": 5.0},
            {"a_sat": 5.0},
            {"a_sat": 5.0},
        ]
        d = compute_team_dispersion(teams)
        assert d.computed is True
        assert "a_sat" in d.subscale_sds
        assert "b_sat" not in d.subscale_sds

    def test_min_athletes_constant(self):
        assert DISPERSION_MIN_ATHLETES == 3
