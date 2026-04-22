# Self-Concordance Trajectory Engine Build Retrospective

Date: 2026-04-21
Scope: Trajectory engine for the Section 16.7 self-concordance layer
Author: Pair-programmed with Claude.

## 1. What shipped

A per-goal trajectory engine for self-concordance scores. Takes a chronologically ordered series of `(goal_id, cycle_index, profile)` points across one or more goals, groups by goal, computes slope, magnitude, and within-series standard deviation per goal, and labels each goal's trajectory as one of five outcomes: becoming_more_autonomous, becoming_more_controlled, stable, oscillating, or insufficient_data. Plain-language coach- and athlete-facing narratives for each label.

This closes the highest-value open item from the per-cycle self-concordance retrospective. Sheldon's central empirical claim is that the *trajectory* of self-concordance predicts attainment-plus-well-being more strongly than any single cycle's level. Per-cycle scoring without trajectory captured only half the construct's value.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| src/python_scoring/self_concordance_trajectory.py | OLS slope, magnitude, within-series SD, five-band classifier; per-goal grouping for multi-goal input | New |
| src/python_scoring/narrative_engine.py | `_SELF_CONCORDANCE_TRAJECTORY_NARRATIVES` (5 labels x 2 audiences = 10), `generate_self_concordance_trajectory_narrative` method, `VALID_TRAJECTORY_LABELS` constant | Extended |
| tests/python_tests/test_self_concordance_trajectory.py | 19 tests across slope direction, oscillation, insufficient data, multi-goal grouping, not_computed filtering, edge cases | New |
| tests/python_tests/test_self_concordance_trajectory_narratives.py | 6 tests across structure, validation, banned terms, readability | New |

### Test result

```
732 passed, 4 xfailed in 11.22s
```

25 new tests this slice. No regressions across the 707 tests pre-trajectory.

Coverage: 100% line and branch on `self_concordance_trajectory.py`.

## 2. Design choices

### 2.1 Goal continuity is the caller's responsibility

The hardest design question for any per-goal trajectory engine is "is this the same goal as last time?" Three options exist:

- Free-text matching: athlete writes goal text each cycle, we string-match. Fragile.
- Athlete-declared continuity: an explicit "same goal as last time" flag. Reliable but requires UI.
- Caller-supplied goal IDs: the product or test caller assigns IDs and groups by them.

I chose the third option. The trajectory engine accepts `goal_id: str` per point and groups blindly. The caller (product or test) handles the goal-identity question. This keeps the math layer focused and pushes the product question downstream where it belongs.

### 2.2 Filter `not_computed` profiles before computing

Points whose underlying `SelfConcordanceProfile` failed the display gate are filtered out before slope, magnitude, or SD are computed. The reasoning: a missing-data cycle is not the same as a real measurement at zero. The trajectory reflects movement on the cycles where we have a reading. The filtered count surfaces in `n_points_total` vs `n_points_computable` for transparency.

### 2.3 Five labels, not three

I considered a simpler three-label scheme (rising / falling / stable). The actual instrument benefits from two more:

- **Oscillating** is its own pattern. A goal whose self-concordance swings from autonomous to controlled and back is contested. That is a clinically meaningful signal that a flat slope alone hides. The narrative for oscillating directs the coach to ask what differs between cycles.
- **Insufficient_data** is honest about when fewer than three computable points are available. Showing a coach a slope inferred from two points is statistical theater.

### 2.4 Magnitude threshold separate from slope tolerance

A trajectory needs both directional sign (slope) and meaningful net change (magnitude) to fire a directional label. The instrument uses two thresholds: slope tolerance of 0.5 points per cycle (anything smaller is flat) and magnitude threshold of 1.0 points (anything smaller is too small to call directional). A goal where slope is positive but the net change is under 1.0 falls back to stable, not becoming_more_autonomous. This guards against the false-positive "trend" calls that a slope-only rule would produce on noisy series.

## 3. Issues encountered and resolutions

### 3.1 Banned-term hit on first run (fixed)

The `insufficient_data` coach narrative used "self-concordance" as a label inside the prose. The banned-terms test caught it on first run. Rewrote to refer to "check-ins on the same goal" without the technical label. The fix took 30 seconds because the CI gate exists.

### 3.2 Two defensive branches uncovered (fixed)

Coverage flagged two lines: the `den == 0` zero-x-variance branch in `_ols_slope`, and the fallback `return "stable", "flat"` in `_classify_label`. The first fires only when all points share the same `cycle_index` (caller error or malformed input). The second fires when slope and magnitude disagree in sign on a noisy multi-point series.

I added two tests:

- `test_zero_x_variance_returns_zero_slope`: passes three points all at `cycle_index=0`, asserts the slope is 0.0 and the trajectory classifies as stable.
- `test_inconsistent_slope_and_magnitude_falls_back_to_stable`: constructs a five-point series `[1, 10, 9, 3, 2]` where magnitude is +1.0 but the OLS slope is -0.5. The classifier correctly falls back to stable rather than firing a directional label.

The second test surfaced a small product-design insight: the rule "directional sign must agree between slope and magnitude" is what prevents false-positive trend calls on noisy series. Documented in Section 2.4.

### 3.3 Pattern transfer continued to hold

This was another clean first-run slice (modulo the two coverage cleanups). No readability drift, no architecture friction, no integration breakage. The retrospective pattern is mature.

## 4. Open items

### 4.1 Trajectory tracker as stateful wrapper

The trajectory engine is a pure function over a supplied list of points. A natural follow-up is a `GoalTrajectoryTracker` class that accumulates points across `EnhancedABCScorer.score()` calls and exposes the current trajectory per goal. This is the same shape as the existing `TransitionTracker`. Not built in this slice; reasonable next pass.

### 4.2 SME review of 10 new trajectory templates

Add to the existing SME packet in a follow-up.

### 4.3 Empirical calibration of trajectory thresholds

`MIN_POINTS_FOR_TRAJECTORY = 3`, `FLAT_SLOPE_TOLERANCE = 0.5`, `OSCILLATION_SD_THRESHOLD = 2.5`, `DIRECTIONAL_MAGNITUDE_THRESHOLD = 1.0` are theoretical priors. Phase A data with goal-attainment outcomes will recalibrate.

### 4.4 Generalization to other layers

The trajectory engine design is goal-specific (one stream per `goal_id`) but the underlying primitive (OLS slope plus magnitude plus SD plus five-band classifier) generalizes to any longitudinal score. Regulatory style and passion quality could plug into a parametrized version. Not in scope for this slice.

### 4.5 Goal-trajectory integration into `EnhancedABCScorer`

The scorer accepts per-cycle self-concordance responses but does not yet retain a history. Hooking the tracker into the scorer (so a multi-cycle athlete sees their trajectory automatically) is the same shape of change as the TransitionTracker integration. Belongs in the tracker slice (4.1).

## 5. What went well

- The CI banned-term gate caught the one drift on first run. The fix was instant. This remains the highest-leverage piece of Section 17 infrastructure.
- The two coverage gaps led to product-relevant tests, not test-for-coverage's-sake. The fallback-to-stable rule is documented because the test surfaced it.
- Goal-ID-as-caller-input is the cleanest separation of concerns. The math layer does not have to care how product identifies a goal.
- Pure-function design (no state, no I/O) makes the engine trivially testable and parametrically reusable.

## 6. What I would do differently

- Build the stateful tracker in the same slice. It is a natural pair with the pure function and would close the integration loop in one pass instead of leaving it as an open item.
- Generalize the slope-plus-magnitude-plus-SD primitive across layers from the outset. The next time a layer wants longitudinal scoring (regulatory style is the obvious candidate), we will end up duplicating this logic if we do not extract it.

## 7. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 732 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on self_concordance_trajectory |
| Readability enforced on new templates | Done |
| Banned-terms enforced on new templates | Done (caught one drift on first run) |
| SME review of 10 new templates | Open (extend packet) |
| Stateful tracker for cross-cycle accumulation | Open (next slice candidate) |
| Integration into EnhancedABCScorer history | Open (depends on tracker) |
| Empirical calibration of trajectory thresholds | Open (Phase A) |
| Generalization across layers | Open (architectural follow-up) |

Five open items: one engineering follow-up (tracker + integration), one packet hygiene item, one architectural extraction, two Phase-A calibration items.
