"""Run leading indicator analysis on synthetic trajectory data.

Reference: abc-assessment-spec Section 11.7
Reference: Minerva optimization framework (objective: minimize detection lag)

Generates synthetic burnout trajectories, runs the trajectory engine,
identifies leading indicators, computes detection lags, and optimizes
alert thresholds. Also demonstrates the Vulnerable-to-Distressed cascade.

Status: SYNTHETIC. All results reflect simulated data properties.

Usage:
    python scripts/run_leading_indicator_analysis.py
"""

import sys
sys.path.insert(0, ".")

import numpy as np

from src.psychometric.leading_indicator_model import (
    compute_detection_lag,
    compute_transition_probability,
    identify_leading_indicators,
    optimize_alert_multidimensional,
    optimize_alert_thresholds,
)
from src.psychometric.trajectory_engine import classify_trajectory_pattern
from src.psychometric.trajectory_simulation import (
    simulate_burnout_trajectories,
    simulate_vulnerable_to_distressed_cascade,
)

SEED = 42
N_PERSONS = 1000
N_TIMEPOINTS = 10


def main():
    print("=" * 70)
    print("ABC Assessment: Leading Indicator Analysis (SYNTHETIC DATA)")
    print("=" * 70)
    print()

    # --- Trajectory Generation ---
    traj = simulate_burnout_trajectories(
        n_persons=N_PERSONS, n_timepoints=N_TIMEPOINTS, seed=SEED
    )
    labels = np.array(traj["labels"])
    onsets = np.array(traj["burnout_onset"])

    print("--- Trajectory Distribution ---")
    for ttype in ["stable", "gradual_decline", "gradual_rise", "acute_event", "volatile"]:
        n = np.sum(labels == ttype)
        burnout_rate = np.mean(onsets[labels == ttype] >= 0) if n > 0 else 0
        print(f"  {ttype:<20} N={n:>4}  burnout rate: {burnout_rate:.1%}")
    print(f"  {'TOTAL':<20} N={N_PERSONS:>4}  burnout rate: {np.mean(onsets >= 0):.1%}")
    print()

    # --- Trajectory Pattern Classification ---
    print("--- Trajectory Pattern Detection ---")
    se = np.full_like(traj["scores"], 0.3)
    detected_patterns = []
    for p in range(N_PERSONS):
        pattern = classify_trajectory_pattern(traj["scores"][p], se[p])
        detected_patterns.append(pattern)
    detected_patterns = np.array(detected_patterns)

    # Confusion: true vs detected
    all_types = ["stable", "gradual_decline", "gradual_rise", "acute_event", "volatile"]
    print(f"  {'True \\ Detected':<20}", end="")
    for dt in all_types:
        print(f" {dt[:8]:>9}", end="")
    print()
    for tt in all_types:
        mask = labels == tt
        print(f"  {tt:<20}", end="")
        for dt in all_types:
            count = np.sum(detected_patterns[mask] == dt)
            print(f" {count:>9}", end="")
        print()
    print()

    # --- Detection accuracy ---
    accuracy = np.mean(labels == detected_patterns)
    decline_mask = labels == "gradual_decline"
    decline_sensitivity = np.mean(detected_patterns[decline_mask] == "gradual_decline") if np.sum(decline_mask) > 0 else 0
    print(f"  Overall accuracy:      {accuracy:.1%}")
    print(f"  Decline sensitivity:   {decline_sensitivity:.1%}")
    print()

    # --- Alert Threshold Optimization ---
    print("--- Alert Threshold Optimization ---")
    print("    Objective: minimize detection lag subject to FPR <= 15%")
    print()

    result = optimize_alert_thresholds(traj["scores"], onsets, se, max_fpr=0.15)

    print(f"  Optimal RCI threshold: {result['optimal_threshold']:.2f}")
    print(f"  Mean detection lag:    {result['mean_detection_lag']:.1f} timepoints")
    print(f"  Sensitivity:           {result['sensitivity']:.1%}")
    print(f"  False positive rate:   {result['false_positive_rate']:.1%}")
    print()

    print("  All candidates tested:")
    print(f"  {'Threshold':>10} {'Lag':>6} {'Sens':>6} {'FPR':>6}")
    print("  " + "-" * 30)
    for r in result["all_results"]:
        fpr_flag = " *" if r["false_positive_rate"] <= 0.15 else ""
        print(
            f"  {r['threshold']:>10.2f} {r['mean_detection_lag']:>6.1f} "
            f"{r['sensitivity']:>6.1%} {r['false_positive_rate']:>5.1%}{fpr_flag}"
        )
    print("  (* = within FPR constraint)")
    print()

    # --- Multi-Dimensional Optimization (Differential Evolution) ---
    print("--- Multi-Dimensional Alert Optimization ---")
    print("    Method: scipy.optimize.differential_evolution")
    print("    (analogous to R's rgenoud: GA + gradient refinement)")
    print("    Decision variables: 3 subscale weights + RCI threshold + window size")
    print()

    # Create 3-subscale version for multi-dimensional optimization
    rng = np.random.default_rng(SEED)
    subscale_scores = {
        "a_frust": traj["scores"] + rng.normal(0, 0.3, traj["scores"].shape),
        "b_frust": traj["scores"] + rng.normal(0, 0.5, traj["scores"].shape),
        "c_frust": traj["scores"] + rng.normal(0, 0.8, traj["scores"].shape),
    }
    subscale_se = {name: np.full_like(s, 0.3) for name, s in subscale_scores.items()}

    multi_result = optimize_alert_multidimensional(
        subscale_scores, subscale_se, onsets, max_fpr=0.15, seed=SEED
    )

    print(f"  Optimal weights:")
    for name, w in multi_result["optimal_weights"].items():
        print(f"    {name}: {w:.3f}")
    print(f"  Optimal RCI threshold: {multi_result['optimal_threshold']:.2f}")
    print(f"  Optimal window size:   {multi_result['optimal_window']}")
    print(f"  Mean detection lag:    {multi_result['mean_detection_lag']:.1f} timepoints")
    print(f"  Sensitivity:           {multi_result['sensitivity']:.1%}")
    print(f"  False positive rate:   {multi_result['false_positive_rate']:.1%}")
    print(f"  Fitness evaluations:   {multi_result['n_evaluations']}")
    print()
    print("  Comparison: grid search (1D) vs differential evolution (5D):")
    print(f"    Grid search:  lag={result['mean_detection_lag']:.1f}, "
          f"sens={result['sensitivity']:.1%}, fpr={result['false_positive_rate']:.1%}")
    print(f"    Diff. evol.:  lag={multi_result['mean_detection_lag']:.1f}, "
          f"sens={multi_result['sensitivity']:.1%}, fpr={multi_result['false_positive_rate']:.1%}")
    print()

    # --- Vulnerable-to-Distressed Cascade ---
    print("--- Vulnerable-to-Distressed Cascade ---")
    cascade = simulate_vulnerable_to_distressed_cascade(
        n_persons=200, n_timepoints=N_TIMEPOINTS, mean_lag=2, seed=SEED
    )

    mean_lag = np.mean(cascade["cascade_lag"])
    print(f"  Mean cascade lag:      {mean_lag:.1f} timepoints")
    print(f"  (frustration rises {mean_lag:.1f} timepoints before satisfaction drops)")
    print()
    print(f"  Timepoint    Mean Sat    Mean Frust")
    print("  " + "-" * 40)
    for t in range(N_TIMEPOINTS):
        ms = np.mean(cascade["satisfaction"][:, t])
        mf = np.mean(cascade["frustration"][:, t])
        print(f"  {t:>9}    {ms:>8.2f}    {mf:>10.2f}")

    print()
    print("--- Interpretation ---")
    print()
    print("  The cascade model shows frustration rising before satisfaction")
    print("  drops, creating a detection window. This is the leading indicator")
    print("  signal: rising frustration in the presence of still-high")
    print("  satisfaction (the Vulnerable state in continuous score space)")
    print("  precedes the decline in satisfaction that marks the transition")
    print("  to Distressed. The mean lag of {:.1f} timepoints is the average".format(mean_lag))
    print("  early warning window available for intervention.")
    print()
    print("WARNING: All results derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
