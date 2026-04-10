"""Tests for the transition engine."""

import pytest

from src.python_scoring.transition_engine import (
    ARCHETYPE_DOMAINS,
    ARCHETYPE_LEVELS,
    FatigueTimescale,
    TransitionTracker,
    TransitionType,
    _compute_slope,
    _confidence_threshold_for_window,
    classify_fatigue_timescale,
    classify_transition,
    get_domains_gained,
    get_domains_lost,
)

# ── Growth hierarchy tests ──────────────────────────────────────────


class TestArchetypeLevels:
    def test_seeker_is_level_0(self):
        assert ARCHETYPE_LEVELS["Seeker"] == 0

    def test_single_domain_types_are_level_1(self):
        for name in ["Pioneer", "Anchor", "Artisan"]:
            assert ARCHETYPE_LEVELS[name] == 1, f"{name} should be level 1"

    def test_dual_domain_types_are_level_2(self):
        for name in ["Captain", "Architect", "Mentor"]:
            assert ARCHETYPE_LEVELS[name] == 2, f"{name} should be level 2"

    def test_integrator_is_level_3(self):
        assert ARCHETYPE_LEVELS["Integrator"] == 3

    def test_all_8_archetypes_present(self):
        assert len(ARCHETYPE_LEVELS) == 8

    def test_domain_sets_match_levels(self):
        for name, level in ARCHETYPE_LEVELS.items():
            domains = ARCHETYPE_DOMAINS[name]
            assert len(domains) == level, f"{name} has {len(domains)} domains but level {level}"


# ── Transition classification tests ─────────────────────────────────


class TestClassifyTransition:
    def test_same_type_is_sustained(self):
        result = classify_transition("Pioneer", "Pioneer")
        assert result == TransitionType.SUSTAINED

    def test_growth_seeker_to_pioneer(self):
        result = classify_transition("Seeker", "Pioneer")
        assert result == TransitionType.GROWTH

    def test_growth_pioneer_to_captain(self):
        result = classify_transition("Pioneer", "Captain")
        assert result == TransitionType.GROWTH

    def test_growth_captain_to_integrator(self):
        result = classify_transition("Captain", "Integrator")
        assert result == TransitionType.GROWTH

    def test_growth_seeker_to_integrator(self):
        result = classify_transition("Seeker", "Integrator")
        assert result == TransitionType.GROWTH

    def test_regression_integrator_to_pioneer(self):
        result = classify_transition("Integrator", "Pioneer")
        assert result == TransitionType.REGRESSION

    def test_regression_captain_to_seeker(self):
        result = classify_transition("Captain", "Seeker")
        assert result == TransitionType.REGRESSION

    def test_exploration_pioneer_to_anchor(self):
        result = classify_transition("Pioneer", "Anchor")
        assert result == TransitionType.EXPLORATION

    def test_exploration_captain_to_mentor(self):
        result = classify_transition("Captain", "Mentor")
        assert result == TransitionType.EXPLORATION

    def test_low_confidence_is_fluctuation(self):
        result = classify_transition(
            "Pioneer",
            "Captain",
            posterior_confidence=0.5,
            weeks_elapsed=2,
        )
        assert result == TransitionType.FLUCTUATION

    def test_high_confidence_short_window_is_growth(self):
        result = classify_transition(
            "Pioneer",
            "Captain",
            posterior_confidence=0.80,
            weeks_elapsed=2,
        )
        assert result == TransitionType.GROWTH

    def test_moderate_confidence_long_window_is_growth(self):
        result = classify_transition(
            "Pioneer",
            "Captain",
            posterior_confidence=0.62,
            weeks_elapsed=10,
        )
        assert result == TransitionType.GROWTH

    def test_moderate_confidence_short_window_is_fluctuation(self):
        result = classify_transition(
            "Pioneer",
            "Captain",
            posterior_confidence=0.62,
            weeks_elapsed=2,
        )
        assert result == TransitionType.FLUCTUATION

    def test_unknown_archetype_raises(self):
        with pytest.raises(ValueError):
            classify_transition("Unknown", "Pioneer")

    def test_unknown_current_raises(self):
        with pytest.raises(ValueError):
            classify_transition("Pioneer", "Unknown")


# ── Confidence threshold tests ──────────────────────────────────────


class TestConfidenceThreshold:
    def test_short_window_high_threshold(self):
        assert _confidence_threshold_for_window(2) == 0.75
        assert _confidence_threshold_for_window(4) == 0.75

    def test_medium_window_moderate_threshold(self):
        assert _confidence_threshold_for_window(5) == 0.65
        assert _confidence_threshold_for_window(8) == 0.65

    def test_long_window_standard_threshold(self):
        assert _confidence_threshold_for_window(9) == 0.60
        assert _confidence_threshold_for_window(20) == 0.60


# ── Domain gain/loss tests ──────────────────────────────────────────


class TestDomainChanges:
    def test_seeker_to_pioneer_gains_ambition(self):
        gained = get_domains_gained("Seeker", "Pioneer")
        assert gained == {"ambition"}

    def test_pioneer_to_captain_gains_belonging(self):
        gained = get_domains_gained("Pioneer", "Captain")
        assert gained == {"belonging"}

    def test_integrator_to_pioneer_loses_belonging_craft(self):
        lost = get_domains_lost("Integrator", "Pioneer")
        assert lost == {"belonging", "craft"}

    def test_same_type_no_changes(self):
        assert get_domains_gained("Pioneer", "Pioneer") == set()
        assert get_domains_lost("Pioneer", "Pioneer") == set()

    def test_exploration_swaps_domains(self):
        gained = get_domains_gained("Pioneer", "Anchor")
        lost = get_domains_lost("Pioneer", "Anchor")
        assert gained == {"belonging"}
        assert lost == {"ambition"}


# ── Fatigue timescale tests ─────────────────────────────────────────


class TestFatigueTimescale:
    def test_short_history_is_acute(self):
        result = classify_fatigue_timescale([3.0, 5.0])
        assert result == FatigueTimescale.ACUTE

    def test_stable_history_is_acute(self):
        result = classify_fatigue_timescale([4.0, 4.1, 4.0, 3.9, 4.0, 4.1])
        assert result == FatigueTimescale.ACUTE

    def test_rising_trend_is_chronic(self):
        result = classify_fatigue_timescale([3.0, 3.5, 4.0, 4.5, 5.0, 5.5])
        assert result == FatigueTimescale.CHRONIC

    def test_sudden_spike_is_acute(self):
        result = classify_fatigue_timescale([3.0, 3.0, 3.0, 3.0, 3.0, 5.0])
        assert result == FatigueTimescale.ACUTE

    def test_spike_on_trend_is_mixed(self):
        result = classify_fatigue_timescale([3.0, 3.5, 4.0, 4.5, 5.0, 7.0])
        assert result == FatigueTimescale.MIXED


# ── Slope computation tests ─────────────────────────────────────────


class TestComputeSlope:
    def test_flat_line(self):
        slope = _compute_slope([5.0, 5.0, 5.0])
        assert abs(slope) < 0.001

    def test_rising_line(self):
        slope = _compute_slope([0.0, 1.0, 2.0, 3.0])
        assert abs(slope - 1.0) < 0.001

    def test_single_value(self):
        slope = _compute_slope([5.0])
        assert slope == 0.0

    def test_empty_list(self):
        slope = _compute_slope([])
        assert slope == 0.0


# ── TransitionTracker tests ─────────────────────────────────────────


class TestTransitionTracker:
    def test_first_record_has_no_transition(self):
        tracker = TransitionTracker()
        result = tracker.record("Pioneer")
        assert result["transition"] is None
        assert result["measurement_number"] == 1

    def test_sustained_sequence(self):
        tracker = TransitionTracker()
        tracker.record("Pioneer")
        result = tracker.record("Pioneer")
        assert result["transition_type"] == "sustained"

    def test_growth_recorded(self):
        tracker = TransitionTracker()
        tracker.record("Seeker")
        result = tracker.record("Pioneer", posterior_confidence=0.9)
        assert result["transition_type"] == "growth"
        assert result["transition"]["domains_gained"] == ["ambition"]

    def test_sustained_count(self):
        tracker = TransitionTracker()
        tracker.record("Pioneer")
        tracker.record("Pioneer")
        tracker.record("Pioneer")
        assert tracker.get_sustained_count() == 3

    def test_sustained_count_resets_on_change(self):
        tracker = TransitionTracker()
        tracker.record("Pioneer")
        tracker.record("Pioneer")
        tracker.record("Captain", posterior_confidence=0.9)
        assert tracker.get_sustained_count() == 1

    def test_growth_trajectory(self):
        tracker = TransitionTracker()
        tracker.record("Seeker")
        tracker.record("Pioneer", posterior_confidence=0.9)
        tracker.record("Captain", posterior_confidence=0.9)
        trajectory = tracker.get_growth_trajectory()
        assert trajectory == [0, 1, 2]

    def test_transition_counts(self):
        tracker = TransitionTracker()
        tracker.record("Seeker")
        tracker.record("Pioneer", posterior_confidence=0.9)
        tracker.record("Pioneer")
        tracker.record("Captain", posterior_confidence=0.9)
        counts = tracker.get_transition_counts()
        assert counts["growth"] == 2
        assert counts["sustained"] == 1

    def test_most_common_type(self):
        tracker = TransitionTracker()
        tracker.record("Pioneer")
        tracker.record("Pioneer")
        tracker.record("Captain", posterior_confidence=0.9)
        assert tracker.get_most_common_type() == "Pioneer"

    def test_current_type(self):
        tracker = TransitionTracker()
        tracker.record("Pioneer")
        tracker.record("Captain", posterior_confidence=0.9)
        assert tracker.get_current_type() == "Captain"

    def test_empty_tracker_summary(self):
        tracker = TransitionTracker()
        summary = tracker.get_summary()
        assert summary["current_type"] is None
        assert summary["measurement_count"] == 0

    def test_full_summary(self):
        tracker = TransitionTracker()
        tracker.record("Seeker")
        tracker.record("Pioneer", posterior_confidence=0.9)
        tracker.record("Pioneer")
        summary = tracker.get_summary()
        assert summary["current_type"] == "Pioneer"
        assert summary["measurement_count"] == 3
        assert summary["highest_level_reached"] == 1
        assert summary["current_level"] == 1
        assert summary["sustained_count"] == 2
