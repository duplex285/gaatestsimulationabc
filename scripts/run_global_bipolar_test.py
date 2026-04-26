"""Run the 1-G vs 2-G bifactor-ESEM comparison on simulated ABC data.

Reference: howard-2024-implementation-plan.md V2-B WI-8
Reference: Toth-Kiraly et al. (2018), bifactor-ESEM on BPNSFS

Generates synthetic ABC-shaped data (24 items: 3 domains x sat/frust x 4
items), fits both global structures, and writes the comparison JSON to
outputs/reports/global_bipolar_test.json.

Status: SYNTHETIC. Results reflect properties of simulated data only.

Usage:
    python scripts/run_global_bipolar_test.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.psychometric.factor_models import (
    ABC_FACTOR_MAP_24,
    ABC_VALENCE_MAP_24,
    compare_one_g_two_g,
)

SEED = 42
N = 600
ITEM_NAMES = [
    f"{p}{i}" for p in ["AS", "AF", "BS", "BF", "CS", "CF"] for i in range(1, 5)
]


def generate_abc_like_data(seed: int) -> np.ndarray:
    """Generate ABC-shaped synthetic data with a mild bipolar global signal.

    Reference: howard-2024-implementation-plan.md V2-B WI-8
    """
    rng = np.random.default_rng(seed)
    g = rng.standard_normal(N)
    spec = rng.standard_normal((N, 6)) * np.sqrt(0.20)
    n_items = 24
    data = np.zeros((N, n_items))
    primary = 0.55
    for f in range(6):
        is_frust = (f % 2) == 1
        sign = -1.0 if is_frust else 1.0
        for i in range(4):
            idx = f * 4 + i
            noise_var = max(1 - primary**2 - 0.20, 0.05)
            data[:, idx] = (
                sign * primary * g
                + spec[:, f]
                + math.sqrt(noise_var) * rng.standard_normal(N)
            )
    return data


def _to_jsonable(obj):
    """Recursively convert numpy/pandas scalars to JSON-friendly types."""
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        return v if math.isfinite(v) else None
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    return obj


def main() -> None:
    print("=" * 70)
    print("ABC Assessment: 1-G vs 2-G Bifactor-ESEM (SYNTHETIC DATA)")
    print("=" * 70)

    data = generate_abc_like_data(SEED)
    factor_map = dict(ABC_FACTOR_MAP_24)
    valence_map = dict(ABC_VALENCE_MAP_24)

    print(f"Fitting 1-G and 2-G bifactor-ESEM (n={N})...")
    result = compare_one_g_two_g(data, ITEM_NAMES, factor_map, valence_map)

    print()
    print(f"  1-G BIC: {result['one_g'].get('bic')}")
    print(f"  2-G BIC: {result['two_g'].get('bic')}")
    print(f"  delta_bic (1G - 2G): {result['delta_bic']}")
    print(f"  G-G correlation: {result['g_g_correlation']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Rationale: {result['rationale']}")

    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "global_bipolar_test.json"

    payload = {
        "seed": SEED,
        "n": N,
        "item_names": ITEM_NAMES,
        "delta_bic": result["delta_bic"],
        "g_g_correlation": result["g_g_correlation"],
        "recommendation": result["recommendation"],
        "rationale": result["rationale"],
        "one_g_fit": {
            k: result["one_g"].get(k) for k in ("chi2", "df", "cfi", "rmsea", "tli", "aic", "bic")
        },
        "two_g_fit": {
            k: result["two_g"].get(k) for k in ("chi2", "df", "cfi", "rmsea", "tli", "aic", "bic")
        },
        "one_g_g_loadings": result["one_g"]["g_loadings"],
        "two_g_g_loadings": result["two_g"]["g_loadings"],
        "warning": "All results derived from SYNTHETIC data.",
    }
    with out_path.open("w") as fh:
        json.dump(_to_jsonable(payload), fh, indent=2)

    print()
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
