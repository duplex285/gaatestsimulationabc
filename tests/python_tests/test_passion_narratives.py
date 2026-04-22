"""Tests for passion and overinvestment narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.2
Reference: improvement-plan-personalization-engine.md Section 17.3 (banned terms)
Reference: improvement-plan-personalization-engine.md Section 17.4 (translation table)

Coverage:
- Every leaning and path produces content for both audiences
- Athlete-facing includes a reflection prompt; coach-facing includes a
  conversation starter
- No banned terms appear in any output
- Content is non-empty and ends with a full stop
- Invalid leaning or path raises ValueError
"""

from __future__ import annotations

import pytest

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _OVERINVESTMENT_NARRATIVES,
    _PASSION_NARRATIVES,
    NarrativeEngine,
)


@pytest.fixture
def engine() -> NarrativeEngine:
    return NarrativeEngine()


class TestPassionNarrativeStructure:
    """Shape of the output dict per audience."""

    def test_athlete_has_summary_and_reflection_prompt(self, engine):
        result = engine.generate_passion_narrative("harmonious", "athlete")
        assert "summary" in result
        assert "reflection_prompt" in result
        assert "conversation_starter" not in result

    def test_coach_has_summary_and_conversation_starter(self, engine):
        result = engine.generate_passion_narrative("harmonious", "coach")
        assert "summary" in result
        assert "conversation_starter" in result
        assert "reflection_prompt" not in result

    def test_all_leanings_have_content_for_both_audiences(self, engine):
        for leaning in engine.VALID_PASSION_LEANINGS:
            for audience in ("athlete", "coach"):
                result = engine.generate_passion_narrative(leaning, audience)
                assert result["summary"]
                assert result["summary"].strip().endswith((".", "?", "!"))


class TestPassionNarrativeValidation:
    def test_invalid_leaning_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_passion_narrative("euphoric", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_passion_narrative("harmonious", "parent")


class TestOverinvestmentNarrativeStructure:
    def test_returns_string(self, engine):
        result = engine.generate_overinvestment_narrative("harmonious", "coach")
        assert isinstance(result, str)
        assert result.strip().endswith((".", "?", "!"))

    def test_all_paths_have_content_for_both_audiences(self, engine):
        for path in engine.VALID_OVERINVESTMENT_PATHS:
            for audience in ("athlete", "coach"):
                text = engine.generate_overinvestment_narrative(path, audience)
                assert isinstance(text, str)
                assert len(text) > 0


class TestOverinvestmentNarrativeValidation:
    def test_invalid_path_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_overinvestment_narrative("collapse", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_overinvestment_narrative("harmonious", "parent")


class TestBannedTerms:
    """No technical term from Section 17.3 appears in any template."""

    def test_passion_templates_have_no_banned_terms(self):
        for leaning, audiences in _PASSION_NARRATIVES.items():
            for audience, content in audiences.items():
                for key, text in content.items():
                    hit, term = contains_banned_term(text)
                    assert not hit, (
                        f"passion template {leaning}/{audience}/{key} "
                        f"contains banned term '{term}': {text!r}"
                    )

    def test_overinvestment_templates_have_no_banned_terms(self):
        for path, audiences in _OVERINVESTMENT_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, (
                    f"overinvestment template {path}/{audience} "
                    f"contains banned term '{term}': {text!r}"
                )
