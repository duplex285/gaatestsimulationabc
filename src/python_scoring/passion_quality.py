"""Passion quality scoring for the ABC Assessment.

Computes harmonious and obsessive passion subscales from six items, produces
a signed balance score, and applies evidence gates that determine whether
the construct is suppressed, displayed with hedged language, or allowed to
drive coach-facing recommendations.

Reference: abc-assessment-spec Section 16.2
Reference: abc-assessment-spec Section 17.5 (evidence gates)
Reference: docs/passion-items-draft.md (item content and scoring model)

Research basis:
  Vallerand, R. J. (2015). The Psychology of Passion. OUP.
  Vallerand & Paquette, Oxford Handbook of SDT, Chapter 19.

The two subscales are independent by construction. A person can score high
on both (intense and conflicted), high on one only, or low on both
(uninvested). Scoring does not collapse this into a single bipolar dimension.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HARMONIOUS_ITEMS = ("HP1", "HP2", "HP3")
OBSESSIVE_ITEMS = ("OP1", "OP2", "OP3")
ALL_ITEMS = HARMONIOUS_ITEMS + OBSESSIVE_ITEMS

MIN_ITEMS_FOR_DISPLAY = 4
MIN_ITEMS_FOR_RECOMMENDATION = 6

BALANCE_LEANING_THRESHOLD = 2.0
BALANCE_AMBIGUOUS_THRESHOLD = 1.0
SUBSCALE_ELEVATED_THRESHOLD = 5.0

PassionLeaning = Literal[
    "harmonious",
    "obsessive",
    "mixed",
    "uninvested",
    "insufficient_signal",
    "not_computed",
]


@dataclass
class PassionQualityResult:
    """Structured output of passion-quality scoring.

    Attributes:
        hp_score: Harmonious passion subscale on 0-10 (None if gate failed).
        op_score: Obsessive passion subscale on 0-10 (None if gate failed).
        balance: Signed score hp_score minus op_score (None if gate failed).
        leaning: One of harmonious, obsessive, mixed, uninvested,
            insufficient_signal, or not_computed.
        items_answered: Count of passion items with valid responses.
        display_gate_passed: True if the construct may be shown to users.
        recommendation_gate_passed: True if the construct may drive alerts.
        gate_reason: Human-readable reason when a gate fails.
    """

    hp_score: float | None
    op_score: float | None
    balance: float | None
    leaning: PassionLeaning
    items_answered: int
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Passion item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Passion item {code} must be 1-7, got {value}")


def _subscale_mean(responses: dict[str, int], items: tuple[str, ...]) -> float | None:
    """Mean of present items in a subscale on the 1-7 scale.

    Returns None only if the subscale has zero items. Under the current
    item bank (3 items per subscale, 4-item display gate) this branch is
    defensive and not reached; any 4-of-6 subset spans both subscales.
    Kept so the function stays safe if the bank expands or the gate
    loosens in the future.
    """
    present = [responses[code] for code in items if code in responses]
    if not present:  # pragma: no cover
        return None
    return sum(present) / len(present)


def _normalize_to_10(mean_1_to_7: float) -> float:
    """Map a 1-7 mean onto the 0-10 subscale scale used across ABC."""
    return ((mean_1_to_7 - 1.0) / 6.0) * 10.0


def _classify_leaning(
    hp_score: float,
    op_score: float,
    balance: float,
) -> PassionLeaning:
    """Map scores and balance to a leaning label.

    Reference: docs/passion-items-draft.md Section 4.
    """
    hp_elevated = hp_score >= SUBSCALE_ELEVATED_THRESHOLD
    op_elevated = op_score >= SUBSCALE_ELEVATED_THRESHOLD

    if hp_elevated and op_elevated:
        return "mixed"
    if not hp_elevated and not op_elevated:
        return "uninvested"
    if balance >= BALANCE_LEANING_THRESHOLD and hp_elevated:
        return "harmonious"
    if balance <= -BALANCE_LEANING_THRESHOLD and op_elevated:
        return "obsessive"
    return "insufficient_signal"


def score_passion_quality(responses: dict[str, int]) -> PassionQualityResult:
    """Compute passion-quality subscales, balance, leaning, and gate state.

    Reference: abc-assessment-spec Section 16.2
    Reference: abc-assessment-spec Section 17.5

    Args:
        responses: Dict mapping passion item codes (HP1-HP3, OP1-OP3) to
            integer responses on the 1-7 scale. Items outside this set are
            ignored. Missing items are allowed up to the gate thresholds.

    Returns:
        PassionQualityResult with scores, leaning, and gate state. If the
        display gate fails, scores are None and leaning is "not_computed".
    """
    filtered = {code: responses[code] for code in ALL_ITEMS if code in responses}
    for code, value in filtered.items():
        _validate_response(code, value)

    items_answered = len(filtered)

    if items_answered < MIN_ITEMS_FOR_DISPLAY:
        return PassionQualityResult(
            hp_score=None,
            op_score=None,
            balance=None,
            leaning="not_computed",
            items_answered=items_answered,
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=(f"fewer than {MIN_ITEMS_FOR_DISPLAY} of 6 passion items answered"),
        )

    hp_mean = _subscale_mean(filtered, HARMONIOUS_ITEMS)
    op_mean = _subscale_mean(filtered, OBSESSIVE_ITEMS)

    # Defensive: under the current 3-items-per-subscale bank plus the
    # 4-item display gate, both means are always present here. Kept so
    # an expanded bank or relaxed gate does not silently crash.
    if hp_mean is None or op_mean is None:  # pragma: no cover
        return PassionQualityResult(
            hp_score=None,
            op_score=None,
            balance=None,
            leaning="not_computed",
            items_answered=items_answered,
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason="one subscale has no answered items",
        )

    hp_score = _normalize_to_10(hp_mean)
    op_score = _normalize_to_10(op_mean)
    balance = hp_score - op_score

    leaning = _classify_leaning(hp_score, op_score, balance)

    all_items_answered = items_answered == MIN_ITEMS_FOR_RECOMMENDATION
    # Rec gate passes when the leaning is classified cleanly. Harmonious
    # and obsessive are directional. Mixed and uninvested are non-
    # directional but still drive specific prose and coach actions, so
    # they pass. Insufficient_signal is the ambiguous case where the
    # leaning could swing either way with one more measurement.
    decisive_leaning = leaning in ("harmonious", "obsessive", "mixed", "uninvested")

    if all_items_answered and decisive_leaning:
        recommendation_passed = True
        gate_reason = "recommendation gate passed"
    elif all_items_answered and abs(balance) < BALANCE_AMBIGUOUS_THRESHOLD:
        recommendation_passed = False
        gate_reason = "pattern still forming; balance close to zero"
    elif not all_items_answered:
        recommendation_passed = False
        gate_reason = f"{items_answered} of 6 items answered; recommendation gate requires all six"
    else:
        recommendation_passed = False
        gate_reason = "leaning not strong enough to drive recommendation"

    return PassionQualityResult(
        hp_score=hp_score,
        op_score=op_score,
        balance=balance,
        leaning=leaning,
        items_answered=items_answered,
        display_gate_passed=True,
        recommendation_gate_passed=recommendation_passed,
        gate_reason=gate_reason,
    )
