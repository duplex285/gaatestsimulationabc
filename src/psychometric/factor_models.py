"""Advanced factor analysis for ABC Assessment.

Fits CFA, bifactor, and method-factor models to test whether the
six-factor structure (3 domains x satisfaction/frustration) reflects
substantive constructs or item-keying artifacts.

Reference: Reise (2012), The Rediscovery of Bifactor Measurement Models
Reference: Asparouhov & Muthen (2009), ESEM
Reference: Murphy et al. (2023), BPNSFS method artifacts
Reference: Marsh (1996), Method Factor Models
"""

import numpy as np
import pandas as pd
import semopy

from src.psychometric.omega_coefficients import (
    compute_ecv,
    compute_omega_hierarchical,
    compute_omega_subscale,
)


def _data_to_df(data: np.ndarray, item_names: list[str]) -> pd.DataFrame:
    """Convert numpy array to DataFrame with item names as columns."""
    return pd.DataFrame(data, columns=item_names)


def _build_cfa_syntax(item_names: list[str], factor_map: dict[int, str]) -> str:
    """Build semopy model syntax for a standard CFA.

    Reference: abc-assessment-spec Section 1.2
    """
    # Group items by factor
    factors = {}
    for idx, factor in factor_map.items():
        if factor not in factors:
            factors[factor] = []
        factors[factor].append(item_names[idx])

    lines = []
    for factor, items in factors.items():
        lines.append(f"{factor} =~ " + " + ".join(items))

    return "\n".join(lines)


def _build_bifactor_syntax(item_names: list[str], factor_map: dict[int, str]) -> str:
    """Build semopy model syntax for a bifactor model.

    General factor loads on all items.
    Specific factors load on their respective items.
    All factors are orthogonal (uncorrelated).
    Factor variances fixed to 1 for identification.

    Reference: Reise (2012)
    """
    # Group items by factor
    factors = {}
    for idx, factor in factor_map.items():
        if factor not in factors:
            factors[factor] = []
        factors[factor].append(item_names[idx])

    lines = []

    # General factor loads on all items
    all_items = [item_names[idx] for idx in sorted(factor_map.keys())]
    lines.append("general =~ " + " + ".join(all_items))

    # Specific factors
    for factor, items in factors.items():
        lines.append(f"{factor} =~ " + " + ".join(items))

    # Fix all factor variances to 1 for identification
    lines.append("general ~~ 1*general")
    for factor in factors:
        lines.append(f"{factor} ~~ 1*{factor}")

    # Orthogonality constraints: all factors uncorrelated
    all_factor_names = ["general"] + list(factors.keys())
    for i in range(len(all_factor_names)):
        for j in range(i + 1, len(all_factor_names)):
            lines.append(f"{all_factor_names[i]} ~~ 0*{all_factor_names[j]}")

    return "\n".join(lines)


def _build_method_factor_syntax(
    item_names: list[str],
    factor_map: dict[int, str],
    reverse_coded_indices: list[int],
) -> str:
    """Build semopy model syntax for CFA with a method factor.

    Adds a method factor loading on all reverse-coded (frustration) items
    to test whether item-keying direction introduces systematic variance.

    Reference: Murphy et al. (2023)
    """
    # Start with standard CFA
    factors = {}
    for idx, factor in factor_map.items():
        if factor not in factors:
            factors[factor] = []
        factors[factor].append(item_names[idx])

    lines = []
    for factor, items in factors.items():
        lines.append(f"{factor} =~ " + " + ".join(items))

    # Method factor on reverse-coded items
    rc_items = [item_names[idx] for idx in reverse_coded_indices]
    lines.append("method_neg =~ " + " + ".join(rc_items))

    # Method factor uncorrelated with substantive factors
    for factor in factors:
        lines.append(f"method_neg ~~ 0*{factor}")

    return "\n".join(lines)


def _extract_fit_indices(model: semopy.Model) -> dict:
    """Extract fit indices from a fitted semopy model."""
    stats = semopy.calc_stats(model)

    result = {}
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
        if semopy_name in stats.columns:
            val = stats[semopy_name].values[0]
            result[our_name] = float(val) if not pd.isna(val) else None
        else:
            result[our_name] = None

    return result


def _extract_loadings(model: semopy.Model, item_names: list[str]) -> dict:
    """Extract factor loadings from a fitted semopy model."""
    estimates = model.inspect()
    loadings = {}

    # Filter to measurement model (=~ operator)
    measurement = estimates[estimates["op"] == "~"]

    for item in item_names:
        item_loadings = measurement[measurement["lval"] == item]
        if len(item_loadings) > 0:
            # Take the first loading (primary factor)
            loadings[item] = float(item_loadings.iloc[0]["Estimate"])
        else:
            loadings[item] = 0.0

    return loadings


def fit_cfa_model(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
) -> dict:
    """Fit a standard 6-factor CFA model.

    Reference: abc-assessment-spec Section 11.3 (CFA validation)

    Args:
        data: response matrix, shape (n_persons, n_items)
        item_names: list of item name strings
        factor_map: dict mapping item index to factor name

    Returns:
        dict with keys: chi2, df, cfi, rmsea, tli, aic, bic, loadings
    """
    df = _data_to_df(data, item_names)
    syntax = _build_cfa_syntax(item_names, factor_map)

    model = semopy.Model(syntax)
    model.fit(df)

    result = _extract_fit_indices(model)

    # Extract loadings per item
    estimates = model.inspect()
    measurement = estimates[estimates["op"] == "~"]
    loadings = {}
    for item in item_names:
        rows = measurement[measurement["lval"] == item]
        if len(rows) > 0:
            loadings[item] = float(rows.iloc[0]["Estimate"])
        else:
            loadings[item] = 0.0
    result["loadings"] = loadings

    return result


def fit_bifactor_model(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
) -> dict:
    """Fit a bifactor model with general factor + 6 specific factors.

    Reference: Reise (2012)

    Tests whether a general need-state factor underlies all items,
    or whether the 6 specific factors carry independent variance.

    Args:
        data: response matrix, shape (n_persons, n_items)
        item_names: list of item name strings
        factor_map: dict mapping item index to factor name

    Returns:
        dict with fit indices plus: general_loadings, specific_loadings,
        omega_h, omega_s (per factor), ecv
    """
    df = _data_to_df(data, item_names)
    syntax = _build_bifactor_syntax(item_names, factor_map)

    model = semopy.Model(syntax)
    model.fit(df)

    result = _extract_fit_indices(model)

    # Extract loadings
    estimates = model.inspect()
    measurement = estimates[estimates["op"] == "~"]

    general_loadings = {}
    specific_loadings = {}

    for item in item_names:
        rows = measurement[measurement["lval"] == item]
        gen_row = rows[rows["rval"] == "general"]
        if len(gen_row) > 0:
            general_loadings[item] = float(gen_row.iloc[0]["Estimate"])
        else:
            general_loadings[item] = 0.0

        # Specific loading: any factor that is not "general"
        spec_rows = rows[rows["rval"] != "general"]
        if len(spec_rows) > 0:
            specific_loadings[item] = float(spec_rows.iloc[0]["Estimate"])
        else:
            specific_loadings[item] = 0.0

    result["general_loadings"] = general_loadings
    result["specific_loadings"] = specific_loadings

    # Compute omega coefficients
    gen_arr = np.array([general_loadings[item] for item in item_names])
    spec_arr = np.array([specific_loadings[item] for item in item_names])

    result["omega_h"] = compute_omega_hierarchical(gen_arr, spec_arr)
    result["ecv"] = compute_ecv(gen_arr, spec_arr)

    # Omega-s per factor
    factors = {}
    for idx, factor in factor_map.items():
        if factor not in factors:
            factors[factor] = []
        factors[factor].append(idx)

    omega_s = {}
    for factor, indices in factors.items():
        gen_sub = np.array([gen_arr[i] for i in indices])
        spec_sub = np.array([spec_arr[i] for i in indices])
        omega_s[factor] = compute_omega_subscale(gen_sub, spec_sub)

    result["omega_s"] = omega_s

    return result


def fit_method_factor_model(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    reverse_coded_indices: list[int],
) -> dict:
    """Fit CFA with a method factor for item-keying direction.

    Reference: Murphy et al. (2023)
    Reference: Marsh (1996)

    Adds a method factor loading on all negatively-keyed (frustration)
    items to test whether the satisfaction/frustration distinction is
    a substantive construct or an artifact of item wording direction.

    Args:
        data: response matrix, shape (n_persons, n_items)
        item_names: list of item name strings
        factor_map: dict mapping item index to factor name
        reverse_coded_indices: indices of negatively-keyed items

    Returns:
        dict with fit indices plus method_loadings dict
    """
    df = _data_to_df(data, item_names)
    syntax = _build_method_factor_syntax(item_names, factor_map, reverse_coded_indices)

    model = semopy.Model(syntax)
    model.fit(df)

    result = _extract_fit_indices(model)

    # Extract method factor loadings
    estimates = model.inspect()
    measurement = estimates[estimates["op"] == "~"]

    method_loadings = {}
    for i, item in enumerate(item_names):
        rows = measurement[(measurement["lval"] == item) & (measurement["rval"] == "method_neg")]
        if len(rows) > 0:
            method_loadings[i] = float(rows.iloc[0]["Estimate"])
        else:
            method_loadings[i] = 0.0

    result["method_loadings"] = method_loadings

    return result


def compare_models(models: dict[str, dict]) -> dict:
    """Compare multiple fitted models on fit indices.

    Reference: Burnham & Anderson (2002), Model Selection

    Computes delta-AIC and delta-BIC relative to the best model.

    Args:
        models: dict mapping model name to fit result dict

    Returns:
        dict mapping model name to result dict with added delta_aic, delta_bic
    """
    result = {}

    # Find best AIC and BIC
    aics = {name: m.get("aic", float("inf")) for name, m in models.items()}
    bics = {name: m.get("bic", float("inf")) for name, m in models.items()}

    valid_aics = {k: v for k, v in aics.items() if v is not None}
    valid_bics = {k: v for k, v in bics.items() if v is not None}

    best_aic = min(valid_aics.values()) if valid_aics else 0
    best_bic = min(valid_bics.values()) if valid_bics else 0

    for name, model_result in models.items():
        entry = dict(model_result)
        aic = model_result.get("aic")
        bic = model_result.get("bic")
        entry["delta_aic"] = float(aic - best_aic) if aic is not None else None
        entry["delta_bic"] = float(bic - best_bic) if bic is not None else None
        result[name] = entry

    return result
