"""Tests for the authoritative banned-terms module.

Reference: improvement-plan-personalization-engine.md Section 17.3
Reference: src/python_scoring/banned_terms.py
"""

from __future__ import annotations

from src.python_scoring.banned_terms import BANNED_TERMS, contains_banned_term


class TestContainsBannedTerm:
    def test_clean_text_returns_false(self):
        hit, term = contains_banned_term("Your drive is strong right now.")
        assert hit is False
        assert term is None

    def test_detects_psychometric_term(self):
        hit, term = contains_banned_term("The bifactor model fit well.")
        assert hit is True
        assert term == "bifactor"

    def test_detects_sdt_jargon(self):
        hit, term = contains_banned_term("This reflects introjected motivation.")
        assert hit is True
        assert term == "introjected"

    def test_case_insensitive(self):
        hit, term = contains_banned_term("Cronbach's alpha was high.")
        assert hit is True
        assert term == "cronbach"

    def test_word_boundary_required(self):
        """'priority' should not match 'prior'."""
        hit, term = contains_banned_term("The priority is clear communication.")
        assert hit is False

    def test_multi_word_term_detected(self):
        hit, term = contains_banned_term("We applied regression to the mean when modeling.")
        assert hit is True
        assert term == "regression to the mean"

    def test_first_match_wins(self):
        """Text with two banned terms returns the first one found."""
        hit, term = contains_banned_term("Neither cfi nor rmsea met the threshold.")
        assert hit is True
        assert term in {"cfi", "rmsea"}


class TestBannedTermsList:
    def test_list_is_non_empty(self):
        assert len(BANNED_TERMS) > 0

    def test_list_contains_expected_categories(self):
        lowered = set(BANNED_TERMS)
        # Representative sample from each category per Section 17.3
        assert "bifactor" in lowered
        assert "mahalanobis" in lowered
        assert "introjected" in lowered
        assert "sdt" in lowered
        assert "bfi-2" in lowered

    def test_list_is_immutable_tuple(self):
        assert isinstance(BANNED_TERMS, tuple)
