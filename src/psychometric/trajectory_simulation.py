"""Trajectory simulation for ABC Assessment.

Generates longitudinal synthetic data with five trajectory types and
associated burnout transition events. Models the Vulnerable-to-Distressed
cascade where frustration rises before satisfaction drops.

Reference: abc-assessment-spec Section 11.7 (trajectory types)
Reference: Vansteenkiste & Ryan (2013), Vulnerable state as burnout precursor

Status: SYNTHETIC. All trajectory patterns are simulated, not empirically derived.
"""

import numpy as np

# Trajectory type proportions (from spec Section 11.7)
TRAJECTORY_PROPORTIONS = {
    "stable": 0.40,
    "gradual_decline": 0.20,
    "gradual_rise": 0.20,
    "acute_event": 0.10,
    "volatile": 0.10,
}

# Burnout threshold: score below which burnout is triggered (on 0-10 scale)
BURNOUT_SCORE_THRESHOLD = 3.5


def simulate_burnout_trajectories(
    n_persons: int = 500,
    n_timepoints: int = 10,
    base_score: float = 5.5,
    noise_sd: float = 0.4,
    seed: int = 42,
) -> dict:
    """Generate longitudinal trajectories with burnout transition events.

    Reference: abc-assessment-spec Section 11.7

    Five trajectory types:
    - Stable (40%): scores fluctuate around baseline with noise
    - Gradual decline (20%): scores decline linearly over time
    - Gradual rise (20%): scores increase linearly over time
    - Acute event (10%): scores drop sharply at a random timepoint
    - Volatile (10%): scores oscillate with large amplitude

    Burnout onset is triggered when a declining or acute trajectory's
    score falls below BURNOUT_SCORE_THRESHOLD.

    Args:
        n_persons: number of simulated athletes
        n_timepoints: number of measurement occasions
        base_score: starting score level (0-10 scale)
        noise_sd: measurement noise SD per timepoint
        seed: random seed for reproducibility

    Returns:
        dict with keys:
            scores: shape (n_persons, n_timepoints), score trajectories
            labels: list of trajectory type labels per person
            burnout_onset: list of first burnout timepoint per person (-1 if none)
    """
    rng = np.random.default_rng(seed)

    # Assign trajectory types
    types = list(TRAJECTORY_PROPORTIONS.keys())
    probs = list(TRAJECTORY_PROPORTIONS.values())
    labels = list(rng.choice(types, size=n_persons, p=probs))

    scores = np.zeros((n_persons, n_timepoints))
    burnout_onset = [-1] * n_persons

    for p in range(n_persons):
        ttype = labels[p]
        noise = rng.normal(0, noise_sd, n_timepoints)

        if ttype == "stable":
            person_base = base_score + rng.normal(0, 1.0)
            scores[p] = person_base + noise

        elif ttype == "gradual_decline":
            person_base = base_score + rng.uniform(0.5, 2.0)
            decline_rate = rng.uniform(0.2, 0.5)
            for t in range(n_timepoints):
                scores[p, t] = person_base - decline_rate * t + noise[t]

        elif ttype == "gradual_rise":
            person_base = base_score + rng.normal(-1.0, 0.5)
            rise_rate = rng.uniform(0.2, 0.5)
            for t in range(n_timepoints):
                scores[p, t] = person_base + rise_rate * t + noise[t]

        elif ttype == "acute_event":
            person_base = base_score + rng.uniform(0.5, 1.5)
            event_time = rng.integers(3, n_timepoints - 2)
            drop_magnitude = rng.uniform(2.5, 4.0)
            for t in range(n_timepoints):
                if t < event_time:
                    scores[p, t] = person_base + noise[t]
                else:
                    scores[p, t] = person_base - drop_magnitude + noise[t]

        elif ttype == "volatile":
            person_base = base_score + rng.normal(0, 0.5)
            amplitude = rng.uniform(1.5, 3.0)
            for t in range(n_timepoints):
                scores[p, t] = person_base + amplitude * np.sin(t * 1.5) + noise[t]

        # Clip to [0, 10]
        scores[p] = np.clip(scores[p], 0, 10)

        # Detect burnout onset (first time score drops below threshold)
        if ttype in ("gradual_decline", "acute_event", "volatile"):
            for t in range(n_timepoints):
                if scores[p, t] < BURNOUT_SCORE_THRESHOLD:
                    burnout_onset[p] = t
                    break

    return {
        "scores": scores,
        "labels": labels,
        "burnout_onset": burnout_onset,
    }


def simulate_vulnerable_to_distressed_cascade(
    n_persons: int = 200,
    n_timepoints: int = 10,
    mean_lag: int = 2,
    initial_sat: float = 7.5,
    initial_frust: float = 5.0,
    sat_decline_rate: float = 0.3,
    frust_rise_rate: float = 0.25,
    noise_sd: float = 0.4,
    seed: int = 42,
) -> dict:
    """Simulate the Vulnerable-to-Distressed cascade in continuous score space.

    Reference: Vansteenkiste & Ryan (2013)

    Models the theorised pathway where frustration rises first (the cost
    accumulates) and satisfaction drops later (performance breaks down).
    The lag between frustration rise and satisfaction drop is the leading
    indicator window: the time during which the psychometric signal
    precedes the physiological transition.

    This operates in continuous score space, not discrete domain states,
    per Phase 2b's finding that state classifications are too unstable
    for reliable transition detection.

    Args:
        n_persons: number of athletes in the cascade
        n_timepoints: number of measurement occasions
        mean_lag: average number of timepoints between frustration rise
                  onset and satisfaction drop onset
        initial_sat: starting satisfaction level (Vulnerable = high)
        initial_frust: starting frustration level (Vulnerable = moderate-high)
        sat_decline_rate: rate of satisfaction decline per timepoint
        frust_rise_rate: rate of frustration rise per timepoint
        noise_sd: measurement noise per timepoint
        seed: random seed

    Returns:
        dict with keys:
            satisfaction: shape (n_persons, n_timepoints)
            frustration: shape (n_persons, n_timepoints)
            cascade_lag: per-person lag between frustration rise and sat drop
    """
    rng = np.random.default_rng(seed)

    satisfaction = np.zeros((n_persons, n_timepoints))
    frustration = np.zeros((n_persons, n_timepoints))
    cascade_lag = np.zeros(n_persons, dtype=int)

    for p in range(n_persons):
        # Person-specific parameters
        person_lag = max(0, int(rng.normal(mean_lag, 1.0)))
        cascade_lag[p] = person_lag

        # Frustration starts rising at timepoint 0
        frust_onset = 0
        # Satisfaction starts declining after the lag
        sat_onset = frust_onset + person_lag

        person_sat = initial_sat + rng.normal(0, 0.5)
        person_frust = initial_frust + rng.normal(0, 0.5)
        person_sat_rate = sat_decline_rate + rng.normal(0, 0.05)
        person_frust_rate = frust_rise_rate + rng.normal(0, 0.05)

        for t in range(n_timepoints):
            # Frustration rises from onset
            frust_change = person_frust_rate * (t - frust_onset) if t >= frust_onset else 0

            # Satisfaction drops after lag
            sat_change = -person_sat_rate * (t - sat_onset) if t >= sat_onset else 0

            frustration[p, t] = person_frust + frust_change + rng.normal(0, noise_sd)
            satisfaction[p, t] = person_sat + sat_change + rng.normal(0, noise_sd)

    # Clip to [0, 10]
    satisfaction = np.clip(satisfaction, 0, 10)
    frustration = np.clip(frustration, 0, 10)

    return {
        "satisfaction": satisfaction,
        "frustration": frustration,
        "cascade_lag": cascade_lag,
    }
