"""Tests for tier-specific reliability reporting.

Reference: APA/AERA/NCME Standards (2014), Standards 2.3, 2.9
"""

import numpy as np
import pytest

from src.psychometric.irt_simulation import generate_synthetic_grm_parameters
from src.psychometric.tier_reliability import (
    compute_tier_information_curves,
    compute_tier_reliability,
    determine_supportable_interpretations,
    generate_tier_reliability_report,
)


@pytest.fixture
def irt_params():
    """Standard synthetic IRT parameters for 36 items."""
    return generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)


class TestComputeTierReliability:
    """Tests for per-tier marginal reliability computation."""

    def test_returns_all_three_tiers(self, irt_params):
        """Output includes reliability for 6, 18, and 36 item tiers."""
        result = compute_tier_reliability(irt_params["discrimination"], irt_params["difficulty"])
        assert "6_item" in result
        assert "18_item" in result
        assert "36_item" in result

    def test_reliability_between_zero_and_one(self, irt_params):
        """Reliability values are in [0, 1]."""
        result = compute_tier_reliability(irt_params["discrimination"], irt_params["difficulty"])
        for tier, rel in result.items():
            assert 0.0 <= rel["marginal_reliability"] <= 1.0, (
                f"{tier} reliability = {rel['marginal_reliability']}"
            )

    def test_more_items_higher_reliability(self, irt_params):
        """More items produce higher reliability (Spearman-Brown principle).

        Reference: Standard 2.9
        """
        result = compute_tier_reliability(irt_params["discrimination"], irt_params["difficulty"])
        r6 = result["6_item"]["marginal_reliability"]
        r18 = result["18_item"]["marginal_reliability"]
        r36 = result["36_item"]["marginal_reliability"]
        assert r36 >= r18 >= r6

    def test_each_tier_reports_sem(self, irt_params):
        """Each tier includes average SEM."""
        result = compute_tier_reliability(irt_params["discrimination"], irt_params["difficulty"])
        for tier in result:
            assert "mean_sem" in result[tier]
            assert result[tier]["mean_sem"] > 0

    def test_each_tier_reports_item_count(self, irt_params):
        """Each tier reports the number of items used."""
        result = compute_tier_reliability(irt_params["discrimination"], irt_params["difficulty"])
        assert result["6_item"]["n_items"] == 6
        assert result["18_item"]["n_items"] == 18
        assert result["36_item"]["n_items"] == 36


class TestComputeTierInformationCurves:
    """Tests for per-tier test information functions."""

    def test_returns_all_tiers(self, irt_params):
        """Output includes information curves for all 3 tiers."""
        result = compute_tier_information_curves(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert "6_item" in result
        assert "18_item" in result
        assert "36_item" in result

    def test_information_non_negative(self, irt_params):
        """Information values are non-negative."""
        result = compute_tier_information_curves(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        for tier in result:
            assert np.all(result[tier]["information"] >= 0)

    def test_more_items_more_information(self, irt_params):
        """More items produce higher total information at every theta."""
        result = compute_tier_information_curves(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        info_6 = np.sum(result["6_item"]["information"])
        info_18 = np.sum(result["18_item"]["information"])
        info_36 = np.sum(result["36_item"]["information"])
        assert info_36 >= info_18 >= info_6

    def test_includes_theta_grid(self, irt_params):
        """Output includes the theta grid used."""
        result = compute_tier_information_curves(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert "theta" in result["6_item"]


class TestDetermineSupportableInterpretations:
    """Tests for per-tier supportable interpretation analysis."""

    def test_returns_all_tiers(self, irt_params):
        """Output includes interpretation assessment for all 3 tiers."""
        result = determine_supportable_interpretations(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert "6_item" in result
        assert "18_item" in result
        assert "36_item" in result

    def test_each_tier_lists_interpretations(self, irt_params):
        """Each tier lists which interpretations it supports."""
        result = determine_supportable_interpretations(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        for tier in result:
            assert "supported" in result[tier]
            assert "not_supported" in result[tier]
            assert isinstance(result[tier]["supported"], list)
            assert isinstance(result[tier]["not_supported"], list)

    def test_36_item_supports_more_than_6_item(self, irt_params):
        """36-item tier supports at least as many interpretations as 6-item.

        Reference: Standard 2.9
        """
        result = determine_supportable_interpretations(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert len(result["36_item"]["supported"]) >= len(result["6_item"]["supported"])

    def test_6_item_does_not_support_type_classification(self, irt_params):
        """6-item tier should not support 24-type classification.

        With 1 item per subscale, type classification is unsupportable.
        """
        result = determine_supportable_interpretations(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert "24_type_classification" not in result["6_item"]["supported"]


class TestGenerateTierReliabilityReport:
    """Tests for the full tier reliability report."""

    def test_returns_complete_report(self, irt_params):
        """Report includes reliability, information, and interpretations per tier."""
        result = generate_tier_reliability_report(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        assert "reliability" in result
        assert "information_curves" in result
        assert "supportable_interpretations" in result

    def test_report_has_all_tiers(self, irt_params):
        """All three tiers present in every section."""
        result = generate_tier_reliability_report(
            irt_params["discrimination"], irt_params["difficulty"]
        )
        for section in ["reliability", "supportable_interpretations"]:
            assert "6_item" in result[section]
            assert "18_item" in result[section]
            assert "36_item" in result[section]
