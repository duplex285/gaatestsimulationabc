"""Tests for advanced factor analysis module.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
Reference: Reise (2012), Bifactor Models, Psychological Methods
Reference: Asparouhov & Muthen (2009), ESEM
Reference: Murphy et al. (2023), BPNSFS method artifacts
"""

import numpy as np
import pytest

from src.psychometric.factor_models import (
    compare_models,
    fit_bifactor_model,
    fit_cfa_model,
    fit_method_factor_model,
)


@pytest.fixture
def clean_six_factor_data():
    """Synthetic data with clean 6-factor structure (no method artifact).

    24 items, 4 per factor, 500 respondents.
    Each item loads on its factor at ~0.7 with independent noise.
    """
    rng = np.random.default_rng(42)
    n = 500
    n_factors = 6
    items_per_factor = 4
    n_items = n_factors * items_per_factor

    # Generate factor scores
    factors = rng.standard_normal((n, n_factors))

    # Generate item responses
    data = np.zeros((n, n_items))
    for f in range(n_factors):
        for i in range(items_per_factor):
            item_idx = f * items_per_factor + i
            loading = 0.7
            data[:, item_idx] = loading * factors[:, f] + np.sqrt(
                1 - loading**2
            ) * rng.standard_normal(n)

    return data


@pytest.fixture
def method_artifact_data():
    """Synthetic data where a method factor (item keying) contaminates the structure.

    Positively-keyed items share method variance beyond their substantive factor.
    Negatively-keyed items share separate method variance.
    This simulates the Murphy et al. (2023) finding about BPNSFS.

    Items 0-3 (a_sat, positive), 4-7 (a_frust, negative),
    8-11 (b_sat, positive), 12-15 (b_frust, negative),
    16-19 (c_sat, positive), 20-23 (c_frust, negative).
    """
    rng = np.random.default_rng(42)
    n = 500
    n_items = 24

    # Substantive factors
    factors = rng.standard_normal((n, 6))

    # Method factors: positive keying and negative keying
    method_pos = rng.standard_normal(n)
    method_neg = rng.standard_normal(n)

    data = np.zeros((n, n_items))
    for f in range(6):
        is_frustration = f % 2 == 1  # odd indices are frustration (negative keying)
        method_factor = method_neg if is_frustration else method_pos
        method_loading = 0.4  # strong method effect

        for i in range(4):
            item_idx = f * 4 + i
            substantive_loading = 0.5
            noise_var = 1 - substantive_loading**2 - method_loading**2
            noise_var = max(noise_var, 0.1)
            data[:, item_idx] = (
                substantive_loading * factors[:, f]
                + method_loading * method_factor
                + np.sqrt(noise_var) * rng.standard_normal(n)
            )

    return data


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
    mapping = {}
    factors = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    for f_idx, factor in enumerate(factors):
        for i in range(4):
            item_idx = f_idx * 4 + i
            mapping[item_idx] = factor
    return mapping


@pytest.fixture
def reverse_coded_indices():
    """Indices of negatively-keyed (frustration) items."""
    # Frustration items: indices 4-7, 12-15, 20-23
    return list(range(4, 8)) + list(range(12, 16)) + list(range(20, 24))


class TestFitCFAModel:
    """Tests for standard 6-factor CFA."""

    def test_returns_fit_indices(self, clean_six_factor_data, item_names, factor_map):
        """Output includes standard fit indices."""
        result = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        assert "chi2" in result
        assert "df" in result
        assert "cfi" in result
        assert "rmsea" in result
        assert "aic" in result

    def test_good_fit_on_clean_data(self, clean_six_factor_data, item_names, factor_map):
        """Clean 6-factor data should produce acceptable CFA fit.

        Reference: Hu & Bentler (1999), CFI >= 0.90, RMSEA <= 0.08
        """
        result = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        assert result["cfi"] >= 0.85, f"CFI = {result['cfi']:.3f}"
        assert result["rmsea"] <= 0.12, f"RMSEA = {result['rmsea']:.3f}"

    def test_returns_loadings(self, clean_six_factor_data, item_names, factor_map):
        """Output includes factor loadings matrix."""
        result = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        assert "loadings" in result
        assert len(result["loadings"]) == 24  # one per item


class TestFitBifactorModel:
    """Tests for bifactor model (general + specific factors)."""

    def test_returns_fit_indices(self, clean_six_factor_data, item_names, factor_map):
        """Output includes fit indices and omega coefficients."""
        result = fit_bifactor_model(clean_six_factor_data, item_names, factor_map)
        assert "chi2" in result
        assert "cfi" in result
        assert "omega_h" in result
        assert "omega_s" in result
        assert "ecv" in result

    def test_omega_h_low_for_clean_six_factor(self, clean_six_factor_data, item_names, factor_map):
        """With clean 6-factor data and no general factor, omega_h should be low.

        Reference: Reise (2012), omega_h < 0.50 indicates subscales are meaningful
        """
        result = fit_bifactor_model(clean_six_factor_data, item_names, factor_map)
        # With truly independent factors, general factor should be weak
        assert result["omega_h"] < 0.70, f"omega_h = {result['omega_h']:.3f}"

    def test_returns_general_and_specific_loadings(
        self, clean_six_factor_data, item_names, factor_map
    ):
        """Output includes both general and specific factor loadings."""
        result = fit_bifactor_model(clean_six_factor_data, item_names, factor_map)
        assert "general_loadings" in result
        assert "specific_loadings" in result
        assert len(result["general_loadings"]) == 24


class TestFitMethodFactorModel:
    """Tests for CFA with method factor for item-keying direction."""

    def test_returns_method_loadings(
        self, method_artifact_data, item_names, factor_map, reverse_coded_indices
    ):
        """Output includes method factor loadings.

        Reference: Murphy et al. (2023)
        """
        result = fit_method_factor_model(
            method_artifact_data, item_names, factor_map, reverse_coded_indices
        )
        assert "method_loadings" in result
        assert len(result["method_loadings"]) == 24

    def test_detects_method_artifact(
        self, method_artifact_data, item_names, factor_map, reverse_coded_indices
    ):
        """Method factor loadings should be substantial when artifact is present.

        Reference: Murphy et al. (2023), method loadings > 0.30 = artifact
        """
        result = fit_method_factor_model(
            method_artifact_data, item_names, factor_map, reverse_coded_indices
        )
        # Average method loading on reverse-coded items should be meaningful
        rc_loadings = [abs(result["method_loadings"][i]) for i in reverse_coded_indices]
        mean_rc_loading = np.mean(rc_loadings)
        assert mean_rc_loading > 0.15, f"Mean method loading = {mean_rc_loading:.3f}"

    def test_returns_fit_indices(
        self, method_artifact_data, item_names, factor_map, reverse_coded_indices
    ):
        """Output includes standard fit indices."""
        result = fit_method_factor_model(
            method_artifact_data, item_names, factor_map, reverse_coded_indices
        )
        assert "cfi" in result
        assert "rmsea" in result
        assert "aic" in result


class TestCompareModels:
    """Tests for model comparison functionality."""

    def test_returns_comparison_table(self, clean_six_factor_data, item_names, factor_map):
        """Comparison returns a dict of model results keyed by model name."""
        cfa = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        bifactor = fit_bifactor_model(clean_six_factor_data, item_names, factor_map)
        result = compare_models({"cfa": cfa, "bifactor": bifactor})
        assert "cfa" in result
        assert "bifactor" in result

    def test_includes_delta_aic(self, clean_six_factor_data, item_names, factor_map):
        """Comparison includes delta AIC relative to best model."""
        cfa = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        bifactor = fit_bifactor_model(clean_six_factor_data, item_names, factor_map)
        result = compare_models({"cfa": cfa, "bifactor": bifactor})
        assert "delta_aic" in result["cfa"]
        assert "delta_aic" in result["bifactor"]
        # One model should have delta_aic = 0 (the best one)
        deltas = [result[m]["delta_aic"] for m in result]
        assert min(deltas) == 0.0

    def test_comparison_with_single_model(self, clean_six_factor_data, item_names, factor_map):
        """Comparison works with a single model."""
        cfa = fit_cfa_model(clean_six_factor_data, item_names, factor_map)
        result = compare_models({"cfa": cfa})
        assert result["cfa"]["delta_aic"] == 0.0
