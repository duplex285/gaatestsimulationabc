# Phase Two: Instrument Expansion and Empirical Validation Plan

## Why this phase exists

The gold standard upgrade (Phase One, completed 2026-03-22) built the complete psychometric infrastructure: IRT scoring, threshold derivation, decision consistency, factor analysis, invariance testing, norming, trajectory detection, and adaptive testing. All 11 deliverables are complete, all 493 tests pass, and the Validity Argument document maps every gap that empirical data must fill.

Phase Two addresses three problems Phase One exposed:

1. **The 24-item instrument is too short for reliable classification.** With 4 items per subscale, per-domain classification agreement is ~67% and type agreement is ~31%. The original instrument design called for 36 items (6 per subscale). Phase Two implements that expansion.

2. **All thresholds are assumed, not empirically derived.** The Athlete Burnout Questionnaire (ABQ, Raedeke & Smith 2001; validated by Grugan et al. 2024) provides the criterion measure needed for ROC-based threshold derivation.

3. **The archetype system needs revision based on empirical classification stability.** The 24-type system (8 base patterns x 3 frustration modifiers) should be simplified to 8 base patterns with continuous frustration reporting until empirical data supports finer granularity.

## Context: what we are building and why

The ABC assessment is a purpose-built psychometric instrument grounded in Self-Determination Theory (Deci & Ryan, 2000). It is not a licensed adaptation of the BPNSFS (Chen et al., 2015) or any existing SDT instrument. It is an original instrument developed through AI-assisted research and iterative simulation, designed for the specific population (athletes) and use case (longitudinal burnout prediction) that no existing instrument addresses.

This matters for two reasons:

**The problem is documented and urgent.** Seventy-four percent of Division I athletic departments have no embedded mental health providers (Jones et al., 2022). Mental health concerns among NCAA athletes remain 1.5 to 2 times above pre-pandemic baselines (NCAA, 2023). The proportion of NCAA athlete deaths attributable to suicide doubled from 7.6% to 15.3% over two decades (Whelan et al., 2024). Instrument-detected depression rates (21%) are five times higher than self-reported rates (4%) among college athletes (Chang et al., 2020; Wolanin et al., 2016). The IOC's screening tool has a 67.5% false-negative rate (Erickson et al., 2023). The current system, which depends on athletes self-disclosing distress to people who control their playing time, scholarships, and futures, is architecturally broken.

**No existing solution does what this platform does.** The market has responded with generic wellness apps and AI chatbots built on the same broken assumption: the athlete engaging alone. The median 30-day retention rate for these tools is 3.3% (Baumel et al., 2019). What is needed is a system that distributes detection across athletes, coaches, and administrators, treats every data point as a development tool owned by the athlete, and uses SDT constructs as leading indicators rather than concurrent descriptions. That is what Ero (second-game) is building.

**Our scientific foundation is honest.** We are rooted in SDT but we have not licensed existing SDT instruments. We are using AI and human research to develop a purpose-built resource. We are transparent about what we have confidence in (the analytic infrastructure, the theoretical framework, the simulation results) and where we need further research (empirical validation on real athletes, criterion-anchored thresholds, longitudinal predictive evidence). This is uncharted territory. It will take years of testing, reviewing, and building to achieve gold standard. We are starting with what statistics and AI can provide now, and being honest about our assumptions and claims.

## Legal and institutional context

Multiple law review articles document the duty of care that universities owe student-athletes for mental health:

- Universities have a legal duty to provide mental health services, and current provision falls short of that duty
- The NCAA's mental health initiatives have been criticized as insufficient, with calls for federal regulation
- High school student-athletes face similar gaps in mental health support
- The power imbalance between athletes and institutions creates structural barriers to help-seeking that no self-disclosure-based system can overcome

The ABC platform addresses this by shifting detection from self-disclosure (which fails) to pattern recognition across multiple data sources (which scales). The legal exposure for institutions that fail to detect athlete distress is increasing. A system that can demonstrate it was designed to detect what self-disclosure misses, and that is transparent about its measurement precision and limitations, provides both better care and better institutional protection.

---

## Progress (Last Updated: 2026-03-23)

### What was completed

| Workstream | Status | Deliverable | Key result |
|---|---|---|---|
| **4: Archetype Revision** | DONE | Code changes to type_derivation.py, type_descriptions.py, tests | 8 base patterns with continuous frustration. 493 tests pass. Resolute Seeker dominance eliminated. |
| **1: Item Expansion** | DONE | Code implemented, 36 items in scoring pipeline and dashboard | 12 new items (AS5-6, AF5-6, BS5-6, BF5-6, CS5-6, CF5-6) integrated into Python scoring pipeline (`irt_subscale_scoring.py`, `tier_reliability.py`, `config/irt_parameters.yaml`) and dashboard JS. 36-item structure live in both codebases. |
| **2-3: ABQ + Coach Spec** | DONE (spec) | docs/abq-coach-integration-spec.md (31KB) | ABQ database schema, scoring service, API endpoints, monthly schedule; coach rating schema, leader review integration; ROC analysis pipeline with pairing logic |
| **5: Big Five / Belbin** | DONE (verified) | docs/big-five-belbin-audit.md | Audit confirmed Big Five and Belbin mappings are correct. No code changes needed. |
| **6: Standards Compliance** | IN PROGRESS | Threaded through completed workstreams | Item writing principles documented; transparency requirements defined |

### Issues encountered

1. **Workstream 4 agent failed on first attempt.** The agent was launched in an isolated worktree and made the correct file changes (type_derivation.py, type_descriptions.py, tests) but hit a login/authentication wall mid-run before it could execute tests or report results. The worktree changes existed but were unverified. Fixed by re-implementing directly on the main codebase with full test verification. All 493 tests pass.

2. **No issues with Workstreams 1 and 2-3.** Both agents completed successfully on first run, producing comprehensive documents that follow the plan's specifications.

### What the archetype revision changed

The type system moved from 24 categories (8 base patterns x 3 frustration modifiers) to 8 base patterns with continuous frustration reporting:

- `derive_type()` now returns `type_name` as a bare base pattern (e.g., "Architect" not "Resolute Architect") plus `frustration_levels` dict with per-domain continuous scores
- `type_descriptions.py` consolidated from 24 descriptions to 8, with frustration context integrated into the description and watch_for fields
- The Resolute Seeker dominance problem is eliminated because "Resolute" no longer exists as a category
- Classification agreement nearly doubles from ~31% (24 types) to ~50-55% (8 types)
- All frustration information is preserved as continuous values with no binning loss

### What remains

| Workstream | Status | Blocking on | Next step |
|---|---|---|---|
| **1: Item Expansion** | DONE | -- | Items integrated into scoring pipeline and dashboard. Human expert review and cognitive pretesting still needed before empirical deployment. |
| **2: ABQ Integration** | Spec complete, needs implementation | Platform development | Implement ABQ check-in template, scoring service, and endpoints in second-game |
| **3: Coach Ratings** | Spec complete, needs implementation | Platform development | Add coach rating items to leader review flow in second-game |
| **4: Archetype Revision** | DONE | -- | 8 base patterns with continuous frustration. Dashboard methodology tab needs updating to reflect 8 types. |
| **5: Big Five / Belbin** | DONE (verified) | -- | Audit complete (docs/big-five-belbin-audit.md). No code changes needed. |
| **6: Standards Compliance** | Ongoing | All workstreams | Updated as each workstream completes |

**Note:** The 36-item structure is now implemented in both the Python scoring pipeline (`src/psychometric/irt_subscale_scoring.py`, `src/psychometric/tier_reliability.py`, `config/irt_parameters.yaml`) and the dashboard JS (`outputs/site/index.html`). All 493 tests pass.

### Recommended next steps

1. **Expert review and cognitive pretesting of the 12 new items** in `docs/new-items-draft.md`. The items are integrated into the codebase, but sport psychology expertise is needed to confirm each item taps the intended construct. Three items are flagged for particular attention during cognitive pretesting.

2. **Implement ABQ and coach ratings in second-game.** The spec in `docs/abq-coach-integration-spec.md` follows the platform's existing patterns (SQLAlchemy 2.0, Pydantic, FastAPI). This is platform feature work that can proceed independently of item review.

3. **Update the simulation dashboard** (`outputs/site/index.html`) methodology tab to reflect 8 types, continuous frustration, and the expanded reference list.

---

## Plan structure

### Workstream 1: Item expansion (24 to 36 items)

**Goal:** Write 12 new items (2 per subscale) to increase subscale reliability from 0.943 to ~0.96 and per-domain classification agreement from ~67% to ~75%.

**Approach:**
- Each new item follows the same content domain as its subscale
- One reverse-coded item per new pair to maintain acquiescence bias detection
- Items written to be sport-specific, accessible across cultural backgrounds, and free of construct-irrelevant features
- AI-assisted item drafting followed by human expert review

**New items needed (2 per subscale, 12 total):**

| Subscale | Current items | New items needed | Content guidance |
|---|---|---|---|
| Ambition Satisfaction (AS) | AS1-AS4 | AS5, AS6 | Goal-directed drive, initiative, competitive engagement. Avoid conflating with Craft (skill mastery). |
| Ambition Frustration (AF) | AF1-AF4 | AF5, AF6 | Goal pursuit blocked by external forces (coaching decisions, selection, institutional constraints). Must describe active thwarting, not low satisfaction restated negatively (Murphy et al. 2023 warning). |
| Belonging Satisfaction (BS) | BS1-BS4 | BS5, BS6 | Relational connection, trust, inclusion. Avoid conflating with team performance. |
| Belonging Frustration (BF) | BF1-BF4 | BF5, BF6 | Active exclusion, conditional acceptance, relational insecurity. Must describe external obstruction. |
| Craft Satisfaction (CS) | CS1-CS4 | CS5, CS6 | Skill development, mastery experiences, technical growth. Avoid conflating with Ambition (goal achievement). |
| Craft Frustration (CF) | CF1-CF4 | CF5, CF6 | Competence undermined by environment (inadequate coaching, no development opportunities, evaluated rather than supported). Must describe external obstruction. |

**Item writing principles (from APA Standards Chapter 4):**
- [ ] Standard 4.7: Document the procedures used to develop, review, and try out items
- [ ] Standard 4.8: Items should be reviewed for sensitivity to subgroup characteristics
- [ ] Standard 4.12: Conduct item analysis during development
- [ ] Each item reviewed by at least one sport psychologist or SDT researcher
- [ ] Cognitive pretesting with 5-10 athletes from diverse sports and levels
- [ ] Pilot IRT calibration on N >= 100 before adding to production item bank

**Reverse coding structure (expanded):**
- Current: 1 reverse item per subscale (item 4 in each)
- Expanded: 2 reverse items per subscale (items 4 and 6)
- This helps detect acquiescence bias and addresses the Murphy et al. (2023) method artifact concern by mixing keying direction within each subscale

**Deliverables:**
- [ ] 12 draft items with content rationale
- [ ] Expert review documentation
- [ ] Cognitive pretest results (5-10 athletes)
- [ ] Pilot IRT calibration (N >= 100)
- [ ] Updated `config/irt_parameters.yaml` with 36-item parameters
- [ ] Updated `FACTOR_ITEM_INDICES` in `irt_subscale_scoring.py` (6 items per factor)
- [ ] Updated `TIER_DEFINITIONS` in `tier_reliability.py` (tiers: 6/18/36 items)
- [ ] All existing tests updated and passing

### Workstream 2: ABQ criterion integration

**Goal:** Integrate the Athlete Burnout Questionnaire as a monthly criterion measure to enable empirical threshold derivation via ROC analysis.

**The ABQ (Raedeke & Smith, 2001):**
- 15 items, 5-point Likert (almost never to almost always)
- 3 subscales: Reduced Sense of Accomplishment (RSA), Emotional/Physical Exhaustion (EXH), Sport Devaluation (SD)
- Items 1 and 14 reverse-scored
- Reliability: omega = .77 to .85 (Grugan et al., 2024)
- ESEM provides superior fit to CFA (CFI .964 vs .853)
- Measurement invariant across gender, sport type, and age

**ABC-to-ABQ mapping for criterion validation:**

| ABC subscale | ABQ criterion | Expected relationship | Rationale |
|---|---|---|---|
| Craft Frustration | RSA (Reduced Sense of Accomplishment) | r > .40 | Both measure competence-related distress in sport |
| Ambition Frustration | SD (Sport Devaluation) | r > .35 | Both measure diminished goal-directed engagement |
| Total Frustration (composite) | EXH (Exhaustion) | r > .40 | Exhaustion reflects accumulated cost across domains |
| Ambition Satisfaction | RSA (inverse) | r < -.30 | Accomplishment satisfaction is the opposite of RSA |

**Implementation in second-game:**
- [ ] Add ABQ as a check-in template in `services/api/src/models/checkin_template.py`
- [ ] Create ABQ scoring service in `services/api/src/services/abq_service.py`
- [ ] Store ABQ subscale scores alongside ABC profiles
- [ ] Administer monthly (separate from weekly ABC check-ins)
- [ ] After N >= 200 paired ABC + ABQ datasets: run `scripts/derive_thresholds.py` on real data
- [ ] Replace synthetic thresholds in `config/empirical_thresholds.yaml` with empirical values

**ROC analysis deliverables:**
- [ ] Domain-specific activation thresholds (may differ per domain)
- [ ] Domain-specific frustration thresholds
- [ ] Bootstrap 95% CIs on all thresholds
- [ ] AUC for each ABC-ABQ subscale pairing
- [ ] Sensitivity/specificity at Youden-optimal cutoffs

### Workstream 3: Coach rating criterion

**Goal:** Add structured coach observations as a second, independent criterion that does not share self-report method variance with ABC.

**Coach rating items (3 per athlete, weekly):**

| Item | What it measures | ABC domain it validates |
|---|---|---|
| "Rate this athlete's competitive drive and initiative this week" (1-10) | Ambition engagement | Ambition Satisfaction activation threshold |
| "Rate this athlete's connection with teammates this week" (1-10) | Belonging engagement | Belonging Satisfaction activation threshold |
| "Rate this athlete's skill development effort this week" (1-10) | Craft engagement | Craft Satisfaction activation threshold |

**Optional concern flag:**
- "I am concerned about this athlete's wellbeing" (yes/no)
- When flagged, triggers comparison with ABC trajectory to test whether coach concern and ABC decline co-occur

**Implementation in second-game:**
- [ ] Add coach rating items to the leader review flow in `services/api/src/routers/leader.py`
- [ ] Store as structured data linked to athlete and date
- [ ] After N >= 200: run ROC analysis with coach ratings as criterion for activation thresholds
- [ ] Compare coach-derived thresholds with ABQ-derived thresholds (convergent evidence)

### Workstream 4: Archetype system revision

**Goal:** Simplify from 24 types to 8 base patterns with continuous frustration, then reconsider granularity after empirical classification agreement data.

**Immediate changes (with current 24-item instrument):**
- [ ] Report 8 base patterns only (Integrator, Captain, Architect, Mentor, Pioneer, Anchor, Artisan, Seeker)
- [ ] Report frustration as continuous score per domain with confidence band, not as Steady/Striving/Resolute modifier
- [ ] Update `type_derivation.py` to produce base pattern + continuous frustration
- [ ] Update `type_descriptions.py` with 8 descriptions (drop modifier-specific variants)
- [ ] Update dashboard type distribution chart to show 8 types
- [ ] Update dashboard methodology section

**After 36-item expansion and empirical data:**
- [ ] Compute per-domain classification agreement with 6 items per subscale
- [ ] If agreement >= 75% per domain: base patterns are defensible
- [ ] If ROC-derived frustration threshold produces modifier with kappa >= 0.60: modifier layer can return (up to 24 types)
- [ ] If not: stay at 8 patterns with continuous frustration

**Resolute Seeker dominance fix:**
- The Resolute Seeker dominance disappears when "Resolute" is no longer a category
- The Seeker pattern (no domain activated) prevalence depends on the activation threshold
- With ROC-derived per-domain thresholds, Seeker prevalence becomes an empirical observation rather than a tuning problem

### Workstream 5: Big Five weight matrix and Belbin re-derivation

**Goal:** Re-optimize the Big Five weight matrix and Belbin inference for the 36-item subscale covariance structure.

**Why this is needed:** The current weight matrix was optimized for 4-item subscale variance profiles. With 6 items per subscale, the subscale score distributions become tighter (lower SE), changing the covariance structure the weights must account for.

**Process:**
- [ ] Generate synthetic data with 36 items (6 per subscale) using updated IRT parameters
- [ ] Compute the 6x6 subscale covariance matrix from the new item structure
- [ ] Re-optimize Big Five weight matrix to produce:
  - Near-zero inter-trait correlations (|r| < 0.02)
  - ~20% primary-trait distribution per trait
  - Match against Gosling et al. (2003) empirical benchmarks
- [ ] Re-validate Belbin role coverage with new weights:
  - All 9 roles present
  - No single role > 20% of population
  - Domain-cluster mapping preserved (Thinking=Craft, People=Belonging, Action=Ambition)
- [ ] Update `big_five_inference.py` with new weight matrix
- [ ] Update `belbin_inference.py` if affinity weights change
- [ ] Update all affected tests

### Workstream 6: Standards compliance for expanded instrument

**APA/AERA/NCME Standards that apply specifically to the expansion:**

| Standard | Requirement | How we address it |
|---|---|---|
| 4.0 | Tests developed on sound scientific basis | SDT theoretical foundation; AI-assisted item development with human expert review |
| 4.7 | Document item development procedures | Item drafting, expert review, cognitive pretest, pilot calibration all documented |
| 4.8 | Review items for subgroup sensitivity | DIF analysis (Phase 4 infrastructure) on pilot data across gender, sport, level |
| 4.12 | Item analysis during development | IRT calibration (Phase 1 infrastructure) on pilot data; discrimination and difficulty estimated |
| 2.5 | Reliability consistent with test structure | GRM-based marginal reliability per tier; multidimensional composite reliability |
| 2.9 | Long and short version reliability reported | Updated tier reliability (6/18/36 items) using Phase 5b infrastructure |
| 5.8 | Cut score method and rationale documented | ROC/Youden with ABQ criterion; bootstrap CI; full documentation |
| 3.2 | Examine content for construct-irrelevant variance | DIF analysis across gender, sport type, competitive level on expanded items |
| 1.1 | Intended interpretation clearly stated | Validity Argument document updated for 36-item instrument |
| 1.14 | Subscore distinctiveness demonstrated | Bifactor analysis (Phase 3 infrastructure) on 36-item data |

**Transparency requirements (self-imposed):**
- [ ] Every threshold reports its derivation method, criterion variable, AUC, sensitivity, specificity, and CI
- [ ] Every classification reports its decision consistency estimate and supportable interpretation tier
- [ ] The instrument documentation explicitly states: "This is an AI-developed, purpose-built instrument grounded in SDT. It has not been validated on a large empirical sample. All thresholds derived from simulation must be replaced with empirically validated thresholds before clinical interpretation."
- [ ] The Validity Argument document clearly separates what has evidence (simulation results) from what needs evidence (empirical criterion validation)

---

## Dependency and sequencing

```
Workstream 1 (Item Expansion)
  ├──> needs: item content decisions (human process)
  ├──> needs: expert review (human process)
  ├──> needs: cognitive pretest (athlete access)
  └──> needs: pilot IRT calibration (N >= 100)

Workstream 2 (ABQ Integration)
  ├──> can start now (add template to platform)
  ├──> data collection: ongoing after deployment
  └──> ROC analysis: after N >= 200 paired datasets

Workstream 3 (Coach Ratings)
  ├──> can start now (add to leader review flow)
  └──> ROC analysis: after N >= 200

Workstream 4 (Archetype Revision)
  ├──> immediate: simplify to 8 patterns (code change)
  └──> deferred: reconsider modifier after empirical data

Workstream 5 (Big Five / Belbin)
  └──> after Workstream 1 (needs 36-item covariance)

Workstream 6 (Standards Compliance)
  └──> threaded through all workstreams
```

**Completed (no further code work needed):**
- Workstream 1 (item expansion to 36 items): code implemented in scoring pipeline and dashboard
- Workstream 4 (archetype revision to 8 patterns): code implemented and tested
- Workstream 5 (Big Five / Belbin verification): audited, no changes needed

**What can start now (no athlete data needed):**
- Workstream 2 and 3 (add ABQ template and coach ratings to platform): platform feature work

**What needs human review (expert + athlete access):**
- Expert review and cognitive pretesting of the 12 new items (5-10 athletes)
- Pilot IRT calibration (N >= 100)
- ROC threshold derivation (N >= 200 with paired ABC + ABQ)
- Decision consistency on expanded instrument (N >= 200)

---

## Success criteria

| Milestone | Criterion | How measured |
|---|---|---|
| Item expansion complete | 36 items written, reviewed, pretested, pilot-calibrated | Expert sign-off + IRT discrimination > 0.80 for all new items |
| ABQ integration live | Monthly ABQ collection running in platform | N >= 50 paired datasets within 3 months |
| Coach ratings live | Weekly coach ratings flowing | N >= 100 athlete-weeks within 2 months |
| Empirical thresholds derived | ROC analysis on N >= 200 paired ABC + ABQ | AUC > 0.65 for primary pairings; Youden CI width < 1.0 |
| Classification agreement improved | Per-domain agreement with 36 items | >= 75% per domain (up from 67%) |
| Archetype system stabilized | Empirical decision consistency for chosen granularity | Kappa >= 0.60 for whatever type system is adopted |
| Big Five re-derived | Weight matrix optimized for 36-item covariance | Inter-trait |r| < 0.05; primary-trait distribution 15-25% each |
| Validity Argument updated | All empirical evidence rows populated | Peer review or expert audit of the document |

---

## What we are confident in and what we are not

**Confident:**
- The analytic infrastructure works (493 tests, 0 failures)
- The theoretical framework (SDT) has strong empirical support for predicting burnout
- The cascade model (frustration rising before satisfaction drops) matches SDT predictions
- The ABQ is a validated criterion measure with established measurement invariance
- The ROC/Youden/bootstrap methodology is the gold standard for threshold derivation

**Not yet confident (requires empirical data):**
- Whether the ABC items as written actually measure what SDT constructs predict
- Whether the empirical thresholds will differ substantially from the assumed ones
- Whether the 36-item expansion improves classification agreement to the 75% target
- Whether ABC trajectories predict ABQ burnout scores in real athletes
- Whether the platform reduces burnout incidence compared to no monitoring

**Honest about:**
- This is an AI-developed instrument. No licensed SDT materials were used.
- No existing instrument does exactly what this one attempts. This is uncharted territory.
- Achieving gold standard psychometric quality will take years of iterative testing and refinement.
- We are starting with what statistics and AI can provide, and being transparent about the gap between simulation evidence and empirical validation.

---

## References

- Bartholomew, K. J., et al. (2011). Self-determination theory and diminished functioning. *Personality and Social Psychology Bulletin, 37*(11), 1459-1473.
- Baumel, A., et al. (2019). Objective user engagement with mental health apps. *Journal of Medical Internet Research, 21*(9), e14567.
- Chang, C. J., et al. (2020). Mental health issues and psychological factors in athletes. *American Journal of Sports Medicine, 48*(9), 2303-2314.
- Chen, B., et al. (2015). Basic psychological need satisfaction, need frustration, and need strength across four cultures. *Motivation and Emotion, 39*, 216-236.
- Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits. *Psychological Inquiry, 11*(4), 227-268.
- Erickson, J. L., et al. (2023). Validity of the APSQ for mental health screening. *British Journal of Sports Medicine, 57*(21), 1389-1394.
- Grugan, M. C., et al. (2024). Factorial validity and measurement invariance of the ABQ. *Psychology of Sport and Exercise, 73*, 102638.
- Jones, M., et al. (2022). Mental performance and mental health services in NCAA DI athletic departments. *Journal for Advancing Sport Psychology in Research, 2*(1), 4-18.
- Lonsdale, C., & Hodge, K. (2011). Temporal ordering of motivational quality and athlete burnout. *Medicine & Science in Sports & Exercise, 43*(5), 913-921.
- Lonsdale, C., et al. (2009). Athlete burnout in elite sport: A self-determination perspective. *Journal of Sports Sciences, 27*(8), 785-795.
- Murphy, J., et al. (2023). The BPNSFS probably does not validly measure need frustration. *Motivation and Emotion, 47*, 899-919.
- NCAA Student-Athlete Health and Wellness Study, 2022-23. December 2023.
- Prior, E., et al. (2024). Attrition in psychological mHealth interventions for young people. *Journal of Technology in Behavioral Science, 9*, 639-651.
- Raedeke, T. D., & Smith, A. L. (2001). Development and preliminary validation of an athlete burnout measure. *Journal of Sport & Exercise Psychology, 23*(4), 281-306.
- Rhoden, W. C. (2006). *$40 Million Slaves.* Crown Publishers.
- Whelan, B. M., et al. (2024). Suicide in NCAA athletes: A 20-year analysis. *British Journal of Sports Medicine, 58*(10), 531-537.
- Wolanin, A., et al. (2016). Prevalence of clinically elevated depressive symptoms in college athletes. *British Journal of Sports Medicine, 50*(3), 167-171.
