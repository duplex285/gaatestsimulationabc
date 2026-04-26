"""Run Johnson (2000) relative weight analysis on simulated ABC subscales.

Reference: Johnson (2000), Multivariate Behavioral Research, 35(1), 1-19
Reference: howard-2024-implementation-plan.md V2-B WI-6

Synthetic illustration: six ABC-like subscales (a_sat, a_frust, b_sat, b_frust,
c_sat, c_frust) predicting a synthetic burnout-like criterion (e.g., ABQ total).
The six subscales are correlated at mean r approx 0.4, mirroring the
expected Phase A correlation structure. OLS coefficients on highly correlated
predictors are unstable; relative weights provide an interpretable additive
decomposition of R^2.

Status: SYNTHETIC. Results reflect simulated data structure only.

Usage:
    python scripts/run_relative_weight.py
"""

import sys

sys.path.insert(0, ".")

import numpy as np

from src.psychometric.relative_weight import relative_weights

SEED = 42
N = 600
SUBSCALES = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]


def _simulate_subscales(n: int, mean_r: float, rng: np.random.Generator) -> np.ndarray:
    """Generate six ABC-like correlated subscale scores.

    Reference: abc-assessment-spec Section 11.1 (simulation parameters)
    """
    p = len(SUBSCALES)
    cov = np.full((p, p), mean_r)
    np.fill_diagonal(cov, 1.0)
    chol = np.linalg.cholesky(cov)
    z = rng.standard_normal((n, p))
    return z @ chol.T


def _simulate_burnout(subscales: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Synthetic burnout outcome: frustration drives, satisfaction protects.

    Reference: Bartholomew (2011); Howard (2020) on need-frustration -> burnout
    """
    # True coefficients on standardized subscales: frust subscales positive,
    # sat subscales negative, ambition slightly stronger.
    # Reference: synthetic illustration only.
    weights = np.array([-0.30, 0.45, -0.20, 0.35, -0.15, 0.30])
    signal = subscales @ weights
    noise = rng.standard_normal(subscales.shape[0]) * 0.6
    return signal + noise


def main() -> None:
    rng = np.random.default_rng(SEED)
    print("=" * 70)
    print("ABC Subscales: Relative Weight Analysis (SYNTHETIC DATA)")
    print("=" * 70)
    print(f"  N = {N}, mean inter-subscale r = 0.40, seed = {SEED}")
    print(f"  Reference: Johnson (2000); Tonidandel & LeBreton (2011)")
    print()

    x = _simulate_subscales(N, mean_r=0.4, rng=rng)
    y = _simulate_burnout(x, rng=rng)

    # Bootstrap CI: 2000 resamples for the script (faster than the 10000 default).
    result = relative_weights(
        x, y, n_bootstrap=2000, alpha=0.05, ci_method="percentile", random_seed=SEED
    )

    print(f"  R^2 = {result['r_squared']:.4f}")
    print(f"  sum(raw_weights) = {result['raw_weights'].sum():.4f} (should equal R^2)")
    print()
    print(
        f"  {'Subscale':<10} {'Raw w':>8} {'95% CI':>20} "
        f"{'Rescaled':>10} {'95% CI':>20}"
    )
    print("  " + "-" * 70)
    for i, name in enumerate(SUBSCALES):
        raw = result["raw_weights"][i]
        rcl = result["rescaled_weights"][i]
        raw_lo, raw_hi = result["ci_raw"][i]
        rcl_lo, rcl_hi = result["ci_rescaled"][i]
        print(
            f"  {name:<10} {raw:>8.4f} [{raw_lo:>7.4f}, {raw_hi:>7.4f}]  "
            f"{rcl * 100:>9.1f}% [{rcl_lo * 100:>6.1f}%, {rcl_hi * 100:>6.1f}%]"
        )
    print()
    print("--- Interpretation ---")
    top_idx = int(np.argmax(result["raw_weights"]))
    print(
        f"  Top contributor: {SUBSCALES[top_idx]} "
        f"({result['rescaled_weights'][top_idx] * 100:.1f}% of explained variance)"
    )
    print(
        "  Frustration subscales typically dominate when burnout is the criterion;"
    )
    print("  satisfaction subscales contribute via shared variance with frustration.")
    print()
    print("WARNING: All results derived from SYNTHETIC data.")


if __name__ == "__main__":
    main()
