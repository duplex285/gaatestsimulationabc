#!/usr/bin/env python3
"""Validate Python scoring pipeline against R ground truth.

Scores 1,000 simulated participants and computes:
- Pearson correlation per subscale (target: >= 0.85)
- Domain state classification accuracy (target: >= 80%)
- Vulnerable state sensitivity (target: >= 75%)
- Type distribution balance (target: no type > 15%)

Reference: abc-assessment-spec Section 11.4 (scoring pipeline verification)
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.python_scoring.scoring_pipeline import ABCScorer

SUBSCALE_NAMES = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
DOMAIN_NAMES = ["ambition", "belonging", "craft"]


def load_ground_truth():
    """Load R-generated ground truth data.

    Reference: abc-assessment-spec Section 11.4
    """
    data_dir = project_root / "outputs" / "datasets"
    responses = pd.read_csv(data_dir / "ground_truth_responses.csv")
    subscales = pd.read_csv(data_dir / "ground_truth_subscales.csv")
    states = pd.read_csv(data_dir / "ground_truth_states.csv")
    return responses, subscales, states


def score_all_participants(responses_df):
    """Score all participants with the Python pipeline.

    Reference: abc-assessment-spec Section 2.1
    """
    scorer = ABCScorer()
    results = []
    for _, row in responses_df.iterrows():
        resp = {col: int(row[col]) for col in responses_df.columns}
        result = scorer.score(resp)
        results.append(result)
    return results


def compute_scoring_accuracy(results, subscales_df):
    """Compute Pearson correlation between Python scores and R observed scores.

    Reference: abc-assessment-spec Section 11.4
    Target: r >= 0.85 per subscale (expect ~1.0 for observed-vs-observed)
    """
    print("=" * 60)
    print("SCORING ACCURACY (Python vs R Observed)")
    print("=" * 60)
    print()

    all_pass = True
    correlations = {}

    for subscale in SUBSCALE_NAMES:
        python_scores = [r["subscales"][subscale] for r in results]
        true_scores = subscales_df[subscale].values

        r, p = stats.pearsonr(python_scores, true_scores)
        rho, _ = stats.spearmanr(python_scores, true_scores)
        status = "PASS" if r >= 0.85 else "FAIL"
        if r < 0.85:
            all_pass = False
        correlations[subscale] = r

        print(f"  {subscale:10s}: r = {r:.3f}  rho = {rho:.3f}  {status}")

    avg_r = np.mean(list(correlations.values()))
    print()
    print(f"  Average r: {avg_r:.3f}  (target: >= 0.85)  {'PASS' if avg_r >= 0.85 else 'FAIL'}")
    print()
    return all_pass, correlations


def compute_classification_accuracy(results, states_df):
    """Compute domain state classification accuracy.

    Reference: abc-assessment-spec Section 11.4
    Target: >= 80% overall, >= 75% Vulnerable sensitivity
    """
    print("=" * 60)
    print("DOMAIN STATE CLASSIFICATION")
    print("=" * 60)
    print()

    total_correct = 0
    total_count = 0
    vulnerable_correct = 0
    vulnerable_total = 0

    for domain in DOMAIN_NAMES:
        python_states = [r["domain_states"][domain] for r in results]
        true_states = states_df[domain].values

        correct = sum(p == t for p, t in zip(python_states, true_states, strict=False))
        total = len(python_states)
        accuracy = correct / total * 100

        total_correct += correct
        total_count += total

        # Vulnerable sensitivity
        v_true = [i for i, t in enumerate(true_states) if t == "Vulnerable"]
        if v_true:
            v_correct = sum(python_states[i] == "Vulnerable" for i in v_true)
            v_sens = v_correct / len(v_true) * 100
            vulnerable_correct += v_correct
            vulnerable_total += len(v_true)
        else:
            v_sens = 0.0

        print(f"  {domain:12s}: accuracy = {accuracy:.1f}%  vulnerable sensitivity = {v_sens:.1f}%")

    overall_accuracy = total_correct / total_count * 100
    overall_v_sens = vulnerable_correct / vulnerable_total * 100 if vulnerable_total > 0 else 0.0

    print()
    print(
        f"  Overall accuracy:          {overall_accuracy:.1f}%  "
        f"(target: >= 80%)  {'PASS' if overall_accuracy >= 80 else 'FAIL'}"
    )
    print(
        f"  Vulnerable sensitivity:    {overall_v_sens:.1f}%  "
        f"(target: >= 75%)  {'PASS' if overall_v_sens >= 75 else 'FAIL'}"
    )
    print()

    acc_pass = overall_accuracy >= 80
    vuln_pass = overall_v_sens >= 75
    return acc_pass, vuln_pass


def compute_type_distribution(results):
    """Compute 36-type distribution balance.

    Reference: abc-assessment-spec Section 11.6
    Target: no type > 15% of population
    """
    print("=" * 60)
    print("TYPE DISTRIBUTION")
    print("=" * 60)
    print()

    types = [r["type_name"] for r in results]
    counter = Counter(types)
    n = len(types)

    print(f"  Types observed: {len(counter)}")
    print()

    max_pct = 0
    for type_name, count in counter.most_common():
        pct = count / n * 100
        max_pct = max(max_pct, pct)
        flag = " <-- EXCEEDS 15%" if pct > 15 else ""
        print(f"    {type_name:20s}: {count:4d} ({pct:5.1f}%){flag}")

    print()
    balance_pass = max_pct <= 15
    print(
        f"  Max single type: {max_pct:.1f}%  (target: <= 15%)  {'PASS' if balance_pass else 'FAIL'}"
    )
    print()
    return balance_pass


def main():
    """Run full scoring validation.

    Reference: abc-assessment-spec Section 11.4
    """
    print()
    print("=" * 60)
    print("  PYTHON SCORING PIPELINE VALIDATION")
    print("=" * 60)
    print()

    # Load data
    responses_df, subscales_df, states_df = load_ground_truth()
    print(f"Loaded {len(responses_df)} participants.\n")

    # Score all participants
    print("Scoring all participants with Python pipeline...")
    results = score_all_participants(responses_df)
    print(f"Scored {len(results)} participants.\n")

    # Validate
    score_pass, correlations = compute_scoring_accuracy(results, subscales_df)
    acc_pass, vuln_pass = compute_classification_accuracy(results, states_df)
    type_pass = compute_type_distribution(results)

    # Final verdict
    print("=" * 60)
    print("FINAL VALIDATION VERDICT")
    print("=" * 60)
    print()

    checks = [
        ("Scoring correlation >= 0.85 per subscale", score_pass),
        ("Domain state accuracy >= 80%", acc_pass),
        ("Vulnerable sensitivity >= 75%", vuln_pass),
        ("Type distribution balanced (<= 15%)", type_pass),
    ]

    all_pass = True
    for desc, passed in checks:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {desc}")

    print()
    if all_pass:
        print("  PYTHON SCORING PIPELINE VALIDATED")
    else:
        print("  VALIDATION FAILED")
        print("  Review failed checks above.")

    print()
    print("=" * 60)

    # Save results
    results_dir = project_root / "outputs" / "reports"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Save correlation results
    cor_df = pd.DataFrame(
        {
            "subscale": list(correlations.keys()),
            "pearson_r": list(correlations.values()),
        }
    )
    cor_df.to_csv(results_dir / "scoring_correlations.csv", index=False)

    # Save scored data
    scored_subscales = pd.DataFrame([r["subscales"] for r in results])
    scored_subscales.to_csv(
        project_root / "outputs" / "datasets" / "python_scored_subscales.csv",
        index=False,
    )

    print(f"\nResults saved to {results_dir}/")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
