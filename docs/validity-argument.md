# ABC Assessment Validity Argument

## Per APA/AERA/NCME Standards for Educational and Psychological Testing (2014)

**Date:** 2026-03-22
**Status:** Framework populated with synthetic evidence. Rows requiring empirical data are marked.
**Governing standard:** Validity is the degree to which evidence and theory support the interpretations of test scores for proposed uses (Standard 1.0). Each intended interpretation requires its own validity argument.

---

## Intended uses and populations

**Instrument:** ABC Assessment, a 24-item self-report questionnaire measuring satisfaction and frustration across three psychological need domains (Ambition, Belonging, Craft) grounded in Self-Determination Theory.

**Intended population:** Athletes across competitive levels (elite, club, youth), sport types (team, individual), and demographic groups.

**Two intended interpretations:**

1. **Descriptive:** "This athlete's current state in each domain is Thriving, Vulnerable, Mild, or Distressed, based on the pattern of satisfaction and frustration scores."

2. **Predictive:** "This pattern of score changes over time predicts burnout transition within k measurement points, with sufficient lead time for intervention."

Each interpretation requires separate validation evidence. The Standards prohibit the unqualified phrase "the validity of the test" (Standard 1.1).

---

## Interpretation A: Descriptive (Current Athlete State)

### (a) Evidence based on test content (Standard 1.11)

**Requirement:** The procedures for identifying and generating test content should be described and justified with reference to the intended population and the construct the test is intended to measure.

**Current evidence:**

- Item pool derived from Self-Determination Theory (Deci & Ryan, 2000), adapted from the Basic Psychological Need Satisfaction and Frustration Scale (Chen et al., 2015)
- Three domains (autonomy/Ambition, relatedness/Belonging, competence/Craft) each measured by 4 satisfaction items and 4 frustration items
- One reverse-coded item per subscale to detect acquiescence bias
- Content domain specified in abc-assessment-spec Section 1.2

**Gaps requiring empirical work:**

- [ ] Expert panel review: sport psychologists and SDT researchers rate each item for domain alignment, accessibility to athletes, and absence of construct-irrelevant features
- [ ] Content coverage analysis: identify aspects of each domain that the 4-item subscales may underrepresent
- [ ] Cultural review: evaluate whether item wording carries different meaning across sport cultures, languages, or demographic groups

### (b) Evidence based on response processes (Standard 1.12)

**Requirement:** If the rationale for score interpretation depends on premises about the psychological processes of test takers, then theoretical or empirical evidence in support of those premises should be provided.

**Current evidence:**

- The instrument assumes athletes can accurately self-report their satisfaction and frustration levels via Likert-scale items
- No empirical response process evidence exists yet

**Gaps requiring empirical work:**

- [ ] Think-aloud protocols: 10-15 athletes from different sports and levels verbalize their thought process while completing the assessment. Key question: do athletes interpret "autonomy" items as sport-relevant autonomy or general life autonomy?
- [ ] Response time analysis: do athletes who take unusually long or short on specific items produce different factor structures?
- [ ] Social desirability assessment: do athletes underreport frustration in team settings?

### (c) Evidence based on internal structure (Standard 1.13)

**Requirement:** If the rationale for a test score interpretation depends on premises about the relationships among test items or among parts of the test, evidence concerning the internal structure of the test should be provided.

**Current evidence (from simulation, Phases 1, 3, 5b):**

| Analysis | Result | Source |
|---|---|---|
| 6-factor CFA fit | CFI = 1.001, RMSEA = 0.000 on synthetic data | Phase 3 |
| Bifactor model: omega-h | 0.246 (subscales carry independent variance, no dominant general factor) | Phase 3 |
| Bifactor model: ECV | 0.061 (specific factors account for 94% of common variance) | Phase 3 |
| Method factor for keying direction | Correctly detects artifacts when present; no artifact in clean data | Phase 3 |
| Omega-s per subscale | 0.82-0.92 (each subscale has substantial unique reliable variance) | Phase 3 |
| IRT item discrimination | Synthetic range 0.91-2.46 (all items discriminate adequately) | Phase 1 |
| 24-item tier reliability | 0.943 marginal reliability | Phase 5b |
| 12-item tier reliability | 0.870 | Phase 5b |
| 6-item tier reliability | 0.714 | Phase 5b |

**Critical caveat:** All internal structure evidence is from synthetic data generated to conform to the 6-factor model. CFA fit of 1.000 on synthetic data is circular. Empirical CFA on real athlete data is the true test. The bifactor analysis framework is built and ready to run on empirical data.

**What the simulation proved:** The analytic pipeline works end-to-end. If the 6-factor structure holds in empirical data, the infrastructure will detect it. If the structure collapses (e.g., Murphy et al. 2023 keying artifact), the method-factor model will flag it.

### (d) Evidence based on relations to other variables (Standards 1.16, 1.17)

**Requirement:** When validity evidence includes empirical analyses of test responses together with data on other variables, the rationale for selecting the additional variables should be provided.

**Current evidence (from simulation, Phase 2):**

| Analysis | Result | Source |
|---|---|---|
| ROC analysis framework | Built and demonstrated with simulated ABQ burnout criterion | Phase 2 |
| Empirical satisfaction threshold | 6.09 (vs fixed 6.46), 95% CI [5.56, 6.37] | Phase 2 |
| Empirical frustration threshold | 4.82 (vs fixed 4.38), 95% CI [4.24, 5.19] | Phase 2 |
| AUC for frustration predicting burnout | 0.879 (synthetic criterion) | Phase 2 |
| AUC for satisfaction predicting wellbeing | 0.900 (synthetic criterion) | Phase 2 |
| Bootstrap CI method | 2,000 resamples, 95% percentile CI | Phase 2 |

**Planned criterion variables for empirical validation:**

| Criterion | Expected relationship | Rationale |
|---|---|---|
| Athlete Burnout Questionnaire (ABQ) | ABC frustration correlates r > 0.50 | Both measure burnout-related constructs |
| Basic Psychological Need Satisfaction Scale (BPNSFS) | ABC satisfaction correlates r > 0.50 with BPNSFS satisfaction | Both operationalize SDT need satisfaction |
| Coach-rated wellbeing | ABC Thriving state associated with higher coach ratings | External criterion independent of self-report |
| Cortisol/HPA biomarkers | ABC frustration trajectories precede cortisol dysregulation | Bridges psychometric to physiological |

**Gaps requiring empirical work:**

- [ ] Convergent validity: ABC satisfaction vs BPNSFS satisfaction (expected r > 0.50)
- [ ] Discriminant validity: ABC domains more distinct than BPNSFS domains
- [ ] Criterion validity: domain states predict coach-rated wellbeing
- [ ] Incremental validity: ABC predicts burnout beyond Big Five personality alone

### (e) Evidence based on consequences of testing (Standards 1.5, 1.25)

**Requirement:** When unintended consequences result from test use, an attempt should be made to investigate whether such consequences arise from the test's sensitivity to characteristics other than those it is intended to assess.

**Current evidence (from simulation, Phase 2b):**

| Analysis | Result | Implication |
|---|---|---|
| Per-domain classification agreement | ~67% on readministration | 1 in 3 athletes receives a different domain state label on retesting |
| Joint classification agreement | ~30% across all 3 domains | Only 30% get the same full profile on retesting |
| Type agreement | ~31% | 24-type assignment is unstable; types should be treated as provisional |
| Difference score reliability | 0.70-0.90 (depends on alpha and sat-frust correlation) | Adequate for domain-level interpretation, marginal for individual classification |

**Identified consequence risks:**

| Risk | Severity | Mitigation |
|---|---|---|
| Athlete labelled "Distressed" experiences stigma or reduced playing time | High | Confidence bands on all classifications; practitioner training on probabilistic interpretation |
| False positive burnout alert causes unnecessary intervention | Medium | FPR constraint in alert optimization (Phase 6: 16% FPR at optimal threshold) |
| False negative: missed burnout due to measurement noise | High | Minimum 24-item tier for classification decisions; RCI-based change detection requires reliable change exceeding measurement error |
| Repeated monitoring causes response fatigue, contaminating scores | Medium | CAT reduces burden (Phase 7); minimum measurement frequency guidance |
| 24-type labels become reified identities rather than provisional classifications | Medium | Type stability of ~31% must be disclosed; types are conversation starters, not diagnostic categories |

**Gaps requiring empirical work:**

- [ ] Longitudinal consequence study: does ABC monitoring actually reduce burnout incidence vs no monitoring?
- [ ] Iatrogenic effect assessment: does the "Distressed" label itself worsen athlete state?
- [ ] Practitioner interpretation study: do coaches and sport psychologists correctly interpret confidence bands and provisional classifications?

---

## Interpretation B: Predictive (Burnout Early Warning)

### (a) Evidence based on test content

Same as Interpretation A. The items are the same; the interpretation differs.

### (b) Evidence based on response processes

**Additional requirement beyond Interpretation A:**

- [ ] Athletes in the Vulnerable state (high satisfaction + high frustration) should be able to articulate the "successful but suffering" experience that the items are designed to detect. Think-aloud protocols should specifically probe whether Vulnerable-state athletes recognize the discrepancy between their performance (satisfaction) and their internal cost (frustration).

### (c) Evidence based on internal structure

**Current evidence (from simulation, Phases 3, 4):**

| Analysis | Result | Source |
|---|---|---|
| Cross-sectional measurement invariance | Configural, metric, scalar invariance holds on synthetic multi-group data | Phase 4 |
| DIF analysis | Logistic regression DIF detection per item; clean data produces few flags; biased items correctly flagged | Phase 4 |
| Chen (2007) criteria | delta-CFI < 0.01, delta-RMSEA < 0.015 implemented and verified | Phase 4 |

**Gap requiring empirical work:**

- [ ] Longitudinal measurement invariance: the 6-factor structure must hold across repeated administrations over time, not just across groups at one timepoint. If the structure changes under fatigue or burnout, scores at different timepoints are not comparable.

### (d) Evidence based on relations to criteria (Standards 1.17, 1.18)

**This is the core evidence for the predictive interpretation.**

**Current evidence (from simulation, Phase 6):**

| Analysis | Result | Source |
|---|---|---|
| Vulnerable-to-Distressed cascade | Frustration rises 1.5 measurement points before satisfaction drops | Phase 6 |
| Alert sensitivity at optimal threshold | 81.1% of burnout cases detected | Phase 6 |
| Mean detection lag | 1.5 timepoints lead time before burnout onset | Phase 6 |
| False positive rate | 16.3% at optimal threshold (RCI = -3.00) | Phase 6 |
| Sensitivity/FPR tradeoff | Relaxing to RCI = -2.25 gives 97% sensitivity but 38% FPR | Phase 6 |
| Multi-subscale optimization | Differential evolution finds non-obvious weight combinations across 6 subscale weights + threshold + window | Phase 6 |
| Trajectory pattern detection | 57.5% overall accuracy; decline sensitivity 44.8% | Phase 6 |
| Jacobson-Truax RCI | Reliable change detection distinguishes signal from measurement noise | Phase 2 |

**Critical caveat:** All predictive evidence is from synthetic trajectories. The cascade model was designed to produce the SDT-predicted pattern. Empirical validation must demonstrate that real athlete frustration trajectories actually precede real burnout events.

**Gaps requiring empirical work:**

- [ ] Prospective prediction study: administer ABC repeatedly to N >= 200 athletes over a season; correlate trajectory patterns with independently measured burnout outcomes (ABQ, cortisol)
- [ ] Predictive lead time: does the 1.5 timepoint detection window hold in real data, or is it an artifact of the simulation's cascade model?
- [ ] Incremental predictive validity: does ABC trajectory analysis predict burnout beyond what a single-timepoint burnout screener (e.g., ABQ alone) can predict?
- [ ] Cross-validation: train alert thresholds on one sample, validate on a held-out sample

### (e) Evidence based on consequences

**Current evidence (from simulation, Phase 6):**

| Analysis | Result | Source |
|---|---|---|
| FPR/sensitivity tradeoff curve | Full curve from RCI = -3.0 (81% sens, 16% FPR) to -0.5 (100% sens, 96% FPR) | Phase 6 |
| Optimal threshold selection | Minimizes detection lag subject to FPR <= 15% constraint | Phase 6 |

**Gaps requiring empirical work:**

- [ ] Does monitoring and early intervention actually reduce burnout incidence? (Standard 1.5: if the claim is that testing produces a specific outcome, evidence for that outcome must be presented)
- [ ] What are the costs of false positives (unnecessary intervention) vs false negatives (missed burnout) in the athlete population? This determines the appropriate FPR constraint.
- [ ] Does the act of repeated monitoring itself change athlete behavior (Hawthorne effect)?

---

## Classification-specific evidence

### Domain state classification (Thriving/Vulnerable/Mild/Distressed)

| Standard | Requirement | Evidence | Source |
|---|---|---|---|
| 2.14 | Conditional SEM at cut scores | ~0.20 theta units at all four thresholds | Phase 2b |
| 2.16 | Decision consistency | Per-domain agreement ~67%; joint ~30% | Phase 2b |
| 5.21-5.23 | Cut score rationale | Empirical thresholds derived via ROC/Youden; fixed thresholds within empirical CIs | Phase 2 |

### 24-type classification

| Standard | Requirement | Evidence | Source |
|---|---|---|---|
| 2.16 | Decision consistency | Type agreement ~31% across readministrations | Phase 2b |
| 1.14 | Subscore distinctiveness | Omega-s 0.82-0.92 per subscale (subscales are distinct) | Phase 3 |

**Conclusion:** The 24-type system is too unstable for reliable individual classification with 4 items per subscale. Types should be presented as provisional, with stability estimates disclosed.

### Measurement tier support (Standard 2.9)

| Tier | Reliability | Supported interpretations | Not supported |
|---|---|---|---|
| 6-item (onboarding) | 0.714 | Directional subscale signal | Subscale scores, domain states, types, signatures, change detection |
| 12-item (standard) | 0.870 | Subscale scores, frustration signatures | Domain states, types, change detection |
| 24-item (full) | 0.943 | All interpretations | None (though agreement is ~67% per domain) |

### Subgroup fairness (Standard 3.0)

| Standard | Requirement | Evidence | Source |
|---|---|---|---|
| 3.0 | Fairness across subgroups | Measurement invariance framework built; configural/metric/scalar testing via semopy | Phase 4 |
| 3.8 | DIF analysis | Logistic regression DIF per item; effect size and flagging | Phase 4 |

**Gap:** All invariance evidence is from synthetic multi-group data. Empirical invariance testing across gender, sport type, competitive level, and cultural background is required before universal thresholds can be applied.

---

## Summary of evidence status

| Evidence type | Interpretation A (Descriptive) | Interpretation B (Predictive) |
|---|---|---|
| Test content | Framework defined; expert review needed | Same |
| Response processes | Think-aloud protocols needed | Same + Vulnerable state articulation |
| Internal structure | Synthetic CFA/bifactor complete; empirical CFA needed | Same + longitudinal invariance needed |
| Relations to variables | ROC framework built; empirical criterion data needed | Cascade model built; prospective prediction study needed |
| Consequences | Classification instability quantified (67%); mitigation defined | FPR/sensitivity tradeoff quantified; outcome study needed |

**What the simulation provides:** The complete analytic infrastructure. Every method needed to evaluate the validity argument is built, tested, and demonstrated on synthetic data. When empirical athlete data arrives, the same functions run on real responses, and the synthetic evidence rows in this document are replaced with empirical results.

**What the simulation cannot provide:** Evidence that the constructs measured by self-report items correspond to the physiological phenomena they are intended to detect. That bridge can only be built with real athletes, real burnout outcomes, and real criterion measures.

---

## References

- APA, AERA, & NCME. (2014). *Standards for Educational and Psychological Testing*.
- Chen, B., et al. (2015). Basic psychological need satisfaction, need frustration, and need strength across four cultures. *Motivation and Emotion*, 39, 216-236.
- Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20, 37-46.
- Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits. *Psychological Inquiry*, 11, 227-268.
- Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes. *Structural Equation Modeling*, 6, 1-55.
- Jacobson, N. S., & Truax, P. (1991). Clinical significance. *Journal of Consulting and Clinical Psychology*, 59, 12-19.
- Murphy, J., et al. (2023). The BPNSFS probably does not validly measure need frustration. *Motivation and Emotion*, 47, 899-919.
- Reise, S. P. (2012). The rediscovery of bifactor measurement models. *Multivariate Behavioral Research*, 47, 667-696.
- Samejima, F. (1969). *Estimation of latent ability using a response pattern of graded scores*. Psychometrika Monograph No. 17.
- Vansteenkiste, M., & Ryan, R. M. (2013). On psychological growth and vulnerability. *Journal of Psychotherapy Integration*, 23, 263-280.
- Youden, W. J. (1950). Index for rating diagnostic tests. *Cancer*, 3, 32-35.
