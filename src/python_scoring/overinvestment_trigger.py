"""Overinvestment trigger with passion-aware routing.

Detects the pattern where an athlete appears to be thriving on ABC
subscales but daily recovery signals are declining. When the pattern
fires, the passion-quality leaning determines the narrative frame and
the coach recommendation.

Reference: abc-assessment-spec Section 16.2
Reference: abc-assessment-spec.md Section 2.2 (original overinvestment rule)

The original rule used only subscale scores and daily cross-signals
(recovery_slope, cognitive_load). This module preserves those inputs as
optional and adds passion quality as the routing layer: a harmonious-
leaning athlete with declining recovery is in a different situation than
an obsessive-leaning athlete with the same signal, and the coach action
differs accordingly.

Daily cross-signals live in the second-game repo, not in this simulation
repo. When they are absent, the trigger uses the ABC-only detection path
and the caller integrates cross-signal gating upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.python_scoring.passion_quality import PassionQualityResult

SAT_THRIVING_THRESHOLD = 7.0
FRUST_LOW_THRESHOLD = 3.0

RECOVERY_DECLINING_THRESHOLD = 40.0
COGNITIVE_LOAD_HIGH_THRESHOLD = 70.0

SAT_KEYS = ("a_sat", "b_sat", "c_sat")
FRUST_KEYS = ("a_frust", "b_frust", "c_frust")

TriggerPath = Literal[
    "not_triggered",
    "harmonious",
    "obsessive",
    "mixed",
    "insufficient_evidence",
]


@dataclass
class DailySignals:
    """Optional daily cross-signal snapshot.

    Both fields are on the 0-100 scale used by the cognitive signal engine.
    The thresholds here match the original rule in abc-assessment-spec
    Section 2.2.
    """

    recovery_slope: float
    cognitive_load: float


@dataclass
class OverinvestmentTriggerResult:
    """Output of the overinvestment trigger.

    Attributes:
        triggered: True if the ABC-side pattern fired (two or more domains
            thriving). Independent of passion routing.
        path: Which routing path the trigger took. not_triggered if the
            ABC pattern did not fire. insufficient_evidence if the pattern
            fired but passion quality lacks the evidence gate to route.
        thriving_domains: Names of domains meeting the thriving criterion.
        cross_signal_present: True if daily signals were provided.
        cross_signal_concern: True if daily signals confirm recovery
            strain. None if signals not provided.
        coach_recommendation: Short label for the coach action, or None.
        rationale: Human-readable explanation. No banned terms, safe to
            log; narrative prose generated separately by narrative_engine.
    """

    triggered: bool
    path: TriggerPath
    thriving_domains: list[str]
    cross_signal_present: bool
    cross_signal_concern: bool | None
    coach_recommendation: str | None
    rationale: str


def _count_thriving_domains(subscales: dict[str, float]) -> list[str]:
    """Return domain names meeting the thriving criterion.

    Thriving = satisfaction >= SAT_THRIVING_THRESHOLD AND
    frustration < FRUST_LOW_THRESHOLD. Matches the original rule in
    abc-assessment-spec Section 2.2.
    """
    thriving: list[str] = []
    for domain in ("ambition", "belonging", "craft"):
        sat_key = f"{domain[0]}_sat"
        frust_key = f"{domain[0]}_frust"
        if (
            subscales.get(sat_key, 0.0) >= SAT_THRIVING_THRESHOLD
            and subscales.get(frust_key, 10.0) < FRUST_LOW_THRESHOLD
        ):
            thriving.append(domain)
    return thriving


def _cross_signal_concern(signals: DailySignals | None) -> bool | None:
    """Whether daily signals indicate recovery strain. None if absent."""
    if signals is None:
        return None
    return (
        signals.recovery_slope < RECOVERY_DECLINING_THRESHOLD
        and signals.cognitive_load > COGNITIVE_LOAD_HIGH_THRESHOLD
    )


def evaluate_overinvestment(
    subscales: dict[str, float],
    passion: PassionQualityResult,
    daily_signals: DailySignals | None = None,
) -> OverinvestmentTriggerResult:
    """Evaluate the overinvestment trigger with passion-aware routing.

    Reference: abc-assessment-spec Section 16.2

    Args:
        subscales: Six ABC subscale scores on 0-10. Keys: a_sat, a_frust,
            b_sat, b_frust, c_sat, c_frust.
        passion: Output of score_passion_quality. The recommendation gate
            on passion must be passed for the trigger to route to a
            harmonious or obsessive path.
        daily_signals: Optional recovery_slope and cognitive_load snapshot.
            When absent, the trigger still evaluates the ABC pattern but
            cross_signal_concern is None and the caller must decide
            whether to escalate.

    Returns:
        OverinvestmentTriggerResult describing whether the pattern fired,
        which path it took, and what coach action is suggested.
    """
    thriving_domains = _count_thriving_domains(subscales)
    abc_pattern = len(thriving_domains) >= 2
    cross_concern = _cross_signal_concern(daily_signals)
    signals_present = daily_signals is not None

    should_escalate = abc_pattern and (cross_concern is True or cross_concern is None)

    if not should_escalate:
        return OverinvestmentTriggerResult(
            triggered=False,
            path="not_triggered",
            thriving_domains=thriving_domains,
            cross_signal_present=signals_present,
            cross_signal_concern=cross_concern,
            coach_recommendation=None,
            rationale=(
                "no overinvestment pattern; fewer than two domains thriving"
                if not abc_pattern
                else "two or more domains thriving, recovery signals clear"
            ),
        )

    if not passion.recommendation_gate_passed:
        return OverinvestmentTriggerResult(
            triggered=True,
            path="insufficient_evidence",
            thriving_domains=thriving_domains,
            cross_signal_present=signals_present,
            cross_signal_concern=cross_concern,
            coach_recommendation="watch",
            rationale=(
                "overinvestment pattern present but passion leaning is "
                f"unclear: {passion.gate_reason}"
            ),
        )

    if passion.leaning == "harmonious":
        return OverinvestmentTriggerResult(
            triggered=True,
            path="harmonious",
            thriving_domains=thriving_domains,
            cross_signal_present=signals_present,
            cross_signal_concern=cross_concern,
            coach_recommendation="protect_recovery",
            rationale=(
                "thriving pattern with harmonious leaning; protect recovery "
                "without reducing engagement"
            ),
        )

    if passion.leaning == "obsessive":
        return OverinvestmentTriggerResult(
            triggered=True,
            path="obsessive",
            thriving_domains=thriving_domains,
            cross_signal_present=signals_present,
            cross_signal_concern=cross_concern,
            coach_recommendation="identity_conversation",
            rationale=(
                "thriving pattern with obsessive leaning; check for identity "
                "capture and conflict with other life domains"
            ),
        )

    if passion.leaning == "mixed":
        return OverinvestmentTriggerResult(
            triggered=True,
            path="mixed",
            thriving_domains=thriving_domains,
            cross_signal_present=signals_present,
            cross_signal_concern=cross_concern,
            coach_recommendation="check_conflict",
            rationale=(
                "thriving pattern with both harmonious and obsessive "
                "elevated; intensity is real, check for underlying conflict"
            ),
        )

    return OverinvestmentTriggerResult(
        triggered=True,
        path="insufficient_evidence",
        thriving_domains=thriving_domains,
        cross_signal_present=signals_present,
        cross_signal_concern=cross_concern,
        coach_recommendation="watch",
        rationale=(f"thriving pattern present but passion leaning is {passion.leaning}"),
    )
