"""Tests for regulatory-style and erosion narrative templates.

Reference: improvement-plan-personalization-engine.md Section 16.1
Reference: improvement-plan-personalization-engine.md Section 17.3 (banned terms)
Reference: improvement-plan-personalization-engine.md Section 17.4 (translation table)
"""

from __future__ import annotations

import pytest

from src.python_scoring.banned_terms import contains_banned_term
from src.python_scoring.narrative_engine import (
    _EROSION_NARRATIVES,
    _REGULATORY_NARRATIVES,
    NarrativeEngine,
)


@pytest.fixture
def engine() -> NarrativeEngine:
    return NarrativeEngine()


class TestRegulatoryNarrativeStructure:
    def test_all_styles_and_domains_return_content(self, engine):
        for style in engine.VALID_REGULATORY_STYLES:
            for domain in engine.VALID_DOMAINS:
                for audience in ("athlete", "coach"):
                    text = engine.generate_regulatory_narrative(domain, style, audience)
                    assert isinstance(text, str)
                    assert len(text.strip()) > 0
                    assert text.strip().endswith((".", "?", "!"))

    def test_domain_wording_swapped_in(self, engine):
        """Domain substitution produces different athlete text per domain."""
        a = engine.generate_regulatory_narrative("ambition", "identified", "athlete")
        b = engine.generate_regulatory_narrative("belonging", "identified", "athlete")
        c = engine.generate_regulatory_narrative("craft", "identified", "athlete")
        assert a != b
        assert b != c
        assert "goals" in a
        assert "teammates" in b
        assert "skills" in c

    def test_coach_wording_differs_by_domain(self, engine):
        """Regression: coach text must name the domain, not say 'this area'.

        Original implementation used a generic "this area" placeholder in
        every coach template. A coach reading three domain entries could
        not tell which was which. Templates now substitute the domain
        phrase.
        """
        for style in ("identified", "conflicted", "introjected", "amotivated"):
            a = engine.generate_regulatory_narrative("ambition", style, "coach")
            b = engine.generate_regulatory_narrative("belonging", style, "coach")
            c = engine.generate_regulatory_narrative("craft", style, "coach")
            assert a != b, f"coach/{style}: ambition and belonging text identical"
            assert b != c, f"coach/{style}: belonging and craft text identical"
            assert "goal pursuit" in a
            assert "team relationships" in b
            assert "skill development" in c

    def test_coach_erosion_names_domain(self, engine):
        """Regression: coach erosion narrative must name the domain too."""
        a = engine.generate_erosion_narrative("ambition", "coach")
        b = engine.generate_erosion_narrative("belonging", "coach")
        c = engine.generate_erosion_narrative("craft", "coach")
        assert "goal pursuit" in a
        assert "team relationships" in b
        assert "skill development" in c
        assert a != b
        assert b != c


class TestRegulatoryNarrativeValidation:
    def test_invalid_style_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_regulatory_narrative("ambition", "whimsical", "athlete")

    def test_invalid_domain_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_regulatory_narrative("elegance", "identified", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_regulatory_narrative("ambition", "identified", "parent")


class TestErosionNarrativeStructure:
    def test_all_domains_both_audiences(self, engine):
        for domain in engine.VALID_DOMAINS:
            for audience in ("athlete", "coach"):
                text = engine.generate_erosion_narrative(domain, audience)
                assert isinstance(text, str)
                assert len(text.strip()) > 0

    def test_domain_specific_wording(self, engine):
        ambition = engine.generate_erosion_narrative("ambition", "athlete")
        belonging = engine.generate_erosion_narrative("belonging", "athlete")
        assert "goals" in ambition
        assert "teammates" in belonging


class TestErosionNarrativeValidation:
    def test_invalid_domain_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_erosion_narrative("elegance", "athlete")

    def test_invalid_audience_raises(self, engine):
        with pytest.raises(ValueError):
            engine.generate_erosion_narrative("ambition", "parent")


class TestBannedTerms:
    """No banned term appears in any regulatory or erosion template."""

    def test_regulatory_templates_clean(self):
        for style, audiences in _REGULATORY_NARRATIVES.items():
            for audience, text in audiences.items():
                hit, term = contains_banned_term(text)
                assert not hit, (
                    f"regulatory template {style}/{audience} contains "
                    f"banned term '{term}': {text!r}"
                )

    def test_erosion_templates_clean(self):
        for audience, text in _EROSION_NARRATIVES.items():
            hit, term = contains_banned_term(text)
            assert not hit, f"erosion template {audience} contains banned term '{term}': {text!r}"

    def test_rendered_regulatory_text_clean(self):
        """Domain substitution must not introduce banned terms."""
        engine = NarrativeEngine()
        for style in engine.VALID_REGULATORY_STYLES:
            for domain in engine.VALID_DOMAINS:
                for audience in ("athlete", "coach"):
                    text = engine.generate_regulatory_narrative(domain, style, audience)
                    hit, term = contains_banned_term(text)
                    assert not hit, (
                        f"rendered {domain}/{style}/{audience} contains "
                        f"banned term '{term}': {text!r}"
                    )
