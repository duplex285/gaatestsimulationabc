"""Group-conscious scoring for the ABC Assessment.

Operationalizes the group-conscious stance from Chapter 53 of the Oxford
Handbook of SDT: need satisfaction exists at the group level, not only
the individual level, and the athlete's perception of collective need
satisfaction produces its own signal beyond personal scores.

Reference: abc-assessment-spec Section 16.5
Reference: abc-assessment-spec Section 17.5 (gates)
Reference: docs/group-conscious-items-draft.md

Research basis:
  Thomaes, S., et al. (2023). A Group-Conscious Approach to Basic
    Psychological Needs Theory. In Ryan & Deci (Eds.), Oxford
    Handbook of SDT, Chapter 53.
  Kachanoff, F. J., et al. (2020). Collective autonomy: Why and when
    collective agency motivates people.

Two surfaces:
  1. Individual-level: per-domain perceived collective satisfaction,
     team identification, and an empathic-risk flag per domain when
     high identification meets low perceived collective satisfaction.
  2. Team-level dispersion: standard deviation of subscale scores
     across a team's athletes. High dispersion is a risk factor in
     itself, independent of the team mean.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, stdev
from typing import Literal

COLLECTIVE_ITEM_BY_DOMAIN: dict[str, str] = {
    "ambition": "AG1",
    "belonging": "BG1",
    "craft": "CG1",
}
TI_ITEMS: tuple[str, ...] = ("TI1", "TI2")

ALL_ITEMS: tuple[str, ...] = tuple(list(COLLECTIVE_ITEM_BY_DOMAIN.values()) + list(TI_ITEMS))

LEVEL_HIGH_THRESHOLD = 7.0
LEVEL_MODERATE_THRESHOLD = 4.0

EMPATHIC_RISK_TI_MIN = 6.0
EMPATHIC_RISK_COLLECTIVE_MAX = 4.0

DISPERSION_TIGHT = 1.5
DISPERSION_HIGH = 2.5
DISPERSION_MIN_ATHLETES = 3

Level = Literal["high", "moderate", "low", "not_computed"]
DispersionBand = Literal["tight", "moderate", "high"]

CORE_SUBSCALE_KEYS: tuple[str, ...] = (
    "a_sat",
    "a_frust",
    "b_sat",
    "b_frust",
    "c_sat",
    "c_frust",
)


@dataclass
class CollectiveSatisfaction:
    """Perceived collective satisfaction on one domain."""

    domain: str
    score: float | None
    level: Level
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


@dataclass
class TeamIdentification:
    """Team identification subscale."""

    score: float | None
    level: Level
    items_answered: int
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


@dataclass
class GroupConsciousProfile:
    """Full group-conscious profile for one athlete.

    Attributes:
        collective: Per-domain CollectiveSatisfaction.
        team_identification: TeamIdentification subscale.
        empathic_risk_domains: Domains where high team identification
            meets low perceived collective satisfaction.
        items_answered: Total count of valid group-conscious responses.
    """

    collective: dict[str, CollectiveSatisfaction]
    team_identification: TeamIdentification
    empathic_risk_domains: list[str]
    items_answered: int


@dataclass
class TeamDispersion:
    """Dispersion of subscale scores across a team's athletes.

    Attributes:
        team_size: Number of athletes contributing to the dispersion.
        subscale_sds: Per-subscale standard deviation on the 0-10 scale.
            Empty dict when team_size is below the minimum.
        subscale_bands: Per-subscale band label.
        high_dispersion_subscales: Subscales whose SD exceeds DISPERSION_HIGH.
        computed: True when team_size met the minimum; False otherwise.
        reason: Human-readable reason when dispersion was not computed.
    """

    team_size: int
    subscale_sds: dict[str, float]
    subscale_bands: dict[str, DispersionBand]
    high_dispersion_subscales: list[str]
    computed: bool
    reason: str


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Group-conscious item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Group-conscious item {code} must be 1-7, got {value}")


def _normalize_to_10(raw_1_to_7: float) -> float:
    return ((raw_1_to_7 - 1.0) / 6.0) * 10.0


def _level_for_score(score: float) -> Level:
    if score >= LEVEL_HIGH_THRESHOLD:
        return "high"
    if score >= LEVEL_MODERATE_THRESHOLD:
        return "moderate"
    return "low"


def _dispersion_band(sd: float) -> DispersionBand:
    if sd < DISPERSION_TIGHT:
        return "tight"
    if sd < DISPERSION_HIGH:
        return "moderate"
    return "high"


def _score_collective(
    responses: dict[str, int],
    domain: str,
    code: str,
) -> CollectiveSatisfaction:
    if code not in responses:
        return CollectiveSatisfaction(
            domain=domain,
            score=None,
            level="not_computed",
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=f"missing item {code}",
        )
    _validate_response(code, responses[code])
    score = _normalize_to_10(responses[code])
    return CollectiveSatisfaction(
        domain=domain,
        score=score,
        level=_level_for_score(score),
        display_gate_passed=True,
        recommendation_gate_passed=True,
        gate_reason="ok",
    )


def _score_team_identification(responses: dict[str, int]) -> TeamIdentification:
    present = {c: responses[c] for c in TI_ITEMS if c in responses}
    for c, v in present.items():
        _validate_response(c, v)
    answered = len(present)

    if answered == 0:
        return TeamIdentification(
            score=None,
            level="not_computed",
            items_answered=0,
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason="no team identification items answered",
        )

    raw_mean = mean(present.values())
    score = _normalize_to_10(raw_mean)
    level = _level_for_score(score)

    rec_passed = answered == len(TI_ITEMS)
    reason = (
        "recommendation gate passed"
        if rec_passed
        else "only one of two team-identification items answered"
    )

    return TeamIdentification(
        score=score,
        level=level,
        items_answered=answered,
        display_gate_passed=True,
        recommendation_gate_passed=rec_passed,
        gate_reason=reason,
    )


def score_group_conscious(responses: dict[str, int]) -> GroupConsciousProfile:
    """Score an athlete's group-conscious profile.

    Reference: abc-assessment-spec Section 16.5

    Args:
        responses: Dict mapping item codes (AG1, BG1, CG1, TI1, TI2) to
            integer responses on the 1-7 scale. Items outside this set
            are ignored.

    Returns:
        GroupConsciousProfile with per-domain collective satisfaction,
        team identification, and empathic-risk flags.
    """
    filtered = {c: responses[c] for c in ALL_ITEMS if c in responses}

    collective = {
        domain: _score_collective(filtered, domain, code)
        for domain, code in COLLECTIVE_ITEM_BY_DOMAIN.items()
    }

    team_identification = _score_team_identification(filtered)

    empathic_risk: list[str] = []
    ti_score = team_identification.score
    if ti_score is not None and ti_score >= EMPATHIC_RISK_TI_MIN:
        for domain, cs in collective.items():
            if cs.score is not None and cs.score < EMPATHIC_RISK_COLLECTIVE_MAX:
                empathic_risk.append(domain)

    return GroupConsciousProfile(
        collective=collective,
        team_identification=team_identification,
        empathic_risk_domains=empathic_risk,
        items_answered=len(filtered),
    )


def compute_team_dispersion(
    athlete_subscales: list[dict[str, float]],
) -> TeamDispersion:
    """Compute per-subscale standard deviation across a team's athletes.

    Reference: abc-assessment-spec Section 16.5

    Args:
        athlete_subscales: List of subscale dicts, one per athlete, each
            with keys a_sat, a_frust, b_sat, b_frust, c_sat, c_frust on
            the 0-10 scale.

    Returns:
        TeamDispersion with per-subscale SDs, bands, and high-dispersion
        flags. When the team has fewer than DISPERSION_MIN_ATHLETES, the
        computed flag is False and the reason explains why.
    """
    team_size = len(athlete_subscales)

    if team_size < DISPERSION_MIN_ATHLETES:
        return TeamDispersion(
            team_size=team_size,
            subscale_sds={},
            subscale_bands={},
            high_dispersion_subscales=[],
            computed=False,
            reason=(f"fewer than {DISPERSION_MIN_ATHLETES} athletes; dispersion not computed"),
        )

    sds: dict[str, float] = {}
    bands: dict[str, DispersionBand] = {}
    high: list[str] = []

    for key in CORE_SUBSCALE_KEYS:
        values = [a[key] for a in athlete_subscales if key in a]
        if len(values) < DISPERSION_MIN_ATHLETES:
            continue
        sd = stdev(values)
        sds[key] = sd
        band = _dispersion_band(sd)
        bands[key] = band
        if band == "high":
            high.append(key)

    return TeamDispersion(
        team_size=team_size,
        subscale_sds=sds,
        subscale_bands=bands,
        high_dispersion_subscales=high,
        computed=True,
        reason="dispersion computed",
    )
