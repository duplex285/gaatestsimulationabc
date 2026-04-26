"""Advanced factor analysis for ABC Assessment.

Fits CFA, bifactor, ESEM-within-CFA, bifactor-ESEM, and method-factor
models to test whether the six-factor structure (3 domains x
satisfaction/frustration) reflects substantive constructs or
item-keying artifacts, and to test 1-G vs 2-G global structures.

Reference: Reise (2012), The Rediscovery of Bifactor Measurement Models
Reference: Asparouhov & Muthen (2009), ESEM
Reference: Marsh et al. (2014), ESEM-within-CFA approximation
Reference: Toth-Kiraly et al. (2018), bifactor-ESEM on BPNSFS
Reference: Murphy et al. (2023), BPNSFS method artifacts
Reference: Marsh (1996), Method Factor Models
"""

# factor_analyzer 0.5.x calls sklearn's check_array with the deprecated
# kwarg `force_all_finite`, which was removed in scikit-learn 1.7+.
# Patch the symbol that factor_analyzer imports so the call site works.
import factor_analyzer.factor_analyzer as _fam_module  # noqa: E402
import numpy as np
import pandas as pd
import semopy
from scipy import linalg as scipy_linalg
from sklearn.utils import check_array as _sklearn_check_array  # noqa: E402


def _patched_check_array(X, force_all_finite=None, **kwargs):  # type: ignore[no-untyped-def]
    """Translate the deprecated `force_all_finite` kwarg to `ensure_all_finite`.

    Reference: sklearn 1.7+ deprecation (factor_analyzer 0.5.x compatibility shim)
    """
    if force_all_finite is not None and "ensure_all_finite" not in kwargs:
        kwargs["ensure_all_finite"] = force_all_finite
    return _sklearn_check_array(X, **kwargs)


_fam_module.check_array = _patched_check_array

from factor_analyzer import FactorAnalyzer  # noqa: E402

from src.psychometric.omega_coefficients import (  # noqa: E402
    compute_ecv,
    compute_omega_hierarchical,
    compute_omega_subscale,
)

# ABC item-to-factor mapping (24 items, 4 per factor)
# Reference: abc-assessment-spec Section 1.2
ABC_FACTOR_MAP_24: dict[int, str] = {
    i: ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"][i // 4] for i in range(24)
}

# Valence mapping: even-indexed factor groups (a_sat, b_sat, c_sat) are 'sat',
# odd-indexed (a_frust, b_frust, c_frust) are 'frust'.
# Reference: abc-assessment-spec Section 1.2
ABC_VALENCE_MAP_24: dict[int, str] = {
    i: ("sat" if (i // 4) % 2 == 0 else "frust") for i in range(24)
}


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


# --------------------------------------------------------------------------
# ESEM-within-CFA (Marsh et al. 2014)
# Reference: howard-2024-implementation-plan.md V2-B WI-2
# Reference: Asparouhov & Muthen (2009)
# --------------------------------------------------------------------------


def _build_target_matrix(
    item_names: list[str],
    factor_map: dict[int, str],
    factor_order: list[str],
) -> np.ndarray:
    """Construct the Procrustes target loading pattern.

    Each item's target loading is 1.0 on its hypothesized factor and
    0.0 on all other factors.

    Reference: Marsh et al. (2014)
    """
    n_items = len(item_names)
    n_factors = len(factor_order)
    target = np.zeros((n_items, n_factors))
    factor_to_col = {f: j for j, f in enumerate(factor_order)}
    for idx in range(n_items):
        f = factor_map[idx]
        target[idx, factor_to_col[f]] = 1.0
    return target


def _procrustes_rotate(unrotated: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Closed-form orthogonal Procrustes rotation toward `target`.

    Returns the rotated loading matrix L_rot = L_unrot @ R, where
    R = U @ V.T from SVD(target.T @ L_unrot).

    Reference: Schoenemann (1966), A generalized solution of the orthogonal
    Procrustes problem
    Reference: Marsh et al. (2014)
    """
    # SVD of target.T @ unrotated
    M = target.T @ unrotated
    U, _, Vt = scipy_linalg.svd(M, full_matrices=False)
    R = Vt.T @ U.T  # rotation that maps unrotated toward target
    return unrotated @ R


def _interfactor_correlations_from_inspect(
    estimates: pd.DataFrame, factor_names: list[str]
) -> dict[str, float]:
    """Extract pairwise correlations among latent factors from semopy inspect output.

    Reference: semopy.Model.inspect() variance/covariance rows (op == '~~')
    """
    cov = estimates[estimates["op"] == "~~"]
    var = {}
    for f in factor_names:
        rows = cov[(cov["lval"] == f) & (cov["rval"] == f)]
        if len(rows) > 0:
            var[f] = float(rows.iloc[0]["Estimate"])
        else:
            var[f] = float("nan")

    correlations: dict[str, float] = {}
    for i in range(len(factor_names)):
        for j in range(i + 1, len(factor_names)):
            fi = factor_names[i]
            fj = factor_names[j]
            row = cov[
                ((cov["lval"] == fi) & (cov["rval"] == fj))
                | ((cov["lval"] == fj) & (cov["rval"] == fi))
            ]
            if len(row) == 0:
                continue
            covariance = float(row.iloc[0]["Estimate"])
            denom = float(np.sqrt(max(var[fi], 1e-12) * max(var[fj], 1e-12)))
            if denom > 0 and np.isfinite(denom):
                correlations[f"{fi}~{fj}"] = covariance / denom
    return correlations


def _extract_interfactor_correlations_cfa(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
) -> dict[str, float]:
    """Helper for tests: fit a strict CFA and return interfactor correlations.

    Reference: abc-assessment-spec Section 11.3 (CFA validation)
    """
    df = _data_to_df(data, item_names)
    syntax = _build_cfa_syntax(item_names, factor_map)
    model = semopy.Model(syntax)
    model.fit(df)
    estimates = model.inspect()
    factor_order = list(dict.fromkeys(factor_map[i] for i in sorted(factor_map)))
    return _interfactor_correlations_from_inspect(estimates, factor_order)


def fit_esem_model(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    cross_loading_threshold: float = 0.10,
) -> dict:
    """Fit ESEM-within-CFA approximation via target-rotated EFA.

    NOT full-information ML ESEM (which requires Mplus or lavaan).
    This is the three-step middle path:
      1. Unrotated ML EFA via factor_analyzer.
      2. Closed-form orthogonal Procrustes rotation toward a binary target
         pattern (1.0 on hypothesized factor, 0.0 elsewhere).
      3. Re-fit in semopy as a CFA-with-cross-loadings (EwC), freeing each
         cross-loading whose Procrustes-rotated absolute value exceeds
         `cross_loading_threshold`. Fit indices come from this semopy model.

    Reference: howard-2024-implementation-plan.md V2-B WI-2
    Reference: Asparouhov & Muthen (2009)
    Reference: Marsh et al. (2014), ESEM-within-CFA approximation

    Args:
        data: response matrix, shape (n_persons, n_items)
        item_names: list of item name strings
        factor_map: dict mapping item index to factor name
        cross_loading_threshold: minimum |loading| in the rotated EFA pattern
            below which a cross-loading is left fixed at zero in the EwC re-fit

    Returns:
        dict with keys:
            chi2, df, cfi, rmsea, tli, aic, bic
            loadings: dict[item -> primary loading on its hypothesized factor]
            cross_loadings: dict[item -> dict[other_factor -> loading]]
            interfactor_correlations: dict["fi~fj" -> r]
    """
    n_items = len(item_names)
    factor_order = list(dict.fromkeys(factor_map[i] for i in sorted(factor_map)))
    n_factors = len(factor_order)

    # Step 1: unrotated ML EFA
    # Reference: howard-2024-implementation-plan.md V2-B WI-2 step 1
    fa = FactorAnalyzer(n_factors=n_factors, rotation=None, method="ml")
    fa.fit(data)
    unrotated = np.asarray(fa.loadings_)  # shape (n_items, n_factors)

    # Step 2: Procrustes rotation toward binary target
    # Reference: howard-2024-implementation-plan.md V2-B WI-2 step 2
    target = _build_target_matrix(item_names, factor_map, factor_order)
    rotated = _procrustes_rotate(unrotated, target)

    # Determine which cross-loadings to free in the EwC re-fit
    # Reference: howard-2024-implementation-plan.md V2-B WI-2 step 3
    factor_to_col = {f: j for j, f in enumerate(factor_order)}
    free_cross: dict[str, list[str]] = {f: [] for f in factor_order}
    for i in range(n_items):
        primary_factor = factor_map[i]
        for f in factor_order:
            if f == primary_factor:
                continue
            if abs(rotated[i, factor_to_col[f]]) > cross_loading_threshold:
                free_cross[f].append(item_names[i])

    # Build EwC syntax: each factor gets its primary indicators plus the
    # freed cross-loaded items. Factor variances scaled by first-indicator
    # marker convention (semopy default).
    items_by_factor: dict[str, list[str]] = {f: [] for f in factor_order}
    for i in range(n_items):
        items_by_factor[factor_map[i]].append(item_names[i])

    lines: list[str] = []
    for f in factor_order:
        primaries = items_by_factor[f]
        crosses = free_cross[f]
        all_indicators = primaries + [c for c in crosses if c not in primaries]
        if not all_indicators:
            continue
        lines.append(f"{f} =~ " + " + ".join(all_indicators))
    syntax = "\n".join(lines)

    df = _data_to_df(data, item_names)
    model = semopy.Model(syntax)
    model.fit(df)

    result = _extract_fit_indices(model)
    estimates = model.inspect()
    measurement = estimates[estimates["op"] == "~"]

    # Primary loadings: each item's loading on its hypothesized factor
    loadings: dict[str, float] = {}
    cross_loadings: dict[str, dict[str, float]] = {}
    for i, item in enumerate(item_names):
        primary_factor = factor_map[i]
        rows = measurement[measurement["lval"] == item]
        primary_row = rows[rows["rval"] == primary_factor]
        loadings[item] = float(primary_row.iloc[0]["Estimate"]) if len(primary_row) > 0 else 0.0
        item_cross: dict[str, float] = {}
        for _, r in rows.iterrows():
            f = r["rval"]
            if f == primary_factor:
                continue
            if f in factor_order:
                item_cross[f] = float(r["Estimate"])
        if item_cross:
            cross_loadings[item] = item_cross

    interfactor = _interfactor_correlations_from_inspect(estimates, factor_order)

    result["loadings"] = loadings
    result["cross_loadings"] = cross_loadings
    result["interfactor_correlations"] = interfactor
    return result


# --------------------------------------------------------------------------
# Bifactor-ESEM: 1-G vs 2-G global structure
# Reference: howard-2024-implementation-plan.md V2-B WI-8
# Reference: Toth-Kiraly et al. (2018)
# --------------------------------------------------------------------------


def _bifactor_esem_target(
    item_names: list[str],
    factor_map: dict[int, str],
    valence_map: dict[int, str],
    g_factors: list[str],
    specific_factors: list[str],
) -> tuple[np.ndarray, list[str]]:
    """Build the Procrustes target for a bifactor-ESEM rotation.

    Columns are ordered as g_factors followed by specific_factors. For each
    item, the target on its assigned global factor(s) is +1.0 (or -1.0 for
    1-G frust items, encoding the bipolar hypothesis), and +1.0 on its
    specific factor; all other entries are 0.0.

    Reference: Toth-Kiraly et al. (2018)
    """
    n_items = len(item_names)
    factor_order = g_factors + specific_factors
    target = np.zeros((n_items, len(factor_order)))
    col = {f: j for j, f in enumerate(factor_order)}

    for i in range(n_items):
        # Specific-factor entry
        target[i, col[factor_map[i]]] = 1.0
        # Global-factor entry
        if len(g_factors) == 1:
            g = g_factors[0]
            sign = 1.0 if valence_map[i] == "sat" else -1.0
            target[i, col[g]] = sign
        else:
            # 2-G: route by valence
            g = "sat_g" if valence_map[i] == "sat" else "frust_g"
            target[i, col[g]] = 1.0
    return target, factor_order


def _fit_bifactor_esem_inner(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    valence_map: dict[int, str],
    g_factors: list[str],
    cross_loading_threshold: float,
    g_g_orthogonal: bool,
) -> dict:
    """Shared core for 1-G and 2-G bifactor-ESEM fits.

    Reference: howard-2024-implementation-plan.md V2-B WI-8
    Reference: Toth-Kiraly et al. (2018)
    """
    n_items = len(item_names)
    specific_factors = list(dict.fromkeys(factor_map[i] for i in sorted(factor_map)))
    n_total = len(g_factors) + len(specific_factors)

    # Step 1: unrotated ML EFA with (G + specific) factors
    fa = FactorAnalyzer(n_factors=n_total, rotation=None, method="ml")
    fa.fit(data)
    unrotated = np.asarray(fa.loadings_)

    # Step 2: Procrustes toward bifactor target
    target, factor_order = _bifactor_esem_target(
        item_names, factor_map, valence_map, g_factors, specific_factors
    )
    rotated = _procrustes_rotate(unrotated, target)
    col = {f: j for j, f in enumerate(factor_order)}

    # Step 3: EwC re-fit. Each item is anchored on its primary specific factor
    # and on its hypothesized G factor(s). Cross-loadings on other specifics
    # and (in 2-G) the other G are freed when |rotated| > threshold.
    items_by_factor: dict[str, list[str]] = {f: [] for f in factor_order}
    # Primary anchors
    for i in range(n_items):
        items_by_factor[factor_map[i]].append(item_names[i])
        if len(g_factors) == 1:
            items_by_factor[g_factors[0]].append(item_names[i])
        else:
            g = "sat_g" if valence_map[i] == "sat" else "frust_g"
            items_by_factor[g].append(item_names[i])
    # Free cross-loadings exceeding threshold
    for i in range(n_items):
        primary_specific = factor_map[i]
        if len(g_factors) == 1:
            primary_g = g_factors[0]
        else:
            primary_g = "sat_g" if valence_map[i] == "sat" else "frust_g"
        for f in factor_order:
            if f in (primary_specific, primary_g):
                continue
            if (
                abs(rotated[i, col[f]]) > cross_loading_threshold
                and item_names[i] not in items_by_factor[f]
            ):
                items_by_factor[f].append(item_names[i])

    lines: list[str] = []
    for f in factor_order:
        indicators = items_by_factor[f]
        if not indicators:
            continue
        lines.append(f"{f} =~ " + " + ".join(indicators))

    # Orthogonality: specific factors uncorrelated with each other and with G
    # factors (standard bifactor identification). G-G covariance is freed in
    # the 2-G case unless `g_g_orthogonal` is True.
    for i in range(len(factor_order)):
        for j in range(i + 1, len(factor_order)):
            fi = factor_order[i]
            fj = factor_order[j]
            both_g = fi in g_factors and fj in g_factors
            if both_g and not g_g_orthogonal:
                # Free correlation between sat_g and frust_g
                lines.append(f"{fi} ~~ {fj}")
            else:
                lines.append(f"{fi} ~~ 0*{fj}")

    syntax = "\n".join(lines)
    df = _data_to_df(data, item_names)
    model = semopy.Model(syntax)
    model.fit(df)

    result = _extract_fit_indices(model)
    estimates = model.inspect()
    measurement = estimates[estimates["op"] == "~"]

    # G-loading per item on its assigned G factor
    g_loadings: dict[str, float] = {}
    for i, item in enumerate(item_names):
        if len(g_factors) == 1:
            g_name = g_factors[0]
        else:
            g_name = "sat_g" if valence_map[i] == "sat" else "frust_g"
        rows = measurement[(measurement["lval"] == item) & (measurement["rval"] == g_name)]
        g_loadings[item] = float(rows.iloc[0]["Estimate"]) if len(rows) > 0 else 0.0

    # Specific-factor loadings (primary)
    spec_loadings: dict[str, float] = {}
    for i, item in enumerate(item_names):
        f = factor_map[i]
        rows = measurement[(measurement["lval"] == item) & (measurement["rval"] == f)]
        spec_loadings[item] = float(rows.iloc[0]["Estimate"]) if len(rows) > 0 else 0.0

    result["g_loadings"] = g_loadings
    result["specific_loadings"] = spec_loadings
    result["g_factors"] = list(g_factors)

    # G-G correlation in 2-G models
    if len(g_factors) == 2 and not g_g_orthogonal:
        cov_rows = estimates[estimates["op"] == "~~"]
        var = {}
        for g in g_factors:
            rows = cov_rows[(cov_rows["lval"] == g) & (cov_rows["rval"] == g)]
            var[g] = float(rows.iloc[0]["Estimate"]) if len(rows) > 0 else float("nan")
        cov_row = cov_rows[
            ((cov_rows["lval"] == g_factors[0]) & (cov_rows["rval"] == g_factors[1]))
            | ((cov_rows["lval"] == g_factors[1]) & (cov_rows["rval"] == g_factors[0]))
        ]
        if len(cov_row) > 0 and np.all(np.isfinite(list(var.values()))):
            covariance = float(cov_row.iloc[0]["Estimate"])
            denom = float(np.sqrt(max(var[g_factors[0]], 1e-12) * max(var[g_factors[1]], 1e-12)))
            r_gg = covariance / denom if denom > 0 else None
            if r_gg is not None and np.isfinite(r_gg):
                # Clamp to [-1, 1] for any minor over-shoot from estimation noise
                r_gg = float(max(-1.0, min(1.0, r_gg)))
            result["g_g_correlation"] = r_gg
        else:
            result["g_g_correlation"] = None
    else:
        result["g_g_correlation"] = None

    return result


def fit_one_g_bifactor_esem(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    valence_map: dict[int, str],
    cross_loading_threshold: float = 0.10,
) -> dict:
    """Bifactor-ESEM with one global need-fulfillment continuum factor.

    Sat items load positive on G; frust items load negative on G (after sign
    correction in the Procrustes target). Six specific factors orthogonal to
    G and to each other.

    Reference: howard-2024-implementation-plan.md V2-B WI-8
    Reference: Toth-Kiraly et al. (2018), bifactor-ESEM on BPNSFS

    Returns:
        dict with fit indices and: g_loadings, specific_loadings, g_factors
    """
    return _fit_bifactor_esem_inner(
        data,
        item_names,
        factor_map,
        valence_map,
        g_factors=["g"],
        cross_loading_threshold=cross_loading_threshold,
        g_g_orthogonal=False,  # only one G; flag has no effect
    )


def fit_two_g_bifactor_esem(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    valence_map: dict[int, str],
    cross_loading_threshold: float = 0.10,
) -> dict:
    """Bifactor-ESEM with two correlated global factors (sat_g, frust_g).

    Sat items load on sat_g; frust items load on frust_g. Six specific
    factors orthogonal to both Gs and to each other. sat_g and frust_g
    correlate freely.

    Reference: howard-2024-implementation-plan.md V2-B WI-8
    Reference: Toth-Kiraly et al. (2018), 1-G vs 2-G comparison

    Returns:
        dict with fit indices and: g_loadings, specific_loadings,
        g_factors, g_g_correlation
    """
    return _fit_bifactor_esem_inner(
        data,
        item_names,
        factor_map,
        valence_map,
        g_factors=["sat_g", "frust_g"],
        cross_loading_threshold=cross_loading_threshold,
        g_g_orthogonal=False,
    )


def compare_one_g_two_g(
    data: np.ndarray,
    item_names: list[str],
    factor_map: dict[int, str],
    valence_map: dict[int, str],
    cross_loading_threshold: float = 0.10,
) -> dict:
    """Run both 1-G and 2-G bifactor-ESEM models and recommend a structure.

    Decision rule (Toth-Kiraly et al. 2018):
      - "1-G" if delta_bic > 10 favoring 1-G AND the G-factor loadings show
        a bipolar pattern (positive on sat items, negative on frust items
        in the majority).
      - "2-G" if 2-G has substantially better BIC AND |G-G correlation| < 0.5.
      - "ambiguous" otherwise.

    Reference: howard-2024-implementation-plan.md V2-B WI-8
    Reference: Toth-Kiraly et al. (2018)

    Returns:
        dict with keys:
            one_g, two_g: per-model result dicts
            delta_bic: bic(1-G) - bic(2-G)  (positive = 2-G preferred)
            g_g_correlation: from the 2-G model
            recommendation: '1-G' | '2-G' | 'ambiguous'
            rationale: human-readable explanation
    """
    one_g = fit_one_g_bifactor_esem(
        data, item_names, factor_map, valence_map, cross_loading_threshold
    )
    two_g = fit_two_g_bifactor_esem(
        data, item_names, factor_map, valence_map, cross_loading_threshold
    )

    bic_1 = one_g.get("bic")
    bic_2 = two_g.get("bic")
    delta_bic = float(bic_1 - bic_2) if (bic_1 is not None and bic_2 is not None) else None

    r_gg = two_g.get("g_g_correlation")

    # Bipolar pattern check on the 1-G G-loadings
    sat_pos = 0
    sat_total = 0
    frust_neg = 0
    frust_total = 0
    for i, item in enumerate(item_names):
        v = valence_map[i]
        loading = one_g["g_loadings"].get(item, 0.0)
        if v == "sat":
            sat_total += 1
            if loading > 0:
                sat_pos += 1
        else:
            frust_total += 1
            if loading < 0:
                frust_neg += 1
    bipolar = (
        sat_total > 0
        and frust_total > 0
        and (sat_pos / sat_total) >= 0.75
        and (frust_neg / frust_total) >= 0.75
    )

    recommendation = "ambiguous"
    rationale_parts: list[str] = []
    if delta_bic is None:
        rationale_parts.append("BIC unavailable for at least one model.")
    else:
        # delta_bic = bic(1G) - bic(2G); positive means 2-G has lower BIC
        if delta_bic < -10 and bipolar:
            recommendation = "1-G"
            rationale_parts.append(
                f"BIC favors 1-G by {-delta_bic:.1f} (>10) and G-loadings are bipolar "
                f"({sat_pos}/{sat_total} sat positive, {frust_neg}/{frust_total} "
                "frust negative)."
            )
        elif delta_bic > 10 and (r_gg is not None and abs(r_gg) < 0.5):
            recommendation = "2-G"
            rationale_parts.append(
                f"BIC favors 2-G by {delta_bic:.1f} (>10) and |r(sat_g, frust_g)| = "
                f"{abs(r_gg):.2f} < 0.5."
            )
        else:
            rationale_parts.append(
                f"delta_bic = {delta_bic:.1f}; bipolar = {bipolar}; "
                f"r(sat_g, frust_g) = {r_gg if r_gg is None else round(r_gg, 3)}."
            )

    return {
        "one_g": one_g,
        "two_g": two_g,
        "delta_bic": delta_bic,
        "g_g_correlation": r_gg,
        "recommendation": recommendation,
        "rationale": " ".join(rationale_parts),
    }
