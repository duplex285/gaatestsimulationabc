"""Tests for coach-circumplex narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.3
Reference: improvement-plan-personalization-engine.md Section 17
"""

from __future__ import annotations

import pytest
import textstat

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _CIRCUMPLEX_APPROACH_NARRATIVES,
    _CIRCUMPLEX_FACET_NARRATIVES,
    _CIRCUMPLEX_GAP_NARRATIVES,
    NarrativeEngine,
)

COACH_MAX_GRADE = 10.0


@pytest.fixture
def engine() -> NarrativeEngine:
    return NarrativeEngine()


class TestFacetNarratives:
    def test_all_facets_and_levels_return_content(self, engine):
        for facet in engine.VALID_CIRCUMPLEX_FACETS:
            for level in engine.VALID_FACET_LEVELS:
                text = engine.generate_circumplex_facet_narrative(facet, level)
                assert isinstance(text, str)
                assert len(text.strip()) > 0
                assert text.strip().endswith((".", "?", "!"))

    def test_invalid_facet_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_circumplex_facet_narrative("excellence", "high")

    def test_invalid_level_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_circumplex_facet_narrative("autonomy_support", "stellar")


class TestApproachNarratives:
    def test_all_approaches_return_content(self, engine):
        for approach in engine.VALID_DOMINANT_APPROACHES:
            text = engine.generate_circumplex_approach_narrative(approach)
            assert isinstance(text, str)
            assert len(text.strip()) > 0

    def test_invalid_approach_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_circumplex_approach_narrative("brilliant")


class TestBannedTerms:
    def test_facet_templates_clean(self):
        for facet, levels in _CIRCUMPLEX_FACET_NARRATIVES.items():
            for level, text in levels.items():
                hit, term = contains_banned_term(text)
                assert not hit, (
                    f"circumplex facet {facet}/{level} contains banned term '{term}': {text!r}"
                )

    def test_approach_templates_clean(self):
        for approach, text in _CIRCUMPLEX_APPROACH_NARRATIVES.items():
            hit, term = contains_banned_term(text)
            assert not hit, (
                f"circumplex approach {approach} contains banned term '{term}': {text!r}"
            )


class TestGapNarratives:
    def test_all_facets_and_directions_return_content(self, engine):
        for facet in engine.VALID_CIRCUMPLEX_FACETS:
            for direction in engine.VALID_GAP_DIRECTIONS:
                text = engine.generate_circumplex_gap_narrative(facet, direction)
                assert isinstance(text, str)
                assert text.strip()
                assert text.strip().endswith((".", "?", "!"))

    def test_invalid_facet_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_circumplex_gap_narrative("excellence", "coach_higher")

    def test_invalid_direction_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_circumplex_gap_narrative("autonomy_support", "aligned")

    def test_gap_templates_clean(self):
        for facet, directions in _CIRCUMPLEX_GAP_NARRATIVES.items():
            for direction, text in directions.items():
                hit, term = contains_banned_term(text)
                assert not hit, f"gap {facet}/{direction} contains banned term '{term}'"


class TestReadability:
    """Coach-facing only; all templates must be <= Grade 10."""

    def test_facet_templates_under_grade_10(self):
        failures: list[str] = []
        for facet, levels in _CIRCUMPLEX_FACET_NARRATIVES.items():
            for level, text in levels.items():
                grade = textstat.flesch_kincaid_grade(text)
                if grade > COACH_MAX_GRADE:
                    failures.append(f"circumplex/{facet}/{level} grade={grade:.1f}: {text!r}")
        assert not failures, "\n".join(failures)

    def test_approach_templates_under_grade_10(self):
        failures: list[str] = []
        for approach, text in _CIRCUMPLEX_APPROACH_NARRATIVES.items():
            grade = textstat.flesch_kincaid_grade(text)
            if grade > COACH_MAX_GRADE:
                failures.append(f"circumplex approach {approach} grade={grade:.1f}: {text!r}")
        assert not failures, "\n".join(failures)

    def test_gap_templates_under_grade_10(self):
        failures: list[str] = []
        for facet, directions in _CIRCUMPLEX_GAP_NARRATIVES.items():
            for direction, text in directions.items():
                grade = textstat.flesch_kincaid_grade(text)
                if grade > COACH_MAX_GRADE:
                    failures.append(f"gap/{facet}/{direction} grade={grade:.1f}: {text!r}")
        assert not failures, "\n".join(failures)
