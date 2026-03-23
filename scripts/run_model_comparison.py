"""Run factor model comparison on synthetic data.

Reference: abc-assessment-spec Section 11.3 (CFA validation)
Reference: Reise (2012), Bifactor Models
Reference: Murphy et al. (2023), BPNSFS method artifacts

Fits CFA, bifactor, and method-factor models to synthetic data and
compares fit indices, omega coefficients, and method factor loadings.

Status: SYNTHETIC. Results reflect properties of simulated data only.

Usage:
    python scripts/run_model_comparison.py
"""

import sys
sys.path.insert(0, ".")

import numpy as np

from src.psychometric.factor_models import (
    compare_models,
    fit_bifactor_model,
    fit_cfa_model,
    fit_method_factor_model,
)

SEED = 42
N = 500
FACTORS = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
ITEM_NAMES = [f"{p}{i}" for p in ["AS", "AF", "BS", "BF", "CS", "CF"] for i in range(1, 5)]
FACTOR_MAP = {}
for f_idx, factor in enumerate(FACTORS):
    for i in range(4):
        FACTOR_MAP[f_idx * 4 + i] = factor
REVERSE_CODED = list(range(4, 8)) + list(range(12, 16)) + list(range(20, 24))


def generate_data(seed):
    """Generate clean 6-factor synthetic data."""
    rng = np.random.default_rng(seed)
    factors = rng.standard_normal((N, 6))
    data = np.zeros((N, 24))
    for f in range(6):
        for i in range(4):
            idx = f * 4 + i
            data[:, idx] = 0.7 * factors[:, f] + np.sqrt(0.51) * rng.standard_normal(N)
    return data


def main():
    print("=" * 70)
    print("ABC Assessment: Factor Model Comparison (SYNTHETIC DATA)")
    print("=" * 70)
    print()

    data = generate_data(SEED)

    # Fit models
    print("Fitting 6-factor CFA...")
    cfa = fit_cfa_model(data, ITEM_NAMES, FACTOR_MAP)

    print("Fitting bifactor model...")
    bifactor = fit_bifactor_model(data, ITEM_NAMES, FACTOR_MAP)

    print("Fitting method-factor model...")
    method = fit_method_factor_model(data, ITEM_NAMES, FACTOR_MAP, REVERSE_CODED)

    print()

    # Compare
    comparison = compare_models({"CFA (6-factor)": cfa, "Bifactor": bifactor, "Method Factor": method})

    print(f"{'Model':<20} {'CFI':>8} {'RMSEA':>8} {'AIC':>12} {'dAIC':>8}")
    print("-" * 60)
    for name, result in comparison.items():
        cfi = f"{result['cfi']:.3f}" if result.get("cfi") is not None else "N/A"
        rmsea = f"{result['rmsea']:.3f}" if result.get("rmsea") is not None else "N/A"
        aic = f"{result['aic']:.1f}" if result.get("aic") is not None else "N/A"
        daic = f"{result['delta_aic']:.1f}" if result.get("delta_aic") is not None else "N/A"
        print(f"{name:<20} {cfi:>8} {rmsea:>8} {aic:>12} {daic:>8}")

    print()

    # Bifactor diagnostics
    print("--- Bifactor Diagnostics ---")
    print(f"  Omega-h:  {bifactor['omega_h']:.3f}  (<0.50 = subscales meaningful)")
    print(f"  ECV:      {bifactor['ecv']:.3f}  (<0.60 = specific factors dominate)")
    print()
    print("  Omega-s per subscale:")
    for factor, omega_s in bifactor["omega_s"].items():
        print(f"    {factor}: {omega_s:.3f}")

    print()

    # Method factor
    print("--- Method Factor Diagnostics ---")
    rc_loadings = [abs(method["method_loadings"][i]) for i in REVERSE_CODED]
    fc_loadings = [abs(method["method_loadings"][i]) for i in range(24) if i not in REVERSE_CODED]
    print(f"  Mean |loading| on reverse-coded items: {np.mean(rc_loadings):.3f}")
    print(f"  Mean |loading| on forward-coded items: {np.mean(fc_loadings):.3f}")
    print(f"  Threshold for artifact (Murphy 2023):  0.30")
    if np.mean(rc_loadings) > 0.30:
        print("  WARNING: Method artifact detected. Frustration items may share")
        print("  method variance beyond their substantive factor.")
    else:
        print("  No method artifact detected.")

    print()
    print("WARNING: All results derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
