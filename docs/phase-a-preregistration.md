---
layout: default
title: Phase A Pre-registration
---

# Phase A Pre-registration

**Date:** 2026-04-25 (initial)
**Status:** Draft for SME review.
**Lock date:** Will be locked before recruitment begins; archived hash on the GitHub repository.
**Scope:** Phase A feasibility pilot of the ABC Assessment.

This document pre-registers the analyses, hypotheses, and decision rules for Phase A. It exists to constrain the analysis to confirmatory tests of pre-specified hypotheses, not exploratory data dredging.

---

## 1. Sample

**Target N:** N >= 100 athletes (feasibility pilot per Decision-4 in `literature-review-activity-log.md`).
**Population:** US college athletes (NCAA Division I, II, or III) and elite club athletes, ages 18 to 25.
**Recruitment:** Athletic departments and club programs, with informed consent and IRB approval.
**Stratification target:** at least 30% female, at least 30% male, at least 25% non-team-sport athletes.

**Out of scope for Phase A (deferred to Phase B with N >= 500):**
- Bifactor-ESEM 1-G vs 2-G test (WI-8) — requires N >= 500 per Zhang 2020
- Latent profile analysis with k > 3 — requires N >= 1,000 per Wang 2016 precedent
- Measurement invariance across more than two groups
- Cross-validation with held-out sample

## 2. Instruments administered

### Core (all participants)

- **ABC Assessment:** 36 items, biweekly cadence, minimum 6 administrations per athlete (one competitive season).
- **Athlete Burnout Questionnaire (ABQ):** baseline + endpoint.
- **Basic Psychological Need Satisfaction and Frustration Scale (BPNSFS):** baseline + endpoint.
- **Subjective Vitality Scale:** every administration paired with ABC.
- **Big Five Inventory 2 (BFI-2):** baseline only.

### Coach-rated (per athlete)

- **Coach-rated wellbeing:** brief 4-item rating, every administration.
- **Interpersonal Behaviours Questionnaire (IBQ):** coach-rated need support, midpoint and endpoint.
- **Coach-rated training engagement:** brief 3-item rating, every administration.

### Subsample supplements (n ~ 100 of N)

- **Aspiration Index:** 6 items per `docs/aspiration-index-supplement.md`. Baseline + endpoint.
- **Athletic Identity Measurement Scale (AIMS):** 7 items, baseline only.
- **Sport Motivation Scale 2 (SMS-2):** baseline + endpoint.

## 3. Pre-registered hypotheses

### H1 (convergent validity, ABC ↔ established instruments)

| Pair | Predicted r | Anomaly threshold |
|---|---|---|
| ABC sat composite x BPNSFS sat composite | .55 to .75 | r < .50 |
| ABC frust composite x BPNSFS frust composite | .55 to .75 | r < .50 |

If r falls below the anomaly threshold for either pair, ABC is not measuring what BPNSFS measures despite a shared SDT framework. This would require investigation of item content drift and possibly subscale-level reanalysis.

### H2 (criterion validity, frustration → burnout)

| Pair | Predicted r | Anomaly threshold |
|---|---|---|
| ABC frust composite x ABQ total | .50 to .65 | r < .40 |
| ABC frust composite x ABQ exhaustion subscale | .55 to .70 | r < .45 |

Source: Bartholomew 2011 (r = .46 with exhaustion); Vasconcellos 2020 (r = .53 with maladaptive). Anomaly threshold below the literature minimum suggests ABC frust items measure low satisfaction rather than active thwarting.

### H3 (criterion validity, satisfaction → vitality)

| Pair | Predicted r | Anomaly threshold |
|---|---|---|
| ABC sat composite x Subjective Vitality | .45 to .55 | r < .30 |

Source: Bartholomew 2011 (r = .47).

### H4 (within-domain sat-frust correlation)

| Pair | Predicted r | Anomaly threshold |
|---|---|---|
| Within-domain ABC sat-frust correlation (mean across A, B, C) | -.20 to -.40 | r < -.55 (bipolar collapse) or > -.10 (unrelated constructs) |

Source: Bartholomew 2011 PNTS (r = -.21 to -.27). If collapse to -.55 or below, run WI-8 1-G B-ESEM; if 1-G fits, ABC measures three bipolar fulfillment continua, not six unipolar subscales.

### H5 (asymmetric paths, Bartholomew 2011 SEM replication)

In a structural equation model with ABC sat composite and ABC frust composite as latent predictors of (a) ABQ burnout and (b) Subjective Vitality:

| Path | Predicted β | Anomaly threshold |
|---|---|---|
| ABC frust → ABQ burnout (controlling for sat) | .30 to .50 | β < .20 |
| ABC sat → Vitality (controlling for frust) | .30 to .50 | β < .20 |
| ABC sat → ABQ burnout (controlling for frust) | -.10 to -.30 (smaller than the asymmetric path) | β > -.40 (would indicate non-asymmetric) |
| ABC frust → Vitality (controlling for sat) | -.10 to -.30 (smaller than the asymmetric path) | β < -.40 |

Asymmetric path replication confirms ABC's dual-pathway theoretical commitment.

### H6 (incremental validity beyond Big Five)

ABC frust composite predicts ABQ burnout incrementally beyond the Big Five (BFI-2):

| Test | Predicted ΔR² | Anomaly threshold |
|---|---|---|
| Hierarchical regression: BFI-2 first (5 traits), then ABC frust composite | ΔR² > 0.05 | ΔR² < 0.02 |

### H7 (subscale-specific unique effects, Howard 2020 / Burton 2006 framework)

Per WI-14:

- B_frust uniquely predicts a team-level outcome (turnover intention or peer-conflict report) above B_sat: β > 0.20
- C_frust uniquely predicts ABQ reduced sense of accomplishment subscale above C_sat: β > 0.20
- A_sat uniquely predicts goal-pursuit persistence above A_frust: β > 0.20

Tested via relative weight analysis (WI-6) and hierarchical regression.

### H8 (goal content moderation, WI-15 subsample)

In the n ~ 100 subsample with the Aspiration Index:

- A_sat × Relative Intrinsic interaction predicts ABQ burnout: athletes with high A_sat AND extrinsic-dominant aspirations show steeper burnout slopes than athletes with high A_sat AND intrinsic-dominant aspirations.
- Specifically, the interaction term in `Burnout ~ A_sat + Relative_Intrinsic + A_sat * Relative_Intrinsic` has β < -0.15 (negative because high intrinsic should buffer the burnout risk).

### H9 (cascade hypothesis selection)

Among the five competing cascade hypotheses (parallel, frustration-leads, satisfaction-leads, reciprocal, asymmetric transition), select the best-fitting model via AIC and LOO cross-validation across all participants with >= 4 timepoints.

**No specific direction is pre-registered.** This is an exploratory selection among five candidate models with no prior commitment to any.

### H10 (keying diagnostic, Kam 2021)

For each subscale, forward-only mean and reverse-only mean (sign-corrected) correlate at:

| Subscale | Predicted r | Anomaly flag |
|---|---|---|
| A_sat | r >= 0.60 | r < 0.60 = logical-response artifact |
| A_frust | r >= 0.60 | r < 0.60 |
| B_sat | r >= 0.60 | r < 0.60 |
| B_frust | r >= 0.60 | r < 0.60 |
| C_sat | r >= 0.60 | r < 0.60 |
| C_frust | r >= 0.60 | r < 0.60 |

Failure on multiple subscales suggests the negated-regular reverse rewrites in v2 are insufficient and a different design is needed.

## 4. Decision rules

### 4.1 Item retention

Items are retained if:
- IRT discrimination >= 0.80 (Lang & Tay 2020 minimum)
- Loading on intended factor in CFA / ESEM >= 0.50
- Loading on any non-intended factor < 0.30 in ESEM
- Forward-only / reverse-only correlation >= 0.60 for that subscale

Items failing two or more criteria are flagged for revision in v3.

### 4.2 Subscale retention

Subscales are retained if:
- Coefficient alpha >= 0.80
- Within-domain sat-frust correlation in [-0.55, -0.10] (per H4)
- At least 3 retained items per subscale after item-level retention

### 4.3 Domain-state classifier validation

Per WI-9, the 2x2 classifier is a display layer. Phase A tests whether continuous (sat, frust) coordinates plus LPA posterior probabilities (when available) provide better individual-classification reliability than the 2x2 hard categorization.

### 4.4 Archetype taxonomy validation

Per Decision-2, ABC's eight archetypes are theoretical. Phase A reports:
- LPA-derived class structure (expect k = 3 to 5)
- Cross-tab of LPA classes vs eight archetypes (Cohen's kappa, adjusted Rand)
- Vansteenkiste 2009-style descriptive labels for empirical classes

The eight archetypes are NOT replaced if LPA disagrees. Both layers are reported.

## 5. Anti-data-dredging commitments

- All p-values are reported and interpreted with Bonferroni or Holm correction across the full set of pre-registered tests (alpha = 0.05 / number of tests).
- Exploratory analyses are clearly labeled as such; no exploratory finding is treated as confirmatory.
- The pre-registration is locked (committed to GitHub with a tag) before recruitment begins. Subsequent changes are documented as amendments, not silently revised.

## 6. Reporting commitments

Phase A results will be reported in a `docs/phase-a-results.md` document with:
- Each pre-registered hypothesis listed
- Outcome (supported / not supported / mixed)
- Effect size with 95% CI
- Anomaly flag status (any flag triggered)
- Whether decision rule outcomes were as predicted

Both supportive and non-supportive results are reported in full. No selective reporting.

## 7. Open science commitments

Per Howard 2024 Ch. 22 Section 5 ("Data Transparency for Secondary Analysis"):
- De-identified data deposited in OSF (Open Science Framework) at the close of Phase A
- Full subscale-level correlation matrices reported in supplementary materials
- Item-level descriptive statistics reported
- Analysis code (Python, R) released under MIT license

## 8. References

Citations for each pre-registered effect-size target are in [validity-argument.md](validity-argument.html) Section (d). The methodological foundations are documented in [methods-audit.md](methods-audit.html). The full implementation plan is in [howard-2024-implementation-plan.md](howard-2024-implementation-plan.html).
