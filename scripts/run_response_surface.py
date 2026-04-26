"""Run Edwards (2001) polynomial response surface analysis on simulated ABC data.

Reference: Edwards (2001), Ten Difference Score Myths
Reference: howard-2024-implementation-plan.md V2-B WI-9

Synthetic illustration: personal vs team subscale scores predicting a
synthetic outcome with a congruence effect (peak when Personal == Team)
and a frustration-amplification term (high values of either degrade outcome).
The script reports the polynomial fit, the difference-score constraint test,
and a calibrated concern probability for a sample case.

Status: SYNTHETIC. Results reflect simulated data structure only.

Usage:
    python scripts/run_response_surface.py
"""

import sys

sys.path.insert(0, ".")

import numpy as np

from src.psychometric.response_surface import (
    calibrated_concern_probability,
    fit_response_surface,
    test_difference_score_constraints,
)

SEED = 42
N = 500


def _simulate_personal_team(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Personal and team subscale scores correlated at r approx 0.5.

    Reference: synthetic illustration of plausible team/personal coupling
    """
    z_personal = rng.standard_normal(N)
    z_team = 0.5 * z_personal + np.sqrt(1 - 0.5**2) * rng.standard_normal(N)
    # Rescale to a 0-10 subscale range, mean 6.0, sd 1.5
    personal = 6.0 + 1.5 * z_personal
    team = 6.0 + 1.5 * z_team
    return personal, team


def _simulate_outcome(
    personal: np.ndarray, team: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Outcome with congruence effect plus a level effect on personal.

    Y = 0.4*P + 0.2*T - 0.15*(P - T)^2 + noise.
    Negative quadratic in (P - T) gives a peak along the line of agreement.

    Reference: Edwards (2001) congruence-model archetype
    """
    return (
        0.4 * personal
        + 0.2 * team
        - 0.15 * (personal - team) ** 2
        + rng.standard_normal(N) * 0.4
    )


def main() -> None:
    rng = np.random.default_rng(SEED)
    print("=" * 70)
    print("Response Surface Analysis: Personal vs Team (SYNTHETIC DATA)")
    print("=" * 70)
    print(f"  N = {N}, seed = {SEED}")
    print(f"  Reference: Edwards (2001); Shanock et al. (2010)")
    print()

    personal, team = _simulate_personal_team(rng)
    outcome = _simulate_outcome(personal, team, rng)

    # --- Polynomial regression fit ---
    surface = fit_response_surface(personal, team, outcome)
    print("--- Polynomial Regression Fit ---")
    print("  Outcome = b0 + b1*P + b2*T + b3*P^2 + b4*P*T + b5*T^2")
    print()
    print(f"  R^2 = {surface['r_squared']:.4f}")
    print()
    print(f"  {'Coef':<6} {'Estimate':>10} {'SE':>10}")
    print("  " + "-" * 28)
    for name in ("b0", "b1", "b2", "b3", "b4", "b5"):
        b = surface["coefficients"][name]
        se = surface["coefficient_se"][name]
        print(f"  {name:<6} {b:>10.4f} {se:>10.4f}")
    print()

    feats = surface["surface_features"]
    print("--- Response Surface Features ---")
    print(f"  Line of agreement slope   (b1+b2): {feats['line_of_agreement_slope']:>+8.4f}")
    print(f"  Line of disagreement slope (b1-b2): {feats['line_of_disagreement_slope']:>+8.4f}")
    print(f"  Curvature along agreement (b3+b4+b5): {feats['curvature_along_agreement']:>+8.4f}")
    print(
        f"  Curvature along disagreement (b3-b4+b5): "
        f"{feats['curvature_along_disagreement']:>+8.4f}"
    )
    if feats["peak_personal"] is not None:
        print(
            f"  Surface stationary point: P={feats['peak_personal']:.2f}, "
            f"T={feats['peak_team']:.2f}, predicted Y={feats['peak_outcome']:.2f}"
        )
    else:
        print("  Surface has no unique stationary point (saddle or degenerate Hessian)")
    print()

    # --- Difference-score constraint test ---
    print("--- Difference-Score Constraint Test ---")
    print("  H0: Outcome ~ k * (Personal - Team), implying b1 = -b2 and b3 = b4 = b5 = 0")
    constraint = test_difference_score_constraints(personal, team, outcome)
    print(
        f"  F({constraint['df_constraint']}, {constraint['df_residual']}) "
        f"= {constraint['f_statistic']:.3f}, p = {constraint['p_value']:.4g}"
    )
    print(
        f"  Reject difference-score hypothesis: "
        f"{constraint['reject_difference_hypothesis']}"
    )
    print(
        f"  R^2 lost by imposing constraints: "
        f"{constraint['effect_size_r_squared_change']:.4f}"
    )
    print()

    # --- Calibrated concern probability for sample cases ---
    print("--- Calibrated Concern Probability ---")
    print(
        "  Replaces the legacy -1.5 difference threshold from context_gap.py"
    )
    print(
        "  with a logistic transform of the predicted outcome relative to a criterion."
    )
    print()
    threshold = float(np.median(outcome))
    print(f"  criterion_threshold = median(outcome) = {threshold:.3f}")
    print()
    sample_cases = [
        (5.0, 5.0, "low/low congruent"),
        (7.0, 7.0, "high/high congruent"),
        (4.0, 8.0, "athlete low, team high"),
        (8.0, 4.0, "athlete high, team low"),
    ]
    print(f"  {'Personal':>10} {'Team':>8} {'P(concern)':>12}  Description")
    print("  " + "-" * 56)
    for p, t, label in sample_cases:
        prob = calibrated_concern_probability(
            p, t, surface, criterion_threshold=threshold
        )
        print(f"  {p:>10.2f} {t:>8.2f} {prob:>12.3f}  {label}")
    print()
    print("WARNING: All results derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
