# Coach Circumplex (Section 16.3) Build Retrospective

Date: 2026-04-20
Scope: Section 16.3 of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

A standalone Coach Circumplex instrument. 24 items across five facets, dual-rater design (coach self-rating plus athlete rating of the coach), a scoring module that produces per-facet scores, need-supportive and need-thwarting composites, a dominant-approach classification, an athlete-aggregation helper, a coach-self-versus-athlete gap computation, and a full coach-facing narrative layer with CI-enforced readability.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/coach-circumplex-items-draft.md | 24 items across autonomy-support, structure, relatedness-support, controlling, chaos. Dual-rater stems, scoring model, gap-band thresholds, calibration open items. | New |
| src/python_scoring/coach_circumplex.py | Per-facet scoring, composites, dominant-approach classification, athlete-aggregation, gap computation, two-tier evidence gates | New |
| src/python_scoring/optional_items.py | Extended with `COACH_CIRCUMPLEX_LAYER` and a new `respondent` field on `OptionalItemLayer` to distinguish athlete-only layers from dual-rater layers | Modified |
| src/python_scoring/narrative_engine.py | `_CIRCUMPLEX_FACET_NARRATIVES` (5 facets x 4 levels), `_CIRCUMPLEX_APPROACH_NARRATIVES` (5 approaches), `generate_circumplex_facet_narrative`, `generate_circumplex_approach_narrative`, class constants | Extended |
| tests/python_tests/test_coach_circumplex.py | 22 tests across scoring, facet levels, composites, display and recommendation gates, validation, athlete aggregation, gap computation | New |
| tests/python_tests/test_coach_circumplex_narratives.py | 13 tests across structure, validation, banned-term enforcement, readability enforcement | New |
| tests/python_tests/test_optional_items.py | 3 new tests for the circumplex layer registration | Modified |

### Test result

```
590 passed, 4 xfailed in 9.90s
```

38 new tests this slice. No regressions in the 552 tests pre-16.3.

100% line and branch coverage on `coach_circumplex.py`.

## 2. Completeness map against the plan

| Section 16.3 deliverable | Status | Notes |
|---|---|---|
| ~24 items across five facets (autonomy-support, structure, relatedness-support, controlling, chaos) | Done | 5+5+5+5+4 = 24 items exactly. Chapter 25 rationale-giving and Chapter 27 conditional-regard items included. |
| Dual-rater: coach self and athlete rating of coach | Done | Same 24 item codes, rater stored as metadata. `Respondent` type on the optional-items layer. |
| Gap between coach self and athlete aggregate | Done | Per-facet `FacetGap` with direction and flag. Threshold 2.0 points on the 0-10 scale. |
| Separate commercial instrument, not mixed with athlete ABC form | Done | `score_circumplex` is independent; zero changes to the core 36-item pipeline. |
| Translation-table entries for each facet | Done | 20 facet narratives (5 facets x 4 levels) plus 5 approach narratives. All coach-facing. |
| Evidence gates per Section 17.5 | Done | Display gate at 3 of n items per facet; recommendation gate at full-facet coverage. Composite suppression when too few facets pass. |
| Athlete-aggregation at minimum 3 raters | Done | `aggregate_athlete_ratings` returns None below threshold. |
| Readability enforcement in CI | Done | All coach templates at or under Grade 10. The readability test caught three templates at Grade 10.1-10.5 on first run and I rewrote them. |

## 3. Issues encountered and resolutions

### 3.1 Three coach templates landed just above Grade 10 (fixed)

The CI readability gate fired on three templates: `autonomy_support/high`, `structure/low`, `controlling/moderate`. All three read at 10.1-10.5. Pattern was the same in each: one long compound sentence with subordinate clauses. Resolved by splitting into short sentences and replacing the internal SDT term "autonomy-support" (which appears in athlete-surface discussion but is borderline for the coach surface) with "this." Grade 8-9 after rewrite. This is exactly what the readability CI test is for.

### 3.2 Item codes had to avoid collisions with core and existing layers (resolved by design)

Core items use AS/AF/BS/BF/CS/CF prefixes. Passion uses HP/OP. Regulatory uses AR/BR/CR. Coach circumplex needed five unique two-letter prefixes. CA, CS, CR would all collide. Used a three-letter scheme: CXA/CXS/CXR/CXC/CXH. The X marks it as circumplex. The third letter marks the facet. No collisions with any existing code.

### 3.3 `OptionalItemLayer` needed a `respondent` field (new subtype)

Passion and regulatory are both athlete-filled. Circumplex is dual-rater. The existing registration did not distinguish. Added `respondent: Literal["athlete", "coach_self_and_athletes"]`. This is forward-compatible: a future athlete-only layer looks like passion or regulatory; a future coach-only layer (rare) can introduce a `coach_self` variant.

### 3.4 Existing `test_optional_items.py` had a union assertion that broke with the new layer (fixed)

`test_all_optional_codes_is_union` compared `ALL_OPTIONAL_CODES` against the passion-plus-regulatory union. Adding the circumplex layer broke the assertion legitimately. Updated the test to include the circumplex set in the expected union.

### 3.5 Three defensive or edge-case lines were initially uncovered (fixed)

Coverage flagged three lines: the defensive "no values for code" branch in `aggregate_athlete_ratings`, the first-arg rater check in `compute_gaps`, and the `direction = "athlete_higher"` branch in gap classification. Added two tests (non-coach-self first arg, athletes-rate-coach-higher) and a `# pragma: no cover` with comment on the truly defensive branch. Module is now at 100% line and branch coverage.

### 3.6 Rendered narrative for lower-level facets was an open design question

Narratives at the "low" level for supportive facets and the "high" level for thwarting facets are the highest-stakes ones; they tell a coach something is wrong. I chose action-first framing (what to try this week) over diagnosis framing (what is wrong with you). This matches the Section 17.7 recommendation output standard and the stance we took on passion and regulatory narratives. SME review will confirm or adjust.

## 4. Open items

### 4.1 SME review of coach-facing templates

25 new coach-facing narrative strings (20 facet variants + 5 approach variants). All are coach-directed and contain behavioral advice. SME review is especially important here because the coach is the one acting on this language and the wrong phrasing can damage the coach-athlete relationship. Add to the existing SME packet (`docs/sme-review-packet-2026-04-20.md`) in a follow-up pass.

### 4.2 Integration into an assessment-delivery surface

The coach-circumplex scoring module is standalone. There is no `EnhancedCoachScorer` yet, and no product surface to administer the instrument to coaches. Coach-facing product work is a separate build from the athlete-side `EnhancedABCScorer` integration. Open item, not blocked.

### 4.3 Empirical calibration of facet thresholds and gap thresholds

The `COMPOSITE_SUPPORT_HIGH = 6.0`, `COMPOSITE_THWART_HIGH = 4.0`, `GAP_FLAG_THRESHOLD = 2.0` constants are theoretical priors. Phase A data (n >= 50 coaches, n >= 5 athletes per coach) will recalibrate against season-end outcomes (coach retention, athlete engagement, burnout). Same pattern as passion and regulatory thresholds.

### 4.4 Psychometric validation of the 24-item bank

Reliability (omega) per facet, factor structure (5-factor CFA versus 2-factor support/thwart model), measurement invariance across sport type and gender. Belongs in Phase A analytics. The ESEM machinery in `factor_models.py` already supports this; running it is a separate workstream.

### 4.5 Convergent validity against a licensed coaching-climate measure

TASQ, PCQ-S, or equivalent. Licensing dependent. Phase A optional.

### 4.6 Athlete aggregate does not yet weight by measurement count

`aggregate_athlete_ratings` computes a simple mean across athletes. Real teams have athletes with different tenure and different item-completion counts. Weighted aggregation (by response rate, by team-role, by season tenure) is a worthwhile enhancement but adds interpretation complexity. Open as a Phase A decision.

### 4.7 Gap analysis narratives not yet templated

The gap computation produces a `FacetGap` with direction and flag, but no gap-specific narrative. A coach who over-estimates their support on autonomy-support gets the "high" facet narrative; they do not yet see a narrative that names the gap. This is a genuine product gap (pun not intended). Add gap narratives in a follow-up pass: per facet x direction x flagged.

## 5. What went well

- The template pattern from 16.1 and 16.2 transferred cleanly. Banned-terms module, readability CI test, evidence-gate structure all reused with zero friction.
- The dual-rater design came out clean. Same items, rater as metadata, aggregation as a separate function. No fork of the scoring pipeline.
- Coverage stayed at 100% on the new module with two extra tests.
- The CI readability gate is paying for itself: it caught three drift templates on the first run, no SME had to. Same pattern as the `not_computed` passion coach template caught in the previous slice.
- Keeping the coach instrument separate from `EnhancedABCScorer` respects the Section 16.3 note that it monetizes independently.

## 6. What I would do differently

- Write the gap narratives in the same pass as the facet narratives. Leaving them for a follow-up introduces a feature gap where the system produces a useful signal but does not surface it.
- Start by drafting the lowest-risk facet ("identified" for regulatory, "high supportive" for circumplex) and then the highest-risk ("introjected", "low supportive"). I went in order of facet index and ended up revisiting the high-stakes templates twice.

## 7. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 590 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on coach_circumplex |
| Readability enforced on new templates | Done (Grade 10 ceiling held) |
| Banned-terms enforced on new templates | Done |
| Item-bank registration (three layers) | Done |
| SME review of 25 new coach templates | Open (extend SME packet) |
| Integration surface for administering to coaches | Open (separate product slice) |
| Empirical calibration of thresholds | Open (Phase A) |
| Gap-direction narratives | Open (follow-up pass) |
| Weighted athlete aggregation | Open (Phase A decision) |
