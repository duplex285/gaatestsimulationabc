"""Regulation erosion detector.

A leading indicator of burnout that the satisfaction/frustration cascade
cannot see on its own. An athlete whose regulatory quality moves down
the autonomy ranking over consecutive measurements is at risk even when
their subscale scores remain in the healthy range.

Reference: abc-assessment-spec Section 16.1
Reference: Lonsdale & Hodge (2011), temporal ordering of self-determination
  decline and burnout.

Design:
- Consumes two or more RegulatoryProfile snapshots in chronological order.
- Checks each domain independently for a sustained decrease in ordinal
  style rank.
- "Sustained" means the rank at measurement t is strictly lower than at
  t-1, and at t is no higher than at t-2 (no recovery). A single-cycle
  drop with recovery does not fire.
- Returns one EroisonEvent per domain that shows the pattern; empty list
  when nothing fires.

Integration with TransitionTracker is deferred to a follow-up pass. This
module is standalone-testable and callable from whatever scheduler owns
the regulatory item stream.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.python_scoring.regulatory_style import (
    STYLE_RANK,
    RegulatoryProfile,
    RegulatoryStyle,
)

DOMAIN_NAMES: tuple[str, ...] = ("ambition", "belonging", "craft")


@dataclass
class ErosionEvent:
    """Regulatory erosion on a single domain.

    Attributes:
        domain: One of ambition, belonging, or craft.
        style_series: The full style history for this domain, oldest
            first. Length equals the number of profiles passed in.
        rank_series: Ordinal ranks corresponding to style_series.
        lookback: Number of measurements considered in the erosion
            decision. Equals the length of style_series actually used
            by the detector (currently 3 or 2 depending on history).
    """

    domain: str
    style_series: list[RegulatoryStyle]
    rank_series: list[int]
    lookback: int


def _rank(style: RegulatoryStyle) -> int:
    return STYLE_RANK[style]


def _domain_series(profiles: list[RegulatoryProfile], domain: str) -> list[RegulatoryStyle]:
    """Extract a domain's style across an ordered profile list."""
    return [p.domains[domain].style for p in profiles]


def _erosion_on_domain(styles: list[RegulatoryStyle]) -> bool:
    """Apply the sustained-decrease rule to one domain's style history.

    Rules:
    - Need at least two computable measurements (not_computed are skipped).
    - With two: the latest rank must be strictly lower than the prior rank.
    - With three or more: monotonic non-increase across the most recent
      three AND a net drop from oldest to newest in that window:
        ranks[-1] <= ranks[-2] <= ranks[-3]  AND  ranks[-1] < ranks[-3]

    The non-increase clause rejects recovery sequences like
    (introjected, conflicted, identified). The net-drop clause catches
    sustained-low-after-drop sequences like (identified, introjected,
    introjected) that a simple latest-vs-prior rule misses.
    """
    computable = [s for s in styles if s != "not_computed"]
    if len(computable) < 2:
        return False

    recent = computable[-3:] if len(computable) >= 3 else computable[-2:]
    ranks = [_rank(s) for s in recent]

    if len(ranks) == 2:
        return ranks[-1] < ranks[-2]

    # len == 3
    monotonic_non_increase = ranks[-1] <= ranks[-2] <= ranks[-3]
    net_drop = ranks[-1] < ranks[-3]
    return monotonic_non_increase and net_drop


def detect_regulation_erosion(
    profiles: list[RegulatoryProfile],
) -> list[ErosionEvent]:
    """Return erosion events for each affected domain.

    Reference: abc-assessment-spec Section 16.1

    Args:
        profiles: Chronologically ordered list of regulatory profiles,
            oldest first. At least two profiles are required for the
            detector to return anything; a single-profile list always
            returns an empty event list.

    Returns:
        List of ErosionEvent, one per domain showing sustained erosion.
        Empty when no domain meets the rule.
    """
    if len(profiles) < 2:
        return []

    events: list[ErosionEvent] = []
    for domain in DOMAIN_NAMES:
        styles = _domain_series(profiles, domain)
        computable = [s for s in styles if s != "not_computed"]
        if not _erosion_on_domain(styles):
            continue
        recent = computable[-3:] if len(computable) >= 3 else computable[-2:]
        events.append(
            ErosionEvent(
                domain=domain,
                style_series=styles,
                rank_series=[_rank(s) for s in styles],
                lookback=len(recent),
            )
        )
    return events
