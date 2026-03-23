"""Derive empirical thresholds via ROC analysis on simulated data.

Reference: abc-assessment-spec Section 2.2 (domain state thresholds)
Reference: Swets (1988), Youden (1950), Jacobson & Truax (1991)

Generates simulated criterion data (burnout inventory scores) correlated
with ABC frustration subscale scores, then derives optimal classification
thresholds via ROC analysis with Youden's J statistic. Outputs a comparison
table of fixed vs. empirically derived thresholds.

Status: SYNTHETIC. All thresholds are derived from simulated data and must
be replaced with empirically validated thresholds before clinical use.

Usage:
    python scripts/derive_thresholds.py
"""

import sys
sys.path.insert(0, ".")

import numpy as np

from src.psychometric.criterion_simulation import simulate_criterion_scores
from src.psychometric.threshold_derivation import (
    bootstrap_threshold_ci,
    compute_roc_curve,
    youden_index_optimal_cutoff,
)

SEED = 42
N_PERSONS = 1000
N_BOOTSTRAP = 2000


def main():
    rng = np.random.default_rng(SEED)

    print("=" * 70)
    print("ABC Assessment: Empirical Threshold Derivation (SYNTHETIC DATA)")
    print("=" * 70)
    print()

    # --- Frustration threshold (predicting burnout) ---
    print("--- Frustration Threshold (Burnout Prediction) ---")
    print()

    # Simulate ABC frustration scores on 0-10 scale
    # Non-burnout athletes: frustration centered at 3.5
    # Burnout athletes: frustration centered at 6.0
    n_half = N_PERSONS // 2
    frust_non_burnout = rng.normal(3.5, 1.5, size=n_half)
    frust_burnout = rng.normal(6.0, 1.5, size=n_half)
    frust_scores = np.clip(np.concatenate([frust_non_burnout, frust_burnout]), 0, 10)
    burnout_criterion = np.concatenate([np.zeros(n_half), np.ones(n_half)])

    roc_frust = compute_roc_curve(frust_scores, burnout_criterion)
    youden_frust = youden_index_optimal_cutoff(
        roc_frust["fpr"], roc_frust["tpr"], roc_frust["thresholds"]
    )
    ci_frust = bootstrap_threshold_ci(
        frust_scores, burnout_criterion, n_bootstrap=N_BOOTSTRAP, seed=SEED
    )

    print(f"  AUC:                 {roc_frust['auc']:.3f}")
    print(f"  Optimal threshold:   {youden_frust['optimal_threshold']:.2f}")
    print(f"  Sensitivity:         {youden_frust['sensitivity']:.3f}")
    print(f"  Specificity:         {youden_frust['specificity']:.3f}")
    print(f"  Youden's J:          {youden_frust['youden_j']:.3f}")
    print(f"  95% CI:              [{ci_frust['ci_lower']:.2f}, {ci_frust['ci_upper']:.2f}]")
    print(f"  Fixed threshold:     4.38")
    print()

    # --- Satisfaction threshold (predicting wellbeing) ---
    print("--- Satisfaction Threshold (Wellbeing Prediction) ---")
    print()

    # Simulate ABC satisfaction scores on 0-10 scale
    # Low wellbeing: satisfaction centered at 4.5
    # High wellbeing: satisfaction centered at 7.5
    sat_low_wellbeing = rng.normal(4.5, 1.5, size=n_half)
    sat_high_wellbeing = rng.normal(7.5, 1.5, size=n_half)
    sat_scores = np.clip(np.concatenate([sat_low_wellbeing, sat_high_wellbeing]), 0, 10)
    wellbeing_criterion = np.concatenate([np.zeros(n_half), np.ones(n_half)])

    roc_sat = compute_roc_curve(sat_scores, wellbeing_criterion)
    youden_sat = youden_index_optimal_cutoff(
        roc_sat["fpr"], roc_sat["tpr"], roc_sat["thresholds"]
    )
    ci_sat = bootstrap_threshold_ci(
        sat_scores, wellbeing_criterion, n_bootstrap=N_BOOTSTRAP, seed=SEED + 1
    )

    print(f"  AUC:                 {roc_sat['auc']:.3f}")
    print(f"  Optimal threshold:   {youden_sat['optimal_threshold']:.2f}")
    print(f"  Sensitivity:         {youden_sat['sensitivity']:.3f}")
    print(f"  Specificity:         {youden_sat['specificity']:.3f}")
    print(f"  Youden's J:          {youden_sat['youden_j']:.3f}")
    print(f"  95% CI:              [{ci_sat['ci_lower']:.2f}, {ci_sat['ci_upper']:.2f}]")
    print(f"  Fixed threshold:     6.46")
    print()

    # --- Comparison Table ---
    print("=" * 70)
    print("COMPARISON: Fixed vs. Empirical Thresholds")
    print("=" * 70)
    print()
    print(f"{'Threshold':<25} {'Fixed':>8} {'Empirical':>10} {'95% CI':>18} {'AUC':>6}")
    print("-" * 70)
    print(
        f"{'Frustration (burnout)':<25} {'4.38':>8} "
        f"{youden_frust['optimal_threshold']:>10.2f} "
        f"{'[' + f'{ci_frust['ci_lower']:.2f}, {ci_frust['ci_upper']:.2f}' + ']':>18} "
        f"{roc_frust['auc']:>6.3f}"
    )
    print(
        f"{'Satisfaction (wellbeing)':<25} {'6.46':>8} "
        f"{youden_sat['optimal_threshold']:>10.2f} "
        f"{'[' + f'{ci_sat['ci_lower']:.2f}, {ci_sat['ci_upper']:.2f}' + ']':>18} "
        f"{roc_sat['auc']:>6.3f}"
    )
    print()
    print("WARNING: All thresholds derived from SYNTHETIC data.")
    print("Replace with empirically validated thresholds before clinical use.")


if __name__ == "__main__":
    main()
