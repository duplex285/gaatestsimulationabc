# Predictive Reassessment and Adaptive Question Selection

**Date:** 2026-04-11
**Status:** Plan (not yet implemented)
**Depends on:** expected-utility-framework.md, improvement-plan-personalization-engine.md

---

## 1. The Problem

The current trajectory system is reactive. It waits for variance to exceed a threshold, then recommends reassessment. By the time the threshold is crossed, the athlete's state has already changed. The system confirms what happened rather than predicting what is coming.

The goal is to predict how soon a player will need reassessment, and when that reassessment happens, to ask the questions that will most improve our understanding of their current state.

---

## 2. Predicting Time to Reassessment

### 2.1 What the check-ins tell us

Each check-in produces a delta from the baseline. Over multiple check-ins, these deltas form a trajectory. The trajectory has three properties that predict reassessment timing:

**Slope:** The rate of change per check-in period. A steep negative slope on satisfaction (or steep positive slope on frustration) predicts the athlete will cross the reassessment threshold sooner. A flat slope predicts they will not need reassessment during this cycle.

**Volatility:** The standard deviation of deltas around the trend line. High volatility means the athlete's state is unstable. Even with a flat trend, high volatility increases the probability of a threshold breach at any given check-in.

**Acceleration:** Is the slope itself changing? A satisfaction score declining at an increasing rate is more urgent than one declining at a constant rate. Acceleration predicts that the slope will be steeper next week than it was this week.

### 2.2 The prediction

For each domain, compute the expected number of check-ins until the reassessment threshold is breached:

$$E[\text{time to breach}] = \frac{\tau - \Delta_{\text{current}}}{\text{slope} + \epsilon}$$

Where:
- $\tau$ = reassessment threshold (currently 3.0 points)
- $\Delta_{\text{current}}$ = current delta from baseline
- slope = OLS slope of deltas over recent check-ins
- $\epsilon$ = small constant to avoid division by zero

This is a point estimate. The confidence interval comes from the volatility:

$$\text{CI}_{95} = E[\text{time}] \pm 1.96 \times \frac{\sigma_{\text{delta}}}{\text{slope}}$$

### 2.3 What the athlete and coach see

**Athlete (trajectory tab):**

> Based on your last 4 check-ins, your Belonging satisfaction is declining at 0.4 points per week. At this rate, a reassessment would be recommended in approximately 3 weeks. This is not a certainty. It is a signal that something in your team environment may be shifting.

**Coach (team view):**

| Athlete | Domain at risk | Current delta | Slope | Predicted reassessment | Confidence |
|---------|---------------|---------------|-------|----------------------|------------|
| #7 Jordan | Belonging | -1.8 | -0.4/wk | ~3 weeks | Moderate |
| #12 Taylor | Craft | -2.1 | -0.6/wk | ~1.5 weeks | High |
| #23 Sam | None | +0.3 | +0.1/wk | Not predicted | High |

This lets the coach intervene before the threshold is crossed, not after. The prediction turns the trajectory from a monitoring tool into a planning tool.

### 2.4 Bayesian updating of the prediction

Each new check-in updates the prediction. The slope estimate has a posterior distribution that narrows with more data:

- After 2 check-ins: wide posterior, low confidence prediction
- After 4 check-ins: moderate posterior, the prediction is becoming reliable
- After 6+ check-ins: narrow posterior, the prediction is stable unless something changes

If a check-in contradicts the predicted trajectory (the score reverses direction), the posterior widens and the prediction shifts. The system does not stubbornly predict reassessment if the trend reverses. It adapts.

---

## 3. Adaptive Question Selection for Reassessment

### 3.1 The problem with uniform reassessment

The current reassessment is the full 36-item instrument. Every item is asked regardless of what the check-ins have revealed. This wastes the information the check-ins already provided.

If check-ins show Belonging frustration rising while Ambition and Craft are stable, the reassessment should focus on Belonging. We already have strong posteriors for Ambition and Craft. The uncertainty is in Belonging.

### 3.2 Information-theoretic question selection

Each item in the 36-item assessment reduces uncertainty about one or more subscales. The amount of uncertainty reduction is measured by expected information gain:

$$\text{IG}(q) = H(\theta_d) - E[H(\theta_d \mid \text{response to } q)]$$

Where:
- $q$ = a candidate question
- $\theta_d$ = the latent trait for subscale $d$
- $H$ = entropy (uncertainty)

Questions that target the most uncertain subscales have the highest information gain. Questions about subscales where the posterior is already narrow (from stable check-ins) have low information gain.

### 3.3 How this works in practice

The Bayesian scorer already maintains a posterior distribution for each subscale. The posterior SD is a direct measure of uncertainty. When reassessment is triggered:

1. Rank the 6 subscales by posterior SD (highest uncertainty first)
2. For the most uncertain subscales, select items with the highest discrimination parameters (from IRT, already in `config/irt_parameters.yaml`)
3. Present those items first
4. After each response, update the posterior and recompute which remaining items have the highest information gain
5. Stop when either: all posteriors are sufficiently narrow (SE < 0.30), or all 36 items have been asked

This is Computerized Adaptive Testing (CAT). The project already has a CAT engine (`src/psychometric/cat_engine.py`, built in Phase 7 of the gold-standard plan). The predictive reassessment system connects the trajectory engine to the CAT engine:

- Trajectory predicts when reassessment is needed
- Check-in data narrows the posterior for stable domains
- CAT selects items for the uncertain domains
- The result is a shorter, more targeted reassessment

### 3.4 What this means for the athlete

Instead of 36 items every time:

> Your Ambition and Craft scores have been stable for 8 weeks. We are confident in those. Your Belonging has shifted. This reassessment focuses on Belonging: 6 items instead of 36. It takes 2 minutes instead of 8.

The athlete answers fewer questions. The questions are more relevant. The measurement is more precise where it matters. This is the opposite of the status quo, where every reassessment asks the same 36 items regardless of what has changed.

### 3.5 Which questions correct the priors

The specific items selected depend on two factors:

**Factor 1: Where is the posterior widest?**

If Belonging frustration has high posterior SD (uncertain), select items from the BF subscale: BF1-BF6. If the IRT parameters show that BF3 has the highest discrimination at the athlete's estimated theta, present BF3 first.

**Factor 2: What kind of uncertainty exists?**

There are two types of uncertainty the check-ins cannot resolve:

- **Level uncertainty:** We do not know where the athlete's true score is. The check-in deltas are noisy. More items at the athlete's estimated level reduce this.
- **Direction uncertainty:** We do not know whether the athlete is improving or declining. The slope estimate has a wide confidence interval. Items that differentiate between high and low states resolve this faster than items that measure the middle of the range.

The IRT item parameters (discrimination and difficulty) determine which items resolve which type of uncertainty. High-discrimination items resolve level uncertainty faster. Items with difficulty parameters near the athlete's estimated theta resolve direction uncertainty faster.

---

## 4. The Longitudinal Cycle, Formalized

The full cycle with predictive reassessment:

```
Week 0:   Full 36-item assessment → establishes baseline
          Posterior: wide (1 measurement, prior-dominated)

Weeks 1-4: Weekly check-ins → track variance from baseline
           Posterior: narrowing for stable domains
           Prediction: "No reassessment needed, all slopes flat"

Week 5:   Check-in shows Belonging delta = -1.2
           Posterior: Belonging widens, others stay narrow
           Prediction: "Belonging reassessment in ~4 weeks at current rate"

Weeks 6-8: Belonging continues declining, others stable
            Posterior: Belonging very wide, others narrow
            Prediction: "Belonging reassessment in ~1 week"

Week 9:   Adaptive reassessment triggered
           CAT selects 8 Belonging items (not 36 uniform items)
           Posterior: Belonging narrows dramatically
           New baseline established for Belonging only
           Ambition and Craft baselines unchanged (still reliable)

Weeks 10+: Check-ins resume from mixed baseline
            (original for A/C, updated for B)
            Prediction resets for Belonging
```

This is more statistically rigorous than point-in-time assessment because:

1. It uses all available information (check-ins + assessment), not just the last assessment
2. It adapts the measurement to what is uncertain, not what is convenient
3. It predicts rather than reacts
4. It produces a posterior, not a point estimate, so confidence is always visible

---

## 5. Implementation in the Simulator

### 5.1 Trajectory prediction (Python + JS)

Add to `transition_engine.py`:

```python
def predict_reassessment_timing(
    delta_history: list[float],
    threshold: float = 3.0,
) -> dict:
    """
    Predict how many check-ins until the reassessment threshold is breached.

    Returns:
        predicted_checkins: int or None (None = not predicted)
        confidence: float (0-1)
        slope: float (per check-in)
        volatility: float (SD of deltas)
        acceleration: float (change in slope)
    """
```

Add to `personalization.js`:

```javascript
ABCPersonalization.predictReassessmentTiming = function(deltaHistory, threshold) { ... }
```

### 5.2 Adaptive question selection (Python)

Connect `src/psychometric/cat_engine.py` to `bayesian_scorer.py`:

```python
def select_reassessment_items(
    posteriors: dict[str, dict],  # per-subscale posterior {mean, sd}
    irt_params: dict,             # from config/irt_parameters.yaml
    max_items: int = 36,
    se_target: float = 0.30,
) -> list[str]:
    """
    Select the items that will most reduce uncertainty.

    Prioritizes subscales with widest posteriors.
    Within each subscale, selects items with highest
    information gain at the athlete's estimated theta.

    Returns ordered list of item IDs (most informative first).
    """
```

### 5.3 Dashboard (JS)

Add to the trajectory tab:
- Predicted reassessment timing per domain (with confidence)
- Visual: dotted line projecting the current trend to the threshold
- When reassessment triggers: show which subscales are targeted and why

---

## 6. What This Does Not Do

- It does not replace the indirect inference layer. Check-ins still come from the second-game's behavioral signals.
- It does not eliminate the full 36-item assessment. The first baseline always uses all 36. Adaptive selection applies to reassessments only.
- It does not assume the athlete's trajectory is linear. The prediction updates with each check-in and adjusts when the trend changes.
- It does not require the athlete to understand posterior distributions. The output is: "Based on your recent check-ins, a Belonging reassessment is likely needed in about 3 weeks. When it happens, it will be shorter than the first assessment because we already have strong data on your Ambition and Craft."
