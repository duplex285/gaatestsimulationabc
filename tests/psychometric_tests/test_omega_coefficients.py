"""Tests for omega coefficient computation.

Reference: McDonald (1999), Test Theory: A Unified Treatment
Reference: Reise, Bonifay, & Haviland (2013), Scoring and Modeling
           Issues in Bifactor Analysis
"""

import numpy as np

from src.psychometric.omega_coefficients import (
    compute_ecv,
    compute_omega_hierarchical,
    compute_omega_subscale,
)


class TestComputeOmegaHierarchical:
    """Tests for omega hierarchical computation."""

    def test_returns_float(self):
        """Omega-h is a single float value."""
        general = np.array([0.5, 0.5, 0.5, 0.5, 0.3, 0.3, 0.3, 0.3])
        specific = np.array([0.4, 0.4, 0.4, 0.4, 0.5, 0.5, 0.5, 0.5])
        result = compute_omega_hierarchical(general, specific)
        assert isinstance(result, float)

    def test_omega_h_between_zero_and_one(self):
        """Omega-h is in [0, 1]."""
        general = np.array([0.5, 0.4, 0.6, 0.3, 0.5, 0.4])
        specific = np.array([0.4, 0.5, 0.3, 0.6, 0.4, 0.5])
        result = compute_omega_hierarchical(general, specific)
        assert 0.0 <= result <= 1.0

    def test_high_omega_h_with_dominant_general_factor(self):
        """When general loadings are large and specific are small, omega-h is high.

        Reference: Reise (2012), omega_h > 0.80 = essentially unidimensional
        """
        general = np.array([0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
        specific = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        result = compute_omega_hierarchical(general, specific)
        assert result > 0.70

    def test_low_omega_h_with_weak_general_factor(self):
        """When general loadings are small and specific are large, omega-h is low.

        Reference: Reise (2012), omega_h < 0.50 = subscales are meaningful
        """
        general = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        specific = np.array([0.8, 0.8, 0.8, 0.8, 0.8, 0.8])
        result = compute_omega_hierarchical(general, specific)
        assert result < 0.30


class TestComputeOmegaSubscale:
    """Tests for omega subscale (omega-s) computation."""

    def test_returns_float(self):
        """Omega-s for a subscale is a single float."""
        general_sub = np.array([0.3, 0.3, 0.3, 0.3])
        specific_sub = np.array([0.6, 0.6, 0.6, 0.6])
        result = compute_omega_subscale(general_sub, specific_sub)
        assert isinstance(result, float)

    def test_omega_s_between_zero_and_one(self):
        """Omega-s is in [0, 1]."""
        general_sub = np.array([0.4, 0.5, 0.3, 0.4])
        specific_sub = np.array([0.5, 0.4, 0.6, 0.5])
        result = compute_omega_subscale(general_sub, specific_sub)
        assert 0.0 <= result <= 1.0

    def test_high_omega_s_when_specific_dominates(self):
        """When specific loadings dominate, omega-s is high (subscale is meaningful)."""
        general_sub = np.array([0.1, 0.1, 0.1, 0.1])
        specific_sub = np.array([0.8, 0.8, 0.8, 0.8])
        result = compute_omega_subscale(general_sub, specific_sub)
        assert result > 0.60

    def test_low_omega_s_when_general_dominates(self):
        """When general loadings dominate, omega-s is low (subscale adds little)."""
        general_sub = np.array([0.8, 0.8, 0.8, 0.8])
        specific_sub = np.array([0.1, 0.1, 0.1, 0.1])
        result = compute_omega_subscale(general_sub, specific_sub)
        assert result < 0.30


class TestComputeECV:
    """Tests for Explained Common Variance."""

    def test_returns_float(self):
        """ECV is a single float."""
        general = np.array([0.5, 0.5, 0.5, 0.5])
        specific = np.array([0.4, 0.4, 0.4, 0.4])
        result = compute_ecv(general, specific)
        assert isinstance(result, float)

    def test_ecv_between_zero_and_one(self):
        """ECV is in [0, 1]."""
        general = np.array([0.5, 0.4, 0.6, 0.3])
        specific = np.array([0.4, 0.5, 0.3, 0.6])
        result = compute_ecv(general, specific)
        assert 0.0 <= result <= 1.0

    def test_ecv_formula(self):
        """ECV = sum(general^2) / (sum(general^2) + sum(specific^2)).

        Reference: Reise, Bonifay, & Haviland (2013)
        """
        general = np.array([0.6, 0.5])
        specific = np.array([0.4, 0.3])
        expected = (0.36 + 0.25) / (0.36 + 0.25 + 0.16 + 0.09)
        result = compute_ecv(general, specific)
        assert abs(result - expected) < 1e-10

    def test_ecv_high_with_dominant_general(self):
        """ECV near 1.0 when general factor dominates."""
        general = np.array([0.9, 0.9, 0.9, 0.9])
        specific = np.array([0.1, 0.1, 0.1, 0.1])
        result = compute_ecv(general, specific)
        assert result > 0.90
