"""Build population norms from synthetic stratified data.

Reference: abc-assessment-spec Section 2.1
Reference: PROMIS scoring manual (T-score: mean=50, SD=10)

Generates a stratified synthetic athlete population, computes T-scores
and percentile ranks, builds norm tables per stratum, and demonstrates
severity band assignment.

Status: SYNTHETIC. All norms must be replaced with empirical data.

Usage:
    python scripts/build_norms.py
"""

import sys
sys.path.insert(0, ".")

import numpy as np

from src.psychometric.norming import (
    assign_severity_bands,
    build_stratified_norms,
    compute_percentile_ranks,
    compute_t_scores,
)
from src.psychometric.norming_simulation import simulate_stratified_population

SEED = 42
SUBSCALES = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]


def main():
    print("=" * 70)
    print("ABC Assessment: Population Norms (SYNTHETIC DATA)")
    print("=" * 70)
    print()

    # Generate population
    pop = simulate_stratified_population(seed=SEED)
    total_n = len(pop["a_sat"])
    print(f"Generated {total_n} synthetic athletes across {len(set(pop['level']))} strata")
    print()

    # Build stratified norms
    norms = build_stratified_norms(pop, stratification_var="level", score_columns=SUBSCALES)

    # --- Overall norms ---
    print("--- Overall Norms (reference population) ---")
    print()
    print(f"  {'Subscale':<12} {'Mean':>8} {'SD':>8} {'N':>6}")
    print("  " + "-" * 36)
    for sub in SUBSCALES:
        stats = norms["overall"][sub]
        print(f"  {sub:<12} {stats['mean']:>8.2f} {stats['sd']:>8.2f} {stats['n']:>6}")
    print()

    # --- Per-stratum norms ---
    strata = [s for s in norms if s != "overall"]
    for stratum in sorted(strata):
        print(f"--- {stratum.capitalize()} Norms ---")
        print(f"  {'Subscale':<12} {'Mean':>8} {'SD':>8} {'N':>6}")
        print("  " + "-" * 36)
        for sub in SUBSCALES:
            stats = norms[stratum][sub]
            print(f"  {sub:<12} {stats['mean']:>8.2f} {stats['sd']:>8.2f} {stats['n']:>6}")
        print()

    # --- T-score demonstration ---
    print("--- T-Score Conversion Examples ---")
    print("    Using overall norms as reference")
    print()
    example_scores = np.array([2.0, 4.0, 5.0, 6.0, 8.0])
    ref_mean = norms["overall"]["a_sat"]["mean"]
    ref_sd = norms["overall"]["a_sat"]["sd"]
    t_scores = compute_t_scores(example_scores, ref_mean, ref_sd)
    ref_dist = np.array(pop["a_sat"])
    percentiles = compute_percentile_ranks(example_scores, ref_dist)
    bands = assign_severity_bands(t_scores)

    print(f"  {'Raw Score':>10} {'T-Score':>10} {'Percentile':>12} {'Band':>20}")
    print("  " + "-" * 56)
    for raw, t, pct, band in zip(example_scores, t_scores, percentiles, bands):
        print(f"  {raw:>10.1f} {t:>10.1f} {pct:>12.1f} {band:>20}")

    print()

    # --- Validation gate check ---
    print("--- Validation Gate Check ---")
    t_all = compute_t_scores(ref_dist, ref_mean, ref_sd)
    t_mean = np.mean(t_all)
    t_sd = np.std(t_all)
    mean_ok = abs(t_mean - 50.0) < 2.0
    sd_ok = abs(t_sd - 10.0) < 1.5
    print(f"  T-score mean: {t_mean:.2f} (target: 50.0 +/- 2.0) {'PASS' if mean_ok else 'FAIL'}")
    print(f"  T-score SD:   {t_sd:.2f} (target: 10.0 +/- 1.5) {'PASS' if sd_ok else 'FAIL'}")

    min_n = min(norms[s]["a_sat"]["n"] for s in strata)
    n_ok = min_n >= 100
    print(f"  Min stratum N: {min_n} (target: >= 100) {'PASS' if n_ok else 'FAIL'}")

    print()
    print("WARNING: All norms derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
