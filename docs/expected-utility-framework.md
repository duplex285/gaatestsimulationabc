# Expected Utility Framework for ABC Assessment

**Date:** 2026-04-11
**Status:** Plan (not yet implemented)
**Depends on:** improvement-plan-personalization-engine.md, abc-assessment-spec.md

---

## 1. Why Expected Utility, Not Expected Value

Expected value treats all outcomes as commensurable numbers on a single scale. Expected utility recognizes that the same score change means different things in different contexts. A 1-point drop in Belonging satisfaction for a freshman transfer athlete is not the same as a 1-point drop for a senior captain. The objective magnitude is identical. The subjective cost is not.

SDT predicts this asymmetry. Need frustration produces distinct negative outcomes (burnout, depression, disengagement) that are not the mirror image of need satisfaction's positive outcomes (intrinsic motivation, engagement, performance). The dark pathway is not the absence of the bright one (Bartholomew et al., 2011). Expected utility captures this: the disutility of frustration exceeds the utility of equivalent satisfaction.

---

## 2. The Utility Functions

### 2.1 Athlete Utility

An athlete's utility is a function of satisfaction and frustration across all three domains. The key insight: domains interact. High Ambition satisfaction with low Belonging satisfaction is not the same total utility as moderate satisfaction in both, even if the arithmetic means are equal.

**Proposed form:**

$$U_{\text{athlete}} = \sum_{d \in \{A,B,C\}} \left[ w_d \cdot u_s(S_d) - \lambda_d \cdot u_f(F_d) \right] + \gamma \cdot I(S_A, S_B, S_C)$$

Where:
- $S_d$ = satisfaction score for domain $d$ (0-10)
- $F_d$ = frustration score for domain $d$ (0-10)
- $w_d$ = domain weight (reflects individual priorities; derived from archetype)
- $\lambda_d$ = loss aversion multiplier for frustration ($\lambda > 1$, frustration hurts more than satisfaction helps)
- $u_s$, $u_f$ = satisfaction and frustration utility curves (concave for satisfaction, convex for frustration)
- $I(S_A, S_B, S_C)$ = integration bonus: additional utility when multiple domains are satisfied simultaneously
- $\gamma$ = integration weight

**Why this form matters:**

1. **Loss aversion ($\lambda > 1$):** A frustration increase of 1 point costs more utility than a satisfaction increase of 1 point provides. This matches the SDT evidence that need frustration uniquely predicts depression beyond low satisfaction (Bartholomew et al., 2011). Estimated $\lambda \approx 1.5$-$2.0$, calibrated from ABQ burnout data.

2. **Diminishing returns (concave $u_s$):** Going from 2.0 to 4.0 satisfaction is more valuable than going from 7.0 to 9.0. The athlete who is starving for competence benefits more from a skill session than the athlete who is already thriving. This has direct coaching implications: interventions should target the lowest-satisfaction domain first.

3. **Accelerating harm (convex $u_f$):** Going from 6.0 to 8.0 frustration is worse than going from 2.0 to 4.0. Frustration compounds. This matches the cascade model: once frustration crosses a threshold, it accelerates into distress.

4. **Integration bonus ($I$):** An Integrator (all three domains satisfied) has higher total utility than the sum of three single-domain athletes. This is because need satisfaction in one domain supports the others. An athlete with strong Belonging recovers faster from Craft frustration because their relational support buffers the setback.

### 2.2 Domain-Specific Scenarios

**Ambition utility scenarios:**

| Scenario | S_A | F_A | Utility implication |
|----------|-----|-----|-------------------|
| Autonomous drive | 8.0 | 2.0 | High positive utility. Goals feel self-chosen. |
| Controlled motivation | 3.0 | 7.0 | Strong negative utility. Goals feel imposed. The athlete is performing for others, not themselves. Burnout risk highest here. |
| Overinvestment | 9.0 | 5.0 | Moderate net utility but unstable. The Vulnerable state: high drive with rising cost. The expected utility of continuing to push is declining because $u_f$ is convex. |
| Amotivation | 3.0 | 2.0 | Low magnitude. Neither driven nor blocked. The Mild state: disengaged. Expected utility of intervention is high because the athlete is near the steepest part of the $u_s$ curve. |

**Belonging utility scenarios:**

| Scenario | S_B | F_B | Utility implication |
|----------|-----|-----|-------------------|
| Authentic connection | 8.0 | 2.0 | High utility. Relationships feel genuine. Buffers stress in other domains. |
| Conditional belonging | 7.0 | 6.0 | Net utility is lower than the scores suggest because $\lambda > 1$ amplifies the frustration. The athlete feels accepted but at a cost. This is the Vulnerable state, and it is the hardest for coaches to detect because satisfaction is still high. |
| Active exclusion | 2.0 | 8.0 | Strong negative utility, amplified by convex $u_f$. Transfer portal risk is highest here. The expected utility of staying on the team is negative. |
| Fresh start (transfer) | 4.0 | 3.0 | Low magnitude. New team, relationships not yet formed. Expected utility of belonging investment is high because the $u_s$ curve is steepest here. This is the onboarding window. |

**Craft utility scenarios:**

| Scenario | S_C | F_C | Utility implication |
|----------|-----|-----|-------------------|
| Flow state | 9.0 | 1.0 | Peak utility for this domain. Skill development is intrinsically rewarding. |
| Evaluated mastery | 7.0 | 6.0 | Similar to conditional belonging: high satisfaction masked by high frustration. The athlete is skilled but feels judged. Expected utility of continued effort is declining. |
| Competence threat | 2.0 | 8.0 | Strong negative utility. The athlete doubts their ability. Combined with low Ambition, this predicts sport devaluation (ABQ SD subscale). |
| Beginner's mind | 4.0 | 2.0 | Low satisfaction but low frustration. The athlete is learning without pressure. Expected utility of coaching investment is high (steep $u_s$ curve). |

### 2.3 Coach Utility

The coach's utility function is different. It is defined over the team distribution, not individual scores.

$$U_{\text{coach}} = \sum_{i=1}^{N} U_{\text{athlete}_i} - C(\text{interventions}) + V(\text{distribution shape})$$

Where:
- $N$ = roster size
- $C$ = cost of interventions (coach time, attention, emotional labor)
- $V$ = value of the distribution shape (a balanced team with diverse archetypes is more resilient than a team of all Pioneers)

**The coach's decision problem:** Given limited time, which interventions maximize expected utility across the team? This is a resource allocation problem under uncertainty:

$$\max_{\text{interventions}} \sum_{i=1}^{N} E\left[ U_{\text{athlete}_i} \mid \text{intervention} \right] - C(\text{intervention})$$

**Key insight from your paper:** "The answer to the coaching constraint is not that coaches do more. It is that the system asks less of any single person." The expected utility framework operationalizes this: the system should recommend the intervention with the highest expected utility per unit of coach cost. A team-wide Belonging activity (low cost per athlete, moderate expected benefit) may dominate individual conversations (high cost per athlete, high expected benefit for that one athlete).

---

## 3. How This Changes the Simulator

### 3.1 For the Athlete

The current results view shows scores, states, and narratives. Expected utility adds a layer: **how much does each domain contribute to your overall wellbeing, and where is the highest-return investment?**

**New output: Domain utility breakdown**

Instead of just showing "Ambition: 7.2 satisfaction, 3.1 frustration, Thriving," show:

> Ambition is contributing positively to your wellbeing. Craft is your highest-return opportunity right now: a small improvement there would matter more than the same improvement in Ambition, because you are on the steeper part of the curve.

This is the $u_s$ curve made concrete. The athlete does not need to understand utility theory. They need to know: where should I focus?

**New output: Frustration cost signal**

> Your Belonging frustration (5.8) is costing you more than you might realize. Research shows that relational frustration weighs roughly 1.5x heavier than the equivalent satisfaction. Your Belonging satisfaction (6.9) looks strong on paper, but the net effect is less positive than the numbers suggest.

This is $\lambda > 1$ made concrete. The Vulnerable state becomes legible.

### 3.2 For the Coach

The current coach view shows individual athletes and aggregated patterns. Expected utility adds: **where is the highest-return coaching investment across the team?**

**New output: Team utility map**

A scatter plot or heatmap showing each athlete's expected utility contribution by domain. Athletes in the lower-left (low satisfaction, high frustration) are the highest-cost individuals. Athletes in the upper-right are contributing the most. The gap between them is the coach's opportunity.

**New output: Intervention expected utility comparison**

| Intervention | Athletes affected | Expected utility gain | Coach cost | EU per unit cost |
|-------------|------------------|----------------------|------------|-----------------|
| Team belonging activity | 44 | +0.3 per athlete | 2 hours | +6.6/hr |
| Individual craft session with athlete #12 | 1 | +2.1 | 1 hour | +2.1/hr |
| Ambition autonomy conversation with athlete #7 | 1 | +1.8 | 0.5 hours | +3.6/hr |

The team activity wins on EU per unit cost even though the individual session has a larger per-athlete effect. This is the "distribute the burden" principle from the paper, expressed as an optimization.

### 3.3 For the Reassessment Decision

Expected utility replaces the current threshold-based reassessment trigger with a decision-theoretic one.

Current: reassess when variance exceeds 3.0 points for 2+ weeks.

Expected utility: reassess when the expected utility of having updated information exceeds the cost of the assessment.

$$EU(\text{reassess}) = P(\text{state changed}) \times V(\text{updated baseline}) - C(\text{assessment time})$$

If the athlete's check-ins show low variance, the probability of a meaningful state change is low, and reassessment has low expected utility even if scheduled. If check-ins show high variance, the expected utility of reassessment is high because the current baseline is unreliable.

This makes the reassessment schedule adaptive, not fixed. Some athletes need reassessment every 6 weeks. Others can go a full season on one baseline. The expected utility calculation determines which.

---

## 4. Calibration: Where Do the Numbers Come From?

The utility function parameters ($w_d$, $\lambda_d$, $\gamma$, curve shapes) are not arbitrary. They are calibrated from:

1. **$\lambda$ (loss aversion):** From SDT burnout literature. Lonsdale et al. (2009) reported frustration accounts for up to 74% of variance in burnout, while satisfaction explains a smaller proportion of engagement. This asymmetry implies $\lambda \approx 1.5$-$2.0$.

2. **$w_d$ (domain weights):** Derived from the athlete's archetype. A Pioneer weights Ambition higher than Belonging. An Anchor weights Belonging higher. These are not preferences the athlete reports. They are inferred from the satisfaction distribution.

3. **$\gamma$ (integration bonus):** From the observation that Integrators (all three domains active) have disproportionately lower burnout risk than the sum of individual domain satisfactions would predict. The Phase A empirical pilot can calibrate this by comparing Integrator burnout rates to predicted rates from a simple additive model.

4. **Curve shapes:** Concavity of $u_s$ and convexity of $u_f$ are calibrated from the Bayesian scorer's posterior distributions. An athlete whose satisfaction has been consistently high (narrow posterior, high mean) is on the flat part of the curve. An athlete whose satisfaction has been consistently low is on the steep part. The posterior shape tells you where on the curve the athlete sits.

---

## 5. Connection to Game Theory

Expected utility is the language game theory uses to model decisions. Once utility functions are defined, the game-theoretic questions from your original framing become precise:

**Institutional design:** What incentive structure (NIL policy, transfer rules, mental health staffing) maximizes expected utility across the student-athlete population? This is mechanism design with the ABC utility function as the objective.

**Coach-team interaction:** Given the coach's utility function and the team's distribution, what is the Nash equilibrium of coaching attention? Does the equilibrium match the EU-optimal allocation, or does it systematically under-invest in Belonging (because Belonging outcomes are less visible than Ambition outcomes)?

**Onboarding design:** The paper notes that freshman Belonging scores are 23% below the team average. The expected utility framework quantifies the cost: freshmen are on the steep part of the $u_s$ curve for Belonging, meaning each unit of Belonging investment produces the highest marginal utility. The optimal onboarding design front-loads Belonging activities because that is where the curve is steepest.

---

## 6. Implementation Phases

| Phase | What | Depends on |
|-------|------|-----------|
| A | Define utility function form and parameter priors | This document (done) |
| B | Add EU computation to EnhancedABCScorer | Phase A + existing Bayesian scorer |
| C | Add "highest-return domain" signal to athlete narratives | Phase B + narrative engine |
| D | Add team utility map to coach view | Phase B + coach intelligence |
| E | Replace threshold-based reassessment with EU-based decision | Phase B + trajectory engine |
| F | Calibrate parameters from Phase A empirical pilot data | Requires real athlete data |

Phase A is this document. Phases B-E are simulator work. Phase F requires the empirical pilot.

---

## 7. What This Does Not Do

This framework does not:

- Replace the SDT foundation. It extends it by quantifying the asymmetry between satisfaction and frustration.
- Require athletes to understand utility theory. The outputs are natural language: "this domain is your highest-return investment."
- Assume rational agents. The utility function describes the psychological reality (frustration hurts more than satisfaction helps). It does not assume athletes optimize.
- Work without the indirect inference layer. The utility function takes subscale scores as inputs. Those scores must come from a measurement system that avoids the self-report failures the paper documents. The simulator validates the measurement. The utility framework interprets it.
