"""Tests for group-conscious narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.5
Reference: improvement-plan-personalization-engine.md Section 17
"""

from __future__ import annotations

import pytest
import textstat

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _COLLECTIVE_SATISFACTION_NARRATIVES,
    _EMPATHIC_RISK_NARRATIVES,
    _TEAM_DISPERSION_NARRATIVES,
    _TEAM_IDENTIFICATION_NARRATIVES,
    NarrativeEngine,
)

ATHLETE_MAX_GRADE = 8.0
COACH_MAX_GRADE = 10.0


@pytest.fixture
def engine() -> NarrativeEngine:
    return NarrativeEngine()


def _target(audience: str) -> float:
    return ATHLETE_MAX_GRADE if audience == "athlete" else COACH_MAX_GRADE


class TestCollectiveStructure:
    def test_all_combinations_return_content(self, engine):
        for domain in engine.VALID_DOMAINS:
            for level in engine.VALID_FACET_LEVELS:
                for audience in ("athlete", "coach"):
                    text = engine.generate_collective_satisfaction_narrative(
                        domain, level, audience
                    )
                    assert isinstance(text, str)
                    assert text.strip()

    def test_invalid_domain_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_collective_satisfaction_narrative("empathy", "high", "athlete")

    def test_invalid_level_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_collective_satisfaction_narrative("ambition", "stellar", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_collective_satisfaction_narrative("ambition", "high", "parent")


class TestTeamIdentificationStructure:
    def test_all_levels_both_audiences(self, engine):
        for level in engine.VALID_FACET_LEVELS:
            for audience in ("athlete", "coach"):
                text = engine.generate_team_identification_narrative(level, audience)
                assert isinstance(text, str)
                assert text.strip()

    def test_invalid_level_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_team_identification_narrative("fervent", "athlete")


class TestEmpathicRiskStructure:
    def test_both_audiences_return_content(self, engine):
        for audience in ("athlete", "coach"):
            text = engine.generate_empathic_risk_narrative(audience)
            assert isinstance(text, str)
            assert text.strip()

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_empathic_risk_narrative("parent")


class TestDispersionStructure:
    def test_all_bands_return_content(self, engine):
        for band in engine.VALID_DISPERSION_BANDS:
            text = engine.generate_team_dispersion_narrative(band)
            assert isinstance(text, str)
            assert text.strip()

    def test_invalid_band_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_team_dispersion_narrative("chaotic")


class TestBannedTerms:
    def test_collective_templates_clean(self):
        for domain, levels in _COLLECTIVE_SATISFACTION_NARRATIVES.items():
            for level, audiences in levels.items():
                for audience, text in audiences.items():
                    hit, term = contains_banned_term(text)
                    assert not hit, (
                        f"collective {domain}/{level}/{audience} contains banned term '{term}'"
                    )

    def test_ti_templates_clean(self):
        for level, audiences in _TEAM_IDENTIFICATION_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, (
                    f"team identification {level}/{audience} contains banned term '{term}'"
                )

    def test_empathic_risk_templates_clean(self):
        for audience, text in _EMPATHIC_RISK_NARRATIVES.items():
            hit, term = contains_banned_term(text)
            assert not hit, f"empathic risk {audience} contains banned term '{term}'"

    def test_dispersion_templates_clean(self):
        for band, text in _TEAM_DISPERSION_NARRATIVES["coach"].items():
            hit, term = contains_banned_term(text)
            assert not hit, f"dispersion {band} contains banned term '{term}'"


class TestReadability:
    def test_collective_under_target(self):
        failures: list[str] = []
        for domain, levels in _COLLECTIVE_SATISFACTION_NARRATIVES.items():
            for level, audiences in levels.items():
                for audience, text in audiences.items():
                    grade = textstat.flesch_kincaid_grade(text)
                    tgt = _target(audience)
                    if grade > tgt:
                        failures.append(
                            f"collective/{domain}/{level}/{audience} "
                            f"grade={grade:.1f} target<={tgt}: {text!r}"
                        )
        assert not failures, "\n".join(failures)

    def test_ti_under_target(self):
        failures: list[str] = []
        for level, audiences in _TEAM_IDENTIFICATION_NARRATIVES.items():
            for audience, text in audiences.items():
                grade = textstat.flesch_kincaid_grade(text)
                tgt = _target(audience)
                if grade > tgt:
                    failures.append(
                        f"ti/{level}/{audience} grade={grade:.1f} target<={tgt}: {text!r}"
                    )
        assert not failures, "\n".join(failures)

    def test_empathic_risk_under_target(self):
        failures: list[str] = []
        for audience, text in _EMPATHIC_RISK_NARRATIVES.items():
            grade = textstat.flesch_kincaid_grade(text)
            tgt = _target(audience)
            if grade > tgt:
                failures.append(
                    f"empathic_risk/{audience} grade={grade:.1f} target<={tgt}: {text!r}"
                )
        assert not failures, "\n".join(failures)

    def test_dispersion_under_coach_target(self):
        failures: list[str] = []
        for band, text in _TEAM_DISPERSION_NARRATIVES["coach"].items():
            grade = textstat.flesch_kincaid_grade(text)
            if grade > COACH_MAX_GRADE:
                failures.append(f"dispersion/{band} grade={grade:.1f}: {text!r}")
        assert not failures, "\n".join(failures)
