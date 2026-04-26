"""Tests for coach circumplex scoring.

Reference: improvement-plan-personalization-engine.md Section 16.3
Reference: src/python_scoring/coach_circumplex.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.coach_circumplex import (
    AGGREGATE_MIN_RATERS,
    ALL_ITEMS,
    FACET_ITEMS,
    aggregate_athlete_ratings,
    compute_gaps,
    score_circumplex,
)


def _uniform(value: int) -> dict[str, int]:
    return dict.fromkeys(ALL_ITEMS, value)


def _supportive_heavy() -> dict[str, int]:
    """High on supportive facets, low on thwarting facets."""
    r = {}
    for facet, codes in FACET_ITEMS.items():
        target = 7 if facet in ("autonomy_support", "structure", "relatedness_support") else 1
        for code in codes:
            r[code] = target
    return r


def _thwarting_heavy() -> dict[str, int]:
    """Low on supportive, high on thwarting."""
    r = {}
    for facet, codes in FACET_ITEMS.items():
        target = 1 if facet in ("autonomy_support", "structure", "relatedness_support") else 7
        for code in codes:
            r[code] = target
    return r


class TestFacetScoring:
    def test_midpoint_scores_5(self):
        profile = score_circumplex(_uniform(4), rater="coach_self")
        for name, facet in profile.facets.items():
            assert facet.score == pytest.approx(5.0), name
            assert facet.display_gate_passed is True

    def test_max_responses_score_10(self):
        profile = score_circumplex(_uniform(7), rater="coach_self")
        for facet in profile.facets.values():
            assert facet.score == pytest.approx(10.0)

    def test_min_responses_score_0(self):
        profile = score_circumplex(_uniform(1), rater="coach_self")
        for facet in profile.facets.values():
            assert facet.score == pytest.approx(0.0)

    def test_recommendation_gate_passes_when_all_items(self):
        profile = score_circumplex(_uniform(4), rater="coach_self")
        for facet in profile.facets.values():
            assert facet.recommendation_gate_passed is True


class TestFacetLevels:
    def test_supportive_high(self):
        profile = score_circumplex(_supportive_heavy(), rater="coach_self")
        assert profile.facets["autonomy_support"].level == "high"
        assert profile.facets["structure"].level == "high"
        assert profile.facets["relatedness_support"].level == "high"

    def test_thwarting_high(self):
        profile = score_circumplex(_thwarting_heavy(), rater="coach_self")
        assert profile.facets["controlling"].level == "high"
        assert profile.facets["chaos"].level == "high"

    def test_supportive_low(self):
        responses = _uniform(2)  # score 1.67 -> low
        profile = score_circumplex(responses, rater="coach_self")
        assert profile.facets["autonomy_support"].level == "low"


class TestComposites:
    def test_supportive_profile(self):
        profile = score_circumplex(_supportive_heavy(), rater="coach_self")
        assert profile.dominant_approach == "supportive"
        assert profile.need_supportive == pytest.approx(10.0)
        assert profile.need_thwarting == pytest.approx(0.0)

    def test_thwarting_profile(self):
        profile = score_circumplex(_thwarting_heavy(), rater="coach_self")
        assert profile.dominant_approach == "thwarting"

    def test_mixed_profile(self):
        """High on everything -> mixed."""
        profile = score_circumplex(_uniform(7), rater="coach_self")
        assert profile.dominant_approach == "mixed"

    def test_under_structured(self):
        """Low on everything -> under-structured."""
        profile = score_circumplex(_uniform(2), rater="coach_self")
        assert profile.dominant_approach == "under-structured"


class TestDisplayGate:
    def test_two_items_fails_display_gate(self):
        responses = {"CXA1": 6, "CXA2": 6}  # only 2 of 5 items in autonomy_support
        profile = score_circumplex(responses, rater="coach_self")
        assert profile.facets["autonomy_support"].display_gate_passed is False
        assert profile.facets["autonomy_support"].score is None
        assert profile.facets["autonomy_support"].level == "not_computed"

    def test_three_items_passes_display_but_not_recommendation(self):
        responses = {"CXA1": 6, "CXA2": 6, "CXA3": 6}
        profile = score_circumplex(responses, rater="coach_self")
        assert profile.facets["autonomy_support"].display_gate_passed is True
        assert profile.facets["autonomy_support"].recommendation_gate_passed is False

    def test_composite_suppressed_when_too_few_facets(self):
        """Only controlling facet answered: need_supportive should be None."""
        responses = dict.fromkeys(FACET_ITEMS["controlling"], 5)
        profile = score_circumplex(responses, rater="coach_self")
        assert profile.need_supportive is None
        assert profile.need_thwarting is not None
        assert profile.dominant_approach == "not_computed"


class TestValidation:
    def test_rejects_non_integer(self):
        responses = dict.fromkeys(ALL_ITEMS, 4)
        responses["CXA1"] = 4.5
        with pytest.raises(TypeError):
            score_circumplex(responses, rater="coach_self")

    def test_rejects_out_of_range(self):
        responses = dict.fromkeys(ALL_ITEMS, 4)
        responses["CXA1"] = 0
        with pytest.raises(ValueError):
            score_circumplex(responses, rater="coach_self")

    def test_ignores_unknown_items(self):
        responses = _uniform(4)
        responses["AS1"] = 7  # not a circumplex item
        profile = score_circumplex(responses, rater="coach_self")
        assert profile.dominant_approach in ("supportive", "mixed", "under-structured", "thwarting")


class TestAthleteAggregate:
    def test_aggregates_multiple_athletes(self):
        athletes = [_uniform(6), _uniform(4), _uniform(2)]
        agg = aggregate_athlete_ratings(athletes)
        assert agg is not None
        assert agg.rater == "athlete_of_coach"
        # Mean response is 4 across items -> 5.0 on 0-10 scale
        for facet in agg.facets.values():
            assert facet.score == pytest.approx(5.0)

    def test_below_min_raters_returns_none(self):
        athletes = [_uniform(6), _uniform(4)]  # only 2, below AGGREGATE_MIN_RATERS
        assert AGGREGATE_MIN_RATERS == 3
        agg = aggregate_athlete_ratings(athletes)
        assert agg is None

    def test_empty_responses_treated_as_no_rater(self):
        athletes = [_uniform(4), _uniform(4), {"AS1": 7}]  # third has no circumplex items
        agg = aggregate_athlete_ratings(athletes)
        assert agg is None


class TestGapComputation:
    def test_gap_coach_higher_flagged(self):
        coach_self = score_circumplex(_uniform(7), rater="coach_self")
        athletes = [_uniform(3), _uniform(3), _uniform(3)]
        athlete_agg = aggregate_athlete_ratings(athletes)
        gaps = compute_gaps(coach_self, athlete_agg)
        for g in gaps:
            assert g.gap > 0
            assert g.flagged is True
            assert g.direction == "coach_higher"

    def test_gap_aligned_when_close(self):
        coach_self = score_circumplex(_uniform(4), rater="coach_self")
        athletes = [_uniform(4), _uniform(4), _uniform(4)]
        athlete_agg = aggregate_athlete_ratings(athletes)
        gaps = compute_gaps(coach_self, athlete_agg)
        for g in gaps:
            assert g.gap == pytest.approx(0.0)
            assert g.flagged is False
            assert g.direction == "aligned"

    def test_gap_rejects_mismatched_raters(self):
        coach = score_circumplex(_uniform(4), rater="coach_self")
        not_athlete = score_circumplex(_uniform(4), rater="coach_self")
        with pytest.raises(ValueError):
            compute_gaps(coach, not_athlete)

    def test_gap_rejects_non_coach_self_first_arg(self):
        not_coach = score_circumplex(_uniform(4), rater="athlete_of_coach")
        athletes = [_uniform(4), _uniform(4), _uniform(4)]
        athlete_agg = aggregate_athlete_ratings(athletes)
        with pytest.raises(ValueError):
            compute_gaps(not_coach, athlete_agg)

    def test_gap_athlete_higher_direction(self):
        """Coach under-rates themselves vs athlete aggregate."""
        coach_self = score_circumplex(_uniform(3), rater="coach_self")
        athletes = [_uniform(7), _uniform(7), _uniform(7)]
        athlete_agg = aggregate_athlete_ratings(athletes)
        gaps = compute_gaps(coach_self, athlete_agg)
        for g in gaps:
            assert g.gap < 0
            assert g.flagged is True
            assert g.direction == "athlete_higher"

    def test_gap_skips_suppressed_facets(self):
        """If a facet is not computed on either side, no gap for it."""
        coach = score_circumplex(dict.fromkeys(FACET_ITEMS["controlling"], 4), rater="coach_self")
        athletes = [_uniform(4), _uniform(4), _uniform(4)]
        athlete_agg = aggregate_athlete_ratings(athletes)
        gaps = compute_gaps(coach, athlete_agg)
        assert {g.facet for g in gaps} == {"controlling"}
