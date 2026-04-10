"""Tests for cross-lagged panel SEM module.

Reference: Hamaker, Kuiper & Grasman (2015), RI-CLPM
Reference: abc-assessment-spec Section 11.7 (trajectory detection)

Status: Phase 8 (structural equations)
"""

import pandas as pd
import pytest

from src.psychometric.structural_equations import (
    build_clpm_syntax,
    build_ri_clpm_syntax,
    compare_cross_lagged_models,
    extract_cross_lagged_effects,
    fit_cross_lagged_model,
    simulate_panel_data,
)
from src.psychometric.structural_equations import (
    test_cascade_asymmetry as check_cascade_asymmetry,
)


@pytest.fixture
def panel_data_asymmetric():
    """Panel data with known asymmetric cross-lagged effects.

    cl_frust_to_sat = -0.3, cl_sat_to_frust = 0.1
    N=500 for stable estimation.
    """
    return simulate_panel_data(
        n_persons=500,
        n_timepoints=4,
        true_params={
            "ar_frust": 0.3,
            "ar_sat": 0.3,
            "cl_frust_to_sat": -0.3,
            "cl_sat_to_frust": 0.1,
            "ri_var_frust": 1.0,
            "ri_var_sat": 1.0,
            "ri_cov": 0.0,
            "within_var": 0.3,
            "error_var": 0.1,
        },
        seed=42,
    )


@pytest.fixture
def panel_data_symmetric():
    """Panel data with equal cross-lagged effects (no asymmetry)."""
    return simulate_panel_data(
        n_persons=500,
        n_timepoints=4,
        true_params={
            "ar_frust": 0.3,
            "ar_sat": 0.3,
            "cl_frust_to_sat": -0.2,
            "cl_sat_to_frust": -0.2,
            "ri_var_frust": 1.0,
            "ri_var_sat": 1.0,
            "ri_cov": 0.0,
            "within_var": 0.3,
            "error_var": 0.1,
        },
        seed=42,
    )


@pytest.fixture
def panel_data_no_between():
    """Panel data with near-zero between-person variance (CLPM ~ RI-CLPM)."""
    return simulate_panel_data(
        n_persons=500,
        n_timepoints=4,
        true_params={
            "ar_frust": 0.3,
            "ar_sat": 0.3,
            "cl_frust_to_sat": -0.3,
            "cl_sat_to_frust": 0.1,
            "ri_var_frust": 0.01,
            "ri_var_sat": 0.01,
            "ri_cov": 0.0,
            "within_var": 0.5,
            "error_var": 0.1,
        },
        seed=42,
    )


class TestBuildCLPMSyntax:
    """Tests for CLPM syntax generation."""

    def test_syntax_contains_regression_paths(self):
        syntax = build_clpm_syntax(n_timepoints=3, domain="A")
        # Should have ~ for regression (but not just ~~)
        non_cov_lines = [line for line in syntax.split("\n") if "~" in line and "~~" not in line]
        assert len(non_cov_lines) > 0

    def test_syntax_has_correct_regression_count_3tp(self):
        """3 timepoints => 2 transitions => 2 lines per transition (f, s) = 4 regression lines.

        Each line has 2 predictors (AR + CL): e.g., fA_t2 ~ fA_t1 + sA_t1
        """
        syntax = build_clpm_syntax(n_timepoints=3, domain="A")
        regression_lines = [
            line for line in syntax.strip().split("\n") if "~" in line and "~~" not in line
        ]
        assert len(regression_lines) == 4

    def test_syntax_has_correct_regression_count_4tp(self):
        """4 timepoints => 3 transitions => 2 lines per transition = 6 regression lines."""
        syntax = build_clpm_syntax(n_timepoints=4, domain="A")
        regression_lines = [
            line for line in syntax.strip().split("\n") if "~" in line and "~~" not in line
        ]
        assert len(regression_lines) == 6

    def test_minimum_timepoints_raises_below_3(self):
        with pytest.raises(ValueError, match="at least 3"):
            build_clpm_syntax(n_timepoints=2, domain="A")

    def test_syntax_parseable_by_semopy(self):
        import semopy

        syntax = build_clpm_syntax(n_timepoints=3, domain="A")
        model = semopy.Model(syntax)
        assert model is not None

    def test_domain_label_in_syntax(self):
        syntax = build_clpm_syntax(n_timepoints=3, domain="B")
        assert "fB_t1" in syntax
        assert "sB_t1" in syntax


class TestBuildRICLPMSyntax:
    """Tests for RI-CLPM syntax generation."""

    def test_syntax_contains_random_intercepts(self):
        syntax = build_ri_clpm_syntax(n_timepoints=3, domain="A")
        assert "RI_fA" in syntax
        assert "RI_sA" in syntax

    def test_syntax_contains_zero_residual_constraints(self):
        syntax = build_ri_clpm_syntax(n_timepoints=3, domain="A")
        assert "0*fA_t1" in syntax

    def test_syntax_contains_within_person_latents(self):
        syntax = build_ri_clpm_syntax(n_timepoints=3, domain="A")
        assert "wfA1" in syntax
        assert "wsA1" in syntax

    def test_syntax_contains_orthogonality_constraints(self):
        syntax = build_ri_clpm_syntax(n_timepoints=3, domain="A")
        assert "RI_fA ~~ 0*wfA1" in syntax
        assert "RI_sA ~~ 0*wfA1" in syntax

    def test_syntax_parseable_by_semopy(self):
        import semopy

        syntax = build_ri_clpm_syntax(n_timepoints=4, domain="A")
        model = semopy.Model(syntax)
        assert model is not None

    def test_minimum_timepoints_raises_below_3(self):
        with pytest.raises(ValueError, match="at least 3"):
            build_ri_clpm_syntax(n_timepoints=2, domain="A")


class TestSimulatePanelData:
    """Tests for panel data generation."""

    def test_returns_dataframe(self):
        result = simulate_panel_data(n_persons=100, n_timepoints=3, seed=42)
        assert isinstance(result["data"], pd.DataFrame)

    def test_correct_shape(self):
        result = simulate_panel_data(n_persons=100, n_timepoints=4, seed=42)
        assert result["data"].shape == (100, 8)

    def test_column_names(self):
        result = simulate_panel_data(n_persons=100, n_timepoints=3, seed=42)
        expected = {"f1", "f2", "f3", "s1", "s2", "s3"}
        assert set(result["data"].columns) == expected

    def test_reproducible_with_seed(self):
        r1 = simulate_panel_data(n_persons=50, n_timepoints=3, seed=42)
        r2 = simulate_panel_data(n_persons=50, n_timepoints=3, seed=42)
        pd.testing.assert_frame_equal(r1["data"], r2["data"])

    def test_returns_true_params(self):
        result = simulate_panel_data(n_persons=50, n_timepoints=3, seed=42)
        assert "true_params" in result
        assert "cl_frust_to_sat" in result["true_params"]

    def test_minimum_timepoints_raises_below_3(self):
        with pytest.raises(ValueError, match="at least 3"):
            simulate_panel_data(n_persons=50, n_timepoints=2, seed=42)


class TestFitCrossLaggedModel:
    """Tests for model fitting."""

    def test_clpm_returns_fit_indices(self, panel_data_asymmetric):
        result = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        assert "fit_indices" in result
        assert "aic" in result["fit_indices"]

    def test_clpm_returns_structural_params(self, panel_data_asymmetric):
        result = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        assert "structural_params" in result
        assert len(result["structural_params"]) > 0

    def test_ri_clpm_returns_fit_indices(self, panel_data_asymmetric):
        result = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="ri_clpm",
        )
        assert "fit_indices" in result

    def test_invalid_model_type_raises(self, panel_data_asymmetric):
        with pytest.raises(ValueError, match="model_type must be"):
            fit_cross_lagged_model(
                panel_data_asymmetric["data"],
                n_timepoints=4,
                domain="A",
                model_type="invalid",
            )

    def test_returns_model_metadata(self, panel_data_asymmetric):
        result = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        assert result["model_type"] == "clpm"
        assert result["domain"] == "A"
        assert result["n_timepoints"] == 4


class TestExtractCrossLaggedEffects:
    """Tests for extracting cross-lagged coefficients."""

    def test_returns_both_directions(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        assert "frust_to_sat" in effects
        assert "sat_to_frust" in effects
        assert len(effects["frust_to_sat"]) > 0
        assert len(effects["sat_to_frust"]) > 0

    def test_returns_autoregressive_paths(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        assert "autoregressive_frust" in effects
        assert "autoregressive_sat" in effects
        assert len(effects["autoregressive_frust"]) > 0

    def test_effects_have_estimate_and_se(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        for effect in effects["frust_to_sat"]:
            assert "estimate" in effect
            assert "se" in effect
            assert "p_value" in effect

    def test_correct_number_of_effects_4tp(self, panel_data_asymmetric):
        """4 timepoints => 3 transitions => 3 effects per direction."""
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        assert len(effects["frust_to_sat"]) == 3
        assert len(effects["sat_to_frust"]) == 3
        assert len(effects["autoregressive_frust"]) == 3

    def test_ri_clpm_extracts_within_person_effects(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="ri_clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        assert len(effects["frust_to_sat"]) > 0


class TestParameterRecovery:
    """Tests that models recover known generating parameters."""

    def test_clpm_cross_lag_sign_recovery(self, panel_data_asymmetric):
        """CLPM should recover negative frust->sat cross-lag."""
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        # True cl_frust_to_sat = -0.3; recovered mean should be negative
        assert effects["mean_cl_frust_to_sat"] < 0, (
            f"Expected negative cross-lag, got {effects['mean_cl_frust_to_sat']}"
        )

    def test_clpm_autoregressive_sign_recovery(self, panel_data_asymmetric):
        """Recovered AR parameters should be positive (true = 0.3)."""
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        for ar in effects["autoregressive_frust"]:
            assert ar["estimate"] > 0, f"Expected positive AR, got {ar['estimate']}"

    def test_ri_clpm_cross_lag_sign_recovery(self, panel_data_asymmetric):
        """RI-CLPM should recover negative frust->sat cross-lag at within-person level."""
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="ri_clpm",
        )
        effects = extract_cross_lagged_effects(fitted)
        assert effects["mean_cl_frust_to_sat"] < 0, (
            f"Expected negative within-person cross-lag, got {effects['mean_cl_frust_to_sat']}"
        )


class TestCascadeAsymmetry:
    """Tests for the SDT cascade asymmetry detection."""

    def test_detects_asymmetry_when_present(self, panel_data_asymmetric):
        """With |cl_fs|=0.3 vs |cl_sf|=0.1, asymmetry should be confirmed.

        Uses RI-CLPM to separate within-person dynamics from between-person
        variance, which is necessary for recovering the true cross-lagged
        asymmetry from the data-generating process.
        """
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="ri_clpm",
        )
        result = check_cascade_asymmetry(fitted)
        assert result["asymmetry_confirmed"] is True

    def test_small_difference_when_symmetric(self, panel_data_symmetric):
        """When true effects are equal, difference should be small."""
        fitted = fit_cross_lagged_model(
            panel_data_symmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        result = check_cascade_asymmetry(fitted)
        assert result["difference"] < 0.15

    def test_returns_confidence_interval(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        result = check_cascade_asymmetry(fitted)
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert result["ci_lower"] is not None

    def test_returns_p_value(self, panel_data_asymmetric):
        fitted = fit_cross_lagged_model(
            panel_data_asymmetric["data"],
            n_timepoints=4,
            domain="A",
            model_type="clpm",
        )
        result = check_cascade_asymmetry(fitted)
        assert "p_value" in result
        assert result["p_value"] is not None


class TestCompareModels:
    """Tests for CLPM vs RI-CLPM comparison."""

    def test_returns_both_models(self, panel_data_asymmetric):
        result = compare_cross_lagged_models(
            panel_data_asymmetric["data"], n_timepoints=4, domain="A"
        )
        assert "clpm" in result
        assert "ri_clpm" in result

    def test_preferred_model_is_valid(self, panel_data_asymmetric):
        """Comparison should return a valid preferred model."""
        result = compare_cross_lagged_models(
            panel_data_asymmetric["data"], n_timepoints=4, domain="A"
        )
        assert result["preferred_model"] in ("clpm", "ri_clpm")

    def test_includes_delta_aic(self, panel_data_asymmetric):
        result = compare_cross_lagged_models(
            panel_data_asymmetric["data"], n_timepoints=4, domain="A"
        )
        assert "delta_aic" in result

    def test_includes_delta_bic(self, panel_data_asymmetric):
        result = compare_cross_lagged_models(
            panel_data_asymmetric["data"], n_timepoints=4, domain="A"
        )
        assert "delta_bic" in result


class TestEdgeCases:
    """Edge case tests."""

    def test_minimum_timepoints_3(self):
        """Model should work with T=3."""
        data = simulate_panel_data(n_persons=300, n_timepoints=3, seed=42)
        result = fit_cross_lagged_model(data["data"], n_timepoints=3, domain="A", model_type="clpm")
        assert result is not None
        assert "fit_indices" in result

    def test_small_sample(self):
        """Model should still fit with small N."""
        data = simulate_panel_data(n_persons=50, n_timepoints=4, seed=42)
        result = fit_cross_lagged_model(data["data"], n_timepoints=4, domain="A", model_type="clpm")
        assert result is not None

    def test_five_timepoints(self):
        """Model should scale to T=5."""
        data = simulate_panel_data(n_persons=300, n_timepoints=5, seed=42)
        result = fit_cross_lagged_model(data["data"], n_timepoints=5, domain="A", model_type="clpm")
        effects = extract_cross_lagged_effects(result)
        assert len(effects["frust_to_sat"]) == 4  # 5 timepoints => 4 transitions
