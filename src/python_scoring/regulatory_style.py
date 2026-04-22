"""Regulatory-style scoring for the ABC Assessment.

Computes per-domain autonomous and controlled regulation subscales from
six items (AR1/AR2 for Ambition, BR1/BR2 for Belonging, CR1/CR2 for
Craft), produces a Relative Autonomy Index per domain, classifies each
domain into one of four styles (identified, conflicted, introjected,
amotivated), and applies display and recommendation gates.

Reference: abc-assessment-spec Section 16.1
Reference: abc-assessment-spec Section 17.5 (evidence gates)
Reference: docs/regulatory-style-items-draft.md (item content and scoring model)

Research basis:
  Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits.
  Pelletier & Rocchi, Oxford Handbook of SDT, Chapter 3.

This module is additive to the core pipeline. It does not modify
satisfaction or frustration subscales, domain states, archetypes, the
Big Five weight matrix, or Belbin roles. It produces an interpretive
layer that conditions the narrative around those outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DOMAIN_ITEMS: dict[str, tuple[str, str]] = {
    "ambition": ("AR1", "AR2"),
    "belonging": ("BR1", "BR2"),
    "craft": ("CR1", "CR2"),
}

ALL_ITEMS: tuple[str, ...] = tuple(code for pair in DOMAIN_ITEMS.values() for code in pair)

STYLE_ELEVATED_THRESHOLD = 5.0
STYLE_AMBIGUOUS_MARGIN = 1.0

RegulatoryStyle = Literal[
    "identified",
    "conflicted",
    "introjected",
    "amotivated",
    "not_computed",
]

# Ordinal rank for erosion detection. Higher is more autonomous.
# amotivated sits below introjected because no regulation is a worse
# prognostic than controlled regulation, even though controlled
# regulation predicts burnout more strongly than amotivation predicts
# performance decline. The ordinal is over autonomy, not over pathology.
STYLE_RANK: dict[RegulatoryStyle, int] = {
    "identified": 3,
    "conflicted": 2,
    "introjected": 1,
    "amotivated": 0,
    "not_computed": -1,
}


@dataclass
class DomainRegulation:
    """Regulation result for a single domain.

    Attributes:
        autonomous_score: Identified/integrated regulation subscale on 0-10.
            None when the display gate fails (either item missing).
        controlled_score: Introjected/external regulation subscale on 0-10.
            None when the display gate fails.
        rai: Relative Autonomy Index, autonomous minus controlled. Range
            -10 to +10. None when gate fails.
        style: Classified dominant style for the domain.
        display_gate_passed: True if both items answered.
        recommendation_gate_passed: True if both scores are at least
            STYLE_AMBIGUOUS_MARGIN away from the elevated threshold.
        gate_reason: Human-readable reason when a gate fails.
    """

    autonomous_score: float | None
    controlled_score: float | None
    rai: float | None
    style: RegulatoryStyle
    display_gate_passed: bool
    recommendation_gate_passed: bool
    gate_reason: str


@dataclass
class RegulatoryProfile:
    """Regulation profile across all three domains.

    Attributes:
        domains: Dict mapping domain name (ambition/belonging/craft) to
            DomainRegulation. Always contains all three keys; suppressed
            domains have None scores and style "not_computed".
        items_answered: Total count of regulatory items with valid
            responses, across all domains.
    """

    domains: dict[str, DomainRegulation]
    items_answered: int


def _validate_response(code: str, value: int) -> None:
    if not isinstance(value, int):
        raise TypeError(f"Regulatory item {code} must be int, got {type(value).__name__}")
    if value < 1 or value > 7:
        raise ValueError(f"Regulatory item {code} must be 1-7, got {value}")


def _normalize_to_10(raw_1_to_7: float) -> float:
    return ((raw_1_to_7 - 1.0) / 6.0) * 10.0


def _classify_style(
    autonomous_score: float,
    controlled_score: float,
) -> RegulatoryStyle:
    """Map two subscale scores onto the four-way style classification.

    Reference: docs/regulatory-style-items-draft.md Section 4.
    """
    autonomous_elevated = autonomous_score >= STYLE_ELEVATED_THRESHOLD
    controlled_elevated = controlled_score >= STYLE_ELEVATED_THRESHOLD

    if autonomous_elevated and not controlled_elevated:
        return "identified"
    if autonomous_elevated and controlled_elevated:
        return "conflicted"
    if not autonomous_elevated and controlled_elevated:
        return "introjected"
    return "amotivated"


def _score_domain(
    responses: dict[str, int],
    auto_code: str,
    ctrl_code: str,
) -> DomainRegulation:
    auto_present = auto_code in responses
    ctrl_present = ctrl_code in responses

    if not (auto_present and ctrl_present):
        missing = [
            code
            for code, present in [(auto_code, auto_present), (ctrl_code, ctrl_present)]
            if not present
        ]
        return DomainRegulation(
            autonomous_score=None,
            controlled_score=None,
            rai=None,
            style="not_computed",
            display_gate_passed=False,
            recommendation_gate_passed=False,
            gate_reason=f"missing item(s): {', '.join(missing)}",
        )

    _validate_response(auto_code, responses[auto_code])
    _validate_response(ctrl_code, responses[ctrl_code])

    autonomous_score = _normalize_to_10(responses[auto_code])
    controlled_score = _normalize_to_10(responses[ctrl_code])
    rai = autonomous_score - controlled_score
    style = _classify_style(autonomous_score, controlled_score)

    # Recommendation gate: both scores at least one ambiguous-margin away
    # from the elevated threshold, so the classification is not a boundary
    # call. A score of exactly 5.0 is ambiguous; a score of 5.1 is too
    # close to 5.0 to confidently say "elevated"; a score of 6.0 is clear.
    auto_clear = abs(autonomous_score - STYLE_ELEVATED_THRESHOLD) >= STYLE_AMBIGUOUS_MARGIN
    ctrl_clear = abs(controlled_score - STYLE_ELEVATED_THRESHOLD) >= STYLE_AMBIGUOUS_MARGIN

    if auto_clear and ctrl_clear:
        rec_passed = True
        reason = "recommendation gate passed"
    else:
        rec_passed = False
        reason = "one or both scores too close to the style boundary"

    return DomainRegulation(
        autonomous_score=autonomous_score,
        controlled_score=controlled_score,
        rai=rai,
        style=style,
        display_gate_passed=True,
        recommendation_gate_passed=rec_passed,
        gate_reason=reason,
    )


def score_regulatory_style(responses: dict[str, int]) -> RegulatoryProfile:
    """Compute a per-domain regulation profile.

    Reference: abc-assessment-spec Section 16.1

    Args:
        responses: Dict mapping regulatory item codes (AR1, AR2, BR1, BR2,
            CR1, CR2) to integer responses on the 1-7 scale. Items
            outside this set are ignored. Missing items cause the
            affected domain to fail the display gate.

    Returns:
        RegulatoryProfile containing per-domain DomainRegulation entries
        for ambition, belonging, and craft.
    """
    filtered = {code: responses[code] for code in ALL_ITEMS if code in responses}

    domains: dict[str, DomainRegulation] = {}
    for domain_name, (auto_code, ctrl_code) in DOMAIN_ITEMS.items():
        domains[domain_name] = _score_domain(filtered, auto_code, ctrl_code)

    return RegulatoryProfile(
        domains=domains,
        items_answered=len(filtered),
    )
