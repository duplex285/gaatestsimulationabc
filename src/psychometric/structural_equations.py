"""Cross-lagged panel SEM for ABC Assessment.

Implements basic CLPM and RI-CLPM (Random Intercepts Cross-Lagged Panel Model)
to formally test the frustration-to-satisfaction causal pathway detected by
the leading indicator model's trend analysis.

The basic CLPM estimates autoregressive and cross-lagged paths between
frustration and satisfaction across timepoints, but confounds between-person
stable differences with within-person temporal dynamics. The RI-CLPM
(Hamaker et al., 2015) partitions these two sources of variance by adding
random intercepts, so cross-lagged effects reflect true within-person
causal influence rather than stable individual differences.

Reference: Hamaker, Kuiper & Grasman (2015), A critique of the cross-lagged
           panel model, Psychological Methods, 20(1), 102-116.
Reference: Mulder & Hamaker (2021), Three extensions of the RI-CLPM
Reference: Usami, Murayama & Hamaker (2019), Unified framework
Reference: Berry & Willoughby (2017), On the practicality of the RI-CLPM
Reference: abc-assessment-spec Section 11.7 (trajectory detection targets)
"""

import numpy as np
import pandas as pd
import semopy
from scipy import stats

# Default true parameters for data generation (asymmetric cascade)
DEFAULT_TRUE_PARAMS = {
    "ar_frust": 0.3,
    "ar_sat": 0.3,
    "cl_frust_to_sat": -0.3,  # Negative: frustration predicts sat DECLINE
    "cl_sat_to_frust": 0.1,  # Weaker: asymmetric cascade per SDT
    "ri_var_frust": 1.0,
    "ri_var_sat": 1.0,
    "ri_cov": 0.0,
    "within_var": 0.3,
    "error_var": 0.1,
}


def _validate_timepoints(n_timepoints: int) -> None:
    """Raise ValueError if fewer than 3 timepoints."""
    if n_timepoints < 3:
        msg = f"Cross-lagged models require at least 3 timepoints, got {n_timepoints}"
        raise ValueError(msg)


def build_clpm_syntax(
    n_timepoints: int,
    domain: str,
) -> str:
    """Generate semopy model syntax for a basic Cross-Lagged Panel Model.

    Reference: Hamaker et al. (2015), Figure 1

    For T timepoints with two constructs (frustration, satisfaction) per domain:
    - Autoregressive paths: construct at t predicted by construct at t-1
    - Cross-lagged paths: each construct at t predicted by the other at t-1
    - Within-time correlations at t=1; within-time residual correlations at t>1

    Args:
        n_timepoints: number of measurement occasions (minimum 3)
        domain: domain label ('A', 'B', or 'C')

    Returns:
        semopy model description string
    """
    _validate_timepoints(n_timepoints)
    d = domain.upper()
    lines = []

    # Autoregressive and cross-lagged regressions
    for t in range(2, n_timepoints + 1):
        prev = t - 1
        lines.append(f"f{d}_t{t} ~ f{d}_t{prev} + s{d}_t{prev}")
        lines.append(f"s{d}_t{t} ~ s{d}_t{prev} + f{d}_t{prev}")

    # Within-time correlations
    for t in range(1, n_timepoints + 1):
        lines.append(f"f{d}_t{t} ~~ s{d}_t{t}")

    return "\n".join(lines)


def build_ri_clpm_syntax(
    n_timepoints: int,
    domain: str,
) -> str:
    """Generate semopy model syntax for a Random Intercepts CLPM.

    Reference: Hamaker, Kuiper & Grasman (2015)

    Separates between-person variance (random intercepts) from within-person
    dynamics (cross-lagged effects). Model components:
    1. Random intercepts with unit loadings on all observed timepoints
    2. Within-person latent variables at each timepoint
    3. Observed residual variances fixed to 0 (variance decomposed into RI + within)
    4. Cross-lagged structural paths on within-person latents
    5. Within-time correlations on within-person residuals
    6. Orthogonality: random intercepts uncorrelated with within-person latents at t=1

    Args:
        n_timepoints: number of measurement occasions (minimum 3)
        domain: domain label ('A', 'B', or 'C')

    Returns:
        semopy model description string
    """
    _validate_timepoints(n_timepoints)
    d = domain.upper()
    lines = []

    # Random intercepts (between-person stable differences)
    f_indicators = " + ".join(f"1*f{d}_t{t}" for t in range(1, n_timepoints + 1))
    s_indicators = " + ".join(f"1*s{d}_t{t}" for t in range(1, n_timepoints + 1))
    lines.append(f"RI_f{d} =~ {f_indicators}")
    lines.append(f"RI_s{d} =~ {s_indicators}")

    # Within-person latent variables
    for t in range(1, n_timepoints + 1):
        lines.append(f"wf{d}{t} =~ 1*f{d}_t{t}")
        lines.append(f"ws{d}{t} =~ 1*s{d}_t{t}")

    # Fix observed residual variances to 0
    for t in range(1, n_timepoints + 1):
        lines.append(f"f{d}_t{t} ~~ 0*f{d}_t{t}")
        lines.append(f"s{d}_t{t} ~~ 0*s{d}_t{t}")

    # Cross-lagged regressions on within-person latents
    for t in range(2, n_timepoints + 1):
        prev = t - 1
        lines.append(f"wf{d}{t} ~ wf{d}{prev} + ws{d}{prev}")
        lines.append(f"ws{d}{t} ~ ws{d}{prev} + wf{d}{prev}")

    # Within-time correlations on within-person latents
    for t in range(1, n_timepoints + 1):
        lines.append(f"wf{d}{t} ~~ ws{d}{t}")

    # Random intercept covariance
    lines.append(f"RI_f{d} ~~ RI_s{d}")

    # Orthogonality: RIs uncorrelated with within-person at t=1
    lines.append(f"RI_f{d} ~~ 0*wf{d}1")
    lines.append(f"RI_f{d} ~~ 0*ws{d}1")
    lines.append(f"RI_s{d} ~~ 0*wf{d}1")
    lines.append(f"RI_s{d} ~~ 0*ws{d}1")

    return "\n".join(lines)


def _extract_fit_indices_safe(model: semopy.Model) -> dict:
    """Extract fit indices from a fitted semopy model, with fallback.

    semopy.calc_stats() can fail on models with many fixed parameters
    (the baseline model may have zero free parameters). This wrapper
    catches failures and returns None for indices that cannot be computed.
    """
    result = {
        "chi2": None,
        "df": None,
        "cfi": None,
        "rmsea": None,
        "aic": None,
        "bic": None,
        "tli": None,
    }

    try:
        stat_table = semopy.calc_stats(model)
        stat_names = {
            "chi2": "chi2",
            "dof": "df",
            "CFI": "cfi",
            "RMSEA": "rmsea",
            "AIC": "aic",
            "BIC": "bic",
            "TLI": "tli",
        }
        for semopy_name, our_name in stat_names.items():
            if semopy_name in stat_table.columns:
                val = stat_table[semopy_name].values[0]
                result[our_name] = float(val) if not pd.isna(val) else None
    except Exception:
        # Fallback: try to extract AIC/BIC from model objective
        try:
            obj_val = model.last_result.fun if hasattr(model, "last_result") else None
            if obj_val is not None:
                n_obs = len(model.mx_data) if hasattr(model, "mx_data") else None
                n_params = len(model.param_vals) if hasattr(model, "param_vals") else None
                if n_obs is not None and n_params is not None:
                    log_lik = -0.5 * obj_val * n_obs
                    result["aic"] = 2 * n_params - 2 * log_lik
                    result["bic"] = n_params * np.log(n_obs) - 2 * log_lik
        except Exception:
            pass

    return result


def fit_cross_lagged_model(
    panel_data: pd.DataFrame,
    n_timepoints: int,
    domain: str,
    model_type: str = "ri_clpm",
) -> dict:
    """Fit a cross-lagged panel model and return results.

    Reference: Hamaker et al. (2015)

    Args:
        panel_data: DataFrame with columns matching model variables.
                    For composite scores: columns like 'fA_t1', 'fA_t2', ...,
                    'sA_t1', 'sA_t2', ...
        n_timepoints: number of measurement occasions
        domain: domain label ('A', 'B', or 'C')
        model_type: 'clpm' or 'ri_clpm' (default)

    Returns:
        dict with keys: model_type, domain, n_timepoints, fit_indices,
        structural_params, covariance_params, fitted_model
    """
    if model_type not in ("clpm", "ri_clpm"):
        msg = f"model_type must be 'clpm' or 'ri_clpm', got '{model_type}'"
        raise ValueError(msg)

    _validate_timepoints(n_timepoints)

    # Rename columns to match syntax expectations
    d = domain.upper()
    col_map = {}
    for t in range(1, n_timepoints + 1):
        col_map[f"f{t}"] = f"f{d}_t{t}"
        col_map[f"s{t}"] = f"s{d}_t{t}"
    df = panel_data.rename(columns=col_map)

    # Build and fit model
    if model_type == "clpm":
        syntax = build_clpm_syntax(n_timepoints, domain)
    else:
        syntax = build_ri_clpm_syntax(n_timepoints, domain)

    model = semopy.Model(syntax)
    model.fit(df)

    # Extract results
    fit_indices = _extract_fit_indices_safe(model)

    estimates = model.inspect()
    structural = estimates[estimates["op"] == "~"].copy()
    covariances = estimates[estimates["op"] == "~~"].copy()

    return {
        "model_type": model_type,
        "domain": domain,
        "n_timepoints": n_timepoints,
        "fit_indices": fit_indices,
        "structural_params": structural,
        "covariance_params": covariances,
        "fitted_model": model,
    }


def extract_cross_lagged_effects(fitted_result: dict) -> dict:
    """Extract cross-lagged coefficients from a fitted model result.

    Reference: Hamaker et al. (2015), Table 1

    Identifies autoregressive and cross-lagged paths, returns them with
    standard errors, z-values, and p-values.

    Args:
        fitted_result: output of fit_cross_lagged_model()

    Returns:
        dict with keys: frust_to_sat, sat_to_frust, autoregressive_frust,
        autoregressive_sat, mean_cl_frust_to_sat, mean_cl_sat_to_frust
    """
    structural = fitted_result["structural_params"]
    d = fitted_result["domain"].upper()
    n_t = fitted_result["n_timepoints"]
    model_type = fitted_result["model_type"]

    # Determine variable naming based on model type
    if model_type == "ri_clpm":
        f_prefix = f"wf{d}"
        s_prefix = f"ws{d}"
    else:
        f_prefix = f"f{d}_t"
        s_prefix = f"s{d}_t"

    frust_to_sat = []
    sat_to_frust = []
    ar_frust = []
    ar_sat = []

    for t in range(2, n_t + 1):
        prev = t - 1
        if model_type == "ri_clpm":
            f_curr = f"{f_prefix}{t}"
            s_curr = f"{s_prefix}{t}"
            f_prev = f"{f_prefix}{prev}"
            s_prev = f"{s_prefix}{prev}"
        else:
            f_curr = f"{f_prefix}{t}"
            s_curr = f"{s_prefix}{t}"
            f_prev = f"{f_prefix}{prev}"
            s_prev = f"{s_prefix}{prev}"

        # Cross-lag: frustration -> satisfaction (f_prev predicts s_curr)
        mask_fs = (structural["lval"] == s_curr) & (structural["rval"] == f_prev)
        rows_fs = structural[mask_fs]
        if len(rows_fs) > 0:
            row = rows_fs.iloc[0]
            frust_to_sat.append(_extract_effect(row, prev, t))

        # Cross-lag: satisfaction -> frustration (s_prev predicts f_curr)
        mask_sf = (structural["lval"] == f_curr) & (structural["rval"] == s_prev)
        rows_sf = structural[mask_sf]
        if len(rows_sf) > 0:
            row = rows_sf.iloc[0]
            sat_to_frust.append(_extract_effect(row, prev, t))

        # Autoregressive: frustration
        mask_ar_f = (structural["lval"] == f_curr) & (structural["rval"] == f_prev)
        rows_ar_f = structural[mask_ar_f]
        if len(rows_ar_f) > 0:
            row = rows_ar_f.iloc[0]
            ar_frust.append(_extract_effect(row, prev, t))

        # Autoregressive: satisfaction
        mask_ar_s = (structural["lval"] == s_curr) & (structural["rval"] == s_prev)
        rows_ar_s = structural[mask_ar_s]
        if len(rows_ar_s) > 0:
            row = rows_ar_s.iloc[0]
            ar_sat.append(_extract_effect(row, prev, t))

    mean_cl_fs = float(np.mean([e["estimate"] for e in frust_to_sat])) if frust_to_sat else 0.0
    mean_cl_sf = float(np.mean([e["estimate"] for e in sat_to_frust])) if sat_to_frust else 0.0

    return {
        "frust_to_sat": frust_to_sat,
        "sat_to_frust": sat_to_frust,
        "autoregressive_frust": ar_frust,
        "autoregressive_sat": ar_sat,
        "mean_cl_frust_to_sat": mean_cl_fs,
        "mean_cl_sat_to_frust": mean_cl_sf,
    }


def _extract_effect(row: pd.Series, from_t: int, to_t: int) -> dict:
    """Extract a single effect from a semopy estimates row."""
    estimate = float(row["Estimate"])
    se = (
        float(row["Std. Err"]) if "Std. Err" in row.index and not pd.isna(row["Std. Err"]) else None
    )
    z_val = (
        float(row["z-value"]) if "z-value" in row.index and not pd.isna(row["z-value"]) else None
    )
    p_val = (
        float(row["p-value"]) if "p-value" in row.index and not pd.isna(row["p-value"]) else None
    )

    return {
        "timepoints": (from_t, to_t),
        "estimate": estimate,
        "se": se,
        "z_value": z_val,
        "p_value": p_val,
    }


def compare_cross_lagged_models(
    panel_data: pd.DataFrame,
    n_timepoints: int,
    domain: str,
) -> dict:
    """Fit both CLPM and RI-CLPM and compare model fit.

    Reference: Burnham & Anderson (2002), Model Selection
    Reference: Hamaker et al. (2015)

    Args:
        panel_data: DataFrame with panel data
        n_timepoints: number of measurement occasions
        domain: domain label

    Returns:
        dict with keys: clpm, ri_clpm, preferred_model, delta_aic, delta_bic
    """
    clpm_result = fit_cross_lagged_model(panel_data, n_timepoints, domain, model_type="clpm")
    ri_clpm_result = fit_cross_lagged_model(panel_data, n_timepoints, domain, model_type="ri_clpm")

    clpm_aic = clpm_result["fit_indices"].get("aic")
    ri_aic = ri_clpm_result["fit_indices"].get("aic")
    clpm_bic = clpm_result["fit_indices"].get("bic")
    ri_bic = ri_clpm_result["fit_indices"].get("bic")

    delta_aic = None
    delta_bic = None
    preferred = "ri_clpm"  # default preference

    if ri_aic is not None and clpm_aic is not None:
        delta_aic = ri_aic - clpm_aic
        preferred = "ri_clpm" if delta_aic < 0 else "clpm"

    if ri_bic is not None and clpm_bic is not None:
        delta_bic = ri_bic - clpm_bic

    return {
        "clpm": clpm_result,
        "ri_clpm": ri_clpm_result,
        "preferred_model": preferred,
        "delta_aic": delta_aic,
        "delta_bic": delta_bic,
    }


def simulate_panel_data(
    n_persons: int = 300,
    n_timepoints: int = 4,
    true_params: dict | None = None,
    seed: int = 42,
) -> dict:
    """Generate synthetic longitudinal panel data with known cross-lagged effects.

    Reference: Hamaker et al. (2015), simulation study
    Reference: abc-assessment-spec Section 11.1 (simulation parameters)

    Generates data from a known RI-CLPM data-generating process:
    1. Between-person random intercepts from bivariate normal
    2. Within-person initial states from bivariate normal
    3. Within-person dynamics via AR + cross-lagged params + innovation noise
    4. Observed = between + within + measurement error

    Args:
        n_persons: number of simulated individuals
        n_timepoints: number of measurement occasions (>= 3)
        true_params: dict with generating parameters (see DEFAULT_TRUE_PARAMS)
        seed: random seed for reproducibility

    Returns:
        dict with keys: data (DataFrame), true_params, true_within, true_between
    """
    _validate_timepoints(n_timepoints)
    params = dict(DEFAULT_TRUE_PARAMS)
    if true_params is not None:
        params.update(true_params)

    rng = np.random.default_rng(seed)

    # Between-person random intercepts
    ri_cov_matrix = np.array(
        [
            [params["ri_var_frust"], params["ri_cov"]],
            [params["ri_cov"], params["ri_var_sat"]],
        ]
    )
    ri = rng.multivariate_normal([0, 0], ri_cov_matrix, n_persons)

    # Within-person dynamics
    wf = np.zeros((n_persons, n_timepoints))
    ws = np.zeros((n_persons, n_timepoints))

    # Initial within-person states
    w_init = rng.multivariate_normal(
        [0, 0],
        [[params["within_var"], 0], [0, params["within_var"]]],
        n_persons,
    )
    wf[:, 0] = w_init[:, 0]
    ws[:, 0] = w_init[:, 1]

    # Propagate dynamics
    for t in range(1, n_timepoints):
        innovation = rng.normal(0, np.sqrt(params["within_var"]), (n_persons, 2))
        wf[:, t] = (
            params["ar_frust"] * wf[:, t - 1]
            + params["cl_sat_to_frust"] * ws[:, t - 1]
            + innovation[:, 0]
        )
        ws[:, t] = (
            params["ar_sat"] * ws[:, t - 1]
            + params["cl_frust_to_sat"] * wf[:, t - 1]
            + innovation[:, 1]
        )

    # Observed = between + within + measurement error
    data = {}
    for t in range(n_timepoints):
        error = rng.normal(0, np.sqrt(params["error_var"]), (n_persons, 2))
        data[f"f{t + 1}"] = ri[:, 0] + wf[:, t] + error[:, 0]
        data[f"s{t + 1}"] = ri[:, 1] + ws[:, t] + error[:, 1]

    return {
        "data": pd.DataFrame(data),
        "true_params": params,
        "true_within": (wf, ws),
        "true_between": ri,
    }


def test_cascade_asymmetry(fitted_result: dict) -> dict:
    """Test whether frustration -> satisfaction cross-lag exceeds the reverse.

    Reference: Hamaker et al. (2015)
    Reference: Vansteenkiste & Ryan (2013), SDT cascade

    The SDT cascade hypothesis predicts that |cl_frust_to_sat| > |cl_sat_to_frust|.
    Tests this using the difference in cross-lagged coefficients and computes
    confidence intervals via the delta method.

    Args:
        fitted_result: output of fit_cross_lagged_model()

    Returns:
        dict with keys: asymmetry_confirmed, mean_cl_frust_to_sat,
        mean_cl_sat_to_frust, difference, ci_lower, ci_upper, p_value
    """
    effects = extract_cross_lagged_effects(fitted_result)

    mean_fs = effects["mean_cl_frust_to_sat"]
    mean_sf = effects["mean_cl_sat_to_frust"]

    # Asymmetry: |frust->sat| should exceed |sat->frust|
    abs_fs = abs(mean_fs)
    abs_sf = abs(mean_sf)
    difference = abs_fs - abs_sf

    # Compute SE of the difference using available SEs
    fs_effects = effects["frust_to_sat"]
    sf_effects = effects["sat_to_frust"]

    # Pool SEs across transitions
    fs_ses = [e["se"] for e in fs_effects if e["se"] is not None]
    sf_ses = [e["se"] for e in sf_effects if e["se"] is not None]

    if fs_ses and sf_ses:
        # SE of mean estimate
        se_fs = float(np.mean(fs_ses)) / np.sqrt(len(fs_ses))
        se_sf = float(np.mean(sf_ses)) / np.sqrt(len(sf_ses))
        # SE of difference (assuming independence of cross-lag directions)
        se_diff = np.sqrt(se_fs**2 + se_sf**2)

        z_val = difference / se_diff if se_diff > 0 else 0.0
        p_val = float(2 * (1 - stats.norm.cdf(abs(z_val))))
        ci_lower = difference - 1.96 * se_diff
        ci_upper = difference + 1.96 * se_diff
    else:
        se_diff = None
        z_val = None
        p_val = None
        ci_lower = None
        ci_upper = None

    # Confirmed if difference > 0.05 threshold
    asymmetry_confirmed = difference > 0.05

    return {
        "asymmetry_confirmed": asymmetry_confirmed,
        "mean_cl_frust_to_sat": mean_fs,
        "mean_cl_sat_to_frust": mean_sf,
        "difference": float(difference),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "p_value": p_val,
    }
