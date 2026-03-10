# ABC Assessment Psychometric Validation

Computational validation of Ero's ABC psychometric model — a 6-subscale instrument measuring satisfaction and frustration across three psychological need domains (Ambition, Belonging, Craft), grounded in Self-Determination Theory.

**Status**: All validation gates PASS. See [`docs/validation-report.md`](docs/validation-report.md) for the full report.

## Purpose

Prove the model's factor structure is statistically sound before production deployment. The simulation validates the math; empirical data validates the instrument.

## Structure

| Phase | Tool | What it proves | Status |
|-------|------|----------------|--------|
| Phase 0 | R (lavaan) | 6-factor CFA fits, sat/frust are separable constructs | PASS |
| Phase A | Python (numpy, scipy) | Scoring pipeline preserves signal from raw responses to typed profiles | PASS |

## Results

| Gate | Target | Achieved |
|------|--------|----------|
| CFA fit (CFI) | >= 0.95 | 1.000 |
| CFA fit (RMSEA) | <= 0.06 | 0.000 |
| Cronbach's alpha | >= 0.70 | All pass |
| Scoring correlation | >= 0.85 | 1.000 |
| Domain accuracy | >= 80% | 100.0% |
| Vulnerable sensitivity | >= 75% | 100.0% |
| Type balance | <= 15% max | 11.0% |
| Unit tests | All pass | 106/106 |
| Code coverage | >= 85% | 97.5% |

## How the Simulation Generates Data

The dashboard generates synthetic participants client-side using fixed statistical parameters. Each run draws from the same underlying distributions, so the graphs will show a consistent spread across runs. This is by design: the simulation validates the scoring pipeline under controlled conditions, not the variance of a real population.

Three mechanisms produce this stability:

1. **Fixed distribution parameters.** Six subscale scores are drawn from independent normal distributions with tuned means (`[0.24, -0.31, 0.24, -0.31, 0.24, -0.31]`). These offsets ensure no single type exceeds 15% of the population.
2. **Cholesky decomposition with an identity correlation matrix.** Subscales are sampled independently (zero inter-subscale correlation). Real respondent data will introduce natural correlations between domains.
3. **Convergence at scale.** With hundreds or thousands of participants, the law of large numbers pulls every run toward the same shape. The noise slider controls item-level variance, but the population-level distribution remains stable.

The offline validation (R and Python) uses fixed random seeds (`set.seed(42)`) and a structured correlation matrix with cross-domain relationships. The dashboard uses simpler parameters to keep the client-side code lightweight and the type distribution unbiased.

Empirical data will replace these fixed parameters and introduce the natural skews, correlations, and variance that real populations produce.

## Quick Start

```bash
# R validation
Rscript src/r_validation/02_abc_6factor_cfa.R
Rscript src/r_validation/03_export_ground_truth.R

# Python scoring (activate venv first)
source abc-venv/bin/activate
pytest tests/python_tests/ -v
python scripts/validate_scoring_accuracy.py
```

## Project Layout

```
src/r_validation/       # Phase 0: CFA scripts (3 files)
src/python_scoring/     # Phase A: Production scoring engine (6 modules)
tests/python_tests/     # 106 unit/integration tests
scripts/                # Validation and pre-commit scripts
config/                 # Correlation matrices, thresholds
outputs/reports/        # CFA and scoring validation outputs
outputs/datasets/       # Ground truth CSVs (1000 participants)
docs/                   # Spec and validation report
```
