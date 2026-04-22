"""
Transition Engine for ABC Assessment.

Classifies archetype transitions as growth, exploration, regression,
or fluctuation. Generates a growth hierarchy across the 8 base patterns
and tracks an athlete's developmental trajectory over time.

The core insight: type instability is not measurement noise. It is
development made visible. An athlete moving from Seeker to Artisan
is not a classification error. It is growth.

Growth hierarchy follows SDT's prediction that need satisfaction
tends to broaden over development (Ryan & Deci, 2017).

Confidence gating follows Fernet et al. (2020), who found motivation
profiles stable over 4 months. Short-window transitions require higher
confidence to distinguish signal from noise.

References:
    Ryan, R. M., & Deci, E. L. (2017). Self-Determination Theory.
    Fernet, C., et al. (2020). European Journal of Work and
        Organizational Psychology, 29, 49-63.
    Muller, T., et al. (2021). Nature Communications, 12, 4593.
"""

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.python_scoring.regulatory_style import RegulatoryProfile


class TransitionType(Enum):
    """Classification of archetype transitions."""

    GROWTH = "growth"
    EXPLORATION = "exploration"
    REGRESSION = "regression"
    FLUCTUATION = "fluctuation"
    SUSTAINED = "sustained"
    REGULATION_EROSION = "regulation_erosion"


class FatigueTimescale(Enum):
    """
    Two-timescale fatigue model from Muller et al. (2021).

    Recoverable fatigue restores with rest. Unrecoverable fatigue
    accumulates with sustained work and requires structural change.
    """

    ACUTE = "acute"
    CHRONIC = "chronic"
    MIXED = "mixed"


# Growth hierarchy: ordered by number of active domains (sat >= 5.5)
# Level 0: no domains active
# Level 1: one domain active
# Level 2: two domains active
# Level 3: all three active
ARCHETYPE_LEVELS = {
    "Seeker": 0,
    "Pioneer": 1,
    "Anchor": 1,
    "Artisan": 1,
    "Captain": 2,
    "Architect": 2,
    "Mentor": 2,
    "Integrator": 3,
}

# Which domains are active for each archetype
ARCHETYPE_DOMAINS = {
    "Seeker": set(),
    "Pioneer": {"ambition"},
    "Anchor": {"belonging"},
    "Artisan": {"craft"},
    "Captain": {"ambition", "belonging"},
    "Architect": {"ambition", "craft"},
    "Mentor": {"belonging", "craft"},
    "Integrator": {"ambition", "belonging", "craft"},
}


def classify_transition(
    previous_type: str,
    current_type: str,
    posterior_confidence: float = 1.0,
    weeks_elapsed: int = 2,
) -> TransitionType:
    """
    Classify an archetype transition.

    Reference: abc-assessment-spec Section 5

    Args:
        previous_type: Previous archetype name.
        current_type: Current archetype name.
        posterior_confidence: Bayesian posterior confidence for the
            current classification (0-1). From BayesianScorer.
        weeks_elapsed: Weeks between measurements.

    Returns:
        TransitionType enum value.

    Rules:
        - Sustained: same type held (no transition)
        - Fluctuation: confidence below threshold for the time window
        - Growth: level increases (more domains active)
        - Exploration: same level, different archetype
        - Regression: level decreases (fewer domains active)
    """
    if previous_type not in ARCHETYPE_LEVELS:
        raise ValueError(f"Unknown archetype: {previous_type}")
    if current_type not in ARCHETYPE_LEVELS:
        raise ValueError(f"Unknown archetype: {current_type}")

    if previous_type == current_type:
        return TransitionType.SUSTAINED

    threshold = _confidence_threshold_for_window(weeks_elapsed)
    if posterior_confidence < threshold:
        return TransitionType.FLUCTUATION

    prev_level = ARCHETYPE_LEVELS[previous_type]
    curr_level = ARCHETYPE_LEVELS[current_type]

    if curr_level > prev_level:
        return TransitionType.GROWTH
    elif curr_level < prev_level:
        return TransitionType.REGRESSION
    else:
        return TransitionType.EXPLORATION


def _confidence_threshold_for_window(weeks_elapsed: int) -> float:
    """
    Shorter windows require higher confidence to report a transition.

    Reference: abc-assessment-spec Section 5

    Fernet et al. (2020) showed 4-month stability in motivation profiles.
    A 2-week type change is more likely noise than signal. An 8-week
    change is more likely real.

    Args:
        weeks_elapsed: Weeks between the two measurements.

    Returns:
        Confidence threshold (0-1).
    """
    if weeks_elapsed <= 4:
        return 0.75
    elif weeks_elapsed <= 8:
        return 0.65
    else:
        return 0.60


def classify_fatigue_timescale(
    frustration_history: list[float],
    window_short: int = 2,
    window_long: int = 6,
    spike_threshold: float = 1.5,
    slope_threshold: float = 0.3,
) -> FatigueTimescale:
    """
    Classify frustration as acute, chronic, or mixed.

    Reference: abc-assessment-spec Section 5

    Acute fatigue is a single spike (likely recoverable with rest or
    schedule change). Chronic fatigue is a sustained trend (requires
    structural change in need satisfaction).

    Based on Muller et al. (2021): two hidden fatigue states operate
    on different timescales. One is recoverable; the other accumulates.

    Args:
        frustration_history: List of frustration scores (0-10) in
            chronological order, most recent last.
        window_short: Number of recent measurements for spike detection.
        window_long: Number of measurements for trend detection.
        spike_threshold: Minimum score increase to count as a spike.
        slope_threshold: Minimum slope (per measurement) for a trend.

    Returns:
        FatigueTimescale enum value.
    """
    if len(frustration_history) < 3:
        return FatigueTimescale.ACUTE

    recent = frustration_history[-window_short:]
    has_spike = False
    if len(recent) >= 2:
        change = recent[-1] - recent[0]
        has_spike = change >= spike_threshold

    history = frustration_history[-window_long:]
    has_trend = False
    if len(history) >= 3:
        slope = _compute_slope(history)
        has_trend = slope >= slope_threshold

    if has_spike and has_trend:
        return FatigueTimescale.MIXED
    elif has_trend:
        return FatigueTimescale.CHRONIC
    else:
        return FatigueTimescale.ACUTE


def _compute_slope(values: list[float]) -> float:
    """
    Compute OLS slope for a sequence of values.

    Reference: abc-assessment-spec Section 5

    Args:
        values: List of float values in chronological order.

    Returns:
        Slope (change per measurement period).
    """
    n = len(values)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = sum(values) / n

    numerator = 0.0
    denominator = 0.0
    for i, y in enumerate(values):
        x_diff = i - x_mean
        numerator += x_diff * (y - y_mean)
        denominator += x_diff * x_diff

    if denominator == 0:
        return 0.0

    return numerator / denominator


def get_domains_gained(previous_type: str, current_type: str) -> set[str]:
    """
    Return the set of domains that became active in a transition.

    Reference: abc-assessment-spec Section 5

    Args:
        previous_type: Previous archetype name.
        current_type: Current archetype name.

    Returns:
        Set of domain names that are active in current but not previous.
    """
    prev = ARCHETYPE_DOMAINS.get(previous_type, set())
    curr = ARCHETYPE_DOMAINS.get(current_type, set())
    return curr - prev


def get_domains_lost(previous_type: str, current_type: str) -> set[str]:
    """
    Return the set of domains that became inactive in a transition.

    Reference: abc-assessment-spec Section 5

    Args:
        previous_type: Previous archetype name.
        current_type: Current archetype name.

    Returns:
        Set of domain names that were active in previous but not current.
    """
    prev = ARCHETYPE_DOMAINS.get(previous_type, set())
    curr = ARCHETYPE_DOMAINS.get(current_type, set())
    return prev - curr


class TransitionTracker:
    """
    Tracks an athlete's archetype history and classifies transitions.

    Maintains the full history of archetypes, posterior confidences,
    and transition classifications. Supports querying growth trajectory,
    sustained periods, and transition frequency.
    """

    def __init__(self):
        """Initialize an empty transition history.

        Reference: abc-assessment-spec Section 5
        """
        self.history: list[dict] = []
        # Aligned with history[]: one entry per recorded measurement.
        # None when no regulatory profile was supplied for that record.
        self.regulatory_profiles: list[RegulatoryProfile | None] = []

    def record(
        self,
        type_name: str,
        posterior_confidence: float = 1.0,
        weeks_since_last: int = 2,
        frustration_scores: dict[str, float] | None = None,  # noqa: ARG002 (reserved for fatigue timescale)
        regulatory_profile: "RegulatoryProfile | None" = None,
    ) -> dict:
        """
        Record a new measurement and classify the transition.

        Reference: abc-assessment-spec Section 5
        Reference: improvement-plan-personalization-engine.md Section 16.1

        Args:
            type_name: Current archetype name.
            posterior_confidence: Bayesian posterior confidence (0-1).
            weeks_since_last: Weeks since the previous measurement.
            frustration_scores: Optional dict with domain frustration
                scores for fatigue timescale classification.
            regulatory_profile: Optional RegulatoryProfile for this
                measurement. Enables regulation-erosion detection across
                the accumulating history.

        Returns:
            Dict with transition classification and metadata. When
            regulatory profiles are supplied, the entry also carries
            `regulation_erosion_events`, a list of affected domains.
        """
        entry: dict = {
            "type_name": type_name,
            "posterior_confidence": posterior_confidence,
            "measurement_number": len(self.history) + 1,
        }

        if len(self.history) == 0:
            entry["transition"] = None
            entry["transition_type"] = None
        else:
            previous = self.history[-1]
            transition = classify_transition(
                previous_type=previous["type_name"],
                current_type=type_name,
                posterior_confidence=posterior_confidence,
                weeks_elapsed=weeks_since_last,
            )
            entry["transition"] = {
                "from": previous["type_name"],
                "to": type_name,
                "type": transition.value,
                "domains_gained": sorted(get_domains_gained(previous["type_name"], type_name)),
                "domains_lost": sorted(get_domains_lost(previous["type_name"], type_name)),
            }
            entry["transition_type"] = transition.value

        self.regulatory_profiles.append(regulatory_profile)

        # Regulation erosion runs across the full regulatory history.
        # Imported lazily so the module has no hard dependency when
        # regulatory profiles are never supplied.
        erosion_domains: list[str] = []
        computable = [p for p in self.regulatory_profiles if p is not None]
        if len(computable) >= 2:
            from src.python_scoring.regulation_erosion import detect_regulation_erosion

            events = detect_regulation_erosion(computable)
            erosion_domains = [e.domain for e in events]
        entry["regulation_erosion_events"] = erosion_domains

        self.history.append(entry)
        return entry

    def get_sustained_count(self) -> int:
        """
        Return how many consecutive measurements the current type
        has been held, including the current one.

        Reference: abc-assessment-spec Section 5

        A single measurement counts as 1. Two sustained measurements
        of the same type count as 2. A transition resets to 1.
        """
        if not self.history:
            return 0

        current_type = self.history[-1]["type_name"]
        count = 0
        for entry in reversed(self.history):
            if entry["type_name"] == current_type:
                count += 1
            else:
                break
        return count

    def get_growth_trajectory(self) -> list[int]:
        """
        Return the sequence of archetype levels over time.

        Reference: abc-assessment-spec Section 5

        Each entry is the growth level (0-3) for that measurement.
        """
        return [ARCHETYPE_LEVELS.get(entry["type_name"], 0) for entry in self.history]

    def get_transition_counts(self) -> dict[str, int]:
        """Return counts of each transition type.

        Reference: abc-assessment-spec Section 5
        """
        counts = {t.value: 0 for t in TransitionType}
        for entry in self.history:
            if entry["transition_type"] is not None:
                tt = entry["transition_type"]
                if tt in counts:
                    counts[tt] += 1
        return counts

    def get_most_common_type(self) -> str | None:
        """Return the archetype that appears most frequently.

        Reference: abc-assessment-spec Section 5
        """
        if not self.history:
            return None
        type_counts: dict[str, int] = {}
        for entry in self.history:
            name = entry["type_name"]
            type_counts[name] = type_counts.get(name, 0) + 1
        return max(type_counts, key=type_counts.get)

    def get_current_type(self) -> str | None:
        """Return the most recent archetype.

        Reference: abc-assessment-spec Section 5
        """
        if not self.history:
            return None
        return self.history[-1]["type_name"]

    def get_summary(self) -> dict:
        """
        Return a comprehensive summary of the athlete's trajectory.

        Reference: abc-assessment-spec Section 5

        Returns:
            Dict with: current_type, most_common_type, measurement_count,
            sustained_count, growth_trajectory, transition_counts,
            current_level, highest_level_reached.
        """
        if not self.history:
            return {
                "current_type": None,
                "most_common_type": None,
                "measurement_count": 0,
                "sustained_count": 0,
                "growth_trajectory": [],
                "transition_counts": {t.value: 0 for t in TransitionType},
                "current_level": None,
                "highest_level_reached": None,
            }

        trajectory = self.get_growth_trajectory()
        latest_erosion = self.history[-1].get("regulation_erosion_events", [])
        return {
            "current_type": self.get_current_type(),
            "most_common_type": self.get_most_common_type(),
            "measurement_count": len(self.history),
            "sustained_count": self.get_sustained_count(),
            "growth_trajectory": trajectory,
            "transition_counts": self.get_transition_counts(),
            "current_level": trajectory[-1],
            "highest_level_reached": max(trajectory),
            "latest_regulation_erosion_domains": latest_erosion,
        }
