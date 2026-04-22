"""Tests for the CoachCircumplexScorer entry point.

Reference: improvement-plan-personalization-engine.md Section 16.3
Reference: src/python_scoring/coach_circumplex_scorer.py
"""

from __future__ import annotations

from src.python_scoring.coach_circumplex import ALL_ITEMS, FACET_ITEMS
from src.python_scoring.coach_circumplex_scorer import (
    AGGREGATE_MIN_RATERS,
    CoachCircumplexScorer,
)


def _uniform(value: int) -> dict[str, int]:
    return dict.fromkeys(ALL_ITEMS, value)


def _supportive_heavy() -> dict[str, int]:
    r = {}
    for facet, codes in FACET_ITEMS.items():
        target = 7 if facet in ("autonomy_support", "structure", "relatedness_support") else 1
        for code in codes:
            r[code] = target
    return r


def _thwarting_heavy() -> dict[str, int]:
    r = {}
    for facet, codes in FACET_ITEMS.items():
        target = 1 if facet in ("autonomy_support", "structure", "relatedness_support") else 7
        for code in codes:
            r[code] = target
    return r


class TestCoachOnlyPath:
    def test_coach_self_score_returns_profile(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        profile = scorer.score_coach_self(_supportive_heavy())
        assert profile.rater == "coach_self"
        assert profile.dominant_approach == "supportive"

    def test_current_profile_reflects_coach_self(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_supportive_heavy())
        p = scorer.current_profile()
        assert p is not None
        assert p.dominant_approach == "supportive"

    def test_report_with_coach_only(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_supportive_heavy())
        report = scorer.current_report()
        assert report.primary_source == "coach_self"
        assert report.coach_self is not None
        assert report.athlete_aggregate is None
        assert len(report.facet_level_narratives) == 5
        assert report.approach_narrative
        assert report.gap_narratives == {}
        assert report.gaps == []


class TestAthletesOnlyPath:
    def test_report_falls_back_to_aggregate_when_no_coach_self(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.record_athlete_rating("a1", _thwarting_heavy())
        scorer.record_athlete_rating("a2", _thwarting_heavy())
        scorer.record_athlete_rating("a3", _thwarting_heavy())
        report = scorer.current_report()
        assert report.primary_source == "athlete_aggregate"
        assert report.coach_self is None
        assert report.athlete_aggregate is not None
        assert len(report.facet_level_narratives) == 5
        assert report.approach_narrative
        # Athletes see thwarting: approach should reflect that
        assert report.athlete_aggregate.dominant_approach == "thwarting"

    def test_below_minimum_athletes_no_aggregate(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.record_athlete_rating("a1", _supportive_heavy())
        scorer.record_athlete_rating("a2", _supportive_heavy())
        assert AGGREGATE_MIN_RATERS == 3
        report = scorer.current_report()
        assert report.primary_source == "none"
        assert report.athlete_aggregate is None
        assert report.n_athlete_raters == 2


class TestDualPath:
    def test_aligned_coach_and_athletes_no_flagged_gaps(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_supportive_heavy())
        scorer.record_athlete_rating("a1", _supportive_heavy())
        scorer.record_athlete_rating("a2", _supportive_heavy())
        scorer.record_athlete_rating("a3", _supportive_heavy())
        report = scorer.current_report()
        assert report.primary_source == "coach_self"
        assert report.athlete_aggregate is not None
        # No flagged gaps when both sides agree
        assert report.gap_narratives == {}
        # But raw gaps still populate for every facet
        assert len(report.gaps) == 5
        assert all(not g.flagged for g in report.gaps)

    def test_coach_overrates_gap_narratives_fire(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_uniform(7))  # coach self-rates everything high
        scorer.record_athlete_rating("a1", _uniform(3))
        scorer.record_athlete_rating("a2", _uniform(3))
        scorer.record_athlete_rating("a3", _uniform(3))
        report = scorer.current_report()
        # Every facet should be flagged because the uniform-7-vs-uniform-3 gap
        # is a 6.67-point spread.
        assert len(report.gap_narratives) == 5
        for gap in report.gaps:
            assert gap.flagged
            assert gap.direction == "coach_higher"

    def test_coach_underrates_athlete_higher_direction(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_uniform(3))  # coach humble
        scorer.record_athlete_rating("a1", _uniform(7))
        scorer.record_athlete_rating("a2", _uniform(7))
        scorer.record_athlete_rating("a3", _uniform(7))
        report = scorer.current_report()
        assert len(report.gap_narratives) == 5
        for gap in report.gaps:
            assert gap.flagged
            assert gap.direction == "athlete_higher"


class TestMultipleAthletesAccumulating:
    def test_athlete_rating_overwrite(self):
        """Recording a second rating for the same athlete supersedes."""
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.record_athlete_rating("a1", _supportive_heavy())
        scorer.record_athlete_rating("a1", _thwarting_heavy())
        assert scorer.athlete_rater_count() == 1

    def test_unique_athletes_accumulate(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        for i in range(5):
            scorer.record_athlete_rating(f"a{i}", _supportive_heavy())
        assert scorer.athlete_rater_count() == 5
        # Aggregate should be computable
        agg = scorer.current_athlete_aggregate()
        assert agg is not None
        assert agg.dominant_approach == "supportive"


class TestEmptyState:
    def test_empty_scorer_report(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        report = scorer.current_report()
        assert report.primary_source == "none"
        assert report.coach_self is None
        assert report.athlete_aggregate is None
        assert report.facet_level_narratives == {}
        assert report.approach_narrative is None
        assert report.gap_narratives == {}
        assert report.gaps == []
        assert report.n_athlete_raters == 0

    def test_empty_scorer_gap_analysis(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        assert scorer.current_gap_analysis() == []

    def test_coach_only_gap_analysis(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.score_coach_self(_supportive_heavy())
        assert scorer.current_gap_analysis() == []

    def test_athletes_only_gap_analysis(self):
        scorer = CoachCircumplexScorer(coach_id="coach-1")
        scorer.record_athlete_rating("a1", _supportive_heavy())
        scorer.record_athlete_rating("a2", _supportive_heavy())
        scorer.record_athlete_rating("a3", _supportive_heavy())
        assert scorer.current_gap_analysis() == []
