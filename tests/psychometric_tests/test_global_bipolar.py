"""Tests for 1-G vs 2-G bifactor-ESEM comparison.

Reference: howard-2024-implementation-plan.md V2-B WI-8
Reference: Toth-Kiraly et al. (2018), bifactor-ESEM on BPNSFS
"""

import numpy as np
import pytest

from src.psychometric.factor_models import (
    ABC_FACTOR_MAP_24,
    ABC_VALENCE_MAP_24,
    compare_one_g_two_g,
    fit_one_g_bifactor_esem,
    fit_two_g_bifactor_esem,
)


@pytest.fixture
def item_names():
    """Standard ABC item names for 24 items."""
    names = []
    for prefix in ["AS", "AF", "BS", "BF", "CS", "CF"]:
        for i in range(1, 5):
            names.append(f"{prefix}{i}")
    return names


@pytest.fixture
def factor_map():
    """Maps each item to its substantive factor."""
    return dict(ABC_FACTOR_MAP_24)


@pytest.fixture
def valence_map():
    """Maps each item to 'sat' or 'frust' valence."""
    return dict(ABC_VALENCE_MAP_24)


def _bipolar_data(n: int = 500, seed: int = 42) -> np.ndarray:
    """One latent fulfillment factor: sat items load +0.6, frust items load -0.6.

    Sat items are at indices 0-3, 8-11, 16-19; frust at 4-7, 12-15, 20-23.
    Each item also has a small specific-factor contribution and noise.
    """
    rng = np.random.default_rng(seed)
    g = rng.standard_normal(n)
    n_items = 24
    data = np.zeros((n, n_items))
    primary = 0.6
    spec_var = 0.15
    spec = rng.standard_normal((n, 6)) * np.sqrt(spec_var)
    for f in range(6):
        is_frust = (f % 2) == 1
        sign = -1.0 if is_frust else 1.0
        for i in range(4):
            idx = f * 4 + i
            noise_var = max(1 - primary**2 - spec_var, 0.05)
            data[:, idx] = (
                sign * primary * g + spec[:, f] + np.sqrt(noise_var) * rng.standard_normal(n)
            )
    return data


def _two_factor_data(n: int = 500, seed: int = 42) -> np.ndarray:
    """Two correlated latent factors (sat-G, frust-G) with r ~ 0.3.

    Sat items load on sat-G; frust items load on frust-G; both positive.
    """
    rng = np.random.default_rng(seed)
    # Construct correlated latent factors with target correlation ~0.3
    z = rng.standard_normal((n, 2))
    target_r = 0.3
    L = np.linalg.cholesky(np.array([[1.0, target_r], [target_r, 1.0]]))
    g = z @ L.T  # n x 2
    sat_g = g[:, 0]
    frust_g = g[:, 1]
    n_items = 24
    data = np.zeros((n, n_items))
    primary = 0.6
    spec_var = 0.15
    spec = rng.standard_normal((n, 6)) * np.sqrt(spec_var)
    for f in range(6):
        is_frust = (f % 2) == 1
        latent = frust_g if is_frust else sat_g
        for i in range(4):
            idx = f * 4 + i
            noise_var = max(1 - primary**2 - spec_var, 0.05)
            data[:, idx] = (
                primary * latent + spec[:, f] + np.sqrt(noise_var) * rng.standard_normal(n)
            )
    return data


class TestOneG:
    """One-global-factor bifactor-ESEM."""

    def test_one_g_returns_g_loadings_with_correct_signs(self, item_names, factor_map, valence_map):
        """sat items should have positive G loading, frust items negative."""
        data = _bipolar_data()
        result = fit_one_g_bifactor_esem(data, item_names, factor_map, valence_map)
        g_loadings = result["g_loadings"]
        # majority sign correctness (allow a few estimation outliers)
        sat_pos = sum(
            1 for idx, v in valence_map.items() if v == "sat" and g_loadings[item_names[idx]] > 0
        )
        frust_neg = sum(
            1 for idx, v in valence_map.items() if v == "frust" and g_loadings[item_names[idx]] < 0
        )
        n_sat = sum(1 for v in valence_map.values() if v == "sat")
        n_frust = sum(1 for v in valence_map.values() if v == "frust")
        assert sat_pos / n_sat >= 0.75, f"only {sat_pos}/{n_sat} sat items had +ve G loading"
        assert frust_neg / n_frust >= 0.75, (
            f"only {frust_neg}/{n_frust} frust items had -ve G loading"
        )


class TestTwoG:
    """Two-global-factor bifactor-ESEM."""

    def test_two_g_returns_correlation(self, item_names, factor_map, valence_map):
        """g_g_correlation should be a finite value in [-1, 1]."""
        data = _two_factor_data()
        result = fit_two_g_bifactor_esem(data, item_names, factor_map, valence_map)
        r = result["g_g_correlation"]
        assert r is not None
        assert -1.0 <= r <= 1.0, f"g_g_correlation = {r}"


class TestCompare:
    """compare_one_g_two_g decision rule."""

    def test_compare_returns_valid_recommendation(self, item_names, factor_map, valence_map):
        """Recommendation must be one of the documented values."""
        data = _bipolar_data()
        result = compare_one_g_two_g(data, item_names, factor_map, valence_map)
        assert result["recommendation"] in {"1-G", "2-G", "ambiguous"}
        assert "rationale" in result
        assert "delta_bic" in result
        assert "g_g_correlation" in result

    def test_one_g_wins_on_bipolar_data(self, item_names, factor_map, valence_map):
        """Truly bipolar data should yield recommendation == '1-G'."""
        data = _bipolar_data()
        result = compare_one_g_two_g(data, item_names, factor_map, valence_map)
        assert result["recommendation"] == "1-G", (
            f"got {result['recommendation']}; rationale: {result['rationale']}"
        )

    def test_two_g_wins_on_two_factor_data(self, item_names, factor_map, valence_map):
        """Two distinct sat/frust factors should yield recommendation == '2-G'."""
        data = _two_factor_data()
        result = compare_one_g_two_g(data, item_names, factor_map, valence_map)
        assert result["recommendation"] == "2-G", (
            f"got {result['recommendation']}; rationale: {result['rationale']}"
        )
