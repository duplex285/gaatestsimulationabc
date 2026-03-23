"""Run decision consistency analysis on synthetic data.

Reference: APA/AERA/NCME Standards (2014), Standards 2.4, 2.14, 2.16

Simulates two independent administrations of the ABC assessment to the
same respondents and reports classification agreement rates, difference
score reliability, and conditional SEM at the domain state thresholds.

Status: SYNTHETIC. Results reflect properties of simulated IRT parameters.

Usage:
    python scripts/run_decision_consistency.py
"""

import sys
sys.path.insert(0, ".")

import numpy as np

from src.psychometric.decision_consistency import (
    compute_conditional_sem_at_thresholds,
    compute_difference_score_reliability,
    simulate_classification_agreement,
)
from src.psychometric.irt_simulation import generate_synthetic_grm_parameters

SEED = 42
N_PERSONS = 500


def main():
    print("=" * 70)
    print("ABC Assessment: Decision Consistency Analysis (SYNTHETIC DATA)")
    print("=" * 70)
    print()

    params = generate_synthetic_grm_parameters(n_items=24, n_categories=7, seed=SEED)

    # --- Classification Agreement ---
    print("--- Classification Agreement (2 independent administrations) ---")
    print(f"    N = {N_PERSONS}, IRT discrimination range: "
          f"[{params['discrimination'].min():.2f}, {params['discrimination'].max():.2f}]")
    print()

    result = simulate_classification_agreement(
        params["discrimination"], params["difficulty"],
        n_persons=N_PERSONS, n_replications=2, seed=SEED,
    )

    print(f"  Domain state agreement (all 3 domains): {result['domain_state_agreement']:.1%}")
    print(f"  Type agreement (24 types):              {result['type_agreement']:.1%}")
    print()
    print("  Per-domain agreement:")
    for domain, agreement in result["per_domain_agreement"].items():
        print(f"    {domain:>12}: {agreement:.1%}")
    print()

    # --- Difference Score Reliability ---
    print("--- Difference Score Reliability (sat - frust per domain) ---")
    print("    Formula: r_diff = (r_sat + r_frust - 2*r_xy) / (2 - 2*r_xy)")
    print()

    # Test at different reliability levels and correlations
    rng = np.random.default_rng(SEED)
    n = 500
    sat = {f"{d}_sat": rng.normal(6, 1.5, n) for d in ["a", "b", "c"]}
    frust = {f"{d}_frust": rng.normal(4, 1.5, n) for d in ["a", "b", "c"]}

    scenarios = [
        ("alpha=0.70, r_xy=0.00", 0.70, 0.70, 0.00),
        ("alpha=0.70, r_xy=-0.30", 0.70, 0.70, -0.30),
        ("alpha=0.80, r_xy=0.00", 0.80, 0.80, 0.00),
        ("alpha=0.80, r_xy=-0.40", 0.80, 0.80, -0.40),
        ("alpha=0.85, r_xy=-0.50", 0.85, 0.85, -0.50),
    ]

    print(f"  {'Scenario':<30} {'Ambition':>10} {'Belonging':>10} {'Craft':>10}")
    print("  " + "-" * 62)
    for label, r_sat, r_frust, r_xy in scenarios:
        diff_rel = compute_difference_score_reliability(
            sat, frust, reliability_sat=r_sat, reliability_frust=r_frust, r_sat_frust=r_xy
        )
        print(
            f"  {label:<30} "
            f"{diff_rel['ambition']:>10.3f} "
            f"{diff_rel['belonging']:>10.3f} "
            f"{diff_rel['craft']:>10.3f}"
        )
    print()

    # --- Conditional SEM at Thresholds ---
    print("--- Conditional SEM at Domain State Thresholds ---")
    print("    Reference: Standard 2.14")
    print()

    thresholds = {
        "satisfaction (6.46)": 6.46,
        "frustration (4.38)": 4.38,
        "type activation (5.50)": 5.50,
        "frust modifier (5.00)": 5.00,
    }

    sem_results = compute_conditional_sem_at_thresholds(
        params["discrimination"], params["difficulty"], thresholds
    )

    print(f"  {'Threshold':<30} {'Score':>8} {'Theta':>8} {'SEM':>8}")
    print("  " + "-" * 56)
    for name, score in thresholds.items():
        theta = (score - 5.0) / 2.5
        sem = sem_results[name]
        print(f"  {name:<30} {score:>8.2f} {theta:>8.2f} {sem:>8.4f}")

    print()
    print("--- Interpretation ---")
    print()
    print("  Per-domain agreement of ~65% with synthetic a=0.8-2.5 means that")
    print("  roughly 1 in 3 athletes would receive a different domain state")
    print("  classification on readministration. Joint agreement across all 3")
    print("  domains is ~28% (0.65^3). This highlights the need for:")
    print("    1. More items per subscale (8+ for reliable classification)")
    print("    2. Confidence bands on all classifications")
    print("    3. Empirical test-retest data to validate these simulated rates")
    print()
    print("WARNING: All results derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
