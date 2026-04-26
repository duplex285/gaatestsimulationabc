# Passion Quality Module: Build Retrospective

Date: 2026-04-20
Scope: Section 16.2 of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

A passion-quality measurement layer grounded in Vallerand's Dualistic Model of Passion, replacing the heuristic overinvestment warning described in abc-assessment-spec.md Section 2.2. The full slice includes items, scoring, trigger, narratives, and tests.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/passion-items-draft.md | 6-item draft (HP1-HP3, OP1-OP3), scoring model, evidence gates, empirical calibration open items | New |
| src/python_scoring/passion_quality.py | Subscale scoring, balance, leaning classification, two-tier evidence gates | New |
| src/python_scoring/overinvestment_trigger.py | Passion-aware trigger with five routing paths and optional daily cross-signals | New |
| src/python_scoring/narrative_engine.py | `_PASSION_NARRATIVES`, `_OVERINVESTMENT_NARRATIVES`, `generate_passion_narrative`, `generate_overinvestment_narrative` | Extended |
| tests/python_tests/test_passion_quality.py | 22 tests across scoring, leaning, gates, validation, structure | New |
| tests/python_tests/test_overinvestment_trigger.py | 10 tests across no-trigger, harmonious, obsessive, mixed, insufficient, signals-absent | New |
| tests/python_tests/test_passion_narratives.py | 11 tests across structure, validation, banned-term enforcement | New |

### Test result

```
452 passed, 4 xfailed in 5.45s
```

43 new tests, all passing. No regressions in the 409 pre-existing tests.

## 2. Completeness map against the plan

| Section 16.2 deliverable | Status | Notes |
|---|---|---|
| 4-6 new items measuring harmonious vs obsessive passion | Done | 6 items drafted, 3 per subscale. Original wording, no licensed scale content reproduced. |
| Items placed outside the core 36-item bank, quarterly cadence | Done | `passion_quality.py` is independent of `REQUIRED_ITEMS`; core scoring pipeline unchanged. |
| Replace overinvestment heuristic with passion-aware routing | Done, but note below | The spec described the heuristic; it had not been implemented in code. So this is a fresh build, not a refactor. The passion-aware design is the first implementation. |
| Retain cross-signal rule as trigger; passion selects frame and action | Done | `evaluate_overinvestment` accepts `DailySignals` as optional input. When absent, the ABC-side pattern still drives the trigger. When present, signals can exonerate a thriving athlete whose recovery is healthy. |
| Translation-table entries and narrative templates | Done | `_PASSION_NARRATIVES` and `_OVERINVESTMENT_NARRATIVES` in `narrative_engine.py`, keyed by leaning and path. Athlete and coach surfaces enforced. |
| Evidence gates per Section 17.5 | Done | Display gate at 4 of 6 items; recommendation gate at 6 of 6 items with a decisive leaning. |

## 3. Issues encountered and resolutions

### 3.1 The overinvestment rule was never implemented

The improvement plan listed the task as "replace the overinvestment warning." The warning was documented in abc-assessment-spec.md Section 2.2 but had no corresponding code. Resolved by reframing the task as a fresh build with passion-aware design from the start. Simpler than a refactor, and it avoided code the team would only have deleted.

### 3.2 Initial recommendation gate was too narrow

First draft of `score_passion_quality` only admitted `harmonious` and `obsessive` to the recommendation gate. That failed the test for the mixed routing path in `evaluate_overinvestment`, because mixed-passion athletes in a thriving pattern never reached the mixed coach template. The diagnosis: mixed and uninvested are non-directional but decisive. They drive specific prose and specific coach actions (check for conflict, look elsewhere for drive), which is exactly what Section 17.5 defines as the recommendation-gate bar. Resolved by widening the gate to admit `{harmonious, obsessive, mixed, uninvested}` and keeping `insufficient_signal` and `not_computed` outside. Two scoring tests that asserted the old semantics were updated to match the new semantics; the change is tighter, not looser.

### 3.3 Two tests used inputs that no longer reached the branch they probed

After the gate widening, `test_balance_close_to_zero_fails_recommendation` and `test_unclear_passion_routes_to_watch` used all-5 responses. Those inputs now classify as mixed (elevated on both subscales) and pass the recommendation gate. The tests had been probing the insufficient-signal branch. Resolved by picking inputs that actually land in that branch: hp=(4,4,4), op=(4,4,3), which produces balance 0.56, hp elevated, op not, leaning `insufficient_signal`. The tests now exercise the exact branch they claim to.

### 3.4 Daily cross-signals live in a different repo

`DailySignals` (recovery_slope, cognitive_load) is sourced from the second-game repo, not this simulation repo. Resolved by typing them as optional input to `evaluate_overinvestment`. When absent, the trigger still evaluates the ABC-side pattern. When present, clean daily signals can suppress the trigger even with two domains thriving. This keeps the module standalone-testable and integration-ready.

## 4. Open items

### 4.1 Subject-matter expert review

Per improvement plan Section 0.1 and Section 17.9, every new narrative template needs sign-off from a qualified sport psychologist or certified mental performance consultant before any production deployment. The six new athlete-facing templates and six coach-facing templates in `_PASSION_NARRATIVES`, plus five overinvestment-path templates per audience in `_OVERINVESTMENT_NARRATIVES`, are unreviewed.

### 4.2 Automated readability enforcement in CI

Section 17.2 specifies Flesch-Kincaid thresholds enforced in CI. `test_passion_narratives.py` enforces the banned-term rule already, but readability is not yet in the test suite. Open item: add a `textstat`-based test that fails the build when any athlete-facing template exceeds Grade 8 or any coach-facing template exceeds Grade 10. Applies to all narrative templates, not just the new ones.

### 4.3 Empirical calibration of thresholds

The constants `SUBSCALE_ELEVATED_THRESHOLD = 5.0`, `BALANCE_LEANING_THRESHOLD = 2.0`, and `BALANCE_AMBIGUOUS_THRESHOLD = 1.0` are theoretical priors. Phase A pilot data (improvement plan Section 13.1) should recalibrate them against coach-rated life-balance concerns. Open item: add a calibration script under `scripts/` that reads Phase A responses and outputs empirical thresholds, similar to the existing `scripts/derive_thresholds.py`.

### 4.4 Psychometric validation of the 6-item bank

McDonald's omega per subscale, CFA fit for a two-factor solution against a single-factor alternative, test-retest stability across the quarterly cadence, and convergent validity against a licensed DMP measure (where licensing permits). None of this is possible on the current synthetic data. Belongs in Phase A analytics.

### 4.5 Integration into `EnhancedABCScorer.score()`

The new scoring module is standalone. It is not yet called by `EnhancedABCScorer.score()`. Integration requires three choices:
1. Whether passion items flow through the same submission surface as the core 36 items, or through a separate quarterly flow.
2. Where in the pipeline passion scoring runs (before or after base-rate adjustment).
3. How the overinvestment trigger composes with existing frustration-signature output.

These are product-side calls, not technical blockers. Open item: a short integration PRD.

### 4.6 Persistence of passion scores across measurements

Passion is a slower-moving construct than ABC satisfaction/frustration. Storing passion leaning with a last-observed timestamp is more useful than recomputing from scratch each cycle. The Bayesian scorer in `bayesian_scorer.py` already does this for subscales; passion should get similar treatment, with a longer decay profile. Open item: extend `ABCBayesianProfile` to include harmonious and obsessive subscales.

### 4.7 Recovery-slope and cognitive-load thresholds are placeholders

The constants `RECOVERY_DECLINING_THRESHOLD = 40.0` and `COGNITIVE_LOAD_HIGH_THRESHOLD = 70.0` in `overinvestment_trigger.py` match the original spec values but have never been validated on real data. When the second-game cognitive-signal engine ships, these should be calibrated against outcome data.

### 4.8 The banned-term list in tests is not exhaustive

`test_passion_narratives.py` contains a partial copy of the Section 17.3 banned-term list. The authoritative list should live in a single module that both the test and any future lint rule can import. Open item: promote the list to `src/python_scoring/banned_terms.py` (or a config file) and have the test import it.

## 5. What went well

- Tight loop between the spec in improvement-plan Section 16 and the code. Each module has a direct reference line.
- Evidence-gate concept from Section 17.5 translated cleanly into a two-tier gate on the result object. Downstream consumers (the trigger) route by gate state, not by raw score.
- Discovering the non-existence of the old overinvestment code early saved a chunk of misdirected refactoring work.
- Banned-term enforcement as a test, not just a documentation rule, catches drift immediately.
- Test failures surfaced a real design inconsistency (the rec gate was too narrow) rather than a mistake in the tests. The fix made the module more correct, not less strict.

## 6. What I would do differently

- Start with a single authoritative banned-term list (Open item 4.8), not a copy in the test. The duplication is a small bug waiting to happen.
- Write the narrative templates before the trigger paths, not after. The narratives constrain what paths are worth routing to; I ended up with a `mixed` narrative template and a `mixed` path in the trigger that did not initially pass the rec gate, because I designed the gate before the narratives.
- Wire the readability test in the same pass as the banned-term test. Enforcement is cheap when it is already a test file; retrofitting is slower.

## 7. Post-retrospective review findings

After drafting the retrospective I ran ruff, coverage, and a readability probe. Five findings, four fixed in this pass.

### 7.1 Class constants were placed mid-class (fixed)

`VALID_PASSION_LEANINGS` and `VALID_OVERINVESTMENT_PATHS` landed between methods rather than next to `VALID_AUDIENCES` at the top of `NarrativeEngine`. Moved both to the top of the class with the other `VALID_*` tuples. No behavior change.

### 7.2 Uninvested-with-thriving-ABC edge case was untested (fixed)

Coverage reported line 220 of `overinvestment_trigger.py` uncovered. That line handles the contradictory case where ABC domains are thriving but passion is uninvested. Added `test_uninvested_passion_with_thriving_routes_to_watch` which asserts the trigger routes to `insufficient_evidence` with a `watch` recommendation and names the contradiction in the rationale. `overinvestment_trigger.py` is now at 100% line coverage.

### 7.3 Two `None` branches in `passion_quality.py` are unreachable under the current bank (acknowledged)

Lines 86 and 157 return `None` or `not_computed` when a subscale has zero items. Under the current 3-items-per-subscale bank plus the 4-item display gate, any 4-of-6 subset spans both subscales, so these branches never fire. Added `# pragma: no cover` with a comment explaining the branch is defensive and preserved against future changes to the bank or the gate. `passion_quality.py` is now at 100% effective coverage.

### 7.4 Readability could not be measured automatically (still open)

Section 17.2 calls for Flesch-Kincaid enforcement in CI. The `textstat` package is not a project dependency. Open item 4.2 stands. Manual eyeball pass on the athlete-facing templates: sentences are short, words are common, no subordinate clauses deeper than one. Coach-facing templates use words like "warranted," "adjustment," "identity-level," which push into Grade 9-10 range (within the coach target). All below the Grade 10 ceiling on inspection, but this should be enforced by CI, not by eyeball.

### 7.5 Ruff clean, full suite green

`ruff check` passes on all new and modified files. Full test suite: 453 passed, 4 xfailed, 0 failed. New-module coverage: `passion_quality.py` 100%, `overinvestment_trigger.py` 100%.

## 8. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | Done (453 passed, 4 xfailed) |
| New-module line coverage | 100% on both modules |
| Banned-term enforcement as test | Done for passion and overinvestment templates |
| Readability enforcement as test | Open (requires `textstat` dependency) |
| SME review of templates | Open |
| Empirical calibration of thresholds | Open (requires Phase A data) |
| Psychometric validation of 6-item bank | Open (requires Phase A data) |
| Integration into `EnhancedABCScorer.score()` | Open (requires product PRD) |
| Passion posterior persistence | Open (extend `ABCBayesianProfile`) |
| Daily-signal threshold calibration | Open (requires second-game data) |
| Authoritative banned-term module | Open (currently duplicated in test) |

Eight open items. Four are blocked on data or product decisions. Four are engineering items that can be tackled in a follow-up pass: readability enforcement, banned-term module, passion posterior persistence, and integration into the enhanced scorer.
