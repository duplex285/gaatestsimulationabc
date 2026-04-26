"""Coach Circumplex scoring for the ABC Assessment.

Scores 24 items across five coaching-climate facets (autonomy-support,
structure, relatedness-support, controlling, chaos), produces composites
and a dominant-approach label, and computes the gap between a coach's
self-rating and an aggregated athlete rating when both are available.

Reference: abc-assessment-spec Section 16.3
Reference: abc-assessment-spec Section 17.5 (evidence gates)
Reference: docs/coach-circumplex-items-draft.md (item content and scoring model)

Research basis:
  Aelterman et al. (2019), circumplex of coaching approaches via
    Chapter 11 of the Oxford Handbook of SDT.
  Soenens & Vansteenkiste, Chapter 25 (autonomy-supportive behaviors
    across socialization domains).
  Slemp et al., Chapter 45 (leadership and need-support).

This is a separate instrument from the athlete-facing ABC core. The
same 24 items are administered to both the coach (self-rating) and
each athlete (rating of the coach). Rater identity is metadata on the
response, not part of the item code.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Literal

FACET_ITEMS: dict[str, tuple[str, ...]] = {
    "autonomy_support": ("CXA1", "CXA2", "CXA3", "CXA4", "CXA5"),
    "structure": ("CXS1", "CXS2", "CXS3", "CXS4", "CXS5"),
    "relatedness_support": ("CXR1", "CXR2", "CXR3", "CXR4", "CXR5"),
    "controlling": ("CXC1", "CXC2", "CXC3", "CXC4", "CXC5"),
    "chaos": ("CXH1", "CXH2", "CXH3", "CXH4"),
}

ALL_ITEMS: tuple[str, ...] = tuple(code for codes in FACET_ITEMS.values() for code in codes)

SUPPORTIVE_FACETS: tuple[str, ...] = (
    "autonomy_support",
    "structure",
    "relatedness_support",
)
THWARTING_FACETS: tuple[str, ...] = ("controlling", "chaos")

DISPLAY_MIN_ITEMS_PER_FACET = 3

COMPOSITE_SUPPORT_HIGH = 6.0
COMPOSITE_THWART_HIGH = 4.0

GAP_FLAG_THRESHOLD = 2.0
AGGREGATE_MIN_RATERS = 3

Rater = Literal["coach_self", "athlete_of_coach"]
FacetLevel = Literal["high", "moderate", "low", "not_computed"]
DominantApproach = Literal[
    "supportive",
    "mixed",
    "under-structured",
    "thwarting",
    "not_computed",
]


@dataclass
class FacetScore:
    """One facet within a Coach Circumplex profile.

    Attributes:
        score: 0-10 mean across answered items in the facet. None when
            the facet did not pass the display gate.
        items_answered: Count of the facet's items with valid responses.
        level: Qualitative level used by narrative selection. high, moderate,
            low, or not_computed.
        display_gate_passed: True if at least DISPLAY_MIN_ITEMS_PER_FACET
            items were answered.
        recommendation_gate_passed: True if all of the facet's items were
            answered (no missing data within the facet).
        gate_reason: Human-readable reason when a gate fails.
    """

    score: float | None
    items_answered: int
    level: FacetLevel
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


@dataclass
class CircumplexProfile:
    """Full profile for a single rater (coach or athlete) of a coach.

    Attributes:
        rater: Who rated the coach.
        facets: Dict of facet name to FacetScore.
        need_supportive: Composite mean across the three supportive
            facets. None if fewer than two supportive facets passed
            the display gate.
        need_thwarting: Composite mean across the two thwarting facets.
            None if fewer than one thwarting facet passed.
        dominant_approach: Label per the dominant-approach table.
    """

    rater: Rater
    facets: dict[str, FacetScore]
    need_supportive: float | None
    need_thwarting: float | None
    dominant_approach: DominantApproach


@dataclass
class FacetGap:
    """Gap between coach self-rating and athlete aggregate on one facet.

    Attributes:
        facet: Name of the facet.
        coach_self_score: Coach's self-reported score for the facet.
        athlete_aggregate_score: Mean of the athlete ratings for the facet.
        gap: coach_self_score minus athlete_aggregate_score.
        flagged: True when the absolute gap exceeds GAP_FLAG_THRESHOLD.
        direction: "coach_higher", "athlete_higher", or "aligned".
    """

    facet: str
    coach_self_score: float
    athlete_aggregate_score: float
    gap: float
    flagged: bool
    direction: Literal["coach_higher", "athlete_higher", "aligned"]


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Circumplex item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Circumplex item {code} must be 1-7, got {value}")


def _normalize_to_10(raw_1_to_7: float) -> float:
    return ((raw_1_to_7 - 1.0) / 6.0) * 10.0


def _level_for_supportive_score(score: float) -> FacetLevel:
    if score >= 7.0:
        return "high"
    if score >= 4.5:
        return "moderate"
    return "low"


def _level_for_thwarting_score(score: float) -> FacetLevel:
    # For thwarting facets, "high" means a lot of pressure or chaos, a
    # negative outcome. The narrative layer consumes the level label, so
    # the naming still refers to score magnitude.
    if score >= 5.0:
        return "high"
    if score >= 3.0:
        return "moderate"
    return "low"


def _score_facet(
    responses: dict[str, int],
    facet_name: str,
    codes: tuple[str, ...],
) -> FacetScore:
    present = {c: responses[c] for c in codes if c in responses}
    answered = len(present)

    if answered < DISPLAY_MIN_ITEMS_PER_FACET:
        return FacetScore(
            score=None,
            items_answered=answered,
            level="not_computed",
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=(
                f"fewer than {DISPLAY_MIN_ITEMS_PER_FACET} items answered for facet {facet_name!r}"
            ),
        )

    for c, v in present.items():
        _validate_response(c, v)

    raw_mean = mean(present.values())
    score = _normalize_to_10(raw_mean)

    if facet_name in SUPPORTIVE_FACETS:
        level = _level_for_supportive_score(score)
    else:
        level = _level_for_thwarting_score(score)

    rec_passed = answered == len(codes)
    reason = (
        "recommendation gate passed"
        if rec_passed
        else f"{answered} of {len(codes)} items answered; full facet needed"
    )

    return FacetScore(
        score=score,
        items_answered=answered,
        level=level,
        display_gate_passed=True,
        recommendation_gate_passed=rec_passed,
        gate_reason=reason,
    )


def _classify_dominant_approach(
    supportive: float | None,
    thwarting: float | None,
) -> DominantApproach:
    if supportive is None or thwarting is None:
        return "not_computed"

    support_high = supportive >= COMPOSITE_SUPPORT_HIGH
    thwart_high = thwarting >= COMPOSITE_THWART_HIGH

    if support_high and not thwart_high:
        return "supportive"
    if support_high and thwart_high:
        return "mixed"
    if not support_high and not thwart_high:
        return "under-structured"
    return "thwarting"


def score_circumplex(
    responses: dict[str, int],
    rater: Rater,
) -> CircumplexProfile:
    """Score a single rater's view of a coach's circumplex profile.

    Reference: abc-assessment-spec Section 16.3

    Args:
        responses: Dict mapping item codes (CXA1-CXA5, CXS1-CXS5,
            CXR1-CXR5, CXC1-CXC5, CXH1-CXH4) to integer responses on
            the 1-7 scale. Items outside this set are ignored.
        rater: Who is rating: `coach_self` or `athlete_of_coach`.

    Returns:
        CircumplexProfile with per-facet scores, composites, and the
        dominant-approach label. Facets that fail the display gate
        have None scores and "not_computed" levels.
    """
    filtered = {c: responses[c] for c in ALL_ITEMS if c in responses}

    facets: dict[str, FacetScore] = {}
    for facet_name, codes in FACET_ITEMS.items():
        facets[facet_name] = _score_facet(filtered, facet_name, codes)

    supportive_scores = [facets[f].score for f in SUPPORTIVE_FACETS if facets[f].score is not None]
    thwarting_scores = [facets[f].score for f in THWARTING_FACETS if facets[f].score is not None]

    need_supportive = mean(supportive_scores) if len(supportive_scores) >= 2 else None
    need_thwarting = mean(thwarting_scores) if len(thwarting_scores) >= 1 else None

    dominant = _classify_dominant_approach(need_supportive, need_thwarting)

    return CircumplexProfile(
        rater=rater,
        facets=facets,
        need_supportive=need_supportive,
        need_thwarting=need_thwarting,
        dominant_approach=dominant,
    )


def aggregate_athlete_ratings(
    responses_by_athlete: list[dict[str, int]],
) -> CircumplexProfile | None:
    """Aggregate multiple athletes' circumplex ratings of one coach.

    Reference: abc-assessment-spec Section 16.3

    Each item's score is the mean across athletes who answered it. The
    aggregated responses are then scored through the usual pipeline so
    the resulting profile has the same structure as a single-rater one.

    Args:
        responses_by_athlete: List of per-athlete response dicts.

    Returns:
        A CircumplexProfile marked with rater=athlete_of_coach, or None
        when fewer than AGGREGATE_MIN_RATERS athletes provided any
        circumplex responses at all.
    """
    valid_respondents = [r for r in responses_by_athlete if any(code in r for code in ALL_ITEMS)]
    if len(valid_respondents) < AGGREGATE_MIN_RATERS:
        return None

    aggregated: dict[str, int] = {}
    for code in ALL_ITEMS:
        values = [r[code] for r in valid_respondents if code in r]
        if not values:  # pragma: no cover (defensive; valid_respondents filter above)
            continue
        # The scoring pipeline expects integers; round half to even.
        aggregated[code] = round(mean(values))

    return score_circumplex(aggregated, rater="athlete_of_coach")


def compute_gaps(
    coach_self: CircumplexProfile,
    athlete_aggregate: CircumplexProfile,
) -> list[FacetGap]:
    """Compute per-facet gaps between coach self-rating and athlete aggregate.

    Reference: abc-assessment-spec Section 16.3

    Only facets where both profiles passed the display gate produce
    gaps. The returned list is ordered by FACET_ITEMS insertion order.
    """
    if coach_self.rater != "coach_self":
        raise ValueError(
            f"coach_self profile must have rater='coach_self', got {coach_self.rater!r}"
        )
    if athlete_aggregate.rater != "athlete_of_coach":
        raise ValueError(
            f"athlete_aggregate profile must have rater='athlete_of_coach', "
            f"got {athlete_aggregate.rater!r}"
        )

    gaps: list[FacetGap] = []
    for facet_name in FACET_ITEMS:
        coach_facet = coach_self.facets[facet_name]
        athlete_facet = athlete_aggregate.facets[facet_name]
        if coach_facet.score is None or athlete_facet.score is None:
            continue

        gap_value = coach_facet.score - athlete_facet.score
        flagged = abs(gap_value) > GAP_FLAG_THRESHOLD
        if gap_value > GAP_FLAG_THRESHOLD:
            direction: Literal["coach_higher", "athlete_higher", "aligned"] = "coach_higher"
        elif gap_value < -GAP_FLAG_THRESHOLD:
            direction = "athlete_higher"
        else:
            direction = "aligned"

        gaps.append(
            FacetGap(
                facet=facet_name,
                coach_self_score=coach_facet.score,
                athlete_aggregate_score=athlete_facet.score,
                gap=gap_value,
                flagged=flagged,
                direction=direction,
            )
        )
    return gaps
