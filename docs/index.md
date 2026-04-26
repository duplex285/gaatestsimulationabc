---
layout: default
title: ABC Assessment Audit Package
---

# ABC Assessment Audit Package

**Athlete Mental Performance Assessment (Ambition, Belonging, Craft)**

A 36-item self-report instrument grounded in Self-Determination Theory, designed for athlete populations, with continuous longitudinal scoring. This audit package documents the instrument, its psychometric infrastructure, the validity argument under APA / AERA / NCME Standards (2014), and the implementation plan derived from a 49-paper literature review of SDT psychometric methods (Howard 2024 Oxford Handbook Ch. 22 and supporting work).

**Audience.** Professional psychometricians and sport psychologists conducting external review.

**Status.** All synthetic-data validation complete (493 tests passing, 0 failures). Empirical Phase A pilot pending. This package documents the theoretical commitments, the measurement model, the open methodological decisions, and the planned empirical work.

**Last updated.** 2026-04-25 (Literature Review v2)

---

## How to use this package

1. **Read the [white paper](white-paper-abc-simulator.html)** for the strategic and theoretical context.
2. **Inspect the [items](#items)** to evaluate construct fidelity.
3. **Evaluate the [validity argument](validity-argument.html)** under APA/AERA/NCME Standards (2014).
4. **Review the [methods page](methods-audit.html)** to assess psychometric defensibility.
5. **Examine the [implementation plan](howard-2024-implementation-plan.html)** to see open work and planned empirical tests.
6. **Use the [audit checklist](audit-checklist.html)** to organize your review.
7. **File reviewer feedback** via GitHub issues on this repository or by direct email to the project owner.

---

## Audit-package contents

### Theoretical foundations

| Document | Purpose |
|---|---|
| [ABC Assessment Spec](abc-assessment-spec.html) | Full product specification: instrument, scoring engine, archetype derivation, trajectory model |
| [White paper (simulator)](white-paper-abc-simulator.html) | Simulation methodology, executive summary |
| [Improvement plan: personalization engine](improvement-plan-personalization-engine.html) | Strategic roadmap from research instrument to personalization platform |

### Items

| Document | Purpose |
|---|---|
| [Items v1: 36-item draft](new-items-draft.html) | Original 36-item instrument (12 new items added 2026-03-22) |
| [Items v2: revisions per Bartholomew 2011 + Kam 2021](new-items-draft-v2.html) | Ten items revised to enforce active-thwarting framing and negated-regular reverse keying. **Pending SME review.** |
| [Aspiration Index supplement](aspiration-index-supplement.html) | 6-item goal-content supplement for Phase A subsample |

### Validity argument

| Document | Purpose |
|---|---|
| [Validity argument (APA Standards 2014)](validity-argument.html) | Five evidentiary categories per Standard 1.0; descriptive and predictive interpretations separated |

### Implementation plan

| Document | Purpose |
|---|---|
| [Howard 2024 implementation plan](howard-2024-implementation-plan.html) | 18 work items derived from Oxford Handbook Ch. 22 + 49-paper literature review. Sequencing, conflicts, decisions, references. |
| [Activity log](literature-review-activity-log.html) | Chronological record of decisions and changes during this implementation |

---

## Items

ABC measures three psychological needs (Self-Determination Theory) translated to athlete context.

| Need (SDT) | ABC Domain | What is measured |
|---|---|---|
| Autonomy | Ambition | Volitional goal pursuit, perceived authorship of one's competitive direction |
| Relatedness | Belonging | Authentic, supportive relationships with teammates and coaches |
| Competence | Craft | Skill development, mastery, sense of growth |

Each domain is measured as TWO subscales: satisfaction (the experience of the need being met) and frustration (the experience of the need being actively thwarted, per Bartholomew et al. 2011). Six subscales total. Six items per subscale (4 forward + 2 reverse). 1-7 frequency Likert scale. Stem: "How often in the past two weeks did you...".

The current 36 items are documented in [new-items-draft.md](new-items-draft.html). Ten items proposed for revision (post-literature review) are documented in [new-items-draft-v2.md](new-items-draft-v2.html). The revisions enforce two principles:

1. **Active-thwarting framing (Bartholomew 2011 PNTS).** Frustration items must describe ACTIVE THWARTING by named agents (coaches, teammates, selectors), not internal dissatisfaction. Items AF1, AF2, BF1, CF3 currently drift toward dissatisfaction and require revision.
2. **Negated-regular reverse keying (Kam, Meyer & Sun 2021).** Reverse-keyed items must literally negate the corresponding forward item ("did NOT feel X") rather than describe the opposite construct in positive language ("felt X-opposite"). Six current reverse items (AS6, AF6, BS6, BF6, CS6, CF6) are "polar opposites" in Kam's terminology and form a method factor with mid-trait respondents. They require rewriting as negated regulars.

---

## Methods

ABC's psychometric infrastructure is implemented in `src/psychometric/` (21 modules) and tested in `tests/psychometric_tests/` (295+ tests as of 2026-04-25).

| Capability | Module | Method |
|---|---|---|
| IRT scoring | `irt_estimation.py` | Samejima Graded Response Model, EAP theta with SE |
| Threshold derivation | `threshold_derivation.py` | ROC, Youden Index, bootstrap CI, Jacobson-Truax RCI |
| Decision consistency | `decision_consistency.py` | Classification agreement, conditional SEM |
| CFA | `factor_models.py` | semopy 6-factor confirmatory model |
| Bifactor | `factor_models.py` | semopy general + 6 specifics, McDonald omega-h, ECV |
| Bifactor + ESEM (1-G vs 2-G) | `factor_models.py` (added 2026-04-25, WI-2/WI-8) | factor_analyzer + Procrustes target rotation + EwC respecification (Marsh 2014); 1-G vs 2-G test per Toth-Kiraly 2018 |
| Latent profile analysis | `profile_analysis.py` (added 2026-04-25, WI-16) | sklearn GaussianMixture, five-criterion model selection |
| Latent transition analysis | `latent_transition.py` (added 2026-04-25, WI-5) | Stacked-LPA simplification (Howard 2020 / Fernet 2020 lite) |
| Relative weight analysis | `relative_weight.py` (added 2026-04-25, WI-6) | Johnson 2000 SVD decomposition + BCa bootstrap |
| Response surface analysis | `response_surface.py` (added 2026-04-25, WI-9) | Edwards 2001 polynomial regression replacing difference scores |
| Keying diagnostic | `keying_diagnostic.py` (added 2026-04-25, WI-13) | Kam 2021 forward-vs-reverse correlation + quadratic method-factor test |
| Measurement invariance | `measurement_invariance.py` | Configural, metric, scalar; DIF; Chen 2007 thresholds |
| Population norming | `norming.py` | T-scores, percentile ranks, severity bands |
| Adaptive testing | `cat_engine.py`, `cat_longitudinal.py` | Max-info and change-aware item selection |

---

## Effect-size benchmarks (pre-registered)

These targets are derived from the SDT literature and serve as anchor benchmarks for Phase A. Empirical results materially below the anomaly thresholds will be flagged for investigation.

| Pair | Target | Anomaly flag | Source |
|---|---|---|---|
| ABC frust composite x ABQ burnout | r = .50 to .65 | r < .40 | Bartholomew 2011; Vasconcellos 2020 |
| ABC sat composite x Subjective Vitality | r = .45 to .55 | r < .30 | Bartholomew 2011 |
| Within-domain ABC sat-frust correlation | r = -.20 to -.40 | r < -.55 (bipolar collapse) or > -.10 | Bartholomew 2011 |
| Coach IBQ support x ABC sat | r = .35 to .55 | r < .25 | Vasconcellos 2020 |
| ABC frust unique β on burnout | β = .30 to .50 | β < .20 | Bartholomew 2011 SEM |
| ABC sat unique β on vitality | β = .30 to .50 | β < .20 | Bartholomew 2011 SEM |

Full table: [validity-argument.md](validity-argument.html) Section (d).

---

## Open methodological decisions

Seven decisions were resolved with the user's "run continuously" authorization. Details in [literature-review-activity-log.md](literature-review-activity-log.html).

| Decision | Resolution |
|---|---|
| ESEM approximation route | factor_analyzer + Procrustes + EwC middle path (pure Python). Plan rpy2/lavaan for Phase B. |
| LPA versus eight archetypes | Keep archetypes as theoretical taxonomy. Run LPA in parallel as discriminant evidence. |
| Item rewrite scope | Rewrite all ten items now via SME review (4-6 week cycle). |
| Phase A sample target | N >= 100 feasibility pilot; commit Phase B to N >= 500. |
| Goal-content supplement | Add as optional supplement for Phase A subsample (n ~ 100 of N >= 500). |
| Cascade reframing | Reframe 1.5-timepoint lag as falsifiable hypothesis. Code unchanged; docstrings and validity argument updated. |
| Coach circumplex IBQ alignment | Adopt IBQ 6x4 as spine, extend with sport-specific items. |

---

## How to file feedback

**For psychometricians.** Focus areas: (a) bipolar-vs-unipolar test specification (WI-3, WI-8); (b) ESEM approximation defensibility (WI-2, Decision-1); (c) LPA model selection criteria (WI-16); (d) reverse-item rewrites (WI-7); (e) effect-size benchmarks. Open issues at the project repository, or email the owner.

**For sport psychologists.** Focus areas: (a) item-level construct fidelity (review [items v2](new-items-draft-v2.html)); (b) active-thwarting framing of frustration items (Bartholomew 2011 alignment); (c) sport-specific cultural accessibility; (d) cognitive pretesting protocol (item BF5 "deliberately leave out" wording, item BS6 alternative for individual sports, item CF6 cultural autonomy assumption); (e) face validity for elite vs collegiate vs club athletes.

**Acceptance criterion for items.** At least 3 of 4 expert reviewers (2 SDT researchers + 2 sport psychologists) rate each revised item >= 4 on a 1 to 5 scale for (a) construct fidelity to active thwarting and (b) Kam 2021 classification correctness.

---

## References

The foundational paper for this implementation:

- Howard, J. L. (2024). Psychometric Approaches in Self-Determination Theory: Meaning and Measurement. In Ryan, R. M. & Deci, E. L. (eds.), *The Oxford Handbook of Self-Determination Theory*, Ch. 22.

The 49-paper literature review supporting v2 of the implementation plan: see [howard-2024-implementation-plan.md](howard-2024-implementation-plan.html) Section V2-J.

The full APA / AERA / NCME Standards governing this validity argument:

- American Educational Research Association, American Psychological Association, & National Council on Measurement in Education. (2014). *Standards for Educational and Psychological Testing*. Washington, DC: AERA.

---

*Repository: [github.com/duplex285/gaatestsimulationabc](https://github.com/duplex285/gaatestsimulationabc) | Branch: literature-review-implementation*
