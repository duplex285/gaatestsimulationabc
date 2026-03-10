# ABC Assessment: Spec-to-Implementation Retrospective

## The core lesson

The original spec assumed psychometric constructs could be defined once and implemented directly. In practice, every layer of the scoring pyramid — thresholds, types, modifiers, team roles — required iterative calibration against simulated populations. Theoretical correctness and empirical balance are different things.

This document records each assumption that changed, why it changed, and what future iterations should carry forward.

---

## 1. Threshold architecture

### What the spec assumed

A single threshold (5.5) would classify both domain states and type activation. One number, applied uniformly.

### What we learned

Three separate thresholds serve three different purposes, and collapsing them creates misclassification:

| Layer | Threshold | Purpose |
|---|---|---|
| Domain states | sat >= 6.46, frust >= 4.38 | Clinical assessment of need fulfilment |
| Type activation | sat >= 5.5 | Which needs are engaged (binary Strong/Developing) |
| Type modifier | frust >= 5.0 | How many domains carry notable frustration |

**Why they diverged.** Domain states answer "is this person thriving?" — a high bar. Type activation answers "is this need engaged?" — a lower bar, because a need can be active before it is fully satisfied. The frustration modifier asks "how many domains carry strain?" — a separate question from whether any single domain is clinically distressed.

**Lesson for future iterations.** When a single number serves multiple classification purposes, test each purpose independently. A threshold that works for clinical triage may fail for personality typing.

---

## 2. Type system structure

### What the spec assumed

Six base types derived from primary and secondary domain ranking (e.g., Captain = Ambition primary + Belonging secondary). Four state modifiers (Steady, Driven, Rising, Gritty) from the primary domain's clinical state.

6 bases x 4 modifiers = 24 types.

### What we learned

**The ranking approach excluded the tertiary domain entirely.** A Captain (Ambition + Belonging) implied nothing about Craft. But Ambition, Belonging, and Craft are motivational needs everyone has — excluding one contradicted the theoretical foundation.

**The state-based modifier tied frustration to the primary domain only.** Someone with high frustration across Belonging and Craft but low frustration in Ambition would still be classified "Steady" because only Ambition (the primary) was checked.

### What replaced it

A two-layer system:

**Layer 1: 125 profile combinations.** Each domain's satisfaction is classified into five levels (Very High, High, Medium, Low, Very Low). The full profile is three levels: "4-3-5" means Ambition:High, Belonging:Medium, Craft:Very High. No domain is excluded.

**Layer 2: 24 named archetypes.** Eight binary base patterns (sat >= 5.5 per domain, 2^3 = 8) crossed with three frustration modifiers (count of domains with frust >= 5.0: Steady/Striving/Resolute).

8 bases x 3 modifiers = 24 types.

| Old approach | New approach |
|---|---|
| Tertiary domain excluded | All three domains represented |
| Modifier from primary domain state | Modifier from frustration count across all domains |
| Ranking-based (ordinal) | Threshold-based (cardinal) |
| 6 bases | 8 bases |
| 4 modifiers | 3 modifiers |

**Lesson for future iterations.** If a construct is theoretically universal ("everyone has all three needs"), the classification system must represent all dimensions for every person. Ranking-based systems inherently drop the lowest-ranked dimension from the label.

---

## 3. Domain state naming

### What the spec assumed

Four states: Thriving, Vulnerable, Distressed, Dormant.

### What we learned

"Dormant" implies the need is inactive or unimportant. In SDT, low satisfaction without frustration is better described as "unengaged" — the need exists but the environment does not stimulate it. "Mild" captures this without suggesting the need has shut down.

The state was renamed to **Mild** across all modules (12+ files).

**Lesson for future iterations.** Name states from the person's perspective, not the system's. "Dormant" describes what the system sees (low scores). "Mild" describes what the person experiences (neither strong fulfilment nor strong obstruction).

---

## 4. Frustration signatures

### What the spec assumed

Frustration signatures required extreme scores: frust > 5.5 for activation, and sat < 4.5 or sat > 5.5 for classification. A gap zone (4.5 <= sat <= 5.5) produced no signature — people in that range were uncategorised.

### What we learned

The gap zone left a meaningful population segment without any frustration signal. Someone with moderate satisfaction and high frustration was neither "Blocked Drive" (medium risk) nor "Controlled Motivation" (high risk) — they were invisible to the system.

**The fix:** Align frustration signature thresholds with domain state thresholds (sat >= 6.46, frust >= 4.38). Binary classification: high satisfaction + high frustration = medium risk; low satisfaction + high frustration = high risk. No gap.

**Lesson for future iterations.** Gap zones in classification systems are bugs, not features. If someone has high frustration, the system should always say something about it. Binary splits (above/below a threshold) are cleaner than three-way splits with a dead zone.

---

## 5. Belbin role inference

### What the spec assumed

Domain affinity weights: primary = 1.0, secondary = 0.5, tertiary = 0.2. All three clusters contributed roles.

### What we learned

Tertiary affinity at 0.2 added noise without signal. A person whose Craft satisfaction was lowest could still receive Craft-cluster roles (Plant, Specialist, Monitor-Evaluator) at 20% strength. These roles lacked the motivational foundation that the model claims drives team behaviour.

**The fix:** Tertiary affinity set to 0.0. Only the top two clusters produce roles. The top role always fires; additional roles above 0.30 score also fire.

### Simulation-specific issue

In the unbiased simulation (designed for even type distribution), three additional Belbin problems emerged:

1. **Tie-breaking bias.** With discrete item scores, domain satisfaction ties are common. Stable sort preserved the fixed order [Ambition > Belonging > Craft], making Ambition the primary domain 38% of the time instead of 33%. Fixed with tiny random jitter before ranking.

2. **Big Five variance asymmetry.** The weight matrix gives Neuroticism smaller weights than Openness, compressing N's percentile range. Roles using N (Completer-Finisher, Monitor-Evaluator) rarely became the top role. Fixed by normalising each trait's z-score by its weight vector's standard deviation.

3. **Big Five mean bias.** Simulation z-offsets that balance the type distribution (sat up, frust down) systematically boost traits loading on satisfaction (Extraversion) and suppress traits loading on frustration (Neuroticism). Fixed by centering each Big Five trait's percentile distribution to 50 across the simulated population, then recomputing Belbin roles.

**Lesson for future iterations.** Downstream inferences (Belbin) inherit all upstream biases (Big Five weights, simulation parameters, tie-breaking rules). Test the full pipeline end-to-end, not just individual modules. A balanced type distribution does not guarantee balanced role distribution.

---

## 6. Simulation design

### What the spec assumed

A correlation matrix derived from literature (Chen et al. 2015, Bartholomew et al. 2011) would drive realistic simulated populations. The simulation's purpose was to validate scoring accuracy.

### What we learned

The simulation serves two distinct purposes that require different parameters:

| Purpose | Requirement |
|---|---|
| **Validation** (audit script) | Realistic correlations, realistic means, test all gates |
| **Dashboard demonstration** | Unbiased distribution, no dominant type, test the UI |

For validation, the original correlation matrix with realistic means (sat ~ 4.7, frust ~ 3.4 on the 1-7 item scale) works well. All seven audit gates pass.

For the dashboard, the same parameters produced dominant types (Resolute Seeker at 38%) because cross-domain correlations made subscales move together. Fixing this required:

1. **Identity correlation matrix** — domains fully independent, so no type combination is structurally favoured.
2. **Tuned z-means** — sat at 0.24 and frust at -0.31, empirically optimised to produce the flattest possible type distribution given the structural constraint that Resolute (2-3 frustrated domains) covers more outcomes than Steady (0 frustrated) or Striving (1 frustrated).
3. **Post-hoc Big Five centering** — subtract each trait's population mean shift, then recompute Belbin.
4. **No-cache headers** — prevent browsers from serving stale simulation code.

**The structural constraint.** With three independent Bernoulli trials (one per domain), P(0 successes), P(1 success), and P(2+ successes) cannot all equal 1/3. The best achievable distribution is roughly 28/44/28 for Steady/Striving/Resolute. Maximum single-type frequency: ~5.7%. This is a mathematical ceiling, not a calibration failure.

**Lesson for future iterations.** Separate validation parameters from demonstration parameters. A simulation that proves the scoring engine works is not the same as a simulation that produces balanced charts. State explicitly which purpose each parameter set serves.

---

## 7. Big Five role in the system

### What the spec assumed

Big Five personality inference would be a visible output — part of the scored profile shown to end users.

### What we learned

Big Five serves two internal purposes and no external one:

1. **Validation.** Correlating inferred Big Five against established standards (Gosling et al. 2003) confirms that the six subscales capture meaningful psychological variance, not noise.
2. **Belbin inference.** Big Five percentiles differentiate roles within each domain cluster (e.g., within the Action cluster, Extraversion selects Shaper while Conscientiousness selects Implementer).

Displaying Big Five percentiles to end users would invite comparison with dedicated Big Five instruments, which the ABC Assessment is not. The unique contribution is the satisfaction-frustration structure across three motivational needs. Big Five is the bridge to existing standards, not the destination.

**Lesson for future iterations.** Internal validation layers should stay internal. If a construct exists only to connect your model to established science, exposing it to end users dilutes both your model's distinctiveness and the established construct's rigour.

---

## 8. Test-driven development in practice

### What the spec assumed

Write all tests first, then implement. Clean separation.

### What we learned

The cycle was tighter than expected. Several test assumptions had to change as the model evolved:

- **Ground truth tests** originally expected midpoint responses (all items = 4) to produce "Mild" domain states. After the threshold split (6.46/4.38), midpoint subscale scores (5.0) fall below 6.46 sat and above 4.38 frust, producing "Distressed" instead.
- **Type tests** were rewritten three times as the type system moved from 6-base to 10-base to 8-base patterns.
- **Belbin tests** needed updating when tertiary affinity changed from 0.2 to 0.0.

The test suite ended at 200 tests. None were deleted — they evolved with the model. The discipline of having tests meant every threshold change was immediately validated against known-answer datasets.

**Lesson for future iterations.** Test-driven development works, but "write all tests first" is aspirational when the model itself is evolving. The realistic pattern is: write tests for the current design, implement, discover a design flaw, update both tests and implementation together. The tests are not prophetic — they are the contract that changes when the design changes.

---

## Summary of changes

| Area | Original spec | Final implementation |
|---|---|---|
| Domain thresholds | Single 5.5 | Split: 6.46 (sat) / 4.38 (frust) |
| Type bases | 6 (primary + secondary domain) | 8 (binary Strong/Developing per domain) |
| Type modifiers | 4 (primary domain state) | 3 (frustrated domain count) |
| Tertiary domain | Excluded from type label | Always represented |
| State naming | Dormant | Mild |
| Frustration signatures | Gap zone, extreme thresholds | No gap, aligned thresholds |
| Belbin tertiary | Affinity 0.2 | Affinity 0.0 |
| Big Five display | User-facing | Internal only |
| Simulation (dashboard) | Correlated, realistic means | Independent, threshold-centred |
| Tests | 100+ planned | 200 final |

---

## What to carry into the next iteration

1. **Start with the pyramid, not the labels.** Define subscales first, classification thresholds second, type names last. Names are the cheapest thing to change; threshold architecture is the most expensive.

2. **Simulate before you name.** Run 10,000 simulated profiles through the classification system before committing to type names or descriptions. If one type captures 30% of the population, the threshold is wrong — not the population.

3. **Separate clinical from typological thresholds.** "Is this person struggling?" and "What is this person's motivational profile?" are different questions requiring different cut points.

4. **Test the full pipeline, not just each module.** Balanced subscales do not guarantee balanced types. Balanced types do not guarantee balanced Belbin roles. Each downstream layer amplifies upstream biases.

5. **Keep validation and demonstration separate.** The audit script uses realistic parameters to prove correctness. The dashboard uses unbiased parameters to show capability. Neither should pretend to be the other.

6. **Real data will change everything.** Every threshold, correlation, and weight in this system was derived from literature and simulation. When actual respondents arrive, expect the correlation matrix, threshold values, and possibly the number of viable types to shift. The infrastructure (scoring pipeline, test suite, dashboard) is ready for that shift. The specific numbers are not final.
