"""Per-goal self-concordance trajectory engine.

Sheldon's central empirical claim is that the *trajectory* of self-concordance
predicts goal attainment and well-being more strongly than the absolute level
in any one cycle. This module turns a chronological series of per-goal
self-concordance profiles into a slope, a magnitude, and a labeled
trajectory.

Reference: abc-assessment-spec Section 16.7
Reference: docs/20260421-self-concordance-retrospective.md (open item 4.2)
Reference: src/python_scoring/self_concordance.py

Research basis:
  Sheldon, K. M., & Houser-Marko, L. (2001). Self-concordance, goal
    attainment, and the pursuit of happiness: Can there be an upward spiral?
  Sheldon & Goffredi, Oxford Handbook of SDT, Chapter 17.

Goal continuity is the caller's responsibility. The product side decides
how to identify a goal as the same across cycles (free-text matching,
athlete-declared continuity, or stored goal IDs). This module receives
a `goal_id` per point and groups by it.

Points whose underlying SelfConcordanceProfile failed the display gate
are filtered out before slope computation; the trajectory is computed
only on cycles where the score is meaningful.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, stdev
from typing import Literal

from src.python_scoring.self_concordance import SelfConcordanceProfile

MIN_POINTS_FOR_TRAJECTORY = 3
FLAT_SLOPE_TOLERANCE = 0.5
OSCILLATION_SD_THRESHOLD = 2.5
DIRECTIONAL_MAGNITUDE_THRESHOLD = 1.0

TrajectoryLabel = Literal[
    "becoming_more_autonomous",
    "becoming_more_controlled",
    "stable",
    "oscillating",
    "insufficient_data",
]
TrajectoryDirection = Literal["rising", "falling", "flat", "insufficient_data"]


@dataclass
class GoalTrajectoryPoint:
    """One self-concordance measurement on a specific goal at a specific cycle.

    Attributes:
        goal_id: Caller-supplied identifier for the goal. Two points with
            the same goal_id are treated as repeated measurements of the
            same goal; different goal_ids are treated as separate goals.
        cycle_index: Ordinal position of the cycle (0, 1, 2, ...). Acts
            as the x-axis for slope computation. Caller controls the
            scaling; one unit per biweekly cycle is the default
            assumption.
        profile: The SelfConcordanceProfile produced by score_self_concordance
            for this goal at this cycle.
    """

    goal_id: str
    cycle_index: int
    profile: SelfConcordanceProfile


@dataclass
class GoalTrajectory:
    """Trajectory result for one goal across cycles.

    Attributes:
        goal_id: The goal this trajectory describes.
        n_points_total: Count of points supplied for this goal.
        n_points_computable: Count of points whose display gate passed
            and whose self_concordance value is therefore usable.
        slope: Linear-regression slope of self_concordance vs
            cycle_index, in points per cycle. None when there are
            fewer than MIN_POINTS_FOR_TRAJECTORY computable points.
        magnitude: Latest self_concordance minus earliest, across the
            computable points. None when insufficient data.
        within_series_sd: Standard deviation of self_concordance across
            the computable points. None when insufficient data.
        direction: rising, falling, flat, or insufficient_data.
        label: Five-way trajectory label for narrative selection.
        latest_self_concordance: Most recent self_concordance value,
            for product display alongside the trajectory.
    """

    goal_id: str
    n_points_total: int
    n_points_computable: int
    slope: float | None
    magnitude: float | None
    within_series_sd: float | None
    direction: TrajectoryDirection
    label: TrajectoryLabel
    latest_self_concordance: float | None


def _ols_slope(xs: list[float], ys: list[float]) -> float:
    """Plain ordinary-least-squares slope. Inline to avoid pulling numpy here."""
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True))
    den = sum((x - x_mean) ** 2 for x in xs)
    if den == 0:
        return 0.0
    return num / den


def _classify_label(
    slope: float,
    magnitude: float,
    sd: float,
) -> tuple[TrajectoryLabel, TrajectoryDirection]:
    """Apply the trajectory-label rules.

    Order of checks matters. Oscillation is checked first because a high-
    variance series can have a small net slope yet still be a meaningful
    pattern. Then magnitude-anchored direction. Then flat fallback.
    """
    if sd >= OSCILLATION_SD_THRESHOLD and abs(magnitude) < DIRECTIONAL_MAGNITUDE_THRESHOLD:
        return "oscillating", "flat"

    if abs(slope) < FLAT_SLOPE_TOLERANCE and abs(magnitude) < DIRECTIONAL_MAGNITUDE_THRESHOLD:
        return "stable", "flat"

    if magnitude >= DIRECTIONAL_MAGNITUDE_THRESHOLD and slope > 0:
        return "becoming_more_autonomous", "rising"

    if magnitude <= -DIRECTIONAL_MAGNITUDE_THRESHOLD and slope < 0:
        return "becoming_more_controlled", "falling"

    # Mixed signal: slope and magnitude disagree, or magnitude is small
    # while slope is non-trivial. Treat as stable with a note.
    return "stable", "flat"


def compute_goal_trajectory(
    points: list[GoalTrajectoryPoint],
) -> GoalTrajectory:
    """Compute the trajectory for a single goal's series of points.

    Reference: abc-assessment-spec Section 16.7

    All points must share the same goal_id; raises if not.

    Args:
        points: Chronologically ordered list of points for one goal.

    Returns:
        GoalTrajectory describing the slope, magnitude, direction, and
        label for this goal's series.
    """
    if not points:
        raise ValueError("compute_goal_trajectory requires at least one point")

    goal_ids = {p.goal_id for p in points}
    if len(goal_ids) > 1:
        raise ValueError(f"all points must share the same goal_id; got {sorted(goal_ids)}")
    goal_id = points[0].goal_id

    computable = [
        p
        for p in points
        if p.profile.display_gate_passed and p.profile.self_concordance is not None
    ]

    n_total = len(points)
    n_computable = len(computable)

    if n_computable < MIN_POINTS_FOR_TRAJECTORY:
        latest = computable[-1].profile.self_concordance if computable else None
        return GoalTrajectory(
            goal_id=goal_id,
            n_points_total=n_total,
            n_points_computable=n_computable,
            slope=None,
            magnitude=None,
            within_series_sd=None,
            direction="insufficient_data",
            label="insufficient_data",
            latest_self_concordance=latest,
        )

    xs = [float(p.cycle_index) for p in computable]
    ys = [p.profile.self_concordance for p in computable]
    assert all(y is not None for y in ys)
    ys_concrete: list[float] = [y for y in ys if y is not None]

    slope = _ols_slope(xs, ys_concrete)
    magnitude = ys_concrete[-1] - ys_concrete[0]
    sd = stdev(ys_concrete)

    label, direction = _classify_label(slope, magnitude, sd)

    return GoalTrajectory(
        goal_id=goal_id,
        n_points_total=n_total,
        n_points_computable=n_computable,
        slope=slope,
        magnitude=magnitude,
        within_series_sd=sd,
        direction=direction,
        label=label,
        latest_self_concordance=ys_concrete[-1],
    )


def compute_all_trajectories(
    points: list[GoalTrajectoryPoint],
) -> dict[str, GoalTrajectory]:
    """Compute trajectories for every goal present in the input.

    Reference: abc-assessment-spec Section 16.7

    Args:
        points: Chronologically ordered list of points across one or
            more goals. Points are grouped by goal_id; within each goal
            the input order is preserved.

    Returns:
        Dict mapping goal_id to GoalTrajectory. Goals with no points
        do not appear (vacuously). Goals with fewer than
        MIN_POINTS_FOR_TRAJECTORY computable points appear with
        label="insufficient_data".
    """
    by_goal: dict[str, list[GoalTrajectoryPoint]] = {}
    for p in points:
        by_goal.setdefault(p.goal_id, []).append(p)

    return {
        goal_id: compute_goal_trajectory(goal_points) for goal_id, goal_points in by_goal.items()
    }


class GoalTrajectoryTracker:
    """Stateful tracker that accumulates per-goal self-concordance points.

    Mirrors the pattern of `TransitionTracker`: callers `record()` a new
    measurement each cycle and read the current trajectory via
    `get_trajectory()` or `get_all_trajectories()`. Points are stored
    internally keyed by goal_id.

    Usage:
        tracker = GoalTrajectoryTracker()
        tracker.record("scholarship", 0, profile_0)
        tracker.record("scholarship", 1, profile_1)
        tracker.record("scholarship", 2, profile_2)
        traj = tracker.get_trajectory("scholarship")

    Reference: abc-assessment-spec Section 16.7
    """

    def __init__(self) -> None:
        self._points_by_goal: dict[str, list[GoalTrajectoryPoint]] = {}

    def record(
        self,
        goal_id: str,
        cycle_index: int,
        profile: SelfConcordanceProfile,
    ) -> None:
        """Append a new point to this goal's history.

        Reference: abc-assessment-spec Section 16.7
        """
        point = GoalTrajectoryPoint(goal_id=goal_id, cycle_index=cycle_index, profile=profile)
        self._points_by_goal.setdefault(goal_id, []).append(point)

    def get_trajectory(self, goal_id: str) -> GoalTrajectory | None:
        """Return the current trajectory for one goal.

        Reference: abc-assessment-spec Section 16.7

        Returns None when the goal has no recorded points. For goals
        with fewer than MIN_POINTS_FOR_TRAJECTORY computable points, a
        GoalTrajectory with label="insufficient_data" is returned.
        """
        points = self._points_by_goal.get(goal_id)
        if not points:
            return None
        return compute_goal_trajectory(points)

    def get_all_trajectories(self) -> dict[str, GoalTrajectory]:
        """Return trajectories for every goal in the tracker.

        Reference: abc-assessment-spec Section 16.7
        """
        return {
            goal_id: compute_goal_trajectory(points)
            for goal_id, points in self._points_by_goal.items()
        }

    def goals(self) -> list[str]:
        """Return the list of goal IDs the tracker has seen, in first-seen order.

        Reference: abc-assessment-spec Section 16.7
        """
        return list(self._points_by_goal.keys())

    def point_count(self, goal_id: str) -> int:
        """Total recorded points for a goal (including not_computed ones).

        Reference: abc-assessment-spec Section 16.7
        """
        return len(self._points_by_goal.get(goal_id, []))


# Re-export the mean function for tests that want to verify slope by hand.
__all__ = [
    "DIRECTIONAL_MAGNITUDE_THRESHOLD",
    "FLAT_SLOPE_TOLERANCE",
    "GoalTrajectory",
    "GoalTrajectoryPoint",
    "GoalTrajectoryTracker",
    "MIN_POINTS_FOR_TRAJECTORY",
    "OSCILLATION_SD_THRESHOLD",
    "TrajectoryDirection",
    "TrajectoryLabel",
    "compute_all_trajectories",
    "compute_goal_trajectory",
    "mean",
]
