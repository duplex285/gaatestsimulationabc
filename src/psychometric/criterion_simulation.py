"""Criterion simulation for ABC Assessment.

Generates simulated external criterion scores (e.g., burnout inventory,
well-being scale) correlated with ABC subscale scores. Used to demonstrate
empirical threshold derivation methods before real criterion data is available.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
Reference: abc-assessment-spec Section 11.7 (trajectory types)

Status: SYNTHETIC. All outputs must carry data_source: synthetic flag.
"""

import numpy as np


def simulate_criterion_scores(
    abc_scores: np.ndarray,
    target_correlation: float,
    criterion_mean: float = 0.0,
    criterion_sd: float = 1.0,
    seed: int = 42,
) -> np.ndarray:
    """Generate criterion scores correlated with ABC subscale scores.

    Reference: abc-assessment-spec Section 11.1

    Uses the Cholesky method: criterion = r * standardized_abc + sqrt(1-r^2) * noise,
    then rescales to the target mean and SD.

    Args:
        abc_scores: array of ABC scores (any subscale), shape (n,)
        target_correlation: desired Pearson correlation with abc_scores
        criterion_mean: target mean of the criterion scores
        criterion_sd: target SD of the criterion scores
        seed: random seed for reproducibility

    Returns:
        Array of criterion scores, shape (n,)
    """
    # Use a derived seed that avoids collision with the seed used to
    # generate abc_scores (which would make noise = abc_scores, r = 1.0)
    rng = np.random.default_rng(seed + 2_000_000)
    n = len(abc_scores)

    # Standardize ABC scores
    abc_std = np.std(abc_scores)
    abc_z = (abc_scores - np.mean(abc_scores)) / max(abc_std, 1e-10)

    # Cholesky decomposition for target correlation
    # criterion_z = r * abc_z + sqrt(1 - r^2) * noise
    # This produces a variable with correlation r to abc_z
    r = target_correlation
    noise = rng.standard_normal(n)
    criterion_z = r * abc_z + np.sqrt(max(1 - r**2, 0)) * noise

    # Rescale to target mean and SD (without re-standardizing, which
    # would destroy the correlation structure)
    criterion = criterion_z * criterion_sd + criterion_mean

    return criterion


def simulate_criterion_trajectories(
    abc_trajectories: np.ndarray,
    target_correlation: float,
    transition_threshold: float = 1.5,
    criterion_mean: float = 0.0,
    criterion_sd: float = 1.0,
    seed: int = 42,
) -> dict:
    """Generate longitudinal criterion data with burnout transition events.

    Reference: abc-assessment-spec Section 11.7 (trajectory types)

    For each person at each timepoint, generates a criterion score correlated
    with the ABC score at that timepoint. A transition event occurs when the
    criterion first exceeds the transition threshold.

    Args:
        abc_trajectories: ABC scores over time, shape (n_persons, n_timepoints)
        target_correlation: desired correlation between ABC and criterion at each timepoint
        transition_threshold: criterion value above which a transition is flagged
        criterion_mean: target mean of criterion scores
        criterion_sd: target SD of criterion scores
        seed: random seed for reproducibility

    Returns:
        dict with keys:
            criterion: shape (n_persons, n_timepoints), simulated criterion scores
            transitions: shape (n_persons, n_timepoints), boolean transition markers
            first_transition: shape (n_persons,), timepoint of first transition (-1 if none)
    """
    np.random.default_rng(seed)
    n_persons, n_timepoints = abc_trajectories.shape

    criterion = np.zeros((n_persons, n_timepoints))
    transitions = np.zeros((n_persons, n_timepoints), dtype=bool)
    first_transition = np.full(n_persons, -1, dtype=int)

    for t in range(n_timepoints):
        # Generate correlated criterion at each timepoint
        # Use a unique sub-seed per timepoint for independence across time
        criterion[:, t] = simulate_criterion_scores(
            abc_trajectories[:, t],
            target_correlation=target_correlation,
            criterion_mean=criterion_mean,
            criterion_sd=criterion_sd,
            seed=seed + t,
        )

    # Detect transition events
    for p in range(n_persons):
        for t in range(n_timepoints):
            if criterion[p, t] >= transition_threshold:
                transitions[p, t] = True
                if first_transition[p] == -1:
                    first_transition[p] = t

    return {
        "criterion": criterion,
        "transitions": transitions,
        "first_transition": first_transition,
    }
