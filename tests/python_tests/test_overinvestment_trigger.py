"""Tests for the overinvestment trigger with passion-aware routing.

Reference: improvement-plan-personalization-engine.md Section 16.2
Reference: src/python_scoring/overinvestment_trigger.py

Coverage:
- Pattern not present: no trigger
- Pattern present, harmonious passion: protect-recovery path
- Pattern present, obsessive passion: identity-conversation path
- Pattern present, mixed passion: check-conflict path
- Pattern present, passion gate fails: watch path
- Daily cross-signals present vs absent
- Cross-signals clear: no trigger even with thriving domains
"""

from __future__ import annotations

from src.python_scoring.overinvestment_trigger import (
    DailySignals,
    evaluate_overinvestment,
)
from src.python_scoring.passion_quality import score_passion_quality


def _two_thriving_subscales() -> dict[str, float]:
    """Ambition and Craft thriving, Belonging neutral."""
    return {
        "a_sat": 8.0,
        "a_frust": 1.5,
        "b_sat": 5.0,
        "b_frust": 3.0,
        "c_sat": 8.0,
        "c_frust": 1.5,
    }


def _one_thriving_subscales() -> dict[str, float]:
    return {
        "a_sat": 8.0,
        "a_frust": 1.5,
        "b_sat": 5.0,
        "b_frust": 3.0,
        "c_sat": 5.0,
        "c_frust": 3.0,
    }


def _harmonious_passion():
    return score_passion_quality({"HP1": 7, "HP2": 7, "HP3": 7, "OP1": 1, "OP2": 1, "OP3": 1})


def _obsessive_passion():
    return score_passion_quality({"HP1": 1, "HP2": 1, "HP3": 1, "OP1": 7, "OP2": 7, "OP3": 7})


def _mixed_passion():
    return score_passion_quality({"HP1": 6, "HP2": 6, "HP3": 6, "OP1": 6, "OP2": 6, "OP3": 6})


def _unclear_passion():
    """All answered, leaning is insufficient_signal: HP just elevated,
    OP just below elevated, balance under the leaning threshold. The
    recommendation gate does not pass."""
    return score_passion_quality({"HP1": 4, "HP2": 4, "HP3": 4, "OP1": 4, "OP2": 4, "OP3": 3})


class TestNoTrigger:
    """Cases where the trigger does not fire."""

    def test_one_thriving_domain_does_not_fire(self):
        result = evaluate_overinvestment(_one_thriving_subscales(), _harmonious_passion())
        assert result.triggered is False
        assert result.path == "not_triggered"
        assert result.coach_recommendation is None

    def test_no_thriving_domains_does_not_fire(self):
        neutral = {
            "a_sat": 5.0,
            "a_frust": 4.0,
            "b_sat": 5.0,
            "b_frust": 4.0,
            "c_sat": 5.0,
            "c_frust": 4.0,
        }
        result = evaluate_overinvestment(neutral, _harmonious_passion())
        assert result.triggered is False

    def test_signals_clear_does_not_fire(self):
        """Thriving pattern present but daily signals are healthy."""
        signals = DailySignals(recovery_slope=70.0, cognitive_load=40.0)
        result = evaluate_overinvestment(_two_thriving_subscales(), _harmonious_passion(), signals)
        assert result.triggered is False
        assert result.cross_signal_concern is False


class TestHarmoniousPath:
    def test_harmonious_path_when_pattern_and_harmonious_passion(self):
        result = evaluate_overinvestment(_two_thriving_subscales(), _harmonious_passion())
        assert result.triggered is True
        assert result.path == "harmonious"
        assert result.coach_recommendation == "protect_recovery"
        assert "recovery" in result.rationale

    def test_harmonious_path_with_confirming_signals(self):
        signals = DailySignals(recovery_slope=30.0, cognitive_load=80.0)
        result = evaluate_overinvestment(_two_thriving_subscales(), _harmonious_passion(), signals)
        assert result.path == "harmonious"
        assert result.cross_signal_present is True
        assert result.cross_signal_concern is True


class TestObsessivePath:
    def test_obsessive_path_when_pattern_and_obsessive_passion(self):
        result = evaluate_overinvestment(_two_thriving_subscales(), _obsessive_passion())
        assert result.triggered is True
        assert result.path == "obsessive"
        assert result.coach_recommendation == "identity_conversation"
        assert "identity" in result.rationale or "life" in result.rationale


class TestMixedPath:
    def test_mixed_path_when_both_passion_subscales_elevated(self):
        result = evaluate_overinvestment(_two_thriving_subscales(), _mixed_passion())
        assert result.triggered is True
        assert result.path == "mixed"
        assert result.coach_recommendation == "check_conflict"


class TestInsufficientEvidence:
    def test_unclear_passion_routes_to_watch(self):
        result = evaluate_overinvestment(_two_thriving_subscales(), _unclear_passion())
        assert result.triggered is True
        assert result.path == "insufficient_evidence"
        assert result.coach_recommendation == "watch"

    def test_passion_gate_failed_routes_to_watch(self):
        empty_passion = score_passion_quality({})
        result = evaluate_overinvestment(_two_thriving_subscales(), empty_passion)
        assert result.triggered is True
        assert result.path == "insufficient_evidence"

    def test_uninvested_passion_with_thriving_routes_to_watch(self):
        """Edge case: ABC domains show thriving but passion is uninvested.

        This is a contradictory signal. The coach action is watch, not a
        specific intervention. The rationale names the contradiction so
        it can be audited upstream.
        """
        uninvested = score_passion_quality(
            {"HP1": 2, "HP2": 2, "HP3": 2, "OP1": 2, "OP2": 2, "OP3": 2}
        )
        assert uninvested.leaning == "uninvested"
        assert uninvested.recommendation_gate_passed is True

        result = evaluate_overinvestment(_two_thriving_subscales(), uninvested)
        assert result.triggered is True
        assert result.path == "insufficient_evidence"
        assert "uninvested" in result.rationale


class TestSignalsAbsent:
    def test_signals_absent_still_evaluates(self):
        result = evaluate_overinvestment(_two_thriving_subscales(), _harmonious_passion())
        assert result.cross_signal_present is False
        assert result.cross_signal_concern is None
        assert result.triggered is True
