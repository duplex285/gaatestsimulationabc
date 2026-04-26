---
layout: default
title: Methods (Audit)
---

# Methods: Psychometric Infrastructure for ABC

**Audience.** Psychometricians conducting external review.
**Purpose.** Document the analytic methods, the libraries used (per CLAUDE_RULES.md Rule 1: no custom statistical implementations), and the specific decisions that depart from default usage.

---

## 1. Measurement model

### 1.1 IRT (Samejima Graded Response Model)

**Library.** `numpy`, `scipy.optimize` (custom EAP integration; `mirt`-equivalent functionality).
**Module.** `src/psychometric/irt_estimation.py`.
**Specification.** Two-parameter graded response with item discrimination (`a`) and per-category thresholds (`b_1` through `b_6` for 7-point Likert).
**Estimation.** Marginal maximum likelihood for item parameters (calibration phase, against synthetic ground truth); EAP with quadrature for person estimates (theta), with standard errors from the posterior variance.
**Reproducibility.** Seed 42 throughout. Parameter recovery validated on synthetic data with known generating parameters.

### 1.2 CFA and bifactor

**Library.** `semopy` (Python equivalent of lavaan, supports MLR for continuous Likert).
**Module.** `src/psychometric/factor_models.py`.
**Specifications fitted.**

| Model | Specification | Parameters |
|---|---|---|
| 6-factor CFA | A_sat, A_frust, B_sat, B_frust, C_sat, C_frust as correlated factors | factor variances fixed to 1 |
| Bifactor (orthogonal) | General factor + 6 specific factors, all orthogonal | factor variances fixed to 1 |
| Method-factor CFA | 6 substantive factors + method factor on the 12 reverse items | method factor uncorrelated with substantive |
| ESEM (added 2026-04-25, WI-2) | EFA via `factor_analyzer` + Procrustes target rotation + EwC respecification in semopy | target pattern from CFA |
| Bifactor-ESEM 1-G (added 2026-04-25, WI-8) | One global fulfillment factor (sat positive, frust negative) + 6 specifics | per Toth-Kiraly 2018 |
| Bifactor-ESEM 2-G (added 2026-04-25, WI-8) | Two correlated globals (sat-G, frust-G) + 6 specifics | per Toth-Kiraly 2018 |

**Decision rule for 1-G vs 2-G (Toth-Kiraly 2018).** Adopt 1-G if (a) ΔBIC > 10 in favor of 1-G OR ΔBIC < 10 favoring 2-G is not enough to overturn the parsimony preference, AND (b) G-factor loadings show the bipolar pattern (positive sat, negative frust). Adopt 2-G if it fits substantially better with low G-G correlation (|r| < 0.5). Otherwise label "ambiguous".

### 1.3 ESEM approximation route (Decision-1)

The current implementation is the three-step "middle path" per Marsh et al. (2014):
1. EFA via `factor_analyzer.FactorAnalyzer(rotation=None, method='ml')`.
2. Procrustes target rotation toward the CFA pattern matrix.
3. Re-fit in semopy as CFA-with-cross-loadings (EwC), freeing every cross-loading whose Procrustes-rotated absolute value exceeds 0.10.

**This is NOT full-information ML ESEM** as Asparouhov & Muthen (2009) define it. Trustworthy fit indices (chi2, CFI, RMSEA) come from step 3 (the CFA respecification), not from the EFA in step 1. The approximation is acceptable for Phase A descriptive validation. For Phase B criterion-validity work with structural paths to outcomes, the plan migrates to `rpy2` + `lavaan` for true ML ESEM.

This limitation is documented in the function docstring and in `validity-argument.md`.

---

## 2. Reliability and decision consistency

### 2.1 Coefficient omega family

**Library.** `numpy` (computed from semopy bifactor estimates).
**Module.** `src/psychometric/omega_coefficients.py`.
**Coefficients reported.**

| Coefficient | Interpretation |
|---|---|
| omega_total | Total reliability of the composite |
| omega_h | Reliability attributable to the general factor (low value = no dominant general factor) |
| omega_h-S | Per-subscale reliability attributable to the specific factor after partialing the general factor |
| omega_s | Per-subscale reliability without controlling for the general factor |
| ECV | Explained common variance attributable to the general factor (proportion of variance) |

**Current synthetic data result.** omega_h = 0.246 (a low value; consistent with no dominant general factor). ECV = 0.061. This is expected and welcome: SDT does not predict a general factor across the three needs (Howard 2024 Ch. 22, pp. 33-34). Empirical Phase A data will determine if this holds.

### 2.2 Tier reliability

**Module.** `src/psychometric/tier_reliability.py`.
**Tiers.** 6-item (onboarding), 12-item (standard), 24-item (full as of v1), 36-item (full as of v2).
**Marginal reliability** (synthetic data): 0.714 / 0.870 / 0.943 / projected 0.96.

### 2.3 Decision consistency

**Module.** `src/psychometric/decision_consistency.py`.
**Methods.** Classification agreement across simulated readministrations; conditional SEM at each cut score; difference reliability per Jacobson-Truax RCI.

---

## 3. Person-centered analysis

### 3.1 Latent profile analysis (LPA, WI-16)

**Library.** `sklearn.mixture.GaussianMixture`.
**Module.** `src/psychometric/profile_analysis.py`.
**Indicators.** Bifactor-ESEM factor scores from the 1-G or 2-G model (whichever wins WI-8), NOT raw subscales. Per Morin & Marsh (2015), bifactor scores separate level (G-factor) from shape (S-factors); raw subscales conflate them.
**Model selection.** Five-criterion convention per Howard 2020, Fernet 2020, Wang 2016:
1. ABIC elbow inspection
2. BIC + CAIC + ABIC weighted majority
3. aLMR (Lo, Mendell, Rubin 2001) or BLRT non-significance
4. Substantive interpretability
5. Entropy >= 0.70 for posterior assignment

**Departure from defaults.** sklearn does not provide aLMR or BLRT directly. For aLMR: analytical chi-square approximation per Lo, Mendell, Rubin 2001. For BLRT: parametric bootstrap (sample from null model, refit alternative; ~100 reps for speed). If implementation cost exceeds time budget, the plan documents that aLMR/BLRT are not yet implemented and selection relies on BIC + ABIC + entropy + interpretability.

**Expected k.** k = 3 to 5 per literature cap (Howard 2020 found k=4 in N=510; Fernet 2020 k=4 in N=438; Wang 2016 k=5 in N=3,220 PE students). ABC's eight a-priori archetypes are theoretical, not empirical; LPA in parallel as discriminant evidence per Decision-2.

### 3.2 Latent transition analysis (LTA, WI-5)

**Library.** Built atop `profile_analysis.py`.
**Module.** `src/psychometric/latent_transition.py`.
**Approach.** Stacked-LPA simplification: fit LPA on stacked-across-time data with class definitions held constant, then assign per timepoint. **NOT** full Mplus LTA with joint likelihood transition probabilities and standard errors. Documented limitation; Phase B can migrate to Mplus or `tidyLPA`.

**Expected transition matrix patterns.** Diagonal in the 0.50-0.75 range based on Fernet 2020 (developmental population, 24-month interval, 30-40% transition rate). Howard 2020 (mature workforce, 4-month interval) showed >97% diagonal stability and is not a relevant comparison for athletes.

---

## 4. Relations to outcomes

### 4.1 Relative weight analysis (RWA, WI-6)

**Library.** `numpy` (eigendecomposition), `scipy.stats` (BCa bootstrap).
**Module.** `src/psychometric/relative_weight.py`.
**Specification.** Johnson 2000 SVD-based decomposition. Five-step algorithm: standardize, eigendecompose R_xx, compute Λ* = Q Λ^(1/2) Q', regress Y on orthogonal Z, sum squared products. Returns raw weights (sum to R²) and rescaled weights (sum to 1.0). 95% CIs via 10,000-replication BCa bootstrap.

**Validation.** Reproduce RWA-Web (Tonidandel & LeBreton 2015) demo dataset to ±0.005 on raw weights.

**Use restrictions.** RWA is a SUPPLEMENT to regression, not a replacement (Tonidandel & LeBreton 2011). Use only when (a) regression model is correctly specified, (b) predictors correlated (r_xx > 0.20 among at least one pair), (c) goal is variance partitioning for explanation, not prediction, (d) criterion is treated as fixed.

### 4.2 Polynomial regression with response surface analysis (WI-9)

**Library.** `numpy.linalg.lstsq`, `scipy.stats`.
**Module.** `src/psychometric/response_surface.py`.
**Replaces.** The legacy difference-score `gap = team - personal` in `context_gap.py` (deprecated 2026-04-25).
**Specification.** `Outcome = b0 + b1*Personal + b2*Team + b3*Personal² + b4*Personal*Team + b5*Team² + e`.
**Difference-score test.** Constraints `b1 = -b2` AND `b3 = b4 = b5 = 0` tested as nested model F-test. If rejected, the difference-score hypothesis fails. Per Edwards (2001) Myth 4, this test almost always rejects.
**Output.** Coefficients with standard errors, surface peak coordinates, line-of-agreement and line-of-disagreement slopes, curvature.

### 4.3 Measurement invariance and DIF

**Modules.** `src/psychometric/measurement_invariance.py`, `src/psychometric/dif_analysis.py`.
**Methods.** Configural/metric/scalar invariance via semopy nested model comparisons. Chen (2007) thresholds: ΔCFI ≤ 0.010, ΔRMSEA ≤ 0.015. Logistic-regression DIF per item across binary group factors. For Phase A: gender, sport type (individual vs team), competitive level, age band.
**For small subgroups.** Plan migrates to alignment method (Asparouhov & Muthen 2014) via `rpy2` to `MplusAutomation` or `sirt::invariance.alignment`; not yet implemented.

---

## 5. Diagnostics

### 5.1 Forward-only vs reverse-only correlation (WI-13)

**Module.** `src/psychometric/keying_diagnostic.py`.
**Test.** Per subscale, correlate forward-only mean (4 items) with reverse-only mean (2 items, sign-corrected via `8 - x`). Per Kam, Meyer & Sun 2021: r >= 0.60 indicates the subscale is unidimensional in the construct-theoretical way; r < 0.60 suggests logical-response artifact OR genuine bidimensionality.

### 5.2 Quadratic trait-by-method interaction (WI-13)

Same module. Define method factor as `reverse_recoded_mean - forward_mean`. Regress on theta and theta². Significant quadratic term (p < 0.05, |coef| >= 0.10) confirms the Kam logical-response artifact.

### 5.3 Ideal-point misfit (WI-18, planned)

For the new bipolar-keyed items (especially polar opposites before WI-7 rewrite): compare GRM (dominance model) vs Generalized Graded Unfolding Model (GGUM, Roberts 2000). If GGUM fits substantially better, ideal-point responding is contaminating dominance-model scores.

---

## 6. Reproducibility

- All randomness seeded with `np.random.default_rng(42)` per CLAUDE_RULES.md Rule 7.
- Test suite: `make test-python` (198 tests on scoring pipeline) + `make test-psychometric` (295+ tests on psychometric engine).
- Configuration as data: `config/irt_parameters.yaml`, `config/empirical_thresholds.yaml`, `config/correlation_matrices.yaml`, `config/norming_tables.yaml`, `config/validation_thresholds.yaml`, `config/base_rates.yaml`.
- One-command reproduction: see `Makefile`.

---

## 7. Single source of truth

| Decision | Source |
|---|---|
| Mathematical formulas | `docs/abc-assessment-spec.md` Section 13 |
| Validation thresholds | `config/validation_thresholds.yaml` |
| Correlation matrices | `config/correlation_matrices.yaml` |
| R methodology | lavaan (no custom CFA code) |
| Python correctness | `tests/python_tests/`, `tests/psychometric_tests/` |
| Expected results | R validation outputs (ground truth) |
| Environment setup | `Makefile` |
| Implementation plan | `docs/howard-2024-implementation-plan.md` |
| Activity log | `docs/literature-review-activity-log.md` |

---

## 8. References (key methods)

- Asparouhov, T., & Muthen, B. (2009). Exploratory structural equation modeling. *Structural Equation Modeling*, 16(3), 397-438.
- Edwards, J. R. (2001). Ten difference score myths. *Organizational Research Methods*, 4, 265-287.
- Howard, J. L. (2024). Psychometric Approaches in Self-Determination Theory: Meaning and Measurement. *Oxford Handbook of SDT*, Ch. 22.
- Howard, J. L., Gagne, M., Van den Broeck, A., et al. (2020). A review and empirical comparison of motivation scoring methods. *Motivation and Emotion*, 44(4), 534-548.
- Johnson, J. W. (2000). A heuristic method for estimating the relative weight of predictor variables in multiple regression. *Multivariate Behavioral Research*, 35(1), 1-19.
- Kam, C. C. S., Meyer, J. P., & Sun, S. (2021). Why do people agree with both regular and reversed items? A logical response perspective. *Assessment*, 28(4), 1110-1124.
- Marsh, H. W., Morin, A. J. S., Parker, P. D., & Kaur, G. (2014). Exploratory structural equation modeling. *Annual Review of Clinical Psychology*, 10, 85-110.
- Morin, A. J. S., & Marsh, H. W. (2015). Disentangling shape from level effects in person-centered analyses. *Structural Equation Modeling*, 22(1), 39-59.
- Toth-Kiraly, I., Morin, A. J. S., Bothe, B., Orosz, G., & Rigo, A. (2018). Investigating the multidimensionality of need fulfillment: A bifactor exploratory structural equation modeling representation. *Structural Equation Modeling*, 25(2), 267-286.

Full reference list in [howard-2024-implementation-plan.md](howard-2024-implementation-plan.html) Section V2-J.
