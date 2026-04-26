"""Causality Orientations scoring for the ABC Assessment.

Scores 12 items across three orientation subscales (autonomy, controlled,
impersonal), produces a dominant-orientation classification using a top-
vs-second margin rule, and applies two-tier evidence gates.

Reference: abc-assessment-spec Section 16.6
Reference: abc-assessment-spec Section 17.5 (gates)
Reference: docs/causality-orientations-items-draft.md

Research basis:
  Deci, E. L., & Ryan, R. M. (1985). The General Causality Orientations
    Scale: Self-determination in personality.
  Koestner, R., Oxford Handbook of SDT, Chapter 5.

Causality orientations are relatively stable individual-difference traits,
administered at onboarding and annually thereafter. They are not a
biweekly measurement. The trait layer here produces:

- Three subscale scores on 0-10.
- A dominant-orientation label or "mixed" or "emergent".
- An evidence gate state consistent with the rest of the system.

Stratification of other signals by orientation is explicitly deferred
to Phase A calibration. This module produces the orientation itself;
downstream consumers decide whether and how to use it.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Literal

SUBSCALE_ITEMS: dict[str, tuple[str, ...]] = {
    "autonomy": ("AO1", "AO2", "AO3", "AO4"),
    "controlled": ("CO1", "CO2", "CO3", "CO4"),
    "impersonal": ("IO1", "IO2", "IO3", "IO4"),
}

ALL_ITEMS: tuple[str, ...] = tuple(code for codes in SUBSCALE_ITEMS.values() for code in codes)

TOTAL_ITEM_COUNT = len(ALL_ITEMS)  # 12
DISPLAY_MIN_TOTAL = 8
DISPLAY_MIN_PER_SUBSCALE = 2

DOMINANT_SCORE_THRESHOLD = 6.0
DOMINANT_MARGIN = 1.5
MIXED_FLOOR = 4.0
EMERGENT_CEILING = 4.0

Orientation = Literal["autonomy", "controlled", "impersonal", "mixed", "emergent", "not_computed"]


@dataclass
class CausalityProfile:
    """Output of the causality-orientations scoring module.

    Attributes:
        autonomy_score: 0-10 autonomy orientation subscale (or None).
        controlled_score: 0-10 controlled orientation subscale (or None).
        impersonal_score: 0-10 impersonal orientation subscale (or None).
        dominant: Classified orientation or descriptor (mixed / emergent /
            not_computed).
        items_answered: Count of valid responses across all subscales.
        display_gate_passed: True if the profile may be shown to users.
        recommendation_gate_passed: True if the profile may drive signal
            stratification or recommendations (all 12 answered and a
            clear dominant orientation).
        gate_reason: Human-readable reason string.
    """

    autonomy_score: float | None
    controlled_score: float | None
    impersonal_score: float | None
    dominant: Orientation
    items_answered: int
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Causality item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Causality item {code} must be 1-7, got {value}")


def _normalize_to_10(raw_1_to_7: float) -> float:
    return ((raw_1_to_7 - 1.0) / 6.0) * 10.0


def _subscale_score(
    responses: dict[str, int],
    codes: tuple[str, ...],
) -> tuple[float | None, int]:
    """Return (score or None, count answered)."""
    present = [responses[c] for c in codes if c in responses]
    if not present:
        return None, 0
    raw = mean(present)
    return _normalize_to_10(raw), len(present)


def _classify_dominant(
    autonomy: float,
    controlled: float,
    impersonal: float,
) -> Orientation:
    """Apply the margin rule to three subscale scores."""
    scored: list[tuple[str, float]] = [
        ("autonomy", autonomy),
        ("controlled", controlled),
        ("impersonal", impersonal),
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    top_name, top_score = scored[0]
    second_score = scored[1][1]

    # All three below the emergent ceiling -> no clear trait yet.
    if top_score < EMERGENT_CEILING:
        return "emergent"

    margin = top_score - second_score
    if top_score >= DOMINANT_SCORE_THRESHOLD and margin >= DOMINANT_MARGIN:
        assert top_name in ("autonomy", "controlled", "impersonal")
        return top_name  # type: ignore[return-value]

    # Top score is at least the emergent floor but not a clear winner.
    return "mixed"


def score_causality_orientations(responses: dict[str, int]) -> CausalityProfile:
    """Score a causality-orientations profile.

    Reference: abc-assessment-spec Section 16.6

    Args:
        responses: Dict mapping item codes (AO1-AO4, CO1-CO4, IO1-IO4)
            to integer responses on the 1-7 scale. Items outside this
            set are ignored.

    Returns:
        CausalityProfile with per-orientation scores, dominant label,
        and evidence-gate state.
    """
    filtered = {c: responses[c] for c in ALL_ITEMS if c in responses}
    for c, v in filtered.items():
        _validate_response(c, v)

    total_answered = len(filtered)

    autonomy_score, autonomy_n = _subscale_score(filtered, SUBSCALE_ITEMS["autonomy"])
    controlled_score, controlled_n = _subscale_score(filtered, SUBSCALE_ITEMS["controlled"])
    impersonal_score, impersonal_n = _subscale_score(filtered, SUBSCALE_ITEMS["impersonal"])

    per_sub_min = min(autonomy_n, controlled_n, impersonal_n)
    display_passed = total_answered >= DISPLAY_MIN_TOTAL and per_sub_min >= DISPLAY_MIN_PER_SUBSCALE

    if not display_passed:
        return CausalityProfile(
            autonomy_score=None,
            controlled_score=None,
            impersonal_score=None,
            dominant="not_computed",
            items_answered=total_answered,
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=(
                f"need at least {DISPLAY_MIN_TOTAL} items total and "
                f"{DISPLAY_MIN_PER_SUBSCALE} per subscale; got "
                f"{total_answered} total and min-per-subscale {per_sub_min}"
            ),
        )

    # With display gate passed, scores are all non-None.
    assert autonomy_score is not None
    assert controlled_score is not None
    assert impersonal_score is not None

    dominant = _classify_dominant(autonomy_score, controlled_score, impersonal_score)

    all_answered = total_answered == TOTAL_ITEM_COUNT
    clear_dominant = dominant in ("autonomy", "controlled", "impersonal")

    if all_answered and clear_dominant:
        rec_passed = True
        reason = "recommendation gate passed"
    elif not all_answered:
        rec_passed = False
        reason = (
            f"{total_answered} of {TOTAL_ITEM_COUNT} items answered; "
            "recommendation gate requires all twelve"
        )
    else:
        rec_passed = False
        reason = "all items answered but no single orientation clearly dominant"

    return CausalityProfile(
        autonomy_score=autonomy_score,
        controlled_score=controlled_score,
        impersonal_score=impersonal_score,
        dominant=dominant,
        items_answered=total_answered,
        display_gate_passed=True,
        recommendation_gate_passed=rec_passed,
        gate_reason=reason,
    )
