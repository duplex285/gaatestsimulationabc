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
