# Causality Orientations (Section 16.6) Build Retrospective

Date: 2026-04-20
Scope: Section 16.6 of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

A trait-level Causality Orientations layer. Twelve items across three subscales (autonomy, controlled, impersonal), scored once at onboarding and re-administered annually. A scoring module produces per-subscale 0-10 scores, a dominant-orientation classification (including mixed and emergent fallbacks), and two-tier evidence gates. Narratives at the orientation level for both athlete and coach audiences.

This is the fifth optional layer on the ABC Assessment. After this slice, the instrument operationalizes BPNT (core), OIT (regulatory style), DMP (passion), COT (causality orientations), plus the group-conscious and coach-circumplex extensions. That is the full SDT mini-theory coverage the plan called for.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/causality-orientations-items-draft.md | 12 items (AO1-AO4, CO1-CO4, IO1-IO4), monthly stem, annual cadence, scoring model, calibration open items | New |
| src/python_scoring/causality_orientations.py | Three subscale scores, dominant-orientation classifier with margin rule, two-tier gates | New |
| src/python_scoring/optional_items.py | Extended with `CAUSALITY_ORIENTATIONS_LAYER` and a new `"annual"` cadence value on `OptionalCadence` | Modified |
| src/python_scoring/narrative_engine.py | `_CAUSALITY_NARRATIVES` (6 entries x 2 audiences = 12), `generate_causality_narrative` method, `VALID_CAUSALITY_ORIENTATIONS` constant | Extended |
| tests/python_tests/test_causality_orientations.py | 20 tests: scoring, dominant classification, margin rule, gates, validation, structure | New |
| tests/python_tests/test_causality_narratives.py | 6 tests: structure, validation, banned terms, readability | New |
| tests/python_tests/test_optional_items.py | 4 new assertions for the layer | Modified |

### Test result

```
671 passed, 4 xfailed in 9.86s
```

29 new tests this slice. No regressions across the 642 tests pre-16.6.

Coverage: 100% line and branch on `causality_orientations.py`.

## 2. Completeness map against the plan

| Section 16.6 deliverable | Status | Notes |
|---|---|---|
| Brief causality-orientation screen, 15-20 items | Done at smaller scale | Shipped as 12 items (4 per subscale) for assessment burden. Phase A reliability will determine whether expansion is needed. |
| Three orientation scores per athlete | Done | Autonomy, controlled, impersonal on 0-10 scales. |
| Administered at onboarding and annually | Done | New `"annual"` cadence on `OptionalCadence`. |
| Dominant-orientation classification | Done | Margin rule: top score >= 6.0 AND (top - second) >= 1.5. Falls back to mixed or emergent. |
| Stratify trajectory interpretation by orientation | Deferred | Explicitly flagged as Phase A calibration open item in the items draft and in the retrospective. Current slice ships measurement; downstream stratification follows data. |
| Personalize coach intervention recommendations by orientation | Deferred | Same reason. Orientation-level coach narratives ship now; per-other-signal stratification awaits Phase A. |

## 3. Issues encountered and resolutions

### 3.1 Three coach templates landed above Grade 10 (fixed)

Readability CI caught the `controlled/coach`, `impersonal/coach`, and `mixed/coach` templates at Grade 11.2-11.4. All three had multi-clause sentences with compound adjectives and lists. Rewrote each into shorter sentences with plainer verbs. All now under Grade 10.

### 3.2 Dominant-classification logic had redundant branches (fixed)

First draft of `_classify_dominant` had five conditional branches to separate "emergent," "mixed," and the three dominant cases. Three of those branches were dead code once the math settled: any top score at or above `MIXED_FLOOR` that does not pass the dominant-margin rule is mixed by definition. Coverage flagged the redundant branches. Simplified to a three-branch structure: emergent (all below ceiling), dominant (top above threshold with margin), mixed (everything else).

### 3.3 Test line lengths exceeded ruff limit (fixed)

Several test inputs inlined the `_orientation_skewed` helper with three kwargs on a single line, pushing over 100 characters. Reformatted to use line continuations inside parentheses. `ruff --fix` did not catch them automatically; manual wrap.

### 3.4 Extension of `OptionalCadence` literal

Added `"annual"` to the `OptionalCadence` type. Existing consumers (passion is quarterly, regulatory is biweekly, circumplex is quarterly, group-conscious is biweekly) are unaffected. Future annual layers can reuse the cadence value.

### 3.5 Stratification integration is the biggest deferred piece

The plan's steps 2 and 3 for Section 16.6 describe orientation as a modifier on how other signals are interpreted. That integration is genuinely bigger than the measurement slice: it requires conditional template selection in every existing narrative layer based on orientation, or a central stratifier that annotates outputs with orientation-dependent recommendations. I chose to ship the measurement cleanly and flag the integration as Phase A calibration rather than guess at the stratification rules before we have data.

## 4. Open items

### 4.1 SME review of 12 new narrative strings

Six orientation entries across two audiences. Add to the existing SME review packet (`docs/sme-review-packet-2026-04-20.md`) in a follow-up pass. Particular attention to the `controlled` and `impersonal` coach narratives, which carry the highest-stakes coaching advice.

### 4.2 Stratification of existing constructs by orientation

The deferred integration from Section 16.6 steps 2 and 3. Holds until Phase A data validates which stratification rules predict outcomes. Candidate rules:

- Regulatory erosion detection weights more heavily for controlled-oriented athletes.
- Passion-obsessive interpretation differs by orientation (an autonomy-oriented athlete's obsession has different developmental implications than a controlled-oriented one).
- Coach intervention recommendations differ: autonomy-oriented athletes tolerate coaching-style variation; controlled-oriented need structured autonomy-support; impersonal-oriented need structural clarity first.

### 4.3 Integration into EnhancedABCScorer

Not done in this slice. Add `causality_responses` as an optional kwarg to `score()` in a follow-up, attach profile to result dict, call orientation narrative. Annual cadence means the profile would typically be cached and reused across many scoring calls, unlike the biweekly layers. Adds a design question: should the scorer accept the most recent profile as an input rather than re-scoring items every call?

### 4.4 Convergent validity against GCOS or equivalent

Phase A can administer GCOS (licensing permitting) alongside our short form to a subset. Target: r >= 0.60 with the full GCOS on each orientation subscale.

### 4.5 Test-retest stability at annual interval

Causality orientations should show substantial stability across a year (r >= 0.70). If Phase A retest data shows lower stability, either the instrument needs refinement or the theoretical assumption about annual stability does not hold for athlete populations under developmental stress.

### 4.6 Margin-rule calibration

The 1.5-point margin for dominance is a theoretical prior. Phase A can calibrate it against outcome measures: what margin best predicts differences in response to autonomy-supportive coaching?

### 4.7 Emergent-orientation interpretation

The `emergent` case (all three subscales below 4.0) is rare and potentially meaningful in itself: it may indicate an athlete who does not read situations along the autonomy-controlled-impersonal axis in a typical way. Phase A data will show how often this fires and whether it predicts anything.

## 5. What went well

- Pattern transfer was fast. Passion/regulatory/circumplex/group-conscious set a strong template; this slice felt like filling in a well-known shape.
- The readability CI caught three coach-facing drift templates on the first run, exactly as it did in 16.2, 16.3, and 16.5. The pattern holds: coach narratives drift toward academic sentence structure unless the gate enforces otherwise.
- Classification simplification. Coverage flagged dead branches in the first-draft logic; removing them made the classifier both shorter and easier to reason about.
- `annual` cadence addition was two-line change that composed cleanly with the existing optional-items registry.

## 6. What I would do differently

- Write the classification logic as a decision table first, not as sequential `if` statements. Would have surfaced the redundant branches immediately.
- The items draft Section 4 specifies the margin rule in English; the scoring module implements it; the test file asserts it. Three copies of the same semantic rule with slight variation in wording. A single constants-with-comments block at the top of the module plus references from the draft would be cleaner.

## 7. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | 671 passed, 4 xfailed, 0 failed |
| New-module line and branch coverage | 100% on causality_orientations |
| Readability enforced on new templates | Done (Grade 8 athlete / Grade 10 coach, held after three fixes) |
| Banned-terms enforced on new templates | Done |
| Optional item registry updated | Done (fifth layer; new `annual` cadence value) |
| SME review of 12 new templates | Open (extend packet) |
| Integration into EnhancedABCScorer | Open (small follow-up) |
| Stratification of other signals by orientation | Deferred to Phase A calibration |
| Convergent validity against GCOS | Open (Phase A) |
| Test-retest stability at annual interval | Open (Phase A) |
| Margin-rule empirical calibration | Open (Phase A) |

Six open items: one engineering follow-up (SME packet extension) that can happen anytime, one integration (EnhancedABCScorer kwarg), and four Phase-A-calibration items that require real data.
