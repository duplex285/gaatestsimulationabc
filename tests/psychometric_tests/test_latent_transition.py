"""Tests for latent transition analysis (LTA) module.

Reference: howard-2024-implementation-plan.md V2-B WI-5
Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
"""

import numpy as np

from src.psychometric.latent_transition import (
    cascade_lead_time,
    estimate_transition_matrix,
    fit_lta,
)


class TestEstimateTransitionMatrix:
    """Tests for estimate_transition_matrix."""

    def test_transition_matrix_rows_sum_to_one(self):
        """Each row sums to 1.0 within tolerance."""
        rng = np.random.default_rng(42)
        n, t = 200, 5
        assigns = rng.integers(0, 3, size=(n, t))
        mat = estimate_transition_matrix(assigns, n_classes=3)
        # Rows that are observed should sum to 1; rows with zero outflow get
        # uniform fallback (still sum to 1).
        assert np.allclose(mat.sum(axis=1), 1.0, atol=1e-9)

    def test_transition_matrix_diagonal_high_when_stable(self):
        """Mostly-stable assignments: mean diagonal > 0.80."""
        rng = np.random.default_rng(42)
        n, t = 300, 6
        assigns = np.tile(rng.integers(0, 3, size=(n, 1)), (1, t))
        # Inject 10% transitions
        flip_mask = rng.random((n, t)) < 0.10
        assigns = np.where(flip_mask, rng.integers(0, 3, size=(n, t)), assigns)
        mat = estimate_transition_matrix(assigns, n_classes=3)
        assert np.mean(np.diag(mat)) > 0.80

    def test_returns_square_matrix(self):
        """Output is K x K."""
        rng = np.random.default_rng(42)
        assigns = rng.integers(0, 4, size=(50, 3))
        mat = estimate_transition_matrix(assigns, n_classes=4)
        assert mat.shape == (4, 4)


class TestFitLTA:
    """Tests for fit_lta: simplified stacked-LPA latent transition analysis."""

    def test_lta_returns_n_minus_1_matrices(self):
        """For T timepoints, returns T-1 transition matrices."""
        rng = np.random.default_rng(42)
        n, t, p = 150, 4, 3
        scores = rng.standard_normal((n, t, p))
        result = fit_lta(scores, n_classes=2, random_state=42)
        assert len(result["transition_matrices"]) == t - 1

    def test_lta_recovers_known_transitions(self):
        """Synthetic two-state Markov: recovered diagonals within 0.10 of truth."""
        rng = np.random.default_rng(42)
        n, t, p = 600, 5, 3
        # Two well-separated centroids, very stable transitions
        centroids = np.array(
            [
                [-2.5, -2.5, -2.5],
                [2.5, 2.5, 2.5],
            ]
        )
        # Each person starts in a state, then with P(stay) = 0.85 keeps it.
        true_stay = 0.85
        scores = np.zeros((n, t, p))
        states = np.zeros((n, t), dtype=int)
        states[:, 0] = rng.integers(0, 2, size=n)
        for tp in range(1, t):
            keep = rng.random(n) < true_stay
            states[:, tp] = np.where(keep, states[:, tp - 1], 1 - states[:, tp - 1])
        for tp in range(t):
            for k in range(2):
                idx = states[:, tp] == k
                scores[idx, tp, :] = centroids[k] + rng.standard_normal((idx.sum(), p)) * 0.4

        result = fit_lta(scores, n_classes=2, random_state=42)
        # Average diagonal across all transition matrices should approximate true_stay.
        diag_means = result["diagonal_means"]
        assert np.all(np.abs(diag_means - true_stay) < 0.10), diag_means

    def test_returns_class_assignments_per_timepoint(self):
        """Class assignments matrix is (n, T)."""
        rng = np.random.default_rng(42)
        n, t, p = 100, 3, 2
        scores = rng.standard_normal((n, t, p))
        result = fit_lta(scores, n_classes=2, random_state=42)
        assert result["class_assignments_per_timepoint"].shape == (n, t)

    def test_returns_class_proportions_per_timepoint(self):
        """Proportions matrix is (T, K) and rows sum to 1."""
        rng = np.random.default_rng(42)
        n, t, p = 80, 4, 2
        scores = rng.standard_normal((n, t, p))
        result = fit_lta(scores, n_classes=3, random_state=42)
        props = result["class_proportions_per_timepoint"]
        assert props.shape == (t, 3)
        assert np.allclose(props.sum(axis=1), 1.0, atol=1e-9)


class TestCascadeLeadTime:
    """Tests for cascade_lead_time."""

    def test_cascade_lead_time_detects_known_pattern(self):
        """Synthetic trajectory: class A precedes class B by 2 steps -> mean_lead in [1.5, 2.5]."""
        rng = np.random.default_rng(42)
        n_persons = 100
        t = 8
        frust_class = 0
        sat_class = 1
        # Construct (T-1) transition matrices that are uniform; the lead-time
        # logic operates on per-person trajectories, not on the matrices.
        # cascade_lead_time interface accepts a list of class assignment trajectories.
        # We'll pass per-person trajectories via the transitions argument,
        # following the spec: each transition matrix is K x K.
        # NOTE: per the docstring, transitions is the LTA output list of matrices
        # plus an internal trajectory list. Interface uses trajectories stored
        # in the result dict's "class_assignments_per_timepoint" to compute lead.
        # We'll simulate:
        trajectories = np.full((n_persons, t), -1, dtype=int)
        for i in range(n_persons):
            # Person enters frust at random timepoint, then sat 2 steps later.
            f_t = rng.integers(0, t - 3)
            trajectories[i, :f_t] = 2  # other class
            trajectories[i, f_t : f_t + 2] = frust_class
            trajectories[i, f_t + 2 :] = sat_class

        # Wrap in the dict format that cascade_lead_time expects:
        # transitions arg is a list of matrices; we also stash the trajectories.
        # Per the API: estimate matrices then call lead-time.
        n_classes = 3
        matrices = []
        for tp in range(t - 1):
            pair = np.column_stack([trajectories[:, tp], trajectories[:, tp + 1]])
            mat = np.zeros((n_classes, n_classes))
            for src, dst in pair:
                mat[src, dst] += 1
            row_sums = mat.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            matrices.append(mat / row_sums)

        # The implementation will need trajectories. We pass them via a dict.
        result = cascade_lead_time(
            {"transition_matrices": matrices, "class_assignments_per_timepoint": trajectories},
            frustration_class=frust_class,
            satisfaction_class=sat_class,
        )
        assert result["mean_lead_timepoints"] is not None
        assert 1.5 <= result["mean_lead_timepoints"] <= 2.5, result
        assert result["n_persons_with_pattern"] > 0

    def test_cascade_lead_time_returns_none_when_no_pattern(self):
        """When no person ever enters the satisfaction class after frustration: returns None."""
        n_persons = 30
        t = 5
        trajectories = np.full((n_persons, t), 0, dtype=int)  # everyone stuck in class 0
        matrices = [np.eye(2) for _ in range(t - 1)]
        result = cascade_lead_time(
            {"transition_matrices": matrices, "class_assignments_per_timepoint": trajectories},
            frustration_class=0,
            satisfaction_class=1,
        )
        assert result["mean_lead_timepoints"] is None
        assert result["n_persons_with_pattern"] == 0
