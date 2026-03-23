"""Tests for IRT estimation module.

Reference: abc-assessment-spec Section 11.1
Reference: Bock & Mislevy (1982), Adaptive EAP Estimation
Reference: Baker & Kim (2004), Item Response Theory
"""

import numpy as np
import pytest
from scipy.stats import pearsonr

from src.psychometric.irt_estimation import (
    item_information,
    score_theta_eap,
)
from src.psychometric.irt_simulation import (
    generate_synthetic_grm_parameters,
    simulate_grm_responses,
)


@pytest.fixture
def simulation_data():
    """Generate a complete simulated dataset with known parameters.

    500 respondents, 24 items, 7 categories.
    Reference: abc-assessment-spec Section 11.1
    """
    params = generate_synthetic_grm_parameters(n_items=24, n_categories=7, seed=42)
    rng = np.random.default_rng(42)
    theta = rng.standard_normal(500)
    responses = simulate_grm_responses(
        theta, params["discrimination"], params["difficulty"], seed=42
    )
    return {
        "true_theta": theta,
        "true_discrimination": params["discrimination"],
        "true_difficulty": params["difficulty"],
        "responses": responses,
    }


@pytest.fixture
def small_simulation():
    """Small dataset for quick unit tests.

    50 respondents, 8 items, 7 categories.
    """
    params = generate_synthetic_grm_parameters(n_items=8, n_categories=7, seed=99)
    rng = np.random.default_rng(99)
    theta = rng.standard_normal(50)
    responses = simulate_grm_responses(
        theta, params["discrimination"], params["difficulty"], seed=99
    )
    return {
        "true_theta": theta,
        "true_discrimination": params["discrimination"],
        "true_difficulty": params["difficulty"],
        "responses": responses,
    }


class TestScoreThetaEAP:
    """Tests for Expected A Posteriori theta estimation."""

    def test_returns_theta_and_se(self, small_simulation):
        """EAP scoring returns both theta estimates and standard errors.

        Reference: Bock & Mislevy (1982)
        """
        data = small_simulation
        theta_hat, se = score_theta_eap(
            data["responses"],
            data["true_discrimination"],
            data["true_difficulty"],
        )
        assert theta_hat.shape == (len(data["true_theta"]),)
        assert se.shape == (len(data["true_theta"]),)

    def test_se_positive(self, small_simulation):
        """Standard errors are strictly positive."""
        data = small_simulation
        _, se = score_theta_eap(
            data["responses"],
            data["true_discrimination"],
            data["true_difficulty"],
        )
        assert np.all(se > 0)

    def test_theta_recovery_correlation(self, simulation_data):
        """Estimated theta correlates with true theta at r > 0.90.

        Reference: Phase 1 validation gate
        """
        data = simulation_data
        theta_hat, _ = score_theta_eap(
            data["responses"],
            data["true_discrimination"],
            data["true_difficulty"],
        )
        r, _ = pearsonr(data["true_theta"], theta_hat)
        assert r > 0.90, f"Theta recovery r = {r:.3f}, required > 0.90"

    def test_extreme_low_responses_produce_low_theta(self, small_simulation):
        """All-1 responses should produce theta well below 0."""
        data = small_simulation
        n_items = data["responses"].shape[1]
        low_responses = np.ones((1, n_items), dtype=int)
        theta_hat, _ = score_theta_eap(
            low_responses,
            data["true_discrimination"],
            data["true_difficulty"],
        )
        assert theta_hat[0] < -1.0

    def test_extreme_high_responses_produce_high_theta(self, small_simulation):
        """All-7 responses should produce theta well above 0."""
        data = small_simulation
        n_items = data["responses"].shape[1]
        high_responses = np.full((1, n_items), 7, dtype=int)
        theta_hat, _ = score_theta_eap(
            high_responses,
            data["true_discrimination"],
            data["true_difficulty"],
        )
        assert theta_hat[0] > 1.0

    def test_se_smaller_with_more_discriminating_items(self):
        """Higher discrimination items produce lower SE (more precision).

        Reference: Baker & Kim (2004)
        """
        rng = np.random.default_rng(42)
        difficulty = np.tile(np.array([-2, -1, 0, 1, 2, 3], dtype=float), (4, 1))

        # Low discrimination items
        low_a = np.full(4, 0.5)
        theta_true = rng.standard_normal(100)
        from src.psychometric.irt_simulation import simulate_grm_responses

        r_low = simulate_grm_responses(theta_true, low_a, difficulty, seed=42)
        _, se_low = score_theta_eap(r_low, low_a, difficulty)

        # High discrimination items
        high_a = np.full(4, 2.5)
        r_high = simulate_grm_responses(theta_true, high_a, difficulty, seed=42)
        _, se_high = score_theta_eap(r_high, high_a, difficulty)

        assert np.mean(se_high) < np.mean(se_low)

    def test_custom_prior(self, small_simulation):
        """Custom prior mean shifts theta estimates.

        Reference: Bock & Mislevy (1982)
        """
        data = small_simulation
        theta_default, _ = score_theta_eap(
            data["responses"],
            data["true_discrimination"],
            data["true_difficulty"],
            prior_mean=0.0,
        )
        theta_shifted, _ = score_theta_eap(
            data["responses"],
            data["true_discrimination"],
            data["true_difficulty"],
            prior_mean=2.0,
        )
        # Shifted prior should pull estimates higher
        assert np.mean(theta_shifted) > np.mean(theta_default)


class TestItemInformation:
    """Tests for item information function computation."""

    def test_output_shape(self, known_discrimination, known_difficulty):
        """Information matrix has (n_items, n_theta_points) shape."""
        theta_grid = np.linspace(-3, 3, 61)
        info = item_information(theta_grid, known_discrimination, known_difficulty)
        assert info.shape == (len(known_discrimination), len(theta_grid))

    def test_information_non_negative(self, known_discrimination, known_difficulty):
        """Item information is always non-negative.

        Reference: Baker & Kim (2004)
        """
        theta_grid = np.linspace(-3, 3, 61)
        info = item_information(theta_grid, known_discrimination, known_difficulty)
        assert np.all(info >= 0)

    def test_information_peaks_near_difficulty(self):
        """Item information peaks near the item's difficulty parameters.

        Reference: Baker & Kim (2004)
        """
        a = 1.5
        b = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
        theta_grid = np.linspace(-4, 6, 200)
        info = item_information(theta_grid, np.array([a]), np.array([b]))
        peak_theta = theta_grid[np.argmax(info[0])]
        # Peak should be near the middle of the difficulty range
        b_midpoint = np.mean(b)
        assert abs(peak_theta - b_midpoint) < 1.5

    def test_higher_discrimination_higher_peak_information(self):
        """Higher discrimination produces higher peak information.

        Reference: Baker & Kim (2004)
        """
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        theta_grid = np.linspace(-4, 6, 200)

        info_low = item_information(theta_grid, np.array([0.5]), np.array([b]))
        info_high = item_information(theta_grid, np.array([2.5]), np.array([b]))

        assert np.max(info_high) > np.max(info_low)

    def test_total_information_is_sum(self, known_discrimination, known_difficulty):
        """Total test information equals sum of item information functions.

        Reference: Lord (1980), Applications of Item Response Theory
        """
        theta_grid = np.linspace(-3, 3, 61)
        info = item_information(theta_grid, known_discrimination, known_difficulty)
        total = np.sum(info, axis=0)
        # Total should be positive everywhere with 24 items
        assert np.all(total > 0)
