"""Self-Concordance scoring for the ABC Assessment.

Scores 4 items along the Perceived Locus of Causality continuum
(external, introjected, identified, intrinsic), produces autonomous
and controlled composites, a signed self-concordance score, and a
three-band classification.

Reference: abc-assessment-spec Section 16.7
Reference: abc-assessment-spec Section 17.5 (gates)
Reference: docs/self-concordance-items-draft.md

Research basis:
  Ryan, R. M., & Connell, J. P. (1989). Perceived Locus of Causality.
  Sheldon, K. M., & Houser-Marko, L. (2001). Self-concordance, goal
    attainment, and the pursuit of happiness.
  Sheldon & Goffredi, Oxford Handbook of SDT, Chapter 17.

The athlete states a current primary goal at the top of the screen; the
goal text is metadata stored alongside the score, not part of the
scoring logic. This module operates purely on the four PLOC ratings.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Literal

CONTROLLED_ITEMS: tuple[str, ...] = ("SC1", "SC2")
AUTONOMOUS_ITEMS: tuple[str, ...] = ("SC3", "SC4")
ALL_ITEMS: tuple[str, ...] = CONTROLLED_ITEMS + AUTONOMOUS_ITEMS

LEANING_THRESHOLD = 3.0
ELEVATED_THRESHOLD = 5.0
DISPLAY_MIN_TOTAL = 3

Concordance = Literal["autonomous", "controlled", "mixed", "not_computed"]


@dataclass
class SelfConcordanceProfile:
    """Output of the self-concordance scoring module.

    Attributes:
        autonomous_score: Mean of SC3 and SC4 on 0-10 (or None).
        controlled_score: Mean of SC1 and SC2 on 0-10 (or None).
        self_concordance: Signed score, autonomous minus controlled,
            range -10 to +10. None when display gate fails.
        leaning: Three-band classification or not_computed.
        items_answered: Count of valid responses.
        display_gate_passed: True if at least 3 items answered and
            both subscales have at least one answered item.
        recommendation_gate_passed: True if all 4 items answered and
            leaning is autonomous or controlled (not mixed).
        gate_reason: Human-readable reason.
        goal_text: Optional goal text supplied by the caller, stored
            alongside the score for product display. Not used in scoring.
    """

    autonomous_score: float | None
    controlled_score: float | None
    self_concordance: float | None
    leaning: Concordance
    items_answered: int
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str
    goal_text: str | None


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Self-concordance item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Self-concordance item {code} must be 1-7, got {value}")


def _normalize_to_10(raw_1_to_7: float) -> float:
    return ((raw_1_to_7 - 1.0) / 6.0) * 10.0


def _subscale_mean(
    responses: dict[str, int],
    items: tuple[str, ...],
) -> tuple[float | None, int]:
    present = [responses[c] for c in items if c in responses]
    if not present:
        return None, 0
    return _normalize_to_10(mean(present)), len(present)


def _classify(
    autonomous: float,
    controlled: float,
    self_concordance: float,
) -> Concordance:
    """Apply the three-band rule.

    Reference: docs/self-concordance-items-draft.md Section 4.
    """
    if self_concordance >= LEANING_THRESHOLD and autonomous >= ELEVATED_THRESHOLD:
        return "autonomous"
    if self_concordance <= -LEANING_THRESHOLD and controlled >= ELEVATED_THRESHOLD:
        return "controlled"
    return "mixed"


def score_self_concordance(
    responses: dict[str, int],
    goal_text: str | None = None,
) -> SelfConcordanceProfile:
    """Score a self-concordance profile.

    Reference: abc-assessment-spec Section 16.7

    Args:
        responses: Dict mapping item codes (SC1-SC4) to integer responses
            on the 1-7 scale. Items outside this set are ignored.
        goal_text: Optional free-text goal the athlete is rating. Stored
            alongside the score for product display. Not used in scoring.

    Returns:
        SelfConcordanceProfile with autonomous/controlled scores, signed
        self-concordance, three-band classification, and gate state.
    """
    filtered = {c: responses[c] for c in ALL_ITEMS if c in responses}
    for c, v in filtered.items():
        _validate_response(c, v)

    items_answered = len(filtered)

    autonomous_score, autonomous_n = _subscale_mean(filtered, AUTONOMOUS_ITEMS)
    controlled_score, controlled_n = _subscale_mean(filtered, CONTROLLED_ITEMS)

    display_passed = items_answered >= DISPLAY_MIN_TOTAL and autonomous_n >= 1 and controlled_n >= 1

    if not display_passed:
        return SelfConcordanceProfile(
            autonomous_score=None,
            controlled_score=None,
            self_concordance=None,
            leaning="not_computed",
            items_answered=items_answered,
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=(
                f"need at least {DISPLAY_MIN_TOTAL} items with both "
                "subscales represented; got "
                f"{items_answered} total, autonomous={autonomous_n}, "
                f"controlled={controlled_n}"
            ),
            goal_text=goal_text,
        )

    assert autonomous_score is not None
    assert controlled_score is not None

    sc = autonomous_score - controlled_score
    leaning = _classify(autonomous_score, controlled_score, sc)

    all_answered = items_answered == len(ALL_ITEMS)
    clear_leaning = leaning in ("autonomous", "controlled")

    if all_answered and clear_leaning:
        rec_passed = True
        reason = "recommendation gate passed"
    elif not all_answered:
        rec_passed = False
        reason = f"{items_answered} of 4 items answered; recommendation gate requires all four"
    else:
        rec_passed = False
        reason = "all items answered but no clear autonomous or controlled lean"

    return SelfConcordanceProfile(
        autonomous_score=autonomous_score,
        controlled_score=controlled_score,
        self_concordance=sc,
        leaning=leaning,
        items_answered=items_answered,
        display_gate_passed=True,
        recommendation_gate_passed=rec_passed,
        gate_reason=reason,
        goal_text=goal_text,
    )
