"""
Coach Intelligence Layer for ABC Assessment.

Aggregates patterns across all athletes a coach has worked with.
Turns coaching experience into explicit, portable knowledge.

The coach's intelligence profile travels with them. When they join
a new team or switch sports, they bring their accumulated pattern
recognition. The system learns from each new context.

Key insight from Shen et al. (2015): burnout transmits through
relationships. A coach's state affects athlete motivation. This
module detects transmission signals when multiple athletes under
one coach show simultaneous frustration increases.

References:
    Shen, B., et al. (2015). British Journal of Educational Psychology,
        85, 519-532.
    Fernet, C., et al. (2020). European Journal of Work and
        Organizational Psychology, 29, 49-63.
"""

from __future__ import annotations

from collections import Counter


def compute_archetype_distribution(
    athlete_types: list[str],
) -> dict[str, dict]:
    """
    Compute archetype frequency distribution across athletes.

    Reference: abc-assessment-spec Section 6

    Args:
        athlete_types: List of archetype names (one per athlete,
            most recent classification).

    Returns:
        Dict with archetype counts, proportions, and total.
    """
    if not athlete_types:
        return {"counts": {}, "proportions": {}, "total": 0}

    counts = dict(Counter(athlete_types))
    total = len(athlete_types)
    proportions = {k: v / total for k, v in counts.items()}

    return {
        "counts": counts,
        "proportions": proportions,
        "total": total,
    }


def compute_frustration_recovery(
    athlete_frustration_histories: list[dict],
    recovery_threshold: float = 4.38,
    max_window: int = 4,
) -> dict[str, dict]:
    """
    Compute frustration recovery statistics across athletes.

    Reference: abc-assessment-spec Section 6

    For each domain, tracks how many athletes had elevated frustration
    and how many recovered within the measurement window.

    Args:
        athlete_frustration_histories: List of dicts, each with keys
            'domain' (str) and 'scores' (list[float] chronological).
        recovery_threshold: Frustration score below which an athlete
            is considered recovered.
        max_window: Maximum measurements to wait for recovery.

    Returns:
        Dict keyed by domain with recovery_rate, median_recovery_time,
        and count of athletes analyzed.
    """
    domain_stats: dict[str, list] = {}

    for history in athlete_frustration_histories:
        domain = history.get("domain", "unknown")
        scores = history.get("scores", [])

        if domain not in domain_stats:
            domain_stats[domain] = []

        episodes = _find_recovery_episodes(scores, recovery_threshold, max_window)
        domain_stats[domain].extend(episodes)

    results = {}
    for domain, episodes in domain_stats.items():
        if not episodes:
            results[domain] = {
                "recovery_rate": 0.0,
                "median_recovery_time": None,
                "episodes_analyzed": 0,
            }
            continue

        recovered = [e for e in episodes if e["recovered"]]
        recovery_rate = len(recovered) / len(episodes) if episodes else 0.0

        recovery_times = [e["time_to_recovery"] for e in recovered]
        median_time = None
        if recovery_times:
            sorted_times = sorted(recovery_times)
            mid = len(sorted_times) // 2
            if len(sorted_times) % 2 == 0:
                median_time = (sorted_times[mid - 1] + sorted_times[mid]) / 2
            else:
                median_time = sorted_times[mid]

        results[domain] = {
            "recovery_rate": recovery_rate,
            "median_recovery_time": median_time,
            "episodes_analyzed": len(episodes),
        }

    return results


def _find_recovery_episodes(
    scores: list[float],
    threshold: float,
    max_window: int,
) -> list[dict]:
    """
    Find episodes of elevated frustration and track recovery.

    Reference: abc-assessment-spec Section 6

    An episode starts when frustration crosses above the threshold
    and ends when it drops below, or when the window expires.
    """
    episodes = []
    i = 0
    while i < len(scores):
        if scores[i] >= threshold:
            onset = i
            recovered = False
            time_to_recovery = None

            for j in range(i + 1, min(i + max_window + 1, len(scores))):
                if scores[j] < threshold:
                    recovered = True
                    time_to_recovery = j - onset
                    i = j
                    break

            if not recovered:
                time_to_recovery = min(max_window, len(scores) - onset - 1)
                i = onset + 1

            episodes.append(
                {
                    "onset_index": onset,
                    "recovered": recovered,
                    "time_to_recovery": time_to_recovery,
                }
            )
        else:
            i += 1

    return episodes


def detect_transmission_signal(
    athlete_frustration_scores: list[dict],
    domain: str = "belonging",
    window: int = 1,
    min_affected: int = 3,
    rise_threshold: float = 1.0,
) -> dict | None:
    """
    Detect burnout transmission: multiple athletes showing simultaneous
    frustration increases under the same coach.

    Reference: abc-assessment-spec Section 6

    Based on Shen et al. (2015): teacher burnout transmits to student
    motivation through reduced autonomy support. The analog in sport:
    a coach's burnout may manifest as rising Belonging frustration
    across multiple athletes.

    Args:
        athlete_frustration_scores: List of dicts with keys 'athlete_id'
            (str) and 'scores' (list[float] chronological, most recent
            last). Each list should have at least window+1 entries.
        domain: Which domain to check (default: belonging).
        window: Number of measurement periods to compare (default: 1,
            meaning compare last measurement to the one before).
        min_affected: Minimum athletes showing increase to trigger
            the signal (default: 3).
        rise_threshold: Minimum score increase to count as a rise.

    Returns:
        None if no signal detected.
        Dict with affected_athletes, domain, proportion_affected,
        and narrative if signal detected.
    """
    affected = []

    for entry in athlete_frustration_scores:
        scores = entry.get("scores", [])
        if len(scores) < window + 1:
            continue

        recent = scores[-1]
        previous = scores[-(window + 1)]
        change = recent - previous

        if change >= rise_threshold:
            affected.append(
                {
                    "athlete_id": entry.get("athlete_id", "unknown"),
                    "change": change,
                    "current_score": recent,
                }
            )

    if len(affected) < min_affected:
        return None

    total_athletes = len(athlete_frustration_scores)
    proportion = len(affected) / total_athletes if total_athletes > 0 else 0.0

    return {
        "affected_athletes": affected,
        "domain": domain,
        "affected_count": len(affected),
        "total_athletes": total_athletes,
        "proportion_affected": proportion,
        "narrative": (
            f"{len(affected)} of your athletes' {domain} frustration "
            f"scores rose in the same measurement window. This pattern "
            f"sometimes reflects changes in the coaching environment "
            f"rather than individual athlete experiences."
        ),
    }


def compute_cross_sport_patterns(
    sport_data: dict[str, list[dict]],
) -> dict:
    """
    Compare archetype distributions and frustration patterns across
    different sports a coach has worked in.

    Reference: abc-assessment-spec Section 6

    Args:
        sport_data: Dict keyed by sport name, each value is a list of
            athlete dicts with keys 'type_name' (str), 'domain_states'
            (dict), and optionally 'frustration_signatures' (list).

    Returns:
        Dict with per-sport summaries and cross-sport comparisons.
    """
    if not sport_data:
        return {"sports": {}, "comparisons": {}}

    sport_summaries = {}
    for sport, athletes in sport_data.items():
        types = [a.get("type_name", "Unknown") for a in athletes]
        dist = compute_archetype_distribution(types)

        states = {}
        for a in athletes:
            for domain, state in a.get("domain_states", {}).items():
                if domain not in states:
                    states[domain] = Counter()
                states[domain][state] += 1

        sig_counts = Counter()
        for a in athletes:
            for sig in a.get("frustration_signatures", []):
                sig_counts[sig.get("label", "unknown")] += 1

        sport_summaries[sport] = {
            "athlete_count": len(athletes),
            "archetype_distribution": dist,
            "domain_state_counts": {d: dict(c) for d, c in states.items()},
            "frustration_signature_counts": dict(sig_counts),
        }

    # Cross-sport comparison: which archetypes appear in all sports
    all_types = set()
    for summary in sport_summaries.values():
        all_types.update(summary["archetype_distribution"]["counts"].keys())

    type_by_sport = {}
    for t in all_types:
        type_by_sport[t] = {
            sport: summary["archetype_distribution"]["proportions"].get(t, 0.0)
            for sport, summary in sport_summaries.items()
        }

    return {
        "sports": sport_summaries,
        "comparisons": {
            "archetype_by_sport": type_by_sport,
            "sports_coached": list(sport_data.keys()),
            "total_athletes": sum(s["athlete_count"] for s in sport_summaries.values()),
        },
    }


class CoachProfile:
    """
    Maintains a coach's accumulated intelligence across athletes,
    teams, and sports.

    The profile is portable: when a coach moves to a new team, their
    historical patterns travel with them.
    """

    def __init__(self, coach_id: str):
        """Initialize a coach profile.

        Reference: abc-assessment-spec Section 6
        """
        self.coach_id = coach_id
        self.athletes: list[dict] = []
        self.sport_history: dict[str, list[dict]] = {}
        self.interventions: list[dict] = []

    def add_athlete(
        self,
        athlete_id: str,
        type_name: str,
        domain_states: dict[str, str],
        frustration_signatures: list[dict] | None = None,
        sport: str = "unknown",
    ) -> None:
        """Record an athlete's current state.

        Reference: abc-assessment-spec Section 6
        """
        entry = {
            "athlete_id": athlete_id,
            "type_name": type_name,
            "domain_states": domain_states,
            "frustration_signatures": frustration_signatures or [],
            "sport": sport,
        }
        self.athletes.append(entry)

        if sport not in self.sport_history:
            self.sport_history[sport] = []
        self.sport_history[sport].append(entry)

    def log_intervention(
        self,
        athlete_id: str,
        domain: str,
        description: str,
        pre_score: float,
        post_score: float | None = None,
    ) -> None:
        """Log a coaching intervention for effectiveness tracking.

        Reference: abc-assessment-spec Section 6
        """
        self.interventions.append(
            {
                "athlete_id": athlete_id,
                "domain": domain,
                "description": description,
                "pre_score": pre_score,
                "post_score": post_score,
            }
        )

    def get_archetype_distribution(self) -> dict:
        """Distribution across all athletes ever coached.

        Reference: abc-assessment-spec Section 6
        """
        types = [a["type_name"] for a in self.athletes]
        return compute_archetype_distribution(types)

    def get_cross_sport_patterns(self) -> dict:
        """Compare patterns across sports.

        Reference: abc-assessment-spec Section 6
        """
        return compute_cross_sport_patterns(self.sport_history)

    def get_intervention_summary(self) -> dict:
        """
        Summarize intervention effectiveness.

        Reference: abc-assessment-spec Section 6

        Only includes interventions with both pre and post scores.
        """
        completed = [i for i in self.interventions if i["post_score"] is not None]

        if not completed:
            return {
                "total_interventions": len(self.interventions),
                "completed": 0,
                "mean_improvement": None,
            }

        improvements = [i["pre_score"] - i["post_score"] for i in completed]
        mean_improvement = sum(improvements) / len(improvements)

        return {
            "total_interventions": len(self.interventions),
            "completed": len(completed),
            "mean_improvement": mean_improvement,
            "improvements_by_domain": _group_by_domain(completed),
        }

    def get_summary(self) -> dict:
        """Comprehensive coach intelligence summary.

        Reference: abc-assessment-spec Section 6
        """
        return {
            "coach_id": self.coach_id,
            "total_athletes": len(self.athletes),
            "sports_coached": list(self.sport_history.keys()),
            "archetype_distribution": self.get_archetype_distribution(),
            "intervention_summary": self.get_intervention_summary(),
        }


def _group_by_domain(interventions: list[dict]) -> dict[str, dict]:
    """Group intervention improvements by domain.

    Reference: abc-assessment-spec Section 6
    """
    by_domain: dict[str, list[float]] = {}
    for i in interventions:
        domain = i["domain"]
        improvement = i["pre_score"] - i["post_score"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(improvement)

    result = {}
    for domain, improvements in by_domain.items():
        result[domain] = {
            "count": len(improvements),
            "mean_improvement": sum(improvements) / len(improvements),
        }
    return result
