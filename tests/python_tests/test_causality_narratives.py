"""Tests for causality-orientation narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.6
Reference: improvement-plan-personalization-engine.md Section 17
"""

from __future__ import annotations

import pytest
import textstat

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _CAUSALITY_NARRATIVES,
    NarrativeEngine,
)

ATHLETE_MAX_GRADE = 8.0
COACH_MAX_GRADE = 10.0


@pytest.fixture
def engine() -> NarrativeEngine:
    return NarrativeEngine()


def _target(audience: str) -> float:
    return ATHLETE_MAX_GRADE if audience == "athlete" else COACH_MAX_GRADE


class TestStructure:
    def test_all_orientations_both_audiences(self, engine):
        for orientation in engine.VALID_CAUSALITY_ORIENTATIONS:
            for audience in ("athlete", "coach"):
                text = engine.generate_causality_narrative(orientation, audience)
                assert isinstance(text, str)
                assert text.strip()
                assert text.strip().endswith((".", "?", "!"))

    def test_distinct_text_across_orientations(self, engine):
        """Each orientation should produce different text."""
        autonomy = engine.generate_causality_narrative("autonomy", "athlete")
        controlled = engine.generate_causality_narrative("controlled", "athlete")
        impersonal = engine.generate_causality_narrative("impersonal", "athlete")
        assert autonomy != controlled
        assert controlled != impersonal
        assert autonomy != impersonal


class TestValidation:
    def test_invalid_orientation_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_causality_narrative("fervent", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_causality_narrative("autonomy", "parent")


class TestBannedTerms:
    def test_all_templates_clean(self):
        for orientation, audiences in _CAUSALITY_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, f"causality/{orientation}/{audience} contains banned term '{term}'"


class TestReadability:
    def test_all_templates_under_target(self):
        failures: list[str] = []
        for orientation, audiences in _CAUSALITY_NARRATIVES.items():
            for audience, text in audiences.items():
                grade = textstat.flesch_kincaid_grade(text)
                tgt = _target(audience)
                if grade > tgt:
                    failures.append(
                        f"causality/{orientation}/{audience} "
                        f"grade={grade:.1f} target<={tgt}: {text!r}"
                    )
        assert not failures, "\n".join(failures)
