# Group-Conscious Layer (Section 16.5) Build Retrospective

Date: 2026-04-20
Scope: Section 16.5 of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

A group-conscious measurement layer for the ABC Assessment. Five new items capture perceived collective need satisfaction and team identification. A scoring module produces per-domain collective satisfaction, team identification, and an empathic-risk flag. A separate dispersion metric takes a list of team members' subscales and returns per-subscale standard deviations with risk bands.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/group-conscious-items-draft.md | 5 items: AG1/BG1/CG1 (collective satisfaction per domain), TI1/TI2 (team identification). Scoring model, empathic-risk rule, dispersion interpretation. | New |
| src/python_scoring/group_conscious.py | Per-domain collective satisfaction, team identification subscale, empathic-risk flagging, team-level dispersion computation | New |
| src/python_scoring/optional_items.py | Extended with `GROUP_CONSCIOUS_LAYER` | Modified |
| src/python_scoring/narrative_engine.py | `_COLLECTIVE_SATISFACTION_NARRATIVES` (3 domains x 4 levels x 2 audiences), `_TEAM_IDENTIFICATION_NARRATIVES` (4 levels x 2 audiences), `_EMPATHIC_RISK_NARRATIVES`, `_TEAM_DISPERSION_NARRATIVES` (coach only), four new methods on `NarrativeEngine` | Extended |
| tests/python_tests/test_group_conscious.py | 22 tests across scoring, levels, empathic risk, gates, validation, dispersion | New |
| tests/python_tests/test_group_conscious_narratives.py | 17 tests across structure, validation, banned terms, readability | New |
| tests/python_tests/test_optional_items.py | 4 new assertions for the group-conscious layer registration | Modified |

### Test result

```
633 passed, 4 xfailed in 11.29s
```

43 new tests this slice. No regressions across the 590 tests pre-16.5.

Coverage on the new module: 100% line, 100% branch.

## 2. Completeness map against the plan

| Section 16.5 deliverable | Status | Notes |
|---|---|---|
| Three items for perceived collective need satisfaction, one per domain | Done | AG1/BG1/CG1, one per domain, behavioral-frequency framing consistent with core. |
| Two items for team identification | Done | TI1 (affective), TI2 (cognitive). |
| Empathic-risk flag (high TI + low collective satisfaction) | Done | Per-domain; fires independently on Ambition, Belonging, Craft. |
| Dispersion metric across team members | Done | `compute_team_dispersion` returns per-subscale SDs and high-dispersion flags. Minimum 3 athletes; below that, not computed. |
| Three bands for dispersion (tight, moderate, high) | Done | 1.5 and 2.5 thresholds on the 0-10 scale. |
| Narratives for collective satisfaction, team identification, empathic risk, dispersion | Done | All plain-language, banned-term enforced, readability enforced. Dispersion is coach-only. |
| Evidence gates per Section 17.5 | Done | Per-item for collective satisfaction; per-subscale for team identification; cross-gate for empathic risk. |

## 3. Issues encountered and resolutions

### 3.1 Two coach templates landed above Grade 10 on first pass (fixed)

The readability CI caught `ti/moderate/coach` at 10.2 and `ti/not_computed/coach` at 15.8. Both featured compound noun constructions ("high-identification athlete") and formal clinical terms ("insufficient data... team identification"). Rewrote as plain-language alternatives. Both now pass.

### 3.2 Missing coverage on the dispersion moderate band (fixed)

Coverage flagged line 153 of `group_conscious.py`, the "moderate" branch of `_dispersion_band`. I tested "tight" (identical athletes) and "high" (polarized team) but had no test for the middle range. Added `test_moderate_dispersion_band` with three athletes at 3.0/5.0/7.0 on a_sat, producing a stdev of 2.0, cleanly landing in the moderate band. Coverage is now 100% on both line and branch.

### 3.3 Test lines exceeded 100-character ruff limit (fixed)

My initial dispersion tests inlined full subscale dicts on single lines, which went over the line-length limit. Extracted a `_flat_athlete(value)` helper and used it throughout. Cleaner and shorter.

### 3.4 Single-item reliability concern for collective satisfaction (documented open)

Each domain's collective satisfaction is measured by a single item (AG1, BG1, CG1). Single-item reliability is structurally bounded. Phase A omega will determine whether expansion to two items per domain is needed before we can trust the construct. Flagged as an explicit open item in the items draft.

### 3.5 Dispersion metric is a team-level primitive, not yet consumed by downstream (deferred)

`compute_team_dispersion` is a standalone function. It does not yet flow into `EnhancedABCScorer`, coach dashboards, or any team-level view. Integrating team-level computation into the existing per-athlete scoring path is a different shape of work and is captured as an open item.

## 4. Open items

### 4.1 SME review of 27 new narrative strings

Collective satisfaction: 3 domains x 4 levels x 2 audiences = 24.
Team identification: 4 levels x 2 audiences = 8 (already in the total above once we add).
Wait, that is 3 x 4 x 2 = 24 for collective, 4 x 2 = 8 for TI, 2 for empathic risk, 3 for dispersion. Total: 37 new strings.

All require SME sign-off before production use. The existing SME packet (`docs/sme-review-packet-2026-04-20.md`) needs to be extended to cover this layer plus the coach circumplex templates from 16.3.

### 4.2 Integration of team-level dispersion into a coach surface

The dispersion metric is callable but nothing consumes it. A team-level coach dashboard needs to call `compute_team_dispersion` on the roster and surface `_TEAM_DISPERSION_NARRATIVES`. Separate product slice; not a measurement gap.

### 4.3 Integration of individual group-conscious scoring into EnhancedABCScorer

Same pattern as passion and regulatory layers: add `group_conscious_responses` as an optional kwarg to `EnhancedABCScorer.score()`, run `score_group_conscious`, attach the profile to the result dict, call the narratives. Small follow-up.

### 4.4 Single-item reliability of collective satisfaction

Phase A data determines whether one item per domain is enough. If omega is weak, expand AG/BG/CG to two items each. Do not pre-expand; let data decide.

### 4.5 Multilevel analysis at Phase A

Chapter 53's empirical claim: perceived collective satisfaction predicts individual burnout trajectory independently of personal satisfaction. Testing that claim requires the multilevel-modeling infrastructure in `src/psychometric/` already in place. Belongs in Phase A analytics.

### 4.6 Empirical calibration of empathic-risk thresholds

The `EMPATHIC_RISK_TI_MIN = 6.0` and `EMPATHIC_RISK_COLLECTIVE_MAX = 4.0` constants are theoretical priors. Phase A recalibration needed against coach-rated empathic-distress outcomes.

### 4.7 Empirical calibration of dispersion bands

`DISPERSION_TIGHT = 1.5` and `DISPERSION_HIGH = 2.5` are also theoretical. Phase A team-level data will inform whether these cutpoints predict team-level outcomes (roster turnover, team burnout).

### 4.8 Weighted versus equal-weight dispersion

Current dispersion is the unweighted standard deviation across athletes. A senior athlete's experience of the team is often more diagnostic than a newcomer's. Weighted aggregation (by tenure, role, or attendance) is a Phase A refinement.

## 5. What went well

- Pattern transfer is now almost frictionless. The passion/regulatory/circumplex template made this slice fast: same shape of scoring module, same narrative infrastructure, same test structure.
- The CI readability gate caught two templates before they could ship. The pattern is: write the first draft, run the test, tighten the two or three that push above the threshold. Cheap iteration.
- The dispersion metric is a clean primitive that composes well with future team views. It does not assume anything about how it will be consumed.
- Keeping collective satisfaction per-domain rather than as a single composite preserves the information downstream analysis will need. A team that perceives collective Belonging as low but collective Ambition as high is a different team than one with the reverse.

## 6. What I would do differently

- Draft the per-band narrative tests alongside the initial narrative templates, not after. Missing the "moderate" dispersion band was a five-line test fix but indicated my initial test matrix was not complete.
- The empathic-risk narrative is generic (not per-domain). Phase-A data may show that empathic distress on Belonging is materially different from empathic distress on Ambition, and we will want per-domain variants. Worth a conversation with the SME before Phase A, not after.

## 7. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 633 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on group_conscious |
| Readability enforced on new templates | Done (Grade 10 ceiling held after two fixes) |
| Banned-terms enforced on new templates | Done |
| Item-bank registration (four layers) | Done |
| SME review of 37 new templates | Open (extend SME packet) |
| Integration into EnhancedABCScorer | Open (small follow-up) |
| Integration into a coach team-view surface | Open (separate product slice) |
| Empirical calibration of empathic-risk and dispersion thresholds | Open (Phase A) |
| Single-item reliability of collective satisfaction | Open (Phase A decision: expand or keep) |
| Weighted dispersion | Open (Phase A refinement) |
| Multilevel validation of Chapter 53's central claim | Open (Phase A analytics) |

Seven open items remain; six are blocked on external inputs (SME or Phase A) and one is a small engineering follow-up (integration into the scorer).
