"""Tests for latent profile analysis (LPA) module.

Reference: howard-2024-implementation-plan.md V2-B WI-16
Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
Reference: Wang, Morin, Ryan, Liu (2016); Vansteenkiste et al. (2009)
"""

import numpy as np
import pandas as pd
import pytest

from src.psychometric.profile_analysis import (
    compare_to_archetypes,
    fit_lpa,
    profile_centroids,
)


@pytest.fixture
def three_class_mixture():
    """Generate (n=600, p=4) data from a mixture of 3 well-separated Gaussians.

    Each centroid is shifted along all 4 dimensions so the classes are
    detectable but realistic for SDT-style indicator data.
    """
    rng = np.random.default_rng(42)
    n_per = 200
    p = 4

    centroids = np.array(
        [
            [-2.0, -2.0, -2.0, -2.0],
            [0.0, 0.0, 0.0, 0.0],
            [2.0, 2.0, 2.0, 2.0],
        ]
    )
    labels = np.repeat(np.arange(3), n_per)
    scores = np.zeros((n_per * 3, p))
    for k in range(3):
        scores[labels == k] = centroids[k] + rng.standard_normal((n_per, p)) * 0.5

    # Shuffle so order does not leak
    perm = rng.permutation(n_per * 3)
    return scores[perm], labels[perm]


@pytest.fixture
def six_dim_data():
    """Generate (n=500, p=6) random Gaussian-mixture data."""
    rng = np.random.default_rng(42)
    n_per = 250
    centroids = np.array(
        [
            [-1.5, -1.5, -1.5, 1.5, 1.5, 1.5],
            [1.5, 1.5, 1.5, -1.5, -1.5, -1.5],
        ]
    )
    labels = np.repeat(np.arange(2), n_per)
    scores = np.zeros((n_per * 2, 6))
    for k in range(2):
        scores[labels == k] = centroids[k] + rng.standard_normal((n_per, 6)) * 0.6
    return scores


class TestFitLPA:
    """Tests for fit_lpa: latent profile analysis with five-criterion selection."""

    def test_lpa_recovers_three_known_classes(self, three_class_mixture):
        """When 3 well-separated Gaussians generate the data, selected_k == 3."""
        scores, _ = three_class_mixture
        result = fit_lpa(scores, k_range=(1, 6), random_state=42)
        assert result["selected_k"] == 3, f"Got k={result['selected_k']}, expected 3"

    def test_lpa_returns_posterior_probabilities_sum_to_one(self, three_class_mixture):
        """Posterior rows sum to 1.0 within tolerance."""
        scores, _ = three_class_mixture
        result = fit_lpa(scores, k_range=(1, 6), random_state=42)
        k = result["selected_k"]
        post = result["results_per_k"][k]["posteriors"]
        row_sums = post.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6)

    def test_lpa_entropy_in_unit_interval(self, three_class_mixture):
        """Normalized entropy must lie in [0, 1]."""
        scores, _ = three_class_mixture
        result = fit_lpa(scores, k_range=(2, 4), random_state=42)
        for k, info in result["results_per_k"].items():
            if k == 1:
                continue
            ent = info["entropy"]
            assert 0.0 <= ent <= 1.0, f"k={k} entropy={ent}"

    def test_lpa_runs_on_six_dim_input(self, six_dim_data):
        """(n=500, p=6) input runs without error."""
        result = fit_lpa(six_dim_data, k_range=(1, 5), random_state=42)
        assert result["selected_k"] >= 1
        assert "selection_rationale" in result

    def test_lpa_selection_prefers_smaller_k_when_close(self):
        """When k=3 and k=4 give close BIC, parsimony prefers k=3."""
        rng = np.random.default_rng(42)
        n_per = 200
        centroids = np.array(
            [
                [-2.0, -2.0],
                [0.0, 0.0],
                [2.0, 2.0],
            ]
        )
        scores = np.vstack([c + rng.standard_normal((n_per, 2)) * 0.6 for c in centroids])
        result = fit_lpa(scores, k_range=(1, 5), random_state=42)
        # 3-class generative truth; selection should not over-extract
        assert result["selected_k"] <= 3


class TestCompareToArchetypes:
    """Tests for compare_to_archetypes: ARI + Cohen's kappa."""

    def test_compare_to_archetypes_returns_kappa_and_ari(self, three_class_mixture):
        """Both metrics returned, ari in [-1, 1], kappa in [-1, 1]."""
        scores, labels = three_class_mixture
        lpa_result = fit_lpa(scores, k_range=(2, 4), random_state=42)
        cmp = compare_to_archetypes(lpa_result, labels)
        assert "adjusted_rand_index" in cmp
        assert "cohens_kappa" in cmp
        assert -1.0 <= cmp["adjusted_rand_index"] <= 1.0
        assert -1.0 <= cmp["cohens_kappa"] <= 1.0
        assert "contingency_table" in cmp

    def test_compare_to_archetypes_perfect_match(self):
        """Identical clusterings: kappa = 1.0, ari = 1.0."""
        rng = np.random.default_rng(42)
        # Synthesize an LPA result whose argmax(posteriors) == labels exactly.
        n = 60
        labels = np.repeat(np.arange(3), 20)
        post = np.zeros((n, 3))
        for i in range(n):
            post[i, labels[i]] = 0.99
            others = [j for j in range(3) if j != labels[i]]
            post[i, others[0]] = 0.005
            post[i, others[1]] = 0.005
        # rng unused but seeded for symmetry across tests
        _ = rng.standard_normal(1)
        lpa_result = {
            "selected_k": 3,
            "results_per_k": {
                3: {
                    "n_classes": 3,
                    "posteriors": post,
                }
            },
        }
        cmp = compare_to_archetypes(lpa_result, labels)
        assert cmp["adjusted_rand_index"] == pytest.approx(1.0, abs=1e-9)
        assert cmp["cohens_kappa"] == pytest.approx(1.0, abs=1e-9)


class TestProfileCentroids:
    """Tests for profile_centroids."""

    def test_returns_dataframe_with_correct_shape(self, three_class_mixture):
        """Returns DataFrame indexed by class, columns = indicator names."""
        scores, _ = three_class_mixture
        result = fit_lpa(scores, k_range=(2, 4), random_state=42)
        names = ["x1", "x2", "x3", "x4"]
        df = profile_centroids(result, names)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == names
        assert len(df) == result["selected_k"]
