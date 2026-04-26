# Self-Concordance (Section 16.7) Build Retrospective

Date: 2026-04-21
Scope: Section 16.7 (goal self-concordance) of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

A goal-level self-concordance layer for the ABC Assessment. Four items along the Perceived Locus of Causality continuum (external, introjected, identified, intrinsic), scored on a stated current goal at biweekly cadence. Produces autonomous and controlled composites, a signed self-concordance score, and a three-band leaning classification. Goal text travels with the result for product display but does not affect scoring.

This is the sixth optional layer on the ABC Assessment. After this slice, the instrument operationalizes BPNT (core), OIT (regulatory style + erosion), DMP (passion), COT (causality orientations), goal self-concordance (this slice), plus the group-conscious and coach-circumplex extensions.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/self-concordance-items-draft.md | 4 items (SC1-SC4) along PLOC, biweekly cadence, scoring model, three-band classification, open items | New |
| src/python_scoring/self_concordance.py | Autonomous and controlled composites, signed self-concordance score, three-band classification, two-tier gates, goal-text passthrough | New |
| src/python_scoring/optional_items.py | Extended with `SELF_CONCORDANCE_LAYER` | Modified |
| src/python_scoring/narrative_engine.py | `_SELF_CONCORDANCE_NARRATIVES` (4 leanings x 2 audiences = 8), `generate_self_concordance_narrative` method, `VALID_SELF_CONCORDANCE_LEANINGS` constant | Extended |
| src/python_scoring/scoring_pipeline.py | `EnhancedABCScorer.score()` accepts `self_concordance_responses` and optional `self_concordance_goal_text`; profile and narrative attached to result | Modified |
| tests/python_tests/test_self_concordance.py | 22 tests: scoring, leaning classification, gates, validation, goal-text passthrough, structure | New |
| tests/python_tests/test_self_concordance_narratives.py | 6 tests: structure, validation, banned terms, readability | New |
| tests/python_tests/test_optional_items.py | 5 new assertions for the layer | Modified |
| tests/python_tests/test_enhanced_pipeline_optional_layers.py | 2 new integration tests + extended backward-compat and full-stack tests | Modified |

### Test result

```
707 passed, 4 xfailed in 11.19s
```

33 new tests this slice. No regressions across the 674 tests pre-16.7.

Coverage: 100% line and branch on `self_concordance.py`.

## 2. Completeness map against the plan

| Section 16.7 (self-concordance) deliverable | Status | Notes |
|---|---|---|
| One-minute prompt per biweekly cycle | Done | Four items, single goal, single screen. |
| PLOC continuum scoring | Done | External, introjected, identified, intrinsic; standard autonomous-minus-controlled formula. |
| Self-concordance slope predicts attainment-plus-well-being | Deferred to trajectory engine | Per-cycle scoring ships; longitudinal trajectory is a separate (not scoped) slice that needs goal continuity logic upstream. |
| Goal text storage for product display | Done | Optional `goal_text` kwarg on the scoring function; flows through to the result dataclass. |
| Narratives at the leaning level | Done | Four leanings x two audiences = eight templates, all under Grade 10. |
| Integration into `EnhancedABCScorer` | Done | Mirrors causality and group-conscious patterns. |

## 3. Issues encountered and resolutions

### 3.1 All tests passed on the first run

Notably no readability or coverage drift on this slice. Three reasons. The narratives are short by design (this is a one-screen prompt, not a multi-construct surface). The classification logic is simple (three bands, no margin-rule complexity). And the pattern transfer from previous slices was tight: I wrote the items, scoring, narratives, registration, integration, and tests in one pass and ran the suite once.

That is not luck. The prior-slice retrospectives surfaced the patterns that reliably break on first run (compound coach narratives, dead-code branches in classification logic, missing dispersion-band coverage). I avoided each of them by design.

### 3.2 Goal text is a metadata field, not a scoring input (decision)

The athlete's goal text could in principle drive narrative selection (substituting the goal name into the template, e.g., "Your goal of 'qualifying for nationals' is sitting in autonomous regulation territory"). I chose not to do that for first slice. Reasons:

- Free-text goals are heterogeneous in length and style; substitution risks awkward phrasing.
- Cross-checking against banned terms in the goal text is harder than against fixed templates.
- The product surface can render the goal text alongside the narrative in its own UI element.

The goal-text field is stored on the result dataclass for the product to use. Narrative selection ignores it.

### 3.3 Trajectory engine not yet built

Sheldon's research treats self-concordance trajectory (movement across cycles) as a stronger predictor than absolute level. Tracking trajectory requires goal continuity logic: knowing that the goal in cycle N is the same goal as in cycle N-1, or recognizing a goal change. That is product-side work and is not in scope for this slice. Flagged as open.

### 3.4 Integration with regulatory-style layer is conceptually overlapping

Both the regulatory-style layer (Section 16.1) and this self-concordance layer use PLOC. The difference: regulatory style is per-domain (Ambition, Belonging, Craft as a whole); self-concordance is per-goal. An athlete with identified regulation on Ambition could still pursue a specific ambition goal for introjected reasons. The two should give different signals on the same athlete and that is by design. Worth flagging in the items draft (which I did) so future SME or product readers do not see them as redundant.

## 4. Open items

### 4.1 SME review of 8 new templates

Add to the existing SME packet (`docs/sme-review-packet-2026-04-20.md`) in a follow-up pass.

### 4.2 Goal continuity and trajectory engine

The biggest open item. Self-concordance trajectory is the high-value signal per Sheldon. Building it requires:
- Goal identity tracking across cycles (athlete states "same goal as last time" or selects from prior).
- A trajectory engine that takes a goal-keyed series of self-concordance scores and produces a slope, direction, and significance estimate.
- Narratives at the trajectory level (e.g., goal is becoming more autonomous, becoming more controlled, oscillating).

Not a measurement gap; a longitudinal-engine gap. Belongs in a future slice.

### 4.3 Goal-domain mapping

Athletes' goals usually fall under one of the three ABC domains. Tagging the goal to a domain (free-text classifier or athlete-selected) would let self-concordance signals interact with the regulatory-style layer (which is already per-domain). Phase A enhancement.

### 4.4 Empirical calibration of the 3.0 leaning threshold

Theoretical prior. Phase A data with goal-attainment outcomes will recalibrate.

### 4.5 Convergent validity against published self-concordance scales

Sheldon's instrument is in the academic public domain; convergent comparison is a clean Phase A study. Target: r >= 0.60 with the published version on the autonomous-controlled difference.

### 4.6 Test-retest at biweekly window

Self-concordance is meant to move slowly within a goal but to differ across goals. The biweekly retest stability question depends on whether the athlete is rating the same goal. Phase A can pilot this with paired biweekly responses on flagged "same goal" cycles.

## 5. What went well

- Cleanest first-run slice of the session. Narratives, scoring, integration, and tests all passed on the first complete pass. The pattern is mature.
- The goal-text passthrough as metadata is a clean separation of concerns: scoring is purely numeric, product gets a free-text field, narrative remains template-driven.
- The integration test `test_all_layers_together` now exercises all six optional layers + daily signals + core in one call. That gives one canonical end-to-end smoke test.
- The plan status snapshot was updated in both repo and Obsidian copies before starting work, so the in-progress flag is visible during the slice.

## 6. What I would do differently

- Build the trajectory engine alongside the per-cycle scorer for self-concordance specifically. Sheldon's central empirical claim is about trajectory; shipping per-cycle scoring without trajectory captures only half the construct's value. Deferred for scope, but worth scheduling soon.
- The four leanings (autonomous, controlled, mixed, not_computed) overlap structurally with the passion four-leaning pattern (harmonious, obsessive, mixed, uninvested, insufficient_signal, not_computed) and the regulatory four-style pattern. Worth considering whether a shared "leaning classifier" abstraction would reduce drift, or whether the per-construct semantics make abstraction premature.

## 7. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 707 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on self_concordance |
| Readability enforced on new templates | Done (Grade 8 athlete / Grade 10 coach, held on first pass) |
| Banned-terms enforced on new templates | Done |
| Optional item registry updated | Done (sixth layer) |
| Integration into EnhancedABCScorer | Done |
| SME review of 8 new templates | Open (extend packet) |
| Goal continuity and trajectory engine | Deferred (future slice) |
| Goal-domain mapping | Open (Phase A) |
| Empirical calibration of leaning threshold | Open (Phase A) |
| Convergent validity against published scale | Open (Phase A) |

Five open items. Three are Phase A calibration or product design. One is the SME packet extension. One is the trajectory engine, which is a meaningful follow-up slice.
