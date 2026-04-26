"""Latent Transition Analysis (LTA) for ABC Assessment.

Simplified LTA per the implementation plan: stack timepoints, fit LPA on
the pooled data so class definitions are held constant across waves, then
assign per timepoint and compute empirical transition matrices.

Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
Reference: howard-2024-implementation-plan.md V2-B WI-5

Limitation. This is NOT full Mplus-style LTA. Mplus estimates transition
probabilities inside the joint likelihood. The simplification fits LPA on
stacked-across-time data and treats per-timepoint posterior assignments as
a Markov chain. This loses the joint estimation benefits but preserves the
descriptive transition matrix that the cascade lead-time analysis needs.

Position. Per the plan, LTA is a person-centered complement to the
continuous-theta cascade in `leading_indicator_model.py`, not a replacement.
"""

from __future__ import annotations

import numpy as np
from sklearn.mixture import GaussianMixture


def estimate_transition_matrix(
    class_assignments: np.ndarray,
    n_classes: int,
) -> np.ndarray:
    """Empirical transition matrix from class assignments at consecutive timepoints.

    Reference: howard-2024-implementation-plan.md V2-B WI-5
    Reference: Norris (1998), Markov Chains, empirical transition estimator

    For each consecutive pair (t, t+1), count transitions from class i to
    class j and row-normalize. When `class_assignments` is (n, T), the
    matrix aggregates over all T-1 consecutive pairs.

    Rows with zero outflow are filled with a uniform 1/K distribution so
    the returned matrix is always row-stochastic.

    Args:
        class_assignments: (n, T) integer labels per person per timepoint.
        n_classes: K, the number of distinct classes.

    Returns:
        K x K row-stochastic transition matrix.
    """
    if class_assignments.ndim != 2:
        raise ValueError("class_assignments must be 2-D (n, T).")
    n, t = class_assignments.shape
    counts = np.zeros((n_classes, n_classes), dtype=float)
    for tp in range(t - 1):
        src = class_assignments[:, tp]
        dst = class_assignments[:, tp + 1]
        for s, d in zip(src, dst, strict=False):
            if 0 <= s < n_classes and 0 <= d < n_classes:
                counts[s, d] += 1.0

    row_sums = counts.sum(axis=1, keepdims=True)
    matrix = np.zeros_like(counts)
    for i in range(n_classes):
        if row_sums[i, 0] > 0:
            matrix[i] = counts[i] / row_sums[i, 0]
        else:
            matrix[i] = np.full(n_classes, 1.0 / n_classes)
    return matrix


def fit_lta(
    scores_over_time: np.ndarray,
    n_classes: int,
    random_state: int = 42,
) -> dict:
    """Simplified LTA: fit LPA on stacked-across-time data, assign per timepoint.

    Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
    Reference: howard-2024-implementation-plan.md V2-B WI-5

    Args:
        scores_over_time: (n, T, p) scores per person per timepoint per indicator.
        n_classes: number of latent classes (held constant across timepoints).
        random_state: seed for reproducibility (Rule 7).

    Returns:
        dict with keys:
          class_assignments_per_timepoint: (n, T) integer labels
          transition_matrices: list of T-1 (K, K) row-stochastic matrices
          diagonal_means: (T-1,) average diagonal per transition matrix
          class_proportions_per_timepoint: (T, K) class shares per wave
          gmm: fitted GaussianMixture (for downstream inspection)
    """
    if scores_over_time.ndim != 3:
        raise ValueError("scores_over_time must be 3-D (n, T, p).")
    n, t, p = scores_over_time.shape

    # Stack: (n*T, p) so a single GMM defines classes across waves.
    stacked = scores_over_time.reshape(n * t, p)
    gmm = GaussianMixture(
        n_components=n_classes,
        covariance_type="diag",
        random_state=random_state,
        n_init=10,
        reg_covar=1e-4,
    )
    gmm.fit(stacked)

    # Assign per timepoint
    assignments = np.zeros((n, t), dtype=int)
    proportions = np.zeros((t, n_classes), dtype=float)
    for tp in range(t):
        assignments[:, tp] = gmm.predict(scores_over_time[:, tp, :])
        for k in range(n_classes):
            proportions[tp, k] = float(np.mean(assignments[:, tp] == k))

    # One transition matrix per consecutive wave-pair
    transition_matrices: list[np.ndarray] = []
    for tp in range(t - 1):
        pair = assignments[:, tp : tp + 2]
        mat = estimate_transition_matrix(pair, n_classes=n_classes)
        transition_matrices.append(mat)

    diagonal_means = np.array([float(np.mean(np.diag(m))) for m in transition_matrices])

    return {
        "class_assignments_per_timepoint": assignments,
        "transition_matrices": transition_matrices,
        "diagonal_means": diagonal_means,
        "class_proportions_per_timepoint": proportions,
        "gmm": gmm,
    }


def cascade_lead_time(
    transitions: list[np.ndarray] | dict,
    frustration_class: int,
    satisfaction_class: int,
) -> dict:
    """Estimate how many timepoints earlier high-frustration class membership
    precedes low-satisfaction class membership.

    Reference: howard-2024-implementation-plan.md V2-B WI-5

    Used as person-centered confirmation of the continuous cascade in
    `leading_indicator_model.py`.

    Args:
        transitions: either an LTA result dict (containing
            'class_assignments_per_timepoint' and 'transition_matrices') or
            a list of transition matrices accompanied by trajectories via
            the dict form. The matrix-only form returns None lead time
            because transition matrices alone do not encode person-level
            ordering.
        frustration_class: integer class index for the "high-frustration" profile.
        satisfaction_class: integer class index for the "low-satisfaction" profile.

    Returns:
        dict with mean_lead_timepoints (float or None),
        n_persons_with_pattern (int), ci_95 (lower, upper) bootstrap CI.
    """
    # Accept either the LTA dict form or a bare list (matrix-only -> no info).
    if isinstance(transitions, dict):
        trajectories = transitions.get("class_assignments_per_timepoint")
    else:
        trajectories = None

    if trajectories is None:
        return {
            "mean_lead_timepoints": None,
            "n_persons_with_pattern": 0,
            "ci_95": (None, None),
            "note": "Trajectory data required; transition matrices alone do not encode lead time.",
        }

    trajectories = np.asarray(trajectories)
    n, t = trajectories.shape

    leads: list[int] = []
    for i in range(n):
        traj = trajectories[i]
        # First timepoint at which the person enters frust class
        f_hits = np.where(traj == frustration_class)[0]
        if f_hits.size == 0:
            continue
        first_f = int(f_hits[0])
        # First timepoint AFTER first_f at which the person enters sat class
        s_hits = np.where(traj[first_f + 1 :] == satisfaction_class)[0]
        if s_hits.size == 0:
            continue
        first_s = int(s_hits[0]) + first_f + 1
        lead = first_s - first_f
        leads.append(lead)

    n_with_pattern = len(leads)
    if n_with_pattern == 0:
        return {
            "mean_lead_timepoints": None,
            "n_persons_with_pattern": 0,
            "ci_95": (None, None),
        }

    arr = np.asarray(leads, dtype=float)
    mean_lead = float(arr.mean())

    # Bootstrap 95% CI (1000 reps) seeded for reproducibility (Rule 7)
    rng = np.random.default_rng(42)
    n_boot = 1000
    boot_means = np.empty(n_boot)
    for b in range(n_boot):
        sample = rng.choice(arr, size=arr.size, replace=True)
        boot_means[b] = sample.mean()
    lower = float(np.percentile(boot_means, 2.5))
    upper = float(np.percentile(boot_means, 97.5))

    return {
        "mean_lead_timepoints": mean_lead,
        "n_persons_with_pattern": n_with_pattern,
        "ci_95": (lower, upper),
    }
