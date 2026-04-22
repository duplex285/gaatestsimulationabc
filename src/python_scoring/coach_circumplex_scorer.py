"""Entry-point scorer for the Coach Circumplex instrument.

The `coach_circumplex` module provides pure functions for scoring a
single rater's profile, aggregating multiple athlete ratings, and
computing coach-vs-athlete gaps per facet. This module assembles those
primitives into a stateful scorer that a product surface can use.

Reference: abc-assessment-spec Section 16.3
Reference: docs/coach-circumplex-items-draft.md
Reference: src/python_scoring/coach_circumplex.py

Design:
- One `CoachCircumplexScorer` instance per coach.
- The coach records a self-rating exactly once per cycle via
  `score_coach_self`.
- Each athlete on the coach's roster records their coach-behavior
  rating via `record_athlete_rating`. Aggregate is recomputed on demand.
- `current_report(audience)` returns the full coach-facing or athlete-
  facing output: per-facet levels, dominant-approach summary, and
  gap narratives (when both a coach self-rating and enough athlete
  ratings are available).

The scorer does not try to impose a cycle structure. It holds the
current-cycle state. Callers that want multi-cycle history wrap
multiple scorer instances or persist `current_profile()` snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from src.python_scoring.coach_circumplex import (
    AGGREGATE_MIN_RATERS,
    CircumplexProfile,
    FacetGap,
    aggregate_athlete_ratings,
    compute_gaps,
    score_circumplex,
)
from src.python_scoring.narrative_engine import NarrativeEngine

ReportAudience = Literal["coach"]


@dataclass
class CircumplexReport:
    """Assembled output for one coach at one point in time.

    Attributes:
        coach_self: The coach's self-rating profile, or None if the
            coach has not yet recorded one in this scorer.
        athlete_aggregate: The aggregated athlete profile, or None when
            fewer than AGGREGATE_MIN_RATERS athletes have submitted.
        n_athlete_raters: Count of athletes who have submitted ratings.
        facet_level_narratives: Per-facet coach-facing narrative strings,
            keyed by facet name. Drawn from the coach self-rating when
            present; falls back to the athlete aggregate when the coach
            has not yet rated.
        approach_narrative: Coach-facing dominant-approach summary for
            whichever profile drove the facet narratives.
        gap_narratives: Per-facet gap narratives, populated only for
            facets where `FacetGap.flagged` is True and both profiles
            produced a score.
        gaps: Raw FacetGap objects for every facet where both profiles
            have a score. Includes aligned gaps that did not fire a
            narrative.
        primary_source: Which profile drove the facet narratives:
            "coach_self", "athlete_aggregate", or "none".
    """

    coach_self: CircumplexProfile | None
    athlete_aggregate: CircumplexProfile | None
    n_athlete_raters: int
    facet_level_narratives: dict[str, str]
    approach_narrative: str | None
    gap_narratives: dict[str, str]
    gaps: list[FacetGap]
    primary_source: Literal["coach_self", "athlete_aggregate", "none"]


@dataclass
class CoachCircumplexScorer:
    """Stateful scorer for one coach's circumplex profile.

    Usage:
        scorer = CoachCircumplexScorer(coach_id="coach-42")
        scorer.score_coach_self(coach_responses)
        scorer.record_athlete_rating("athlete-A", athlete_a_responses)
        scorer.record_athlete_rating("athlete-B", athlete_b_responses)
        scorer.record_athlete_rating("athlete-C", athlete_c_responses)
        report = scorer.current_report()
    """

    coach_id: str
    _coach_self_profile: CircumplexProfile | None = field(default=None, init=False, repr=False)
    _athlete_responses: dict[str, dict[str, int]] = field(
        default_factory=dict, init=False, repr=False
    )
    _narrative: NarrativeEngine = field(default_factory=NarrativeEngine, init=False, repr=False)

    def score_coach_self(self, responses: dict[str, int]) -> CircumplexProfile:
        """Record the coach's self-rating and return the profile.

        Reference: abc-assessment-spec Section 16.3
        """
        profile = score_circumplex(responses, rater="coach_self")
        self._coach_self_profile = profile
        return profile

    def record_athlete_rating(
        self,
        athlete_id: str,
        responses: dict[str, int],
    ) -> None:
        """Record one athlete's rating of the coach.

        Reference: abc-assessment-spec Section 16.3

        Subsequent calls with the same athlete_id overwrite the previous
        response for that athlete. This reflects real delivery: an
        athlete may submit once per cycle and updates supersede.
        """
        self._athlete_responses[athlete_id] = responses

    def athlete_rater_count(self) -> int:
        """Number of athletes who have submitted a rating in this scorer."""
        return len(self._athlete_responses)

    def current_profile(self) -> CircumplexProfile | None:
        """Return the coach's self-rating profile, or None if not yet recorded.

        Reference: abc-assessment-spec Section 16.3
        """
        return self._coach_self_profile

    def current_athlete_aggregate(self) -> CircumplexProfile | None:
        """Return the aggregated athlete profile, or None when under minimum.

        Reference: abc-assessment-spec Section 16.3
        """
        return aggregate_athlete_ratings(list(self._athlete_responses.values()))

    def current_gap_analysis(self) -> list[FacetGap]:
        """Return per-facet gaps. Empty when either side is missing.

        Reference: abc-assessment-spec Section 16.3
        """
        if self._coach_self_profile is None:
            return []
        athlete_agg = self.current_athlete_aggregate()
        if athlete_agg is None:
            return []
        return compute_gaps(self._coach_self_profile, athlete_agg)

    def current_report(self) -> CircumplexReport:
        """Assemble the full coach-facing report.

        Reference: abc-assessment-spec Section 16.3

        The primary source for facet level narratives is the coach's
        self-rating when present, falling back to the athlete aggregate
        when only athletes have submitted. When neither is available the
        report still returns; it simply carries empty narrative dicts
        and `primary_source="none"`.

        Gap narratives populate only when both the coach self-rating
        and the athlete aggregate are available and the gap is flagged.
        """
        coach_self = self._coach_self_profile
        athlete_agg = self.current_athlete_aggregate()
        n_raters = self.athlete_rater_count()

        primary: Literal["coach_self", "athlete_aggregate", "none"]
        if coach_self is not None:
            primary = "coach_self"
            source_profile = coach_self
        elif athlete_agg is not None:
            primary = "athlete_aggregate"
            source_profile = athlete_agg
        else:
            return CircumplexReport(
                coach_self=None,
                athlete_aggregate=None,
                n_athlete_raters=n_raters,
                facet_level_narratives={},
                approach_narrative=None,
                gap_narratives={},
                gaps=[],
                primary_source="none",
            )

        facet_narratives: dict[str, str] = {}
        for facet_name, facet in source_profile.facets.items():
            facet_narratives[facet_name] = self._narrative.generate_circumplex_facet_narrative(
                facet_name, facet.level
            )

        approach = self._narrative.generate_circumplex_approach_narrative(
            source_profile.dominant_approach
        )

        gap_narratives: dict[str, str] = {}
        gaps = self.current_gap_analysis()
        for gap in gaps:
            if gap.flagged and gap.direction in ("coach_higher", "athlete_higher"):
                gap_narratives[gap.facet] = self._narrative.generate_circumplex_gap_narrative(
                    gap.facet, gap.direction
                )

        return CircumplexReport(
            coach_self=coach_self,
            athlete_aggregate=athlete_agg,
            n_athlete_raters=n_raters,
            facet_level_narratives=facet_narratives,
            approach_narrative=approach,
            gap_narratives=gap_narratives,
            gaps=gaps,
            primary_source=primary,
        )


__all__ = [
    "AGGREGATE_MIN_RATERS",
    "CircumplexReport",
    "CoachCircumplexScorer",
]
