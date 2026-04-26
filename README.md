# ABC Assessment Simulation

Psychometric validation and simulation of the ABC assessment, a 36-item instrument measuring satisfaction and frustration across three psychological need domains (Ambition, Belonging, Craft), grounded in Self-Determination Theory.

## What this is

A purpose-built psychometric instrument developed through AI-assisted research and iterative simulation. The simulation validates the scoring infrastructure on synthetic data before empirical deployment with real athletes. Every threshold, weight, and classification is documented for auditor review.

**Status:** All simulation phases complete. 493+ tests passing, 0 failures. Empirical validation pending.

**External audit package.** A GitHub Pages site at `docs/index.md` contains the full audit package for external review by psychometricians and sport psychologists. Browse [docs/index.md](docs/index.md), [docs/audit-checklist.md](docs/audit-checklist.md), [docs/external-review-package.md](docs/external-review-package.md), [docs/methods-audit.md](docs/methods-audit.md), [docs/howard-2024-implementation-plan.md](docs/howard-2024-implementation-plan.md). Once enabled, the site will be live at https://duplex285.github.io/gaatestsimulationabc/.

## Instrument

| Property | Value |
|---|---|
| Items | 36 (6 per subscale) |
| Subscales | 6 (satisfaction + frustration per domain) |
| Domains | 3 (Ambition, Belonging, Craft) |
| Response scale | 1-7 Likert |
| Reverse-coded items | 12 (items 4 and 6 per subscale) |
| Archetype types | 8 base patterns with continuous frustration |
| Measurement tiers | 6 / 18 / 36 items |
| Mean type stability | 90% (with 6 items per subscale) |

## Dashboard

Open `outputs/site/index.html` in a browser to run the interactive simulation. The dashboard includes:

- Population generation with configurable parameters
- Type distribution (8 archetypes)
- Domain state classification (Thriving/Vulnerable/Mild/Distressed)
- Satisfaction vs frustration scatter plots per domain
- Belbin team role inference
- Frustration signature detection
- Trajectory analysis with burnout cascade modeling
- Stability analysis with boundary participant identification
- Full methodology reference (14 sections, 27 numbered academic references)
- Run computation log showing exact parameters and sample participants

## Psychometric Engine

The `src/psychometric/` package (21 modules) provides gold standard methods:

| Capability | Module | Method |
|---|---|---|
| IRT scoring | irt_estimation.py | Graded Response Model, EAP theta with SE |
| Threshold derivation | threshold_derivation.py | ROC, Youden Index, bootstrap CI, Jacobson-Truax RCI |
| Decision consistency | decision_consistency.py | Classification agreement, difference reliability, conditional SEM |
| Factor analysis | factor_models.py | CFA, bifactor, method-factor via semopy |
| Measurement invariance | measurement_invariance.py | Configural/metric/scalar, DIF |
| Population norming | norming.py | T-scores, percentile ranks, severity bands |
| Tier reliability | tier_reliability.py | Per-tier reliability and supportable interpretations |
| Leading indicators | leading_indicator_model.py | Trajectory detection, cascade model, differential evolution optimizer |
| Adaptive testing | cat_engine.py, cat_longitudinal.py | Max-info and change-aware item selection |
| Integrated pipeline | psychometric_pipeline.py | ABCPsychometricScorer with tier-aware output |

## Quick Start

```bash
# Setup
make setup

# Run Python tests (493 tests)
make test-python        # Original scoring pipeline (198 tests)
make test-psychometric  # Psychometric engine (295 tests)
make validate-all       # Both

# Run analysis scripts
python scripts/derive_thresholds.py
python scripts/run_model_comparison.py
python scripts/run_decision_consistency.py
python scripts/build_norms.py
python scripts/run_leading_indicator_analysis.py
```

## Project Layout

```
src/python_scoring/     # Production scoring engine (36-item pipeline)
src/psychometric/       # Gold standard psychometric engine (21 modules)
tests/python_tests/     # Scoring pipeline tests (198)
tests/psychometric_tests/ # Psychometric engine tests (295)
scripts/                # Analysis and validation scripts
config/                 # IRT parameters, thresholds, correlation matrices, norms
outputs/site/           # Interactive simulation dashboard
docs/                   # Specifications, plans, and validation documents
```

## Documentation

| Document | Purpose |
|---|---|
| [gold-standard-upgrade-plan.md](docs/gold-standard-upgrade-plan.md) | Complete work plan with phase-by-phase results |
| [phase-two-plan-instrument-expansion.md](docs/phase-two-plan-instrument-expansion.md) | 36-item expansion and archetype revision plan |
| [validity-argument.md](docs/validity-argument.md) | Formal validity argument per APA Standards (2014) |
| [new-items-draft.md](docs/new-items-draft.md) | 12 new items for expert review |
| [abq-coach-integration-spec.md](docs/abq-coach-integration-spec.md) | ABQ and coach rating integration specification |
| [prd-second-game-criterion-integration.md](docs/prd-second-game-criterion-integration.md) | PRD for platform integration |
| [big-five-belbin-audit.md](docs/big-five-belbin-audit.md) | Big Five weight matrix and Belbin audit |
| [abc-assessment-spec.md](docs/abc-assessment-spec.md) | Technical specification |
| [white-paper-abc-simulator.md](docs/white-paper-abc-simulator.md) | Simulation methodology |

## Key Findings

1. **Type stability at 90%** with 6 items per subscale (up from 82% with 4 items)
2. **Frustration rises 1.5 timepoints before satisfaction drops** (SDT cascade confirmed)
3. **8 base patterns** are more reliable than 24 types (~50-55% vs ~31% agreement)
4. **Empirical thresholds** (frust: 4.82, sat: 6.09) differ from fixed (4.38, 6.46) but both within 95% CIs
5. **Bifactor omega-h = 0.246**: six subscales carry independent variance, no dominant general factor

## Transparency

This is an AI-developed instrument. No licensed SDT materials were used. We are transparent about what has confidence (the analytic infrastructure, the theoretical framework, the simulation results) and where further research is needed (empirical criterion validation, item-level calibration on real data). See [validity-argument.md](docs/validity-argument.md) for the full evidence map.
