# Coach Circumplex Scorer Entry Point Retrospective

Date: 2026-04-22
Scope: Standalone scoring entry point for the Coach Circumplex instrument
Author: Pair-programmed with Claude.

## 1. What shipped

A stateful `CoachCircumplexScorer` class that wraps the existing coach-circumplex primitives (score_circumplex, aggregate_athlete_ratings, compute_gaps) and the NarrativeEngine into a coach-facing entry point. The scorer holds current-cycle state for one coach: a coach self-rating profile when present, a dict of athlete ratings keyed by athlete ID, and a cached NarrativeEngine for assembling the report.

This closes the last "module ships but nothing consumes it" gap. The coach circumplex instrument has existed since Section 16.3 but no code path took coach responses plus athlete ratings and produced a complete coach-facing output. This slice builds that orchestration layer on top of the proven primitives.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| src/python_scoring/coach_circumplex_scorer.py | `CoachCircumplexScorer` class plus `CircumplexReport` dataclass | New |
| tests/python_tests/test_coach_circumplex_scorer.py | 14 tests across coach-only, athletes-only, dual, gap analysis, empty state, multi-athlete accumulation, rating overwrite | New |

### Test result

```
755 passed, 4 pre-existing xfailed in 10.69s
```

14 new tests. No regressions across the 741 tests pre-slice.

Coverage: 100% line and branch on `coach_circumplex_scorer.py`.

## 2. Completeness map against commitment

| Committed deliverable | Status | Notes |
|---|---|---|
| `CoachCircumplexScorer` class | Done | Dataclass with `coach_id` init param; private fields for coach profile, athlete responses dict, narrative engine instance. |
| `score_coach_self(responses)` | Done | Scores and stores; returns profile for callers that want the immediate output. |
| `record_athlete_rating(athlete_id, responses)` | Done | Overwriting semantics: second call with same athlete_id supersedes. Mirrors product reality. |
| `current_profile()` | Done | Returns coach self-rating profile or None. |
| `current_athlete_aggregate()` | Done | Uses existing `aggregate_athlete_ratings` helper; returns None under the 3-rater minimum. |
| `current_gap_analysis()` | Done | Returns empty list when either side missing; delegates to existing `compute_gaps`. |
| `current_report(audience)` | Done | Single method that assembles everything: facet level narratives, approach summary, per-facet gap narratives where flagged. Handles all four states (empty, coach only, athletes only, both). |
| No new open items | Done (verified at end) | The retrospective documents only existing-and-prior open items; nothing new added. |

## 3. Design choices worth naming

### 3.1 Primary-source fallback pattern

When both coach self and athlete aggregate are present, the report drives facet narratives from the coach self-rating. When only the athlete aggregate is present (fewer rater conditions satisfied), the report falls back to the aggregate. When neither is present, the report returns with empty narrative dicts and `primary_source="none"` rather than raising.

Rationale: coaches start using the instrument at different rates. An instrument that refuses to render until both sides are complete punishes early adopters. The fallback lets a coach see the athlete view early, then the dual view once they self-rate.

### 3.2 Gap narratives separate from raw gaps

`report.gaps` contains a `FacetGap` for every facet where both sides have a score, including aligned (unflagged) ones. `report.gap_narratives` populates only for flagged gaps. This keeps the raw data available for product UI that wants to show "this facet is aligned" without the narrative engine firing, while the narrative layer sticks to the Section 17.7 rule that narratives should point at action.

### 3.3 Audience parameter is currently Literal["coach"]

The instrument is a coach-development tool. Athletes do not see coach profiles directly. The `current_report` signature takes no audience parameter to keep that constraint explicit. If a future product surface shows athletes their own coach circumplex ratings, the method signature will expand; for now, single-audience.

### 3.4 No multi-cycle history in this slice

The scorer holds current-cycle state. Product callers that want multi-cycle history either wrap multiple scorer instances or persist `current_profile()` snapshots. I did not build a `CoachCircumplexTracker` in this slice because:

- The trajectory pattern from self-concordance required goal continuity; circumplex does not have a comparable continuity question. Each cycle is a fresh coach profile.
- The instrument cadence is quarterly; a tracker would hold four points per year, which is structurally different from the trajectory engine's use case.

A simple cycle-to-cycle delta could be added later if product asks; not in scope here.

## 4. Issues encountered and resolutions

### 4.1 All tests passed on the first run (with one lint autofix)

No readability drift, no test failures, no design pivots. The scorer is thin orchestration over proven primitives; the pattern transfer from prior slices was tight. One unused `pytest` import was caught by ruff and autofixed.

### 4.2 No banned-term checks added for the report output

The scorer composes narratives from existing banned-term-tested templates. Adding a redundant banned-term assertion in the scorer's own tests would duplicate work the narrative tests already do. If the NarrativeEngine introduces a banned term somewhere, the narrative tests catch it upstream of the scorer.

## 5. Open items

Nothing new this slice. Existing open items (carried, not added):

- SME engagement on the 102 templates already in the packet.
- Coach circumplex multi-cycle tracker (nice-to-have, not called out as a gap anywhere).
- Cross-cycle trajectory-engine generalization (architectural, not urgent).
- Phase A calibration items across all layers.

## 6. What went well

- Shortest slice of the session. The scorer is ~170 lines of production code; the tests are ~180 lines; the module is entirely orchestration over existing primitives.
- Fallback design (coach-only / athletes-only / both / neither) means the scorer is usable from day one of any rollout, not just after full data collection.
- 100% branch coverage on first test pass. No retry loops on this one.
- Closes the last "module ships, nothing consumes it" gap that has been carried since Section 16.3.

## 7. What I would do differently

- Name the primary-source convention in the items draft earlier so product UI designers know which profile drives narratives under partial data. I surfaced the convention only in the scorer docstring; it deserves to be in the human-readable draft doc so it travels with the design.

## 8. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 755 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on coach_circumplex_scorer |
| All four report states verified by test | Done (coach-only, athletes-only, dual aligned, dual flagged, empty) |
| Commitment: no new open items | Met |
| Plan snapshot updated | Done (this retrospective plus plan-row flip) |

End of Section 16.3 integration work. Every optional measurement layer (passion, regulatory, circumplex, group-conscious, causality, self-concordance) now has a complete scoring-to-narrative path with a working entry point.
