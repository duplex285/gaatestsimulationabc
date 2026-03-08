# ABC Assessment Psychometric Validation

Computational validation of Ero's ABC psychometric model — a 6-subscale instrument measuring satisfaction and frustration across three psychological need domains (Ambition, Belonging, Craft), grounded in Self-Determination Theory.

## Purpose

Prove the model's factor structure is statistically sound before production deployment. The simulation validates the math; empirical data validates the instrument.

## Structure

| Phase | Tool | What it proves |
|-------|------|----------------|
| Phase 0 | R (lavaan) | 6-factor CFA fits, sat/frust are separable constructs |
| Phase A | Python (numpy, scipy) | Scoring pipeline preserves signal from raw responses to typed profiles |

## Key Thresholds

- **CFA fit**: CFI >= 0.95, RMSEA <= 0.06, SRMR <= 0.08
- **Internal consistency**: Cronbach's alpha >= 0.70 per subscale
- **Scoring accuracy**: r >= 0.85 with ground truth per subscale
- **Domain classification**: >= 80% accuracy, >= 75% Vulnerable sensitivity

## Quick Start

```bash
# R validation
Rscript src/r_validation/01_simple_cfa_test.R
Rscript src/r_validation/02_abc_6factor_cfa.R

# Python scoring (activate venv first)
source abc-venv/bin/activate
pytest tests/python_tests/ -v
```

## Project Layout

```
src/r_validation/       # Phase 0: CFA scripts
src/python_scoring/     # Phase A: Production scoring engine
tests/python_tests/     # Comprehensive test suite (100+ tests)
config/                 # Correlation matrices, thresholds
outputs/reports/        # Validation reports
docs/                   # Spec and documentation
```
