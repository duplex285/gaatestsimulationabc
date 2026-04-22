# Causality Orientations Items Draft

Date: 2026-04-20
Status: Draft, pending expert review and cognitive pretesting
Source plan: improvement-plan-personalization-engine.md Section 16.6

## 1. Purpose

This document presents 12 items operationalizing Causality Orientations Theory (Deci & Ryan, 1985; Koestner, Chapter 5 of the Oxford Handbook of Self-Determination Theory). Causality orientations are relatively stable individual-difference traits that describe how an athlete characteristically interprets and responds to situations. Three orientations are recognized in the theory:

- **Autonomy orientation:** tendency to read situations as offering choice, to act from internal values, and to adjust based on personal fit.
- **Controlled orientation:** tendency to read situations as demands or expectations, and to act in response to external or internal pressure.
- **Impersonal orientation:** tendency to read situations as beyond one's influence, and to feel stuck, disconnected, or subject to outcomes rather than shaping them.

Everyone has some level of all three. The practical question is which orientation dominates an athlete's pattern of interpretation, because orientation moderates how other signals (frustration trajectories, regulatory shifts, passion patterns) land for that athlete.

The full Gosling-Deci GCOS is 17 vignettes with three responses each (51 items) and is a licensed instrument. This ABC short form is 12 direct items and does not reproduce GCOS content. A Phase A comparison against GCOS scores is a planned validation step.

These items are original to Ero. No licensed scale content is reproduced.

## 2. Design constraints

- **Cadence:** Annual. Administered once at onboarding and re-administered roughly every 12 months. Not biweekly or quarterly; orientations move slowly.
- **Placement:** Outside `REQUIRED_ITEMS`. Scored by a parallel module.
- **Stem:** "Over the past month, how often did you..." (monthly frame, not biweekly; orientations are read across a longer window).
- **Response scale:** 1 = Never, 4 = Sometimes, 7 = Very Often. Matches the core bank.
- **No reverse-scored items:** Each item targets one orientation directly. Reverse coding across orientations would collapse the three-dimensional construct into a single scale.
- **Independence of the three orientations:** An athlete can score high on all three (a pattern associated with anxious perfectionism), low on all three (a pattern associated with low engagement), or with one dominant. Scoring respects the three-dimensional structure.

## 3. The 12 items

### 3.1 Autonomy orientation (AO1 to AO4)

**AO1**
"Over the past month, how often did you make a decision because it felt right for you, regardless of what others thought?"

- **Construct:** Internal locus of decision-making.
- **Rationale:** Captures the core autonomy-orientation signal: decisions routed through personal fit rather than external evaluation.

**AO2**
"Over the past month, how often did you notice what you wanted before deciding what to do?"

- **Construct:** Attention to internal state as input to action.
- **Rationale:** Autonomy orientation is partly a perceptual habit. The athlete who checks in with their own preferences before acting is reading situations autonomously, whether or not the eventual choice is autonomous.

**AO3**
"Over the past month, how often did you change direction when a path no longer fit what you wanted?"

- **Construct:** Responsiveness to internal signals across time.
- **Rationale:** An autonomy-oriented athlete updates course when internal and external signals diverge. Distinct from impulsivity: the item emphasizes "no longer fit what you wanted," not "felt restless."

**AO4**
"Over the past month, how often did you approach a hard task by figuring out what interested you about it?"

- **Construct:** Intrinsic-motivation scaffolding under difficulty.
- **Rationale:** Under stress, the autonomy-oriented athlete reaches for what is interesting or meaningful in the task. Pairs with the regulatory-style layer's identified-regulation items but is orientation-level, not task-level.

### 3.2 Controlled orientation (CO1 to CO4)

**CO1**
"Over the past month, how often did you make a decision based on what others would think?"

- **Construct:** External-evaluation-routed decision-making.
- **Rationale:** The core controlled-orientation signal: other people's likely reactions drive the choice.

**CO2**
"Over the past month, how often did you follow a plan because you were supposed to, not because you wanted to?"

- **Construct:** Should-based rather than want-based action.
- **Rationale:** Captures the introjected and external end of the regulation continuum at the orientation level: the athlete's default is compliance with expectation.

**CO3**
"Over the past month, how often did you feel you had to meet an expectation, even when it did not fit you?"

- **Construct:** Obligation overriding personal fit.
- **Rationale:** Distinguishes controlled orientation from situations where expectations happen to align with preference. Taps the chronic override experience.

**CO4**
"Over the past month, how often did you approach a hard task by focusing on what would look good?"

- **Construct:** Image-management under difficulty.
- **Rationale:** Pairs with AO4. Under stress, the controlled-oriented athlete reaches for what will satisfy the audience.

### 3.3 Impersonal orientation (IO1 to IO4)

**IO1**
"Over the past month, how often did a situation feel out of your hands, like it was happening to you?"

- **Construct:** External-locus perception.
- **Rationale:** The defining impersonal-orientation signal: events are read as happening to the self rather than through the self.

**IO2**
"Over the past month, how often did you feel stuck when a decision needed to be made?"

- **Construct:** Decision-paralysis as a pattern.
- **Rationale:** Impersonal orientation predicts decision-avoidance. Distinct from autonomy orientation's "waiting for clarity": the impersonal-oriented athlete does not expect clarity to come.

**IO3**
"Over the past month, how often did an outcome feel like it was mostly luck, good or bad?"

- **Construct:** Attribution to external/random causes.
- **Rationale:** Attributional style marker. An athlete who reads successes and failures as mostly luck is reading through an impersonal lens, regardless of the objective controllability of the situation.

**IO4**
"Over the past month, how often did you find yourself unable to act on what you wanted?"

- **Construct:** Disconnect between internal state and action.
- **Rationale:** Pairs with AO2. Where the autonomy-oriented athlete notices what they want and acts on it, the impersonal-oriented athlete notices but feels unable to close the loop.

## 4. Scoring model

Each subscale is the mean of its four items on the 1-7 scale, normalized to 0-10:

```
orientation_score = ((mean(items) - 1) / 6) * 10
```

Dominant-orientation classification uses the top-vs-second margin:

| Condition | Dominant orientation |
|-----------|----------------------|
| Top score >= 6.0 AND (top - second highest) >= 1.5 | That orientation |
| Top two within 1.5 points AND both >= 4.0 | `mixed` |
| All three below 4.0 | `emergent` (no clear orientation, annual cycle too early or pattern not settled) |
| Top score >= 4.0 AND (top - second) < 1.5 | `mixed` |

The 1.5-point margin is the smallest gap we trust as a signal of true dominance over classification noise, and it matches the margin we use in the regulatory-style layer. Phase A will recalibrate against GCOS or equivalent criterion.

## 5. Evidence gates

Consistent with improvement-plan-personalization-engine.md Section 17.5:

| Condition | Gate | Effect |
|-----------|------|--------|
| All 12 items answered | Passes display and recommendation gates | Dominant orientation shown with full confidence |
| 8 to 11 items answered, at least 2 per subscale | Passes display, fails recommendation | Profile shown with hedged language |
| Fewer than 8 items OR any subscale with fewer than 2 items | Fails display | Profile suppressed, `not_computed` returned |

Orientations are stable traits. A missing-response gate is stricter than on the biweekly layers: if the athlete does not complete enough of the screen, the measurement should not produce a profile at all.

## 6. How orientation stratifies other signals (deferred integration)

The plan (Section 16.6 step 3) describes orientation as a modifier on how other signals are interpreted:

- An autonomy-oriented athlete's frustration trajectory means something different than a controlled-oriented athlete's trajectory with the same slope. The controlled-oriented athlete is more vulnerable to persistent controlled contexts.
- Regulatory-erosion detection should weight more heavily for controlled-oriented athletes, who are more susceptible to drift under pressure.
- Coach intervention recommendations should differ: autonomy-oriented athletes tolerate coaching-style variation; controlled-oriented athletes benefit more from intensive autonomy-support coaching; impersonal-oriented athletes need structural clarity first.

This stratification integration is explicitly deferred to Phase A calibration. The current slice ships the measurement and the orientation-level narratives. Phase A data will validate which stratification rules hold empirically before they modify the narrative or coach-recommendation layers.

## 7. Empirical calibration open items

- Subscale reliability (omega) per orientation at n >= 100. With four items per subscale, reliability is adequate in principle but Phase A will confirm.
- Convergent validity against GCOS (licensing permitting) or a published short form.
- Test-retest stability across an annual window. Orientations should show substantial stability (r >= 0.70); if they do not, the instrument needs refinement.
- Empirical margin for dominance classification. The 1.5-point rule is theoretical; Phase A data can recalibrate against outcomes.
- Predictive validity for Phase A outcome measures: does orientation predict season-end burnout, engagement, and retention beyond what personal need satisfaction explains?
