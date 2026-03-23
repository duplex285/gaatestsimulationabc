"""Tests for IRT simulation module.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
Reference: Samejima (1969), Estimation of Latent Ability
"""

import numpy as np

from src.psychometric.irt_simulation import (
    generate_synthetic_grm_parameters,
    grm_probability,
    simulate_grm_responses,
)


class TestGenerateSyntheticGRMParameters:
    """Tests for synthetic GRM parameter generation."""

    def test_returns_discrimination_and_difficulty(self):
        """Parameters dict contains discrimination and difficulty arrays."""
        params = generate_synthetic_grm_parameters(seed=42)
        assert "discrimination" in params
        assert "difficulty" in params

    def test_discrimination_shape(self):
        """Discrimination has one value per item.

        Reference: abc-assessment-spec Section 1.2 (24 items)
        """
        params = generate_synthetic_grm_parameters(n_items=24, seed=42)
        assert params["discrimination"].shape == (24,)

    def test_difficulty_shape(self):
        """Difficulty has (n_items, n_categories - 1) shape.

        Reference: Samejima (1969), 7 categories -> 6 thresholds per item
        """
        params = generate_synthetic_grm_parameters(n_items=24, n_categories=7, seed=42)
        assert params["difficulty"].shape == (24, 6)

    def test_discrimination_positive(self):
        """All discrimination parameters are positive.

        Reference: Baker & Kim (2004)
        """
        params = generate_synthetic_grm_parameters(seed=42)
        assert np.all(params["discrimination"] > 0)

    def test_discrimination_realistic_range(self):
        """Discrimination values fall within realistic range for personality items.

        Reference: Baker & Kim (2004), typical range 0.5-3.0
        """
        params = generate_synthetic_grm_parameters(seed=42)
        assert np.all(params["discrimination"] >= 0.5)
        assert np.all(params["discrimination"] <= 3.0)

    def test_difficulty_ordered_within_items(self):
        """Thresholds are strictly increasing within each item.

        Reference: Samejima (1969), ordered category model
        """
        params = generate_synthetic_grm_parameters(seed=42)
        for i in range(params["difficulty"].shape[0]):
            diffs = np.diff(params["difficulty"][i])
            assert np.all(diffs > 0), f"Item {i} thresholds not ordered: {params['difficulty'][i]}"

    def test_reproducibility_with_same_seed(self):
        """Same seed produces identical parameters.

        Reference: CLAUDE_RULES.md Rule 7
        """
        p1 = generate_synthetic_grm_parameters(seed=99)
        p2 = generate_synthetic_grm_parameters(seed=99)
        np.testing.assert_array_equal(p1["discrimination"], p2["discrimination"])
        np.testing.assert_array_equal(p1["difficulty"], p2["difficulty"])

    def test_different_seeds_produce_different_parameters(self):
        p1 = generate_synthetic_grm_parameters(seed=1)
        p2 = generate_synthetic_grm_parameters(seed=2)
        assert not np.array_equal(p1["discrimination"], p2["discrimination"])

    def test_custom_item_count(self):
        params = generate_synthetic_grm_parameters(n_items=12, seed=42)
        assert params["discrimination"].shape == (12,)

    def test_custom_category_count(self):
        params = generate_synthetic_grm_parameters(n_categories=5, seed=42)
        assert params["difficulty"].shape == (24, 4)


class TestGRMProbability:
    """Tests for GRM category probability computation."""

    def test_probabilities_sum_to_one(self):
        """Category probabilities sum to 1.0 for any theta.

        Reference: Samejima (1969)
        """
        a = 1.5
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        for theta in [-3.0, -1.0, 0.0, 1.0, 3.0]:
            probs = grm_probability(theta, a, b)
            np.testing.assert_almost_equal(np.sum(probs), 1.0, decimal=10)

    def test_probabilities_non_negative(self):
        """All probabilities are non-negative."""
        a = 1.5
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        for theta in np.linspace(-4.0, 4.0, 20):
            probs = grm_probability(theta, a, b)
            assert np.all(probs >= 0), f"Negative probability at theta={theta}"

    def test_correct_number_of_categories(self):
        """Returns one probability per category."""
        a = 1.5
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        probs = grm_probability(0.0, a, b)
        assert len(probs) == 7  # 6 thresholds -> 7 categories

    def test_high_theta_favors_high_categories(self):
        """Very high theta should have highest probability in top category."""
        a = 1.5
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        probs = grm_probability(5.0, a, b)
        assert np.argmax(probs) == 6  # category 7 (0-indexed: 6)

    def test_low_theta_favors_low_categories(self):
        """Very low theta should have highest probability in bottom category."""
        a = 1.5
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        probs = grm_probability(-5.0, a, b)
        assert np.argmax(probs) == 0  # category 1 (0-indexed: 0)

    def test_higher_discrimination_sharper_curves(self):
        """Higher discrimination produces more peaked probability distribution."""
        b = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
        probs_low_a = grm_probability(0.5, 0.5, b)
        probs_high_a = grm_probability(0.5, 2.5, b)
        # Higher discrimination -> higher max probability (more peaked)
        assert np.max(probs_high_a) > np.max(probs_low_a)


class TestSimulateGRMResponses:
    """Tests for GRM response simulation."""

    def test_response_shape(self, known_discrimination, known_difficulty, known_theta):
        """Response matrix has (n_persons, n_items) shape."""
        responses = simulate_grm_responses(
            known_theta, known_discrimination, known_difficulty, seed=42
        )
        assert responses.shape == (len(known_theta), len(known_discrimination))

    def test_responses_in_valid_range(self, known_discrimination, known_difficulty, known_theta):
        """All responses are integers in [1, n_categories].

        Reference: abc-assessment-spec Section 1.2 (7-point Likert)
        """
        responses = simulate_grm_responses(
            known_theta, known_discrimination, known_difficulty, seed=42
        )
        assert np.all(responses >= 1)
        assert np.all(responses <= 7)

    def test_responses_are_integers(self, known_discrimination, known_difficulty, known_theta):
        """Responses are whole numbers (discrete categories)."""
        responses = simulate_grm_responses(
            known_theta, known_discrimination, known_difficulty, seed=42
        )
        np.testing.assert_array_equal(responses, responses.astype(int))

    def test_reproducibility(self, known_discrimination, known_difficulty, known_theta):
        """Same seed produces identical responses.

        Reference: CLAUDE_RULES.md Rule 7
        """
        r1 = simulate_grm_responses(known_theta, known_discrimination, known_difficulty, seed=42)
        r2 = simulate_grm_responses(known_theta, known_discrimination, known_difficulty, seed=42)
        np.testing.assert_array_equal(r1, r2)

    def test_high_theta_produces_higher_mean_responses(
        self, known_discrimination, known_difficulty
    ):
        """People with higher theta should produce higher mean responses."""
        low_theta = np.full(200, -2.0)
        high_theta = np.full(200, 2.0)
        r_low = simulate_grm_responses(low_theta, known_discrimination, known_difficulty, seed=42)
        r_high = simulate_grm_responses(high_theta, known_discrimination, known_difficulty, seed=42)
        assert np.mean(r_high) > np.mean(r_low)

    def test_marginal_distribution_plausible(
        self, known_discrimination, known_difficulty, known_theta
    ):
        """Response distribution uses all categories (no empty categories in aggregate)."""
        responses = simulate_grm_responses(
            known_theta, known_discrimination, known_difficulty, seed=42
        )
        unique_values = np.unique(responses)
        # With 500 respondents and 24 items, all 7 categories should appear
        assert len(unique_values) == 7
