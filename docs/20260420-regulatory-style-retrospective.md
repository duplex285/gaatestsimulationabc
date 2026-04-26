# Regulatory-Style Layer: Build Retrospective

Date: 2026-04-20
Scope: Section 16.1 of improvement-plan-personalization-engine.md
Author: Pair-programmed with Claude.

## 1. What shipped

An Organismic Integration Theory regulatory-style layer for the ABC Assessment. The slice adds six items, a scoring module, a regulation-erosion detector, plain-language narratives for four styles across three domains, a shared banned-terms module that the passion tests now depend on, and a test suite with 53 new tests at 100% module coverage.

### Artifacts

| Path | Purpose | Status |
|------|---------|--------|
| docs/regulatory-style-items-draft.md | 6-item draft (AR1/AR2, BR1/BR2, CR1/CR2), scoring model, evidence gates, erosion signal, calibration open items | New |
| src/python_scoring/banned_terms.py | Authoritative Section 17.3 banned-term list with `contains_banned_term` helper | New |
| src/python_scoring/regulatory_style.py | Per-domain autonomous/controlled subscales, RAI, four-way style classification, two-tier evidence gates | New |
| src/python_scoring/regulation_erosion.py | Leading-indicator detector: sustained downward style movement across two or more measurements | New |
| src/python_scoring/narrative_engine.py | `_REGULATORY_NARRATIVES`, `_EROSION_NARRATIVES`, `_DOMAIN_PLAIN`, two new methods on `NarrativeEngine` | Extended |
| tests/python_tests/test_banned_terms.py | Direct tests of the shared banned-terms module | New |
| tests/python_tests/test_regulatory_style.py | 18 tests across scoring, classification, gates, validation, structure | New |
| tests/python_tests/test_regulation_erosion.py | 13 tests across baselines, two- and three-profile series, multi-domain isolation, not-computed handling | New |
| tests/python_tests/test_regulatory_narratives.py | 12 tests across structure, validation, banned-term enforcement on raw and rendered templates | New |
| tests/python_tests/test_passion_narratives.py | Refactored to import from the new banned_terms module | Modified |

### Test result

```
506 passed, 4 xfailed in 5.72s
```

53 new tests. No regressions across the 453 pre-existing tests (452 passed + 1 new test from the prior review pass).

Coverage on the new modules:

```
banned_terms.py          100%
regulation_erosion.py    100%
regulatory_style.py      100%
```

## 2. Completeness map against the plan

| Section 16.1 deliverable | Status | Notes |
|---|---|---|
| Six items (two per domain) distinguishing autonomous from controlled regulation | Done | Original wording, no licensed-scale content. |
| Per-domain Relative Autonomy Index (RAI) | Done | Signed, range -10 to +10. |
| Module: src/python_scoring/regulatory_style.py | Done | Produces per-domain `DomainRegulation` plus a `RegulatoryProfile` wrapper. |
| Translation-table entries and narratives for each style | Done | Four styles × three domains × two audiences = 24 athlete/coach rendered variants, plus a `not_computed` pair per domain. |
| New leading-indicator signal: regulation erosion | Done as standalone detector | Integration into `TransitionTracker` is a follow-up open item; the detector is standalone-callable. |
| Tests mirroring the passion pattern, with banned-term enforcement | Done | Plus a direct test for the banned-terms helper. |
| Retrospective | Done | This document. |

## 3. Issues encountered and resolutions

### 3.1 Raw response of 4 sits exactly at the elevated threshold

On the 1-7 scale, a raw response of 4 normalizes to 5.0 on the 0-10 scale. My first draft test expected a 4/4 response to produce an `amotivated` style (both subscales below threshold). It produced `conflicted` instead, because `>= 5.0` evaluates true at 5.0 exactly. The behavior is correct per the spec, but the test needed fixing. Resolved by using a raw response of 3, which produces 3.33 and is unambiguously below threshold. The boundary behavior is also now explicitly exercised in `test_boundary_score_fails_recommendation_gate`.

### 3.2 Two items per domain is a tight reliability budget

OIT's full five-point regulation continuum (amotivation, external, introjected, identified, integrated) typically needs four to six items per domain to separate reliably. We ship two per domain by choice, trading granularity for assessment burden. The scoring module reflects this by collapsing to a four-way classification (identified, conflicted, introjected, amotivated) rather than the full continuum. The draft doc flags expansion to four items per domain as a Phase A decision contingent on the n>=100 omega result. Called out in open items so Phase A is primed to make the call.

### 3.3 Coverage on the banned-terms positive-match branch

The narrative tests only exercise the negative case (no banned term). The positive-match `return True, term` line stayed uncovered. Added `test_banned_terms.py` with direct positive-match assertions including case insensitivity, word boundaries, and multi-word terms. All three new modules are now at 100% line coverage.

### 3.4 Keeping the test import symbol clean

Moving the banned-term check out of `test_passion_narratives.py` and into the shared module meant renaming the function from the test-local `_contains_banned_term` to the public `contains_banned_term`. A single replace_all handled it, but worth noting that any future test file that copies the old pattern will need the same rename.

## 4. Open items

### 4.1 Integration with `TransitionTracker`

`detect_regulation_erosion` is a standalone helper. The existing `TransitionTracker` in `transition_engine.py` owns archetype transitions. Integration adds a new `TransitionType` (or parallel tracker method) so regulatory-shift events land in the same audit stream the rest of the trajectory engine produces. Deferred because `TransitionTracker` has its own confidence-threshold and windowing logic that I did not want to reshape under the 16.1 scope.

### 4.2 Integration into `EnhancedABCScorer.score()`

Same status as passion. The scoring module is standalone and not yet called from the main pipeline. Integration needs three product-side decisions:

- Whether regulatory items join the core biweekly flow (same submission) or a separate tab.
- Where in the pipeline regulatory scoring runs (before or after base-rate adjustment; before or after the narrative engine call).
- How erosion events compose with frustration signatures and archetype transitions in the coach-facing surface.

### 4.3 Readability enforcement in CI

Still open. Section 17.2 target is Grade 8 for athlete-facing and Grade 10 for coach-facing. `textstat` is not a project dependency. Manual read of the four rendered style narratives: all three domain variants of `identified` and `amotivated` are short, concrete, Grade 7-ish. `conflicted` and `introjected` coach variants push toward Grade 9-10 with words like "fragile" and "ownership," still within coach-facing target. The erosion coach narrative mentions "values-based" and "pressure-based" compound adjectives that increase complexity; within target but a readability pass would confirm.

### 4.4 Empirical calibration of the four-way classification

Threshold 5.0 and ambiguous margin 1.0 are theoretical priors. Phase A data will calibrate:

- Empirical cutpoints against coach-rated motivation quality.
- Whether four styles is the right granularity or whether the data supports five (splitting `identified` from a higher-autonomy `integrated`, or `introjected` from a purer `external`).
- Subscale omega at n>=100 determines whether item expansion to four per domain is needed.

### 4.5 RAI rank encoding assumes amotivated sits below introjected

The erosion detector ranks `identified > conflicted > introjected > amotivated`. This places amotivation below controlled regulation, reflecting an autonomy ordering (more autonomy = higher rank). Some clinical readings place amotivation at the pathology extreme, below controlled. For our use case (leading indicator of burnout), the current ordering is defensible: a shift from introjected to amotivated is also a concerning erosion, and the current ranking fires that event. Worth confirming with SME review.

### 4.6 Item-bank registration

Neither passion items (HP/OP) nor regulatory items (AR/BR/CR) appear in `REQUIRED_ITEMS`, `item_bank.py`, or `config/irt_parameters.yaml`. They are currently hardcoded in their respective scoring modules. When an assessment-delivery system or IRT calibration touches them, they need to be registered formally. Open item across both layers.

### 4.7 SME review of templates

Twenty-four rendered regulatory-style narrative variants plus six erosion narrative variants are unreviewed. Section 0.1 and Section 17.9 require a qualified sport psychologist or certified mental performance consultant to sign off before production deployment.

### 4.8 Big Five weight matrix augmentation (Phase F decision)

The analysis in the "how does this impact..." discussion identified Phase F as the window for deciding whether to expand the 5×6 Big Five weight matrix to 5×12 by including regulatory items. Theoretically:

- Conscientiousness should gain from identified-regulation items.
- Neuroticism should gain from introjected-regulation items.
- Openness should gain from intrinsic-regulation items.

Phase A data against BFI-2 criterion scores determines whether the augmented matrix improves trait recovery. Not an immediate engineering item; a calibration decision with empirical data behind it.

## 5. What went well

- Banned-terms consolidation removed one open item from the passion retrospective and made the 16.1 narrative tests a two-line import.
- Per-domain `DomainRegulation` structure cleanly matches the architecture decision that this layer is additive to per-domain outputs, not a global score. Downstream consumers route domain-by-domain.
- Erosion detector design (no-recovery clause across three-measurement windows) rejects the single-cycle drop noise that the ABC team had flagged as an issue with trajectory-based alerts generally.
- Template rendering with `_DOMAIN_PLAIN` substitution keeps the banned-terms test meaningful: the test checks both raw templates and rendered output, so a future translation-table edit that introduces jargon cannot pass by hiding in a placeholder.

## 6. What I would do differently

- Load the threshold-boundary behavior into a dedicated test class from the start, not a single test. The 4-raw-to-5.0-normalized case is the most common source of off-by-one style errors in this instrument and deserves a named test class across every scoring module.
- Write the narrative `_DOMAIN_PLAIN` dictionary first, so each template is designed against a fixed noun-phrase vocabulary. I added it after drafting the templates and had to revisit for consistency.

## 7. Post-retrospective review

Ran ruff, coverage with the authoritative banned-terms list, and a spot readability pass.

### 7.1 Ruff clean

All new files and the modified `narrative_engine.py` pass `ruff check` with the project's existing rule set.

### 7.2 Coverage at 100% on all three new modules

After adding `test_banned_terms.py`:

```
banned_terms.py          100%
regulation_erosion.py    100%
regulatory_style.py      100%
```

### 7.3 Full suite 506 passing, 0 failing, 4 pre-existing xfailed

No regressions. 53 new tests from this slice.

### 7.4 Per-domain style classification boundary is now explicit

Added `test_boundary_score_fails_recommendation_gate`. A raw-4 response (normalized 5.0) sits at the boundary; both subscales land there, producing `conflicted` with `recommendation_gate_passed=False`. The downstream narrative consumer would show hedged text ("pattern still forming" style) rather than driving a specific coach action.

## 8. Post-review fix pass (2026-04-20, same session)

After the initial retrospective I ran a second-pass review that surfaced five code-fixable issues. All five are now resolved.

### 8.1 Coach regulatory narratives did not name the domain (fixed)

All four coach-facing style templates used a generic "this area" filler. No domain substitution happened on the coach side. Fix: restructured `_DOMAIN_PLAIN` into per-audience keys (`athlete_target`, `athlete_verb`, `coach_target`), added `{target}` placeholders to every coach template, and updated `generate_regulatory_narrative` to select the right key by audience. Coach-facing output now names the domain in plain language ("goal pursuit", "team relationships", "skill development").

### 8.2 Erosion detector missed sustained-low-after-drop (fixed)

The 3-element rule checked `ranks[-1] < ranks[-2]`, which returned False for sequences like `(identified, introjected, introjected)` where an athlete dropped once and stayed low. Fix: changed the rule to monotonic non-increase with net drop: `ranks[-1] <= ranks[-2] <= ranks[-3] AND ranks[-1] < ranks[-3]`. All pre-existing tests still pass; added three new tests covering sustained-low, plateau-after-step-down, and step-down-after-plateau cases.

### 8.3 Coach erosion narrative was Grade 11-12 (fixed)

Rewrote to split the long sentence, replaced "subscale scores" (semi-jargon) with "the usual scores," replaced "non-performance conversation" (compound noun) with "a conversation that is not about performance," and reordered clauses for active voice.

### 8.4 Conflicted and introjected coach templates used abstract construction (fixed)

- `conflicted` coach: "fracture the engagement" became "break the engagement"; added domain naming; dropped the "it" pronoun that mismatched plural "team relationships."
- `introjected` coach: "fragile place to operate from" became "thin foundation"; "is the intervention" became "is the action" (matches other templates).

### 8.5 Regression tests added

- `test_coach_wording_differs_by_domain`: iterates all four styles and asserts coach output for ambition, belonging, and craft contain their respective domain phrases and are pairwise distinct. Would have caught bug 8.1 on the first pass.
- `test_coach_erosion_names_domain`: same assertion pattern for the erosion narrative.
- `test_sustained_low_after_drop_fires`: locks in bug-8.2 fix.
- `test_plateau_after_step_down_fires` and `test_step_down_after_plateau_fires`: cover the two other monotonic-with-net-drop shapes the new rule accepts.

### 8.6 Final post-fix metrics

- Full suite: 511 passed, 4 xfailed, 0 failed.
- Ruff clean on all modified files.
- Line and branch coverage: 100% on `regulatory_style.py`, `regulation_erosion.py`, `banned_terms.py`.
- 58 tests covering the three new modules (53 original + 5 regression).

## 9. Final status

| Item | Status |
|------|--------|
| Code written, linted, tested | Done |
| Full test suite green | Done (511 passed, 4 xfailed) |
| New-module line and branch coverage | 100% on regulatory_style, regulation_erosion, banned_terms |
| Banned-terms module consolidated | Done (closes open item 4.8 from passion retrospective) |
| Banned-terms enforcement on rendered narratives | Done |
| Coach domain-naming bug (§8.1) | Fixed in-session |
| Erosion sustained-low-after-drop bug (§8.2) | Fixed in-session |
| Coach readability above Grade 10 (§8.3, §8.4) | Fixed in-session |
| Readability enforcement as test | Open (requires `textstat` dependency) |
| SME review of templates | Open |
| Integration with `TransitionTracker` | Open |
| Integration into `EnhancedABCScorer.score()` | Open |
| Empirical calibration of thresholds | Open (requires Phase A data) |
| Rank-order amotivated-below-introjected (SME call) | Open |
| Erosion behavior on oscillation patterns (Phase A calibration) | Open |
| Item-bank registration across passion and regulatory layers | Open |
| Big Five augmented weight matrix decision | Phase F (explicit open item, not blocking) |

Seven open items remain. Two are engineering follow-ups (readability in CI, item-bank registration). Two are integration items (TransitionTracker, EnhancedABCScorer). Three are blocked on Phase A data or SME review. One is a Phase F empirical decision.

## 10. Engineering open-items closure pass (2026-04-20, same session)

Four of the engineering items from Section 9 are now closed in a follow-up pass.

### 10.1 Readability enforcement in CI (closed)

Added `textstat>=0.7.4` to `requirements.txt`. Wrote `tests/python_tests/test_readability.py` covering all passion, overinvestment, regulatory, and erosion templates at both raw and rendered levels. Thresholds: Flesch-Kincaid Grade 8 for athlete-facing, Grade 10 for coach-facing. The test caught one drift on the first run: `passion/not_computed/coach/summary` read at Grade 16.2 ("Insufficient responses to compute passion quality"). Rewrote to "Not enough answers yet. Hold for another cycle." Grade 4. Test suite enforces the rule going forward.

### 10.2 Item-bank registration (closed)

Added `src/python_scoring/optional_items.py` with a typed registry (`OptionalItemLayer`) for the passion and regulatory layers. Exports cadence, item codes, scoring-module path, and reference-doc path per layer. Added `is_optional_item`, `layer_for_item`, and `get_layer` lookup helpers. Added `tests/python_tests/test_optional_items.py` with 16 tests asserting that the registry agrees with each scoring module's own `ALL_ITEMS` constant and that the two layers have disjoint codes.

### 10.3 TransitionTracker integration (closed)

Added a new `TransitionType.REGULATION_EROSION` enum value and extended `TransitionTracker.record()` with an optional `regulatory_profile` kwarg. The tracker keeps a parallel `regulatory_profiles: list[RegulatoryProfile | None]` aligned with `history`. On each `record()`, it runs `detect_regulation_erosion` across the accumulated profiles and stores the affected domains on the entry. `get_summary()` now surfaces `latest_regulation_erosion_domains`. Import is lazy so the tracker has no hard dependency when no profiles are supplied. Added `test_transition_erosion_integration.py` with 10 tests covering backward compatibility, erosion detection across history, partial history with missing profiles, and summary integration.

### 10.4 EnhancedABCScorer integration (closed)

Extended `EnhancedABCScorer.score()` with three optional kwargs: `passion_responses`, `regulatory_responses`, and `daily_signals`. When supplied:

- `passion_responses` runs `score_passion_quality`, then `evaluate_overinvestment` (with subscales and optional daily signals), then both narrative methods. Result attaches `passion`, `overinvestment`, `narratives.passion`, `narratives.overinvestment`.
- `regulatory_responses` runs `score_regulatory_style` and feeds the profile into `TransitionTracker.record()` so erosion is tracked. Per-domain regulatory narratives land in `narratives.regulatory`. Any erosion events detected populate `narratives.erosion`.

Core 36-item flow is unchanged and all three optional kwargs default to `None`. Nineteen existing enhanced-pipeline tests still pass. Added `test_enhanced_pipeline_optional_layers.py` with 8 integration tests covering backward compatibility, each layer in isolation, the full stack together, and cross-measurement erosion through the scorer.

### 10.5 Incidental bug surfaced and fixed (closed)

Installing `textstat` pulled in a top-level `tests` package into site-packages (a transitive dependency). That package shadowed the repo's `tests/` directory because `tests/__init__.py` did not exist, breaking three pre-existing tests that import `from tests.python_tests.conftest import ALL_ITEMS`. Added `tests/__init__.py` (empty) so the local package takes precedence. Worth flagging because it could bite again the next time a dev installs a package named similarly to a local directory.

### 10.6 Post-closure metrics

- Full suite: **552 passed, 4 xfailed, 0 failed**. 99 tests added in this session across both 16.1 and 16.2 slices.
- Ruff clean on all new and modified files.
- Branch coverage preserved on all new modules.

### 10.7 What still cannot be closed without external input

Three items remain genuinely blocked, consistent with Section 9:

| Item | Blocking reason |
|------|-----------------|
| SME review of all new narrative templates | Requires qualified sport psychologist or certified mental performance consultant |
| Empirical calibration of thresholds and oscillation rule | Requires Phase A pilot data (n >= 100, multiple measurement cycles) |
| Rank-order amotivated below introjected | Requires SME adjudication |
| Big Five augmented weight matrix decision | Phase F decision with explicit empirical criteria, requires BFI-2 criterion data |

These are documented as open, not pretend-closed. They will resolve when the inputs arrive, not through code.
