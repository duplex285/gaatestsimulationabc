"""Tests for self-concordance trajectory narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.7
Reference: improvement-plan-personalization-engine.md Section 17
"""

from __future__ import annotations

import pytest
import textstat

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _SELF_CONCORDANCE_TRAJECTORY_NARRATIVES,
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
    def test_all_labels_both_audiences(self, engine):
        for label in engine.VALID_TRAJECTORY_LABELS:
            for audience in ("athlete", "coach"):
                text = engine.generate_self_concordance_trajectory_narrative(label, audience)
                assert isinstance(text, str)
                assert text.strip()
                assert text.strip().endswith((".", "?", "!"))

    def test_distinct_text_across_labels(self, engine):
        rising = engine.generate_self_concordance_trajectory_narrative(
            "becoming_more_autonomous", "athlete"
        )
        falling = engine.generate_self_concordance_trajectory_narrative(
            "becoming_more_controlled", "athlete"
        )
        flat = engine.generate_self_concordance_trajectory_narrative("stable", "athlete")
        oscillating = engine.generate_self_concordance_trajectory_narrative(
            "oscillating", "athlete"
        )
        assert len({rising, falling, flat, oscillating}) == 4


class TestValidation:
    def test_invalid_label_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_self_concordance_trajectory_narrative(
                "improving_dramatically", "athlete"
            )

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_self_concordance_trajectory_narrative("stable", "parent")


class TestBannedTerms:
    def test_all_templates_clean(self):
        for label, audiences in _SELF_CONCORDANCE_TRAJECTORY_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, f"trajectory/{label}/{audience} contains banned term '{term}'"


class TestReadability:
    def test_all_templates_under_target(self):
        failures: list[str] = []
        for label, audiences in _SELF_CONCORDANCE_TRAJECTORY_NARRATIVES.items():
            for audience, text in audiences.items():
                grade = textstat.flesch_kincaid_grade(text)
                tgt = _target(audience)
                if grade > tgt:
                    failures.append(
                        f"trajectory/{label}/{audience} grade={grade:.1f} target<={tgt}: {text!r}"
                    )
        assert not failures, "\n".join(failures)
