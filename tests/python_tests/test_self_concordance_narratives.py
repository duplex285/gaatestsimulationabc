"""Tests for self-concordance narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.7
Reference: improvement-plan-personalization-engine.md Section 17
"""

from __future__ import annotations

import pytest
import textstat

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _SELF_CONCORDANCE_NARRATIVES,
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
    def test_all_leanings_both_audiences(self, engine):
        for leaning in engine.VALID_SELF_CONCORDANCE_LEANINGS:
            for audience in ("athlete", "coach"):
                text = engine.generate_self_concordance_narrative(leaning, audience)
                assert isinstance(text, str)
                assert text.strip()
                assert text.strip().endswith((".", "?", "!"))

    def test_distinct_text_across_leanings(self, engine):
        autonomous = engine.generate_self_concordance_narrative("autonomous", "athlete")
        controlled = engine.generate_self_concordance_narrative("controlled", "athlete")
        mixed = engine.generate_self_concordance_narrative("mixed", "athlete")
        assert autonomous != controlled
        assert controlled != mixed
        assert autonomous != mixed


class TestValidation:
    def test_invalid_leaning_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_self_concordance_narrative("euphoric", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_self_concordance_narrative("autonomous", "parent")


class TestBannedTerms:
    def test_all_templates_clean(self):
        for leaning, audiences in _SELF_CONCORDANCE_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, (
                    f"self_concordance/{leaning}/{audience} contains banned term '{term}'"
                )


class TestReadability:
    def test_all_templates_under_target(self):
        failures: list[str] = []
        for leaning, audiences in _SELF_CONCORDANCE_NARRATIVES.items():
            for audience, text in audiences.items():
                grade = textstat.flesch_kincaid_grade(text)
                tgt = _target(audience)
                if grade > tgt:
                    failures.append(
                        f"self_concordance/{leaning}/{audience} "
                        f"grade={grade:.1f} target<={tgt}: {text!r}"
                    )
        assert not failures, "\n".join(failures)
