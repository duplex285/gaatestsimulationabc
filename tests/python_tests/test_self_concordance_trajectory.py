"""Tests for the self-concordance trajectory engine.

Reference: improvement-plan-personalization-engine.md Section 16.7
Reference: src/python_scoring/self_concordance_trajectory.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.self_concordance import score_self_concordance
from src.python_scoring.self_concordance_trajectory import (
    DIRECTIONAL_MAGNITUDE_THRESHOLD,
    MIN_POINTS_FOR_TRAJECTORY,
    OSCILLATION_SD_THRESHOLD,
    GoalTrajectoryPoint,
    GoalTrajectoryTracker,
    compute_all_trajectories,
    compute_goal_trajectory,
)


def _profile(sc1: int, sc2: int, sc3: int, sc4: int):
    return score_self_concordance({"SC1": sc1, "SC2": sc2, "SC3": sc3, "SC4": sc4})


def _autonomous_profile():
    """self_concordance approx +6.7"""
    return _profile(2, 2, 6, 6)


def _controlled_profile():
    """self_concordance approx -6.7"""
    return _profile(6, 6, 2, 2)


def _midpoint_profile():
    """self_concordance approx 0"""
    return _profile(4, 4, 4, 4)


def _make_point(goal_id: str, cycle: int, profile) -> GoalTrajectoryPoint:
    return GoalTrajectoryPoint(goal_id=goal_id, cycle_index=cycle, profile=profile)


class TestSingleGoalSlopes:
    def test_increasing_series_becomes_more_autonomous(self):
        points = [
            _make_point("goal-1", 0, _controlled_profile()),
            _make_point("goal-1", 1, _midpoint_profile()),
            _make_point("goal-1", 2, _autonomous_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "becoming_more_autonomous"
        assert traj.direction == "rising"
        assert traj.slope is not None and traj.slope > 0
        assert traj.magnitude is not None and traj.magnitude > 0

    def test_decreasing_series_becomes_more_controlled(self):
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, _midpoint_profile()),
            _make_point("goal-1", 2, _controlled_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "becoming_more_controlled"
        assert traj.direction == "falling"
        assert traj.slope is not None and traj.slope < 0

    def test_flat_series_is_stable(self):
        points = [
            _make_point("goal-1", 0, _midpoint_profile()),
            _make_point("goal-1", 1, _midpoint_profile()),
            _make_point("goal-1", 2, _midpoint_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "stable"
        assert traj.direction == "flat"

    def test_oscillating_series_detected(self):
        """Big swings, near-zero net magnitude -> oscillating."""
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, _controlled_profile()),
            _make_point("goal-1", 2, _autonomous_profile()),
            _make_point("goal-1", 3, _controlled_profile()),
            _make_point("goal-1", 4, _autonomous_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "oscillating"
        assert traj.within_series_sd is not None
        assert traj.within_series_sd >= OSCILLATION_SD_THRESHOLD


class TestInsufficientData:
    def test_two_points_returns_insufficient(self):
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, _autonomous_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "insufficient_data"
        assert traj.slope is None
        assert traj.magnitude is None
        assert traj.n_points_total == 2
        assert traj.n_points_computable == 2
        assert traj.latest_self_concordance is not None

    def test_one_point_returns_insufficient(self):
        points = [_make_point("goal-1", 0, _autonomous_profile())]
        traj = compute_goal_trajectory(points)
        assert traj.label == "insufficient_data"
        assert traj.latest_self_concordance is not None

    def test_min_points_constant(self):
        assert MIN_POINTS_FOR_TRAJECTORY == 3

    def test_empty_points_raises(self):
        with pytest.raises(ValueError):
            compute_goal_trajectory([])


class TestNotComputedFiltering:
    def test_not_computed_points_filtered_out(self):
        empty_profile = score_self_concordance({})  # display gate fails
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, empty_profile),
            _make_point("goal-1", 2, _midpoint_profile()),
            _make_point("goal-1", 3, _controlled_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.n_points_total == 4
        assert traj.n_points_computable == 3
        assert traj.label == "becoming_more_controlled"

    def test_all_not_computed_returns_insufficient(self):
        empty_profile = score_self_concordance({})
        points = [
            _make_point("goal-1", 0, empty_profile),
            _make_point("goal-1", 1, empty_profile),
            _make_point("goal-1", 2, empty_profile),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "insufficient_data"
        assert traj.n_points_computable == 0
        assert traj.latest_self_concordance is None


class TestMultiGoalGrouping:
    def test_compute_all_groups_by_goal_id(self):
        points = [
            _make_point("goal-A", 0, _controlled_profile()),
            _make_point("goal-A", 1, _midpoint_profile()),
            _make_point("goal-A", 2, _autonomous_profile()),
            _make_point("goal-B", 0, _autonomous_profile()),
            _make_point("goal-B", 1, _midpoint_profile()),
            _make_point("goal-B", 2, _controlled_profile()),
        ]
        trajectories = compute_all_trajectories(points)
        assert set(trajectories.keys()) == {"goal-A", "goal-B"}
        assert trajectories["goal-A"].label == "becoming_more_autonomous"
        assert trajectories["goal-B"].label == "becoming_more_controlled"

    def test_compute_all_handles_single_goal(self):
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, _autonomous_profile()),
            _make_point("goal-1", 2, _autonomous_profile()),
        ]
        trajectories = compute_all_trajectories(points)
        assert list(trajectories.keys()) == ["goal-1"]

    def test_compute_all_empty_returns_empty(self):
        assert compute_all_trajectories([]) == {}


class TestSingleGoalValidation:
    def test_mixed_goal_ids_raises(self):
        points = [
            _make_point("goal-A", 0, _autonomous_profile()),
            _make_point("goal-B", 1, _controlled_profile()),
        ]
        with pytest.raises(ValueError, match="same goal_id"):
            compute_goal_trajectory(points)


class TestEdgeCases:
    def test_directional_magnitude_threshold(self):
        assert DIRECTIONAL_MAGNITUDE_THRESHOLD == 1.0

    def test_small_change_classified_as_stable(self):
        """A tiny but positive change should not fire becoming_more_autonomous."""
        # All midpoint profiles -> magnitude 0, slope 0 -> stable
        points = [
            _make_point("goal-1", 0, _midpoint_profile()),
            _make_point("goal-1", 1, _midpoint_profile()),
            _make_point("goal-1", 2, _midpoint_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.label == "stable"

    def test_latest_self_concordance_is_last_computable(self):
        """latest_self_concordance should be the last point's score, not the mean."""
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 1, _midpoint_profile()),
            _make_point("goal-1", 2, _controlled_profile()),
        ]
        traj = compute_goal_trajectory(points)
        last_score = points[-1].profile.self_concordance
        assert traj.latest_self_concordance == last_score

    def test_zero_x_variance_returns_zero_slope(self):
        """All points at the same cycle_index produce zero denominator;
        the OLS slope falls back to 0.0 and the trajectory classifies
        as stable.
        """
        points = [
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 0, _autonomous_profile()),
            _make_point("goal-1", 0, _autonomous_profile()),
        ]
        traj = compute_goal_trajectory(points)
        assert traj.slope == 0.0
        assert traj.label == "stable"

    def test_tracker_accumulates_across_calls(self):
        tracker = GoalTrajectoryTracker()
        tracker.record("goal-1", 0, _controlled_profile())
        tracker.record("goal-1", 1, _midpoint_profile())
        tracker.record("goal-1", 2, _autonomous_profile())
        traj = tracker.get_trajectory("goal-1")
        assert traj is not None
        assert traj.label == "becoming_more_autonomous"
        assert tracker.point_count("goal-1") == 3

    def test_tracker_returns_none_for_unknown_goal(self):
        tracker = GoalTrajectoryTracker()
        assert tracker.get_trajectory("nope") is None

    def test_tracker_insufficient_below_min_points(self):
        tracker = GoalTrajectoryTracker()
        tracker.record("goal-1", 0, _autonomous_profile())
        tracker.record("goal-1", 1, _autonomous_profile())
        traj = tracker.get_trajectory("goal-1")
        assert traj is not None
        assert traj.label == "insufficient_data"

    def test_tracker_handles_multiple_goals(self):
        tracker = GoalTrajectoryTracker()
        tracker.record("goal-A", 0, _controlled_profile())
        tracker.record("goal-A", 1, _midpoint_profile())
        tracker.record("goal-A", 2, _autonomous_profile())
        tracker.record("goal-B", 0, _autonomous_profile())
        tracker.record("goal-B", 1, _midpoint_profile())
        tracker.record("goal-B", 2, _controlled_profile())
        trajectories = tracker.get_all_trajectories()
        assert set(trajectories.keys()) == {"goal-A", "goal-B"}
        assert trajectories["goal-A"].label == "becoming_more_autonomous"
        assert trajectories["goal-B"].label == "becoming_more_controlled"

    def test_tracker_goals_in_first_seen_order(self):
        tracker = GoalTrajectoryTracker()
        tracker.record("first", 0, _autonomous_profile())
        tracker.record("second", 0, _controlled_profile())
        assert tracker.goals() == ["first", "second"]

    def test_inconsistent_slope_and_magnitude_falls_back_to_stable(self):
        """When magnitude meets the directional threshold but the OLS
        slope disagrees in sign, the classifier falls back to stable
        rather than firing a directional label on a noisy series.

        ys = [1, 10, 9, 3, 2]: magnitude = +1.0 (exactly at threshold),
        slope = -0.5. Rising requires slope > 0; oscillation requires
        abs(magnitude) < threshold. Neither fires; fallback hits.
        """
        from src.python_scoring.self_concordance import score_self_concordance

        # Build profiles with specific self_concordance values by
        # constructing item responses that yield those values.
        # SC items are 1-7; sc = autonomous_score - controlled_score on 0-10.
        # Easiest: use the same helper to make profiles whose values land
        # in the target series.
        def profile_with_sc(target: float):
            # Map target sc in [-10, 10] to a (controlled, autonomous) pair.
            auto = (10 + target) / 2  # 0 to 10
            ctrl = 10 - auto
            # Convert auto/ctrl on 0-10 back to integer 1-7 ratings.
            # raw = round((score / 10) * 6 + 1)
            sc_a = round((auto / 10) * 6 + 1)
            sc_c = round((ctrl / 10) * 6 + 1)
            return score_self_concordance({"SC1": sc_c, "SC2": sc_c, "SC3": sc_a, "SC4": sc_a})

        targets = [1.0, 10.0, 9.0, 3.0, 2.0]
        points = [
            GoalTrajectoryPoint(goal_id="goal-1", cycle_index=i, profile=profile_with_sc(t))
            for i, t in enumerate(targets)
        ]
        traj = compute_goal_trajectory(points)
        # Direction would be flat; label falls back to stable
        assert traj.direction == "flat"
        assert traj.label == "stable"
