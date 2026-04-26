# Howard 2024 (Oxford Handbook Ch. 22) Implementation Plan

**Source paper:** Howard, J. L. (2024). Psychometric Approaches in Self-Determination Theory: Meaning and Measurement. In Ryan & Deci (eds.), *Oxford Handbook of Self-Determination Theory*, Ch. 22.

**Created:** 2026-04-25
**Last updated:** 2026-04-25 (literature review v2 added; see Section "Literature Review v2" at end)
**Owner:** Greg Akinbiyi
**Status:** Plan drafted, awaiting decisions on three original blockers plus four new blockers from literature review. Implementation paused pending item-rewrites (WI-7).

---

## Purpose

Track the work needed to align ABC's psychometric pipeline with Howard's recommendations. This file is a living progress log: every work item carries a status, every open question carries a blocker tag, every issue raised mid-implementation goes here.

This plan was extracted from a review of Chapter 22 against ABC's current architecture (`src/psychometric/factor_models.py`, `src/psychometric/leading_indicator_model.py`, `src/python_scoring/type_derivation.py`, `src/python_scoring/domain_classification.py`, `docs/validity-argument.md`).

---

## Quick reference: what Howard's chapter says

| Howard recommendation | ABC current state | Gap |
|---|---|---|
| Subscale-level scoring is the truest representation | Six subscales preserved end-to-end | None |
| Bifactor for needs is methodological, not theoretical | Bifactor run; framing currently ambiguous | Reframe in validity-argument.md |
| ESEM solves multicollinearity | Referenced in docstring, not implemented | Build it |
| Bipolar vs unipolar test for sat/frust | Untested; CFA mechanically favors unipolar | Build per-domain bifactor |
| Latent profile analysis is the gold standard for archetypes | 8 archetypes are a-priori binary | Add LPA in parallel |
| Latent transition analysis for trajectory work | Continuous-theta cascade only | Add LTA as complement |
| Relative weight analysis for correlated predictors | Not implemented | Build for criterion validation |
| IRT is underused in SDT | Already done (Graded Response Model, EAP) | None |
| Anchor-item bifactor (Zhang 2020), S-1 (Burns 2019) | Not implemented | Lower priority follow-up |
| Open data, full subscale-level reporting | Already the convention | Reaffirm in publication plan |

---

## Work items

Status legend: PLANNED, IN PROGRESS, BLOCKED, COMPLETE, ABANDONED.

### WI-1: Reframe bifactor as methodological in validity-argument.md

**Status:** PLANNED
**Priority:** 1 (do first, cheapest)
**Files touched:** `docs/validity-argument.md` only.
**Effort:** 30 minutes.
**Tests:** none (documentation only).

**Description.** After line 79 in section (c), insert a paragraph stating that ABC's bifactor analysis is a methodological test of multidimensionality (Howard 2024, pp. 33-34), not a theoretical claim of a general need-satisfaction factor. SDT does not predict a general factor across the three needs (unlike the self-determination continuum in motivation regulations). Omega-h = 0.246 and ECV = 0.061 are the expected and welcome result, not a weakness.

**Cross-reference.** Section 16.4 of `improvement-plan-personalization-engine.md` already calls for adding a bifactor S-1 specification for the same reasons. Coordinate the language so both documents agree.

**Blockers:** none.

---

### WI-2: ESEM in factor_models.py

**Status:** PLANNED
**Priority:** 2
**Files touched:** `src/psychometric/factor_models.py`, `tests/psychometric_tests/test_factor_models.py`.
**Effort:** 1 to 2 days.
**Depends on:** decision on Conflict-3 (ESEM approximation route).

**New API.**
```
fit_esem_model(data, item_names, factor_map, target_loadings=None) -> dict
```

**Implementation.** Two-step procedure: (a) `factor_analyzer.FactorAnalyzer(rotation=None)` extracts six unrotated factors. (b) Procrustes target rotation toward the CFA pattern matrix using closed-form SVD on `Λ_target.T @ Λ_unrotated`. Factor correlations re-estimated from the rotated structure. Output dict shape matches `fit_cfa_model` plus `cross_loadings` and `interfactor_correlations`.

**Why not lavaan.** Full-information ML ESEM lives in Mplus and lavaan. The pure-Python target-rotated EFA approximation avoids adding `rpy2` and an R install to CI. The actionable comparison (do interfactor correlations drop materially under cross-loadings) is preserved. Document the approximation in the docstring.

**Tests.**

| Test name | Fixture | Assertion |
|---|---|---|
| `test_esem_fits_clean_data` | `clean_six_factor_data` | returns dict with `cfi`, `rmsea`, `cross_loadings`, `interfactor_correlations` |
| `test_esem_reduces_interfactor_correlation` | new fixture: 6-factor with simulated cross-loadings of 0.2 | mean off-diagonal of `interfactor_correlations` from ESEM < CFA on same data |
| `test_esem_recovers_target_pattern` | `clean_six_factor_data` | each item's primary loading > sum of its absolute cross-loadings |
| `test_esem_cross_loadings_small_when_clean` | `clean_six_factor_data` | 95th percentile of absolute cross-loadings < 0.20 |

**Cross-reference.** Section 12.6 of `improvement-plan-personalization-engine.md` cites Grugan et al. (2024) and promotes ESEM to Phase A as a hard gate. Section 16.4 lists ESEM as already implemented; this is incorrect (see Discrepancy D-1 below). This work item closes that gap.

**Blockers:** Conflict-3 decision.

---

### WI-3: Per-domain bipolar-vs-unipolar bifactor test

**Status:** PLANNED
**Priority:** 3
**Files touched:** `src/psychometric/factor_models.py`, `scripts/run_bipolar_test.py` (new), `tests/psychometric_tests/test_bipolar_unipolar.py` (new).
**Effort:** 1 day.
**Depends on:** WI-2 refactor of `_build_bifactor_syntax`.

**New API.**
```
fit_per_domain_bifactor(data, item_names, domain_map, valence_map) -> dict
```
Returns three nested dicts keyed by domain (Ambition, Belonging, Craft), each containing fit indices and omega coefficients for the per-domain bifactor (general domain factor + sat S-factor + frust S-factor).

**New script.** `scripts/run_bipolar_test.py`. For each domain, fit three competing models on the relevant 12 items:

1. *Bipolar*: one-factor CFA, frustration items reverse-scored.
2. *Unipolar*: two-factor CFA, sat and frust as correlated factors.
3. *Bifactor*: general domain + sat + frust S-factors.

Decision rule (Howard pp. 35-36): unipolar is supported if (a) bifactor S-factor mean loadings > 0.30 and (b) S-factors uniquely predict an external criterion above the general factor. Bipolar is supported if S-factor loadings collapse toward zero.

**Tests.**

| Test name | Fixture | Assertion |
|---|---|---|
| `test_unipolar_synthetic_recovers_two_factors` | data simulated with two distinct sat/frust factors per domain (r ≈ 0.4) | bifactor S-factor mean loading > 0.40 for both sat and frust |
| `test_bipolar_synthetic_collapses_s_factors` | data simulated with one bipolar factor per domain | bifactor sat or frust S-factor mean loading < 0.20 |
| `test_per_domain_returns_three_domains` | `clean_six_factor_data` | result keys == {Ambition, Belonging, Craft} |
| `test_per_domain_omega_h_per_domain` | `clean_six_factor_data` | each domain's general-factor omega-h is between 0 and 1 |

**Refactor needed.** `_build_bifactor_syntax` currently builds one general factor across all 24 items. Extract `_build_bifactor_syntax_subset(items, specific_factor_map)`; have the existing function delegate to it. Backwards-compatible.

**New conftest fixture needed.** `bipolar_synthetic_data`: data generated from a single bipolar factor per domain, frustration items reverse-loaded. Local to the test file; do not perturb the global simulator generators.

**Cross-reference.** None directly in `improvement-plan-personalization-engine.md`. This is a net-new analytic capability not previously planned.

**Blockers:** WI-2 must land first.

---

### WI-4: Latent profile analysis

**Status:** BLOCKED on Conflict-1 decision.
**Priority:** 4
**Files touched:** `src/psychometric/profile_analysis.py` (new), `scripts/run_lpa.py` (new), `tests/psychometric_tests/test_profile_analysis.py` (new).
**Effort:** 1 to 2 days.

**New API.**
```
fit_lpa(scores, k_range=(2, 10), random_state=42) -> dict
compare_to_archetypes(lpa_result, archetype_labels) -> dict
profile_centroids(lpa_result, scores) -> pd.DataFrame
```

`fit_lpa` wraps `sklearn.mixture.GaussianMixture` for each k, returns BIC, AIC, entropy, log-likelihood, posterior class probabilities, and selected k via lowest BIC with a 2% tolerance rule.

`compare_to_archetypes` computes adjusted Rand index and confusion matrix between empirical LPA classes and the eight a-priori archetypes from `type_derivation.py`.

**Tests.**

| Test name | Fixture | Assertion |
|---|---|---|
| `test_lpa_recovers_known_classes` | mixture of three Gaussians with separated means | selected k == 3 |
| `test_lpa_bic_decreases_then_increases` | three-class data | BIC at k=3 < BIC at k=2 and BIC at k=3 < BIC at k=8 |
| `test_lpa_returns_posterior_probabilities` | three-class data | posterior shape == (n_persons, k); rows sum to 1 |
| `test_compare_to_archetypes_returns_ari` | known matched labels | adjusted Rand index = 1.0 for identical clusterings |
| `test_lpa_runs_on_six_dim_subscale_input` | simulator output, 6 columns | no error, k between 2 and 10 |

**Cross-reference.** Section 12.7 of `improvement-plan-personalization-engine.md` cites Fernet et al. (2020) on profile stability via LTA but does not implement LPA. This work item is the missing prerequisite for any LTA work.

**Blockers:** Conflict-1 decision required (LPA versus the eight a-priori archetypes).

---

### WI-5: Latent transition analysis

**Status:** BLOCKED on WI-4.
**Priority:** 5
**Files touched:** `src/psychometric/latent_transition.py` (new), `scripts/run_lta.py` (new), `tests/psychometric_tests/test_latent_transition.py` (new).
**Effort:** 2 days.

**New API.**
```
estimate_transition_matrix(class_assignments, n_classes) -> np.ndarray
fit_lta(scores_over_time, n_classes, n_timepoints) -> dict
cascade_lead_time(transitions, frustration_class, satisfaction_class) -> float
```

**Implementation note.** Fully Bayesian LTA (Mplus-style) is out of scope for this iteration. The simplification: fit LPA on stacked-across-time data with class definitions held constant, then assign per timepoint. Document this clearly.

**Tests.**

| Test name | Fixture | Assertion |
|---|---|---|
| `test_transition_matrix_rows_sum_to_one` | random class assignments | each row sums to 1.0 within tolerance |
| `test_transition_matrix_diagonal_high_when_stable` | mostly-stable assignments | mean of diagonal > 0.80 |
| `test_lta_recovers_known_transitions` | synthetic two-state Markov chain with known transition matrix | recovered matrix within 0.05 of true |
| `test_cascade_lead_time_detects_frustration_first` | synthetic trajectory where frustration class precedes satisfaction class by 2 timepoints | returns lead time in [1.5, 2.5] |

**Cross-reference.** Section 12.7 of the personalization plan cites LTA as motivation for adjusting confidence thresholds in the transition engine but does not propose an LTA implementation. This work item delivers the missing analytic capability.

**Critical.** Do not retire `leading_indicator_model.py`. LTA is a complement, not a replacement. Phase 2b explicitly retreated from categorical state classification because it produced ~31% agreement (per `type_derivation.py:18-23`). Position LTA as person-centered confirmation of the continuous-trajectory cascade.

**Blockers:** WI-4 must land first.

---

### WI-6: Relative weight analysis

**Status:** PLANNED
**Priority:** 6 (but can run in parallel with WI-2)
**Files touched:** `src/psychometric/relative_weight.py` (new), `scripts/run_relative_weight.py` (new), `tests/psychometric_tests/test_relative_weight.py` (new).
**Effort:** half a day.

**New API.**
```
relative_weights(predictors: np.ndarray, criterion: np.ndarray) -> dict
```

Implements Johnson (2000) via SVD of the predictor correlation matrix, regression of criterion on the orthogonal components, then transformation back to the original predictor space. Returns raw weights and rescaled-to-100% weights summing to R².

**Tests.**

| Test name | Fixture | Assertion |
|---|---|---|
| `test_weights_sum_to_r_squared` | synthetic correlated predictors with known R² | sum of raw weights ≈ R² within 1e-6 |
| `test_uncorrelated_predictors_give_squared_betas` | orthogonal predictors | weights ≈ squared standardized betas |
| `test_rescaled_weights_sum_to_one` | any data | rescaled weights sum to 1.0 |
| `test_dominant_predictor_gets_highest_weight` | one strong, five noise predictors | dominant predictor has highest weight |
| `test_handles_six_correlated_subscales` | six ABC-like predictors, mean r ≈ 0.4 | runs, returns six weights, none NaN |

**Cross-reference.** Not previously planned. `validity-argument.md` lines 101 to 105 list ABQ, BPNSFS, and coach ratings as criterion variables; relative weight analysis is the right tool for those regressions because the six ABC subscales will be highly correlated and OLS coefficients unstable.

**Blockers:** none.

---

## Open decisions (BLOCKERS)

These must be resolved before the implementation can proceed past WI-1.

### Conflict-1: LPA versus the eight a-priori archetypes

**Status:** OPEN
**Blocks:** WI-4, WI-5.
**Decision needed by:** before WI-4 starts.

`type_derivation.py:13-29` defines eight archetypes via binary thresholds on satisfaction. They are theoretical, not data-derived. LPA on real data could produce a different number of profiles, or profiles whose centroids do not map to the binary archetypes (for example, a "moderate-everything" cluster the binary scheme cannot represent).

Three options:

1. **Recommended.** Keep the eight archetypes as the theoretical taxonomy used in scoring and reports. Run LPA in parallel and report it as discriminant-validity evidence in `validity-argument.md`. If LPA strongly disagrees (BIC delta > 10, entropy > 0.80), flag it as a finding, not an automatic override.
2. Replace archetypes with LPA classes if the empirical solution is decisively preferred. Risk: every report and downstream module that references the eight archetype names breaks.
3. Hybrid: keep archetypes for population-level reports; use LPA posterior probabilities for individual-level confidence statements.

### Conflict-2: LTA versus the continuous-theta cascade model

**Status:** ADDRESSED (recommendation locked in plan; user confirm).
**Recommendation.** LTA complements `leading_indicator_model.py`; it does not replace it. Both reported in parallel. No code retired.

### Conflict-3: ESEM approximation route

**Status:** OPEN
**Blocks:** WI-2, WI-3.

Pure-Python target-rotated EFA via `factor_analyzer` is not full-information ML ESEM. The dominant comparison (interfactor correlations under CFA versus ESEM) is preserved, but `chi2`, `CFI`, `RMSEA` are computed from the rotated solution and are not identical to lavaan or Mplus ESEM output.

Two options:

1. **Recommended.** Ship the `factor_analyzer` approximation now, document the limitation in the docstring, leave a stub for an `rpy2`-based exact implementation if reviewers demand it.
2. Add `rpy2` and an R install to CI now, implement true lavaan-driven ESEM. Higher infrastructure cost; cleaner numbers.

---

## Discrepancies and overlaps with `improvement-plan-personalization-engine.md`

### D-1: ESEM is claimed as implemented but is not

**Severity:** high
**Location:** `improvement-plan-personalization-engine.md` Section 16.4 status row (line 1416).

The status table says "ESEM already exists in `factor_models.py`." Direct inspection shows `factor_models.py` references ESEM only in a docstring comment (`factor_models.py:8`) and never implements `fit_esem_model` or any rotation logic. Section 12.6 of the same plan promotes ESEM to a Phase A hard gate and clearly assumes a working implementation.

**Resolution.** WI-2 closes this gap. Update Section 16.4 of the personalization plan once WI-2 lands.

### D-2: Bifactor S-1 is in 16.4 but not yet specified

**Severity:** medium
**Location:** Section 16.4 (lines 1525 to 1527).

The personalization plan calls for a bifactor S-1 specification anchored on overall satisfaction across the three domains. The Howard chapter recommends anchor items more broadly (Zhang et al. 2020). Both point in the same direction.

**Resolution.** Add bifactor S-1 as WI-8 (a follow-up after WI-2, WI-3) once the ESEM and per-domain bifactor work has shipped. The S-1 specification is small (one new function in `factor_models.py`) but should not run before the bipolar test, because the per-domain results inform what the S-1 anchor should be.

### D-3: LPA and LTA are motivated in 12.7 but not implemented

**Severity:** medium
**Location:** Section 12.7 (lines 1320 to 1341).

The personalization plan cites Fernet et al. (2020) on profile stability via LTA and uses it to justify adjusting confidence thresholds in `transition_engine.py`. No LPA or LTA module is proposed. The threshold change applies on top of the existing rule-based archetype system.

**Resolution.** WI-4 and WI-5 deliver the missing analytic infrastructure. The threshold change in 12.7 stands on its own and does not require WI-4 or WI-5 to ship.

### D-4: Relative weight analysis is absent from the personalization plan

**Severity:** low
**Location:** Section 13.1 to 13.2 (validation roadmap).

The validation roadmap names BPNSFS, ABQ, BFI-2, and coach ratings as criterion variables but does not specify the regression methodology. The six ABC subscales are highly correlated; OLS regression coefficients will be unstable. Relative weight analysis (Howard chapter pp. 13 to 15) is the standard remedy.

**Resolution.** WI-6 delivers it. Cross-link from Section 13 of the personalization plan once WI-6 lands.

### D-5: Bipolar versus unipolar test is absent everywhere

**Severity:** medium
**Location:** not present.

Neither the personalization plan nor the validity argument tests whether satisfaction and frustration are two unipolar constructs or one bipolar continuum. Howard names this as the single most consequential test for instruments like ABC that measure both poles separately (Ch. 22 pp. 35 to 36).

**Resolution.** WI-3 delivers it. Add a results section to `validity-argument.md` once WI-3 ships.

### D-6: Eight-archetype taxonomy is "Done" in 16; LPA threat unrecognized

**Severity:** medium
**Location:** `improvement-plan-personalization-engine.md` Section 16.9 ("What this section does not change") and Section 14 implementation priority.

Section 16.9 lists "the 8-pattern archetype system and frustration-signature detection remain unchanged" as a non-negotiable. LPA on Phase A data may produce a different empirical class structure. The personalization plan does not anticipate this conflict.

**Resolution.** Conflict-1 above. Whichever option the user picks, update Section 16.9 of the personalization plan to reflect the chosen rule.

### Overlap-1: Output rigor (Section 17) applies to all new modules

**Severity:** informational
**Location:** Section 17 (lines 1591 to end).

Section 17 mandates that no technical construct from Sections 12 or 16 ever appears in athlete- or coach-facing surfaces. The same gate applies to LPA classes, LTA transition matrices, and ESEM cross-loadings. None of WI-2 through WI-6 produce athlete-facing output directly; they are analytic infrastructure. But any narrative or report that consumes their output must route through the translation layer.

**Resolution.** Document this constraint in each new module's docstring. No additional code changes needed at this stage.

### Overlap-2: Bayesian architecture (Section 15) applies to LPA posteriors

**Severity:** informational
**Location:** Section 15 (lines 1388 to 1396).

The Bayesian principle (prior, likelihood, posterior) applies cleanly to LPA: the posterior class probabilities from `fit_lpa` are exactly the kind of uncertainty estimate Section 15 calls for. If the user picks the hybrid option for Conflict-1, LPA posteriors plug directly into the existing Bayesian narrative engine.

**Resolution.** No change needed. Worth noting when WI-4 lands.

---

## Sequencing

```
WI-1  ────► (text only, lands first)
                                          ┌─► WI-3 ────┐
WI-2  ────►(after Conflict-3 decision)────┤            ├─► WI-8 (S-1, follow-up)
                                          └────────────┘
WI-6  ────► (parallel with WI-2; independent)

WI-4  ────►(after Conflict-1 decision)────► WI-5
```

---

## Issue log

Empty. Append entries here as implementation surfaces problems.

Format:
```
- [YYYY-MM-DD] WI-X: short title
  Description.
  Resolution: ... or OPEN.
```

---

## What this plan does not cover

- **Anchor-item bifactor (Zhang 2020).** Mentioned in Howard pp. 38; lower priority. Add as WI-9 if reviewers request. (Update from Lit Review v2: now elevated; see WI-8 below.)
- **S-1 bifactor (Burns 2019).** Folded into WI-8 (see D-2). (Update from Lit Review v2: now first-class; see WI-8 below.)
- **Open data infrastructure.** Howard pp. 51 to 56 calls for raw data made publicly available. Procedural, not technical. Out of scope for this plan.
- **IRT.** Already implemented in `irt_estimation.py`. No work needed. (Update from Lit Review v2: DIF and ideal-point misfit now needed; see WI-17, WI-18.)

---

# Literature Review v2 (2026-04-25)

**Purpose.** Six parallel research agents read 49 papers in `Library/CloudStorage/ProtonDrive-greg@allostasis.xyz-folder/SDT/Psychometric Assessments/`. The findings substantially extend and in places overturn the v1 plan above. This section captures the new findings, the new work items they generate, and the discrepancies they expose against `abc-assessment-spec.md`, `new-items-draft.md`, `validity-argument.md`, and `improvement-plan-personalization-engine.md`.

**Method.** Cluster 1: bifactor and bifactor-ESEM in SDT (8 papers). Cluster 2: ESEM methodology and MWMS (4 papers). Cluster 3: person-centered analysis (LPA, LTA, profiles) (6 papers). Cluster 4: RAI, continuum, scoring methods (8 papers). Cluster 5: need thwarting and SDT meta-analyses (9 papers). Cluster 6: relative weight analysis, IRT, reverse items (5 papers). Foundational and open-science papers (9 papers) read for context only.

## V2-A: Headline shifts from v1

| v1 position | v2 finding | Source |
|---|---|---|
| ESEM via factor_analyzer + Procrustes is "approximate ESEM" | Don't call it ESEM. Use the three-step middle path: EFA + Procrustes target rotation, then re-fit in semopy as CFA-with-cross-loadings (EwC) for valid fit indices. Plan rpy2 + lavaan for Phase B. | Asparouhov & Muthen 2009; Marsh et al. 2014 |
| WI-3 tests bipolar vs unipolar per domain | Run the GLOBAL 1-G vs 2-G bifactor-ESEM test FIRST. Toth-Kiraly et al. 2018 directly compared these on the BPNSFS (closest analogue to ABC) and 1-G won (single bipolar fulfillment continuum + 6 specifics). The per-domain test in WI-3 is the second-priority follow-up. | Toth-Kiraly 2018 |
| Bifactor omega-h = 0.246 = "no general factor, hold the line" | Reframe: it could mean the items are too local/fragmented OR that the population truly has no general factor. The interpretive question is whether the G-factor adds incremental validity over specifics, not whether omega-h crosses a cutoff. Sanchez-Oliva 2017 retained B-ESEM despite an autonomy S-factor collapsing to omega = .325. | Sanchez-Oliva 2017; Toth-Kiraly 2018; Howard 2018 |
| LPA decision rule: BIC delta > 10 | Replace with five-criterion convention: ABIC elbow + BIC + CAIC + ABIC weighted majority + aLMR or BLRT non-significance + interpretability + entropy >= 0.70. The literature does not use BIC delta > 10. | Howard 2020; Fernet 2020; Wang 2016 |
| LPA may find more or fewer than 8 archetypes | Literature cap is k = 4 to 5 for SDT motivation data. Wang 2016 (closest sport analogue) found k = 5 with N = 3,220. ABC's k = 8 is empirically indefensible at any plausible Phase A sample size. The eight archetypes encode shape (Morin & Marsh 2015); LPA on raw subscales likely returns mostly level. Keep archetypes as theoretical taxonomy; report LPA in parallel. | Howard 2020; Fernet 2020; Wang 2016; Morin & Marsh 2015 |
| LPA indicators: raw subscales | Use bifactor factor scores as LPA indicators (Howard 2020, Fernet 2020). Raw subscales conflate level and shape; bifactor scores separate them. | Morin & Marsh 2015; Howard 2020 |
| Phase A target N >= 100 | Bifactor-ESEM literature requires N >= 500. Sanchez-Oliva N = 366; Gillet N = 523; Toth-Kiraly N = 2,301 + 504; Wang N = 3,220. Zhang 2020 simulations recommend N >= 600 for stable bifactor predictive models. Phase A target should rise to N >= 500 minimum. | Zhang 2020; Sanchez-Oliva 2017; Gillet 2019; Toth-Kiraly 2018 |
| Cascade lag (frustration leads satisfaction by 1.5 timepoints) is asserted in `leading_indicator_model.py` | Empirically unsupported in the corpus. Bartholomew 2011 SEM shows parallel pathways, not lagged. Howard 2020 too stable to detect cascades. Reframe as a falsifiable hypothesis, not an asserted parameter. | Bartholomew 2011; Howard 2020; Vasconcellos 2020 |
| Reverse items addressed via Murphy 2023 design (mixing keying within subscale) | Murphy fix is necessary but not sufficient. Kam, Meyer & Sun 2021 (logical-response perspective): some ABC reverse items (AS6, AF6, CF6) are "polar opposites" that form a method factor among mid-trait respondents regardless of keying mix. Rewrite as "negated regulars". | Kam, Meyer & Sun 2021 |
| Context gap = team_score - personal_score, flag at -1.5 | Difference scores fail Johns 1981 / Edwards 2001. Replace with polynomial regression + response surface analysis. The -1.5 threshold has no empirical foundation. | Johns 1981; Edwards 2001; Howard 2020 |
| 2x2 domain-state classifier (Thriving, Vulnerable, Mild, Distressed) is the primary categorization | Edwards 2001 Myth 4: trichotomizing a continuous comparison loses ~26% variance. Defensible only as a *display* layer, not the analytic unit. Always report the (sat, frust) coordinates alongside the label. Hard classify only when posterior >= 0.75; else "uncertain". | Edwards 2001; Howard 2020 |
| Ambition subscale measures need satisfaction in goal pursuit | Conflates need satisfaction with goal CONTENT (intrinsic vs extrinsic). Two athletes with identical A_sat but different aspirations have different burnout trajectories. Add 4-6 item Aspiration Index supplement as interaction layer. | Kasser & Ryan 1996; Martela 2019 |
| Frustration items are framed as active thwarting by named agents | True for AF5, BF5, CF5 (the new items). NOT true for AF1, AF2, BF1, CF3 (existing items), which drift toward dissatisfaction language and risk loading with low-satisfaction in CFA. Bartholomew's PNTS framework requires named-agent active thwarting. | Bartholomew 2011 |

## V2-B: New work items (WI-7 through WI-18)

### WI-7: Audit and rewrite reverse items per Kam 2021 (BLOCKER)

**Status:** PLANNED, BLOCKER for empirical interpretation of WI-2 and WI-3.
**Priority:** 0 (above WI-1; do this before any field test).
**Files touched:** `docs/new-items-draft.md`, `src/python_scoring/reverse_scoring.py`, `config/irt_parameters.yaml`.
**Effort:** 2 to 3 days, including expert review.

**Problem.** Kam, Meyer & Sun 2021 distinguish four item types: regular ("I am tall"), polar opposite ("I am short"), negated regular ("I am not tall"), negated polar opposite ("I am not short"). Their empirical finding (N = 529 height study): mid-trait respondents *logically* disagree with both regular and polar-opposite items. Polar opposites and their negations form a separate factor from regulars and their negations. **Mixing keying within a subscale (the Murphy 2023 fix) does not eliminate this artifact.**

**Items at high risk (polar opposites in Kam's terminology):**

| Item | Current text | Classification | Recommended rewrite |
|---|---|---|---|
| AS6 | "felt like your competitive goals no longer mattered to you" | Polar opposite | "did not feel that your competitive goals mattered to you" |
| AF6 | "felt that your training environment encouraged you to pursue your own competitive ambitions" | Polar opposite (positive content in a frust subscale) | "did not feel that your training environment supported your competitive ambitions" |
| CF6 | "your coaches create opportunities for you to practise and improve at your own pace" | Polar opposite (positive content in a frust subscale) | "your coaches did not give you opportunities to practise at your own pace" |

**Items requiring audit (text not yet classified):** BS6, BF6, CS6 likely follow the same pattern; AS5, AF5, BS5, BF5, CS5, CF5 are forward items and lower risk.

**Tradeoff to surface.** Rewriting all reverse items as negated regulars reduces content variety (every reverse becomes "did not feel X"). One option: hybrid where each subscale has one negated-regular reverse and one polar-opposite reverse, then test which loads better in Phase A and drop the worse-fitting variant in v2.

**Tests.** Add `tests/python_tests/test_reverse_item_classification.py` with one assertion per reverse item: each item's classification (regular, polar opposite, negated regular, negated polar opposite) is recorded in a config table and checked against a static expected mapping. This is documentation, not behavior, but it forces explicit classification.

**Conflict with `improvement-plan-personalization-engine.md`.** Section 17.3 (banned-term list) and Section 17 generally do not address Kam's distinction. Add to that document.

### WI-8: Global bifactor-ESEM 1-G vs 2-G test

**Status:** PLANNED, the SINGLE MOST IMPORTANT psychometric test ABC can run.
**Priority:** 1 (paired with WI-2; runs immediately after Phase A data lands).
**Files touched:** `src/psychometric/factor_models.py`, `scripts/run_global_bipolar_test.py` (new), `tests/psychometric_tests/test_global_bipolar.py` (new).
**Effort:** 1 to 2 days after WI-2 lands.

**Test specification.** Toth-Kiraly et al. 2018 ran exactly this test on the BPNSFS:
1. **1-G B-ESEM:** one global need-fulfillment continuum factor (positive loadings on 24 sat items, negative loadings on 24 frust items after sign correction) plus 6 specific factors (A_sat, A_frust, B_sat, B_frust, C_sat, C_frust), all orthogonal, target rotation.
2. **2-G B-ESEM:** two correlated global factors (one for satisfaction, one for frustration) plus 6 specifics, all orthogonal within each G-block, target rotation.
3. **Decision criteria:** lower BIC, higher CFI, interpretable G-factor loadings (positive sat / negative frust for 1-G; coherent within-G for 2-G), and crucially, the G-G correlation in the 2-G specification. Toth-Kiraly found r = -.85 (B-CFA) reduced under B-ESEM but still high enough to favor 1-G.

**Decision rule for ABC.** If 1-G fits at least as well as 2-G (Delta-BIC < 10 in favor of 2-G is not enough; need Delta-BIC > 10 favoring 1-G), and G-factor loadings show the bipolar fulfillment pattern, adopt 1-G as the primary measurement model. If 2-G fits substantially better with low G-G correlation (|r| < .5), keep the dual-pathway 2-G model.

**Implication if 1-G wins.** ABC's archetype derivation (`type_derivation.py`) currently uses binary thresholds on satisfaction. Under 1-G, the global fulfillment score (a continuous bipolar continuum) becomes the primary level estimator, and the six specifics encode shape deviations. This restructures Conflict-1 (LPA vs archetypes): archetypes are then defined as patterns of S-factor residuals around the G-factor mean, not raw subscale combinations.

**Tests.**

| Test | Assertion |
|---|---|
| `test_one_g_two_g_returns_both` | Both models fit, return distinct fit-index dicts |
| `test_g_loadings_have_correct_sign` | Under 1-G: sat items load positive, frust items load negative (after consistent keying) |
| `test_2g_correlation_estimable` | Under 2-G: G-G correlation is in [-1, 1] and SE < 0.20 |
| `test_decision_function_returns_recommendation` | Returns "1-G", "2-G", or "ambiguous" with rationale string |

### WI-9: Replace context-gap difference scores with polynomial regression

**Status:** PLANNED.
**Priority:** 3 (after WI-7, WI-8, WI-2).
**Files touched:** `src/python_scoring/context_gap.py`, new `src/psychometric/response_surface.py`, new `scripts/run_response_surface.py`.
**Effort:** 2 days.

**Replacement.** For each subscale, fit:
```
Outcome ~ b0 + b1·Personal + b2·Team + b3·Personal² + b4·(Personal·Team) + b5·Team² + e
```
Test the difference-score constraints (b1 = -b2; b3 = b4 = b5 = 0) as nested model comparisons. If the constraints fail (almost always), report the response surface: line of agreement (Personal = Team), line of disagreement (Personal = -Team), curvature parameters, surface peak coordinates.

**Display layer.** Replace the categorical "team context concern" flag with a 2D plot per subscale: (Personal, Team) point with the line of agreement drawn and the response surface gradient overlay.

**Calibrate the threshold.** Replace the -1.5 hard cutoff with the calibrated probability of concern based on the fitted surface, derived against a criterion (turnover, ABQ, dropout) once Phase A data is available.

**Tests.**

| Test | Assertion |
|---|---|
| `test_response_surface_recovers_known_pattern` | Synthetic data with congruence effect: surface peak at line of agreement, low elsewhere |
| `test_difference_score_constraint_test` | When data is generated from `Y = (Personal - Team)`, the nested-model test should NOT reject the constraints; when generated from `Y = Personal + Team^2`, it should reject |
| `test_polynomial_handles_collinearity` | Personal and Team correlated at r = 0.9, no Heywood |
| `test_visualization_emits_sat_per_athlete` | Returns coordinates for plotting, not a label |

**Conflict with current architecture.** `context_gap.py` is consumed downstream by `narrative_engine.py` and the coach dashboard. Both expect a categorical flag. Plan: keep the categorical flag as a wrapper around the polynomial result for backward compatibility, but mark it deprecated and emit the surface coordinates as the primary output.

### WI-10: Reframe cascade hypothesis as falsifiable

**Status:** PLANNED.
**Priority:** 1 (text changes only, lands with WI-1).
**Files touched:** `src/psychometric/leading_indicator_model.py` (docstrings only, no code changes), `docs/abc-assessment-spec.md`, `docs/validity-argument.md`.
**Effort:** 2 hours.

**Change.** The 1.5-timepoint frustration-leads-satisfaction cascade in `leading_indicator_model.py` is currently asserted as a model parameter. The literature reviewed (Howard 2020 work motivation LTA; Fernet 2020 24-month nurse LTA; Bartholomew 2011 sport SEM; Vasconcellos 2020 PE meta-analysis) does not support a 1.5-timepoint specific lag. Bartholomew's SEM shows parallel pathways (need support → satisfaction → vitality; need thwarting → frustration → exhaustion) with no lag claim. Fernet's LTA found directional asymmetry (Self-Determined never transitions to Poorly Motivated; reverse open) consistent with frustration-leads-satisfaction qualitatively but does not estimate a lag.

**Reframing language.** Replace "frustration rises 1.5 timepoints before satisfaction drops" with: "ABC's leading-indicator model hypothesizes that need frustration trajectories shift before need satisfaction trajectories in the burnout cascade, with a lag to be estimated empirically. Phase A data will test alternative hypotheses (parallel, simultaneous, reciprocal feedback, frustration-leads, satisfaction-leads) and select the best-fitting model."

### WI-11: Revise Phase A sample target to N >= 500

**Status:** PLANNED.
**Priority:** 2 (informs Phase A recruitment, no code changes).
**Files touched:** `docs/improvement-plan-personalization-engine.md` Section 13.1, `docs/validity-argument.md`, `docs/prd-second-game-criterion-integration.md`.

**Justification.** Bifactor-ESEM literature N range: Sanchez-Oliva 366, Gillet 523, Toth-Kiraly 2,301 + 504, Wang 3,220, Howard 1,124, Litalien 547. Zhang 2020 Monte Carlo recommends N >= 500 for stable bifactor predictive models, advises against ABiM for N < 300. With N = 100 (current Phase A target), omega_h estimates and bifactor convergence will be unreliable; the WI-2, WI-3, WI-8 results will not be interpretable.

**Recommendation.** Phase A target N >= 500 if budget allows. Minimum acceptable N = 300 for descriptive validation. If only N = 100 is feasible, frame Phase A as "feasibility pilot" and defer all bifactor-ESEM analyses to Phase B with N >= 500.

### WI-12: Revise frustration items AF1, AF2, BF1, CF3 toward active thwarting

**Status:** PLANNED.
**Priority:** 1 (must precede Phase A administration).
**Files touched:** `docs/abc-assessment-spec.md` Section 1.2, `docs/new-items-draft.md`, `config/irt_parameters.yaml`.
**Effort:** 1 day plus expert review cycle.

**Problem.** Bartholomew 2011 PNTS framework requires frustration items to describe ACTIVE THWARTING by named agents, not internal dissatisfaction. Current ABC items at risk:

| Item | Current text | Issue | Suggested revision |
|---|---|---|---|
| AF1 | "How often did you feel like you were held back" | "Held back" passive; no agent named | "How often did your coach or training plan stop you from pursuing what you wanted to work on" |
| AF2 | "How often did you feel like you were going through the motions without knowing why" | Reads as anhedonia or amotivation, not external thwarting | "How often did training feel like something done to you rather than something you chose" |
| BF1 | "How often did you feel like you had to perform a version of yourself to fit in" | Self-monitoring, not active exclusion | "How often did teammates or coaches signal that you would not be accepted as you are" |
| CF3 | "How often did you feel like feedback on your skill was more about judgment than improvement" | Captures evaluative climate but agent ambiguous | "How often did your coaches give feedback that focused on judging you rather than helping you develop" |

**Expert review gate.** Send revised items to two SDT researchers and two sport psychologists. Threshold: at least 3 of 4 reviewers rate each item as clearly tapping active thwarting on a 1-5 scale (>= 4 average). Revise until the threshold is met.

**Conflict with `new-items-draft.md`.** That document already commits to the new AF5, BF5, CF5 in this active-thwarting style. The existing AF1-AF4, BF1-BF4, CF1-CF4 items predate this commitment and are inconsistent. WI-12 brings the older items into alignment.

### WI-13: Add forward-only vs reverse-only subscale diagnostic

**Status:** PLANNED.
**Priority:** 4 (Phase A diagnostic; runs after item revision in WI-7 and WI-12).
**Files touched:** `src/psychometric/dif_analysis.py` or new `src/psychometric/keying_diagnostic.py`, `tests/psychometric_tests/test_keying_diagnostic.py`.
**Effort:** half a day.

**Test.** For each subscale, compute the correlation between the forward-only mean (4 items) and the reverse-only mean (2 items, after sign-reversal). Threshold from Kam 2021: r >= 0.60 indicates the subscale is unidimensional in the way the construct theory predicts; r < 0.60 indicates a logical-response artifact OR genuine bidimensionality.

**Also fit Kam's latent-difference method-factor model:** define a method factor as (reverse_score - forward_score) per subscale, regress it on quadratic theta. If method variance > 0.15 and is predicted by quadratic theta, confirm artifact.

**Tests.** Standard fixture and assertion patterns; one test per subscale.

### WI-14: Add unique-effects pre-registration with effect-size benchmarks

**Status:** PLANNED.
**Priority:** 2 (text changes; lands with WI-1).
**Files touched:** `docs/validity-argument.md`, new `docs/phase-a-preregistration.md`.
**Effort:** 1 day.

**Pre-registered hypotheses (samples from the literature).**

| Pair | Predicted effect | Source |
|---|---|---|
| ABC frust composite x ABQ total burnout | r = .50 to .65 | Bartholomew 2011 (r = .46 with exhaustion); Vasconcellos 2020 (r = .53 with maladaptive) |
| ABC sat composite x Subjective Vitality | r = .45 to .55 | Bartholomew 2011 (r = .47) |
| ABC within-domain sat-frust correlation | r = -.20 to -.40 | Bartholomew 2011 (r = -.21 to -.27) |
| ABC sat composite x BPNSFS sat composite | r = .55 to .75 | Construct overlap |
| ABC frust composite x BPNSFS frust composite | r = .55 to .75 | Construct overlap |
| Coach-rated IBQ support x ABC sat | r = .35 to .55 | Vasconcellos 2020 r = .57 teacher AS-need-sat; cross-rater discount ~.15 |
| ABC frust unique β on burnout (controlling for sat) | β = .30 to .50 | Bartholomew 2011 SEM |
| ABC sat unique β on vitality (controlling for frust) | β = .30 to .50 | Bartholomew 2011 SEM |
| B_frust unique effect on team turnover (controlling for B_sat) | β > 0.20 | Burton 2006 analogue |
| C_frust unique effect on burnout (controlling for C_sat) | β > 0.20 | Howard 2021 analogue |

**Anomaly flags.** ABC frust composite r with ABQ < .40 means the frust items measure low satisfaction, not thwarting; revise. Within-domain sat-frust correlation more extreme than -.55 suggests bipolar collapse; the 1-G B-ESEM (WI-8) would already detect this. ABC factor loadings on need-specific factors below .50 in ESEM means item content is weak.

**Phase A criterion variables to add:**
- Aspiration Index (12 items short form; for WI-15 goal-content discriminant validity)
- Athletic Identity Measurement Scale (AIMS, 7 items; identity foreclosure)
- Sport Motivation Scale 2 (SMS-2; behavioral regulation type, since ABC measures need satisfaction but not whether resulting motivation is intrinsic, identified, or introjected)
- Subjective Vitality Scale (Ryan & Frederick 1997; primary positive criterion for satisfaction subscales, used in Bartholomew 2011)
- Coach-rated training engagement (Big Five incremental validity test)

### WI-15: Add goal-content supplement (Aspiration Index)

**Status:** PLANNED.
**Priority:** 5.
**Files touched:** `docs/abc-assessment-spec.md` Section 1.2 (additions), new items file.
**Effort:** 2 days for item drafting and SME review.

**Justification.** Kasser & Ryan 1996 and Martela 2019 show two athletes with identical A_sat but different intrinsic-vs-extrinsic aspirations have different burnout trajectories. The current Ambition subscale (AS1 "felt genuinely excited about a goal you're working toward") does not specify whether the goal is mastery, fame, contract, or selection. ABC will misclassify these athletes if not measured.

**Items.** 4 to 6 items, separate scale (not part of the 36-item core), drawn from the Aspiration Index or SMS-2:
- Two intrinsic (mastery, growth)
- Two extrinsic (recognition, financial)
- One ambivalent (winning a major championship)

**Use.** Interaction layer: predict that athletes high on extrinsic-relative-to-intrinsic show steeper burnout cascades for the same A_frust score.

### WI-16: Update LPA decision criteria and indicators (revises WI-4)

**Status:** REPLACES the original WI-4 spec.
**Files touched:** `src/psychometric/profile_analysis.py` (new spec), `scripts/run_lpa.py`.

**Three changes to WI-4.**

1. **Replace BIC delta > 10 with five-criterion convention.** Use ABIC elbow + BIC + CAIC + ABIC weighted majority + aLMR or BLRT non-significance + interpretability + entropy >= 0.70. Test k = 1 to k = 6, expect to retain k = 3 to 5.
2. **Use bifactor-ESEM factor scores as LPA indicators**, not raw subscales. Bifactor scores separate level (G-factor) from shape (S-factors); raw subscales conflate them and LPA on raw subscales returns mostly level-ordered profiles. This depends on WI-2 and WI-8 landing first.
3. **Add Morin & Marsh 2015 Model 3 sensitivity.** LPA with a single global factor controlling level, alongside the standard LPA. Compare profile recovery between the two parameterizations.

**Labels.** Vansteenkiste-style descriptive labels for LPA classes ("High Quality Athletes," "Low Quantity Athletes," etc.); keep archetype names (Pacesetter, Anchor, etc.) for athlete-facing reports only. Every archetype reference in technical documentation must carry the descriptive sat/frust pattern alongside the name.

### WI-17: IRT-based DIF analysis for Phase A

**Status:** PLANNED.
**Priority:** 4.
**Files touched:** Extension to `src/psychometric/dif_analysis.py`, new `scripts/run_dif_analysis.py`.
**Effort:** 2 days.

**Spec.** Item-level DIF for gender (M/F/non-binary), sport type (individual vs team), competitive level (recreational, collegiate, elite), age band, and self-identified race/ethnicity. Use the IRT-covariate approach (Tay, Huang, & Vermunt 2016). For unequal subgroup sizes use random-item IRT (De Boeck 2008).

### WI-18: Ideal-point misfit check for new bipolar items

**Status:** PLANNED.
**Priority:** 4.
**Files touched:** `src/psychometric/irt_estimation.py` extension or new `src/psychometric/ideal_point.py`.
**Effort:** 2 days.

**Justification.** Lang & Tay 2020: "ideal point responding on a bipolar dimension can lead to ostensible orthogonal unipolar dimensions when dominance models are applied." Current ABC IRT uses Samejima's GRM (a dominance model). For the new polar-opposite-keyed reverse items (AS6, AF6, CF6 before WI-7 rewrite), check ideal-point misfit by comparing GRM vs Generalized Graded Unfolding Model (GGUM, Roberts 2000). Use Nye et al. 2019 comparison procedure.

## V2-C: Item-level revision summary

Combining WI-7 and WI-12, the following items need revision before Phase A administration:

| Item | Current text | Reason | Revised text |
|---|---|---|---|
| AS6 | "felt like your competitive goals no longer mattered to you" | Polar opposite (Kam 2021) | "did not feel that your competitive goals mattered to you" |
| AF1 | "felt like you were held back" | Passive, no agent (Bartholomew 2011) | "your coach or training plan stop you from pursuing what you wanted to work on" |
| AF2 | "felt like you were going through the motions without knowing why" | Anhedonia, not thwarting (Bartholomew 2011) | "training felt like something done to you rather than something you chose" |
| AF6 | "felt that your training environment encouraged you to pursue your own competitive ambitions" | Polar opposite (Kam 2021) | "did not feel that your training environment supported your competitive ambitions" |
| BF1 | "felt like you had to perform a version of yourself to fit in" | Self-monitoring, not exclusion (Bartholomew 2011) | "teammates or coaches signal that you would not be accepted as you are" |
| BS6 | TBD (audit needed) | Likely polar opposite (Kam 2021) | TBD |
| BF6 | TBD (audit needed) | Likely polar opposite (Kam 2021) | TBD |
| CS6 | TBD (audit needed) | Likely polar opposite (Kam 2021) | TBD |
| CF3 | "feedback on your skill was more about judgment than improvement" | Agent ambiguous (Bartholomew 2011) | "your coaches give feedback that focused on judging you rather than helping you develop" |
| CF6 | "your coaches create opportunities for you to practise and improve at your own pace" | Polar opposite (Kam 2021) | "your coaches did not give you opportunities to practise at your own pace" |

**Plus one new item to add:** teammate envy (PNTS R4 analogue). Suggested BF7 (or expand BF subscale to 7 items with this and revise spec): "How often in the past two weeks did teammates seem resentful or dismissive when you performed well?"

## V2-D: Theory revisions to `abc-assessment-spec.md`

1. **Strategic Context (current line 5-9).** Add explicit caveat: "ABC's six-subscale structure is empirically defensible only if the sat/frust distinction holds in the 1-G vs 2-G B-ESEM test (WI-8). If a single bipolar fulfillment continuum fits better, the six subscales remain measurement-meaningful but the global score is the primary level estimator and the six are shape deviations."

2. **Section 1.2 subscale map.** Revise the "What it captures" column for frustration subscales to explicitly invoke active thwarting by named agents:
   - A-frust: "Goal pursuit is *actively obstructed* by coaches, selectors, or organizational constraints"
   - B-frust: "Belonging is *actively thwarted* by exclusion, conditional acceptance, or rejection from teammates and coaches"
   - C-frust: "Skill development is *actively impeded* by evaluative climate, denied opportunities, or punishment for mistakes"

3. **Section 2.2 domain state classification.** Add: "The 2x2 categorization is a display layer, not the analytic unit. Per Edwards 2001, trichotomizing a continuous comparison loses approximately 26% of explained variance. Always report (sat, frust) coordinates alongside the label. Hard classification only when posterior class membership exceeds 0.75; otherwise label 'uncertain'."

4. **Section 2.7 context gap.** Replace difference-score formulation with response-surface methodology per WI-9. Update the formula and threshold language.

5. **Section 2.8 trajectory and volatility.** Soften the cascade claim per WI-10. Replace "leading indicators" with "candidate leading indicators to be empirically tested."

6. **Section 2.9 reciprocal effects and causal interpretation.** Strengthen this section: explicitly enumerate the four candidate cascade hypotheses (parallel, simultaneous, reciprocal feedback, frustration-leads, satisfaction-leads) and pre-register the test that selects among them.

7. **New section "Goal content qualifier" (after 2.x).** Reference the WI-15 Aspiration Index supplement and its interaction with Ambition.

## V2-E: Updated effect-size benchmarks for `validity-argument.md`

See WI-14 table above. Add to validity-argument.md sections (d) and (e). Each criterion correlation gets a target range, an anomaly flag threshold, and a citation.

## V2-F: New discrepancies with `improvement-plan-personalization-engine.md`

### D-7: Section 16.4 ESEM is "Done" but the implementation is the wrong kind

**Severity:** HIGH (subsumes earlier D-1).
**Location:** Section 16.4 status row.

D-1 already flagged that ESEM does not exist in `factor_models.py`. New finding from Lit Review v2: even when ESEM is added (WI-2), the factor_analyzer + Procrustes approach is NOT ESEM in the Asparouhov & Muthen 2009 sense. Section 16.4 must be updated to reflect both what is done (none yet) and what will be delivered (the EwC middle path, not full-information ML ESEM until rpy2 + lavaan in Phase B).

### D-8: Section 16.4 bifactor S-1 anchor is undefined

**Severity:** MEDIUM.
**Location:** Section 16.4 line 1527.

Says "anchor the S-1 general factor on a single reference construct (candidate: overall satisfaction across the three domains as a proxy for autonomous functioning)." Per Burns 2019 the anchor must be (a) theoretically primary, (b) the most outstanding facet, or (c) developmentally upstream. "Overall satisfaction across three domains" does not satisfy (a) or (b). Better candidates: Belonging satisfaction (per the Sanchez-Oliva pattern of autonomy collapse and relatedness stability) OR Zhang 2020's recommendation of adding 3 to 6 general-content items rather than picking a reference facet.

### D-9: Section 12.7 confidence threshold is built on misread of Fernet 2020

**Severity:** MEDIUM.
**Location:** Section 12.7 lines 1320 to 1341.

Section 12.7 cites Fernet 2020 as showing "highly stable" profiles over 4 months. Lit Review v2: Fernet found 30 to 40% transition rate at 24 months, which is the SAME as ABC's ~31% retest agreement at biweekly cadence in a developmental population. The "rapid changes are noise" inference is overstated. Howard 2020 was 4-month and showed extreme stability (>97% diagonal); Fernet 2020 was 24-month and showed moderate stability (60 to 70% diagonal). ABC's 31% biweekly is closer to Fernet's 24-month rate, which suggests ABC's biweekly cadence is detecting genuine change at developmentally meaningful intervals. The 0.75 confidence threshold for short windows may be too strict.

### D-10: Section 12 narrative engine assumes archetypes are stable categorical states

**Severity:** MEDIUM.
**Location:** Sections 3, 4, 5 throughout.

Section 5 transition tracking and Section 4 Bayesian scoring assume the eight archetypes are the unit of analysis. Lit Review v2: archetypes encode shape; LPA likely returns level. If WI-8 1-G wins, archetypes redefine as S-factor residuals around the G-factor mean. The narrative engine and growth hierarchy in Section 5 must accommodate this.

### D-11: Section 16.9 locks the eight-archetype system as non-negotiable

**Severity:** MEDIUM (was already flagged as D-6; v2 strengthens the case).
**Location:** Section 16.9.

Lit Review v2 confirms: literature cap is k = 4 to 5 for SDT motivation data at any plausible Phase A sample. The eight archetypes are theoretically defensible as a 2x2x2 binary design but empirically indefensible as data-driven clusters. Section 16.9 must clarify that the eight-archetype LOCK applies to the *theoretical taxonomy* used in athlete-facing reports; the empirical analysis layer uses LPA-derived classes (likely k = 3 to 5) reported alongside.

### D-12: Phase A sample target N >= 100 conflicts with bifactor-ESEM literature

**Severity:** HIGH.
**Location:** Section 13.1.

See WI-11. N = 100 is insufficient for bifactor-ESEM, LPA with k > 3, or stable measurement invariance tests. Phase A must either revise upward to N >= 500 OR reframe Phase A as "feasibility pilot" with all bifactor-ESEM and LPA analyses deferred to Phase B.

### D-13: Section 12.6 ESEM citation of Grugan et al. 2024 needs the alignment method

**Severity:** LOW.
**Location:** Section 12.6.

Section 12.6 cites Grugan 2024 ABQ as motivating ESEM promotion. Grugan also used the alignment method (Asparouhov & Muthen 2014) for measurement invariance with small subgroups. ABC should adopt alignment as the fallback when subgroup n < 100. Section 12.6 already promotes ESEM; adding the alignment method to the same protocol completes the alignment.

## V2-G: Updated sequencing

```
WI-7 (item rewrite) ──────────► WI-12 (item revision) ──────────►
  │                                                                │
  │                                                                ▼
  │                                                        Phase A field test
  │                                                                │
WI-1 (text only)            WI-10 (cascade reframe)               │
WI-11 (sample target)       WI-14 (preregistration)               │
                                                                   ▼
                                                            ┌──── WI-2 ESEM (with method factor)
                                                            ├──── WI-13 keying diagnostic
                                                            ├──── WI-17 DIF
                                                            ├──── WI-18 ideal-point check
                                                            ├──── WI-6 RWA (validate vs RWA-Web)
                                                            ▼
                                                            WI-8 1-G vs 2-G B-ESEM
                                                            │
                                                  ┌─────────┤
                                                  ▼         ▼
                                                WI-3      WI-16 LPA (factor scores)
                                              (per-domain)  │
                                                            ▼
                                                          WI-5 LTA
                                                            │
                                                            ▼
                                                          WI-9 response surface
                                                            │
                                                            ▼
                                                       WI-15 goal-content
                                                       (separate item study)
```

## V2-H: Revised open decisions (BLOCKERS)

These must be resolved. Numbered for clarity.

### Decision-1: ESEM approximation route

(Original Conflict-3.) Three options now visible:
1. **Recommended:** factor_analyzer + Procrustes + EwC middle path. Pure Python. Document as approximation. Plan rpy2 + lavaan for Phase B.
2. rpy2 + lavaan now. Heavier infrastructure but defensible "ESEM" claim.
3. Mplus integration via MplusAutomation. Closest to literature standard but requires Mplus license.

### Decision-2: LPA versus eight-archetype taxonomy

(Original Conflict-1, REINFORCED.) Lit Review v2 makes Option 1 the only defensible path: keep archetypes as theoretical taxonomy, run LPA on bifactor factor scores in parallel. Confirm: do you accept that ABC's archetype count is a theoretical commitment, not an empirical claim?

### Decision-3: Item rewrites scope

WI-7 + WI-12 propose rewriting nine items (AS6, AF1, AF2, AF6, BF1, BS6, BF6, CS6, CF3, CF6 plus a possible new BF7). This is more than half the reverse items and four of the existing forward frustration items. Two options:
1. **Recommended:** Rewrite all nine before Phase A administration. Cost: SME review cycle, possibly 4 to 6 weeks. Benefit: empirical results from Phase A are interpretable.
2. Field-test current items in Phase A as an exploratory study to empirically detect the Kam/Bartholomew problems, then revise for Phase B. Cost: Phase A interpretation will be ambiguous. Benefit: recruitment and timeline preserved.

### Decision-4: Sample size for Phase A

Either N >= 500 (literature standard) or reframe Phase A as feasibility pilot with all factor analyses deferred to Phase B. Confirm direction.

### Decision-5: Goal-content supplement (WI-15)

Add or defer? Adding now strengthens Ambition validity but extends instrument length. Recommend: add as an OPTIONAL supplement administered to a subset of Phase A participants (n ~ 100 of N >= 500); use the subset for the goal-content x A_sat interaction analysis.

### Decision-6: Cascade hypothesis reframing

WI-10 reframes the 1.5-timepoint lag in `leading_indicator_model.py` as an empirical hypothesis. Confirm: do you accept that the lag value should be estimated from data, not asserted? If yes, the model code itself does not change (it still computes slopes); only the docstrings and validity-argument language change.

### Decision-7: Coach circumplex IBQ alignment

Per Cluster 5 findings, recommend the coach circumplex (`coach_circumplex.py`) adopt the IBQ 6 x 4 structure as the spine and extend with sport-specific items rather than rebuilding from scratch. Confirm direction. This affects Section 16.3 of the personalization plan.

## V2-I: Issue log additions

Empty. Append entries here as implementation surfaces problems.

## V2-J: References (key citations from Lit Review v2)

**Bifactor and ESEM in SDT:**
- Sanchez-Oliva, D., Morin, A. J. S., Teixeira, P. J., et al. (2017). A bifactor exploratory structural equation modeling representation of the structure of the Basic Psychological Needs at Work Scale. Journal of Vocational Behavior, 98, 173-187.
- Toth-Kiraly, I., Morin, A. J. S., Bothe, B., Orosz, G., & Rigo, A. (2018). Investigating the multidimensionality of need fulfillment: A bifactor exploratory structural equation modeling representation. Structural Equation Modeling, 25(2), 267-286.
- Howard, J. L., Gagne, M., Morin, A. J. S., & Forest, J. (2018). Using bifactor exploratory structural equation modeling to test for a continuum structure of motivation. Journal of Management, 44(7), 2638-2664.
- Gillet, N., Morin, A. J. S., Huart, I., Colombat, P., & Fouquereau, E. (2019). The forest and the trees: Investigating the globality and specificity of employees' basic need satisfaction at work. Journal of Personality Assessment, 102(5), 1-12.
- Burns, G. L., Geiser, C., Servera, M., et al. (2019). Application of the bifactor S-1 model to multisource ratings of ADHD/ODD symptoms. Journal of Abnormal Child Psychology, 48(7), 1-14.
- Zhang, B., Sun, T., Cao, M., & Drasgow, F. (2020). Using bifactor models to examine the predictive validity of hierarchical constructs. Organizational Research Methods, 24(3), 530-571.

**ESEM methodology:**
- Asparouhov, T., & Muthen, B. (2009). Exploratory structural equation modeling. Structural Equation Modeling, 16(3), 397-438.
- Marsh, H. W., Morin, A. J. S., Parker, P. D., & Kaur, G. (2014). Exploratory structural equation modeling. Annual Review of Clinical Psychology, 10, 85-110.
- Asparouhov, T., & Muthen, B. (2014). Multiple-group factor analysis alignment. Structural Equation Modeling, 21(4), 495-508.

**LPA / LTA:**
- Howard, J. L., Morin, A. J. S., & Gagne, M. (2020). A longitudinal analysis of motivation profiles at work. Motivation and Emotion, 45(1), 39-59.
- Fernet, C., Litalien, D., Morin, A. J. S., et al. (2020). On the temporal stability of self-determined work motivation profiles. European Journal of Work and Organizational Psychology, 29(1), 49-63.
- Morin, A. J. S., & Marsh, H. W. (2015). Disentangling shape from level effects in person-centered analyses. Structural Equation Modeling, 22(1), 39-59.
- Wang, J. C. K., Morin, A. J. S., Ryan, R. M., & Liu, W. C. (2016). Students' motivational profiles in the physical education context. Journal of Sport and Exercise Psychology, 38(6), 612-630.
- Vansteenkiste, M., Sierens, E., Soenens, B., et al. (2009). Motivational profiles from a self-determination perspective. Journal of Educational Psychology, 101(3), 671.

**RAI and continuum:**
- Howard, J. L., Gagne, M., Van den Broeck, A., et al. (2020). A review and empirical comparison of motivation scoring methods. Motivation and Emotion, 44(4), 534-548.
- Sheldon, K. M., Osin, E. N., Gordeeva, T. O., et al. (2017). Evaluating the dimensionality of self-determination theory's relative autonomy continuum. Personality and Social Psychology Bulletin, 43(9), 1215-1238.
- Litalien, D., Morin, A. J. S., Gagne, M., et al. (2017). Evidence of a continuum structure of academic self-determination. Contemporary Educational Psychology, 51, 67-82.
- Tay, L., & Jebb, A. T. (2018). Establishing construct continua in construct validation. Advances in Methods and Practices in Psychological Science, 1(3), 375-388.
- Edwards, J. R. (2001). Ten difference score myths. Organizational Research Methods, 4, 265-287.
- Johns, G. (1981). Difference score measures of organizational behavior variables. Organizational Behavior and Human Performance, 27, 443-463.
- Burton, K. D., Lydon, J. E., D'Alessandro, D. U., & Koestner, R. (2006). The differential effects of intrinsic and identified motivation on well-being and performance. Journal of Personality and Social Psychology, 91(4), 750.
- Losier, G. F., & Koestner, R. (1999). Intrinsic versus identified regulation in distinct political campaigns. Personality and Social Psychology Bulletin, 25, 287-298.

**Need thwarting and SDT meta-analyses:**
- Bartholomew, K. J., Ntoumanis, N., Ryan, R. M., & Thogersen-Ntoumani, C. (2011). Psychological need thwarting in the sport context. Journal of Sport and Exercise Psychology, 33(1), 75-102.
- Rocchi, M., Pelletier, L., Cheung, S., Baxter, D., & Beaudry, S. (2017). Assessing need-supportive and need-thwarting interpersonal behaviours: The Interpersonal Behaviours Questionnaire (IBQ). Personality and Individual Differences, 104, 423-433.
- Vasconcellos, D., Parker, P. D., Hilland, T., et al. (2020). Self-determination theory applied to physical education: A systematic review and meta-analysis. Journal of Educational Psychology, 112(7), 1444.
- Van den Broeck, A., Ferris, D. L., Chang, C. H., & Rosen, C. C. (2016). A review of self-determination theory's basic psychological needs at work. Journal of Management, 42(5), 1195-1229.
- Ntoumanis, N., Ng, J. Y. Y., Prestwich, A., et al. (2021). A meta-analysis of self-determination theory-informed intervention studies in the health domain. Health Psychology Review, 15(2), 214-244.
- Kasser, T., & Ryan, R. M. (1996). Further examining the American dream. Personality and Social Psychology Bulletin, 22(3), 280-287.
- Martela, F., Bradshaw, E. L., & Ryan, R. M. (2019). Expanding the map of intrinsic and extrinsic aspirations using network analysis and multidimensional scaling. Frontiers in Psychology, 10, 2174.

**Relative weight, IRT, reverse items:**
- Johnson, J. W., & LeBreton, J. M. (2004). History and use of relative importance indices in organizational research. Organizational Research Methods, 7(3), 238-257.
- Tonidandel, S., & LeBreton, J. M. (2011). Relative importance analysis: A useful supplement to regression analysis. Journal of Business and Psychology, 26(1), 1-9.
- Tonidandel, S., & LeBreton, J. M. (2015). RWA web. Journal of Business and Psychology, 30(2), 207-216.
- Lang, J. W. B., & Tay, L. (2020). The science and practice of item response theory in organizations. Annual Review of Organizational Psychology and Organizational Behavior, 8, 311-338.
- Kam, C. C. S., Meyer, J. P., & Sun, S. (2021). Why do people agree with both regular and reversed items? A logical response perspective. Assessment, 28(4), 1110-1124.
