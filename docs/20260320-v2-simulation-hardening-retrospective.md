# ABC Simulation: Hardening Retrospective

**Date**: 2026-03-20
**Scope**: Dashboard simulation improvements, trajectory refactor, baseline diagnostics

## The core problem

The v1 simulation proved the scoring pipeline worked. It did not prove the instrument would survive contact with real data. Every validation gate passed perfectly (CFI 1.000, accuracy 100%, correlation 1.000) because the system tested a deterministic pipeline against its own synthetic output. Perfect scores on every metric meant the validation tested nothing meaningful. The simulation answered "does the code run correctly?" but never asked "will the classifications hold up under measurement noise, threshold sensitivity, or atypical baselines?"

This session closed that gap.

---

## 1. The correlation matrix was wrong

### What existed

The dashboard generated participants with an identity correlation matrix: all six subscales were statistically independent. Ambition satisfaction and ambition frustration had zero correlation. This contradicted the project's own `correlation_matrices.yaml`, which specified realistic cross-subscale relationships (within-domain correlations of -0.50 to -0.55, cross-domain correlations of 0.25 to 0.40).

### What changed

The primary correlation matrix from Chen et al. (2015) and Bartholomew et al. (2011) now drives the simulation by default. All three scenarios (primary, conservative, strong) are available through a dropdown, alongside the original identity matrix. Two adversarial scenarios were added: floor effects (responses restricted to 5-7) and acquiescence bias (+1 shift on all items).

### Why it matters

Independent subscales cannot produce the pattern structure that SDT predicts. When satisfaction and frustration within a domain are uncorrelated, the Vulnerable state (high sat, high frust) appears at the same rate as Thriving. In reality, within-domain anticorrelation makes Vulnerable the rarest state, which is exactly why it is the most clinically important to detect. The simulation now reflects this.

---

## 2. Thresholds had no sensitivity analysis

### What existed

Four fixed thresholds (6.46, 4.38, 5.5, 5.0) controlled every classification in the system. No mechanism existed to test what would happen if any threshold shifted by half a point. A participant scoring 6.40 on satisfaction received a different type, domain state, and set of frustration signatures from one scoring 6.50, with no way to see how many participants sat in that boundary zone.

### What changed

A threshold sensitivity panel in the sidebar lets the user drag all four thresholds and re-classify the entire population instantly. The "Re-classify" button recomputes every domain state, archetype, and frustration signature without regenerating the underlying data. A "Reset Defaults" button restores the original values.

### Why it matters

If moving the satisfaction threshold from 6.46 to 6.00 causes 40% of participants to change type, the type system is too fragile for a 4-item subscale with discrete scores spaced 0.417 apart. The sensitivity panel makes this visible before empirical deployment, not after.

---

## 3. No test-retest stability measurement

### What existed

Every participant received a single type label with no indication of how stable that label was. A participant one Likert point from a threshold boundary received the same certainty as one four points away.

### What changed

A new Stability tab computes test-retest reliability. Each participant is re-measured 50 times with plus or minus one Likert point of noise per item. The system reports three stability metrics: type stability (% of trials producing the same archetype), state stability (% producing the same domain states across all three domains), and signature stability (% producing the same number of frustration signatures).

The tab shows:
- Histograms of per-participant stability scores
- A boundary participants table ranking the most unstable profiles by proximity to thresholds
- Per-participant uncertainty in the detail panel, including which thresholds they sit near

### Why it matters

A type label that flips 40% of the time under one-point noise is not a reliable classification. Coaches and athletes should not receive confident labels for participants whose scores sit on threshold boundaries. The stability analysis identifies exactly which profiles are reliable and which are not, before anyone acts on them.

---

## 4. Big Five inference had no external anchor

### What existed

The Big Five weight matrix mapped six subscales to five traits through fixed, theory-derived weights. The formula produced percentiles that depended entirely on the weight choices, with no ground truth to compare against.

### What changed

A round-trip validation generates 500 ground-truth Big Five profiles, maps them to ABC subscale scores through a reverse transformation, runs the inference pipeline, and measures Pearson correlation between ground truth and recovered values. The results appear in the Stability tab with per-trait and mean recovery statistics.

### Why it matters

The round-trip test reveals which traits the weight matrix can actually recover and which it cannot. If Neuroticism recovers at r = 0.3 while Extraversion recovers at r = 0.8, the weight matrix captures some traits better than others. This information should guide which inferred traits to surface to users and which to treat as rough estimates.

---

## 5. Belbin roles lacked falsifiability metrics

### What existed

The Belbin role distribution was displayed without any measure of how many distinct role combinations the system actually produced.

### What changed

The Belbin table now reports the number of distinct role combinations observed (out of 512 theoretical) and the distribution of roles per person. The Stability tab shows this count alongside the stability metrics.

### Why it matters

If the system only produces 30 of 512 possible role combinations, the Belbin inference has far fewer effective degrees of freedom than its design implies. This is not necessarily a flaw: the subscale correlations may structurally prevent certain combinations. But it needs to be visible.

---

## 6. Participant-level uncertainty was absent

### What existed

Every participant received classifications with equal confidence regardless of how close their scores sat to threshold boundaries.

### What changed

The participant detail panel now includes a "Classification Confidence" section showing type stability, state stability, and explicit warnings when any subscale score falls within 1.5 points of a classification threshold. The assessment results page shows a boundary notice when scores are near thresholds, with a recommendation to take the full 24-item assessment if a shorter tier was used.

### Why it matters

A coach should respond differently to "Steady Integrator (92% stable)" than to "Steady Integrator (54% stable, 0.3 points from Pioneer threshold)." The uncertainty display makes this distinction visible at the point of decision.

---

## 7. Trajectory tracked only Belonging

### What existed

The trajectory tab tracked two subscales: B-Satisfaction and B-Frustration. The other four subscales were invisible to the longitudinal system.

### What changed

The trajectory now tracks all six subscales across Ambition, Belonging, and Craft. The chart shows six lines (solid for satisfaction, dashed for frustration, coloured by domain). The delta table displays all six raw scores and all six deltas per week. The coaching tip engine identifies the worst-drifting domain and generates its insight from that domain's trajectory. The per-domain drift summary shows all three domains' changes at a glance.

### Why it matters

An athlete whose Craft satisfaction drops three points over six weeks while Belonging stays stable has a fundamentally different intervention need from one whose Belonging drops. Tracking only Belonging missed two-thirds of the signal.

---

## 8. Reassessment alerts could not distinguish baseline noise from real change

### What existed

The reassessment alert fired whenever any subscale drifted beyond 3.0 points from baseline. It treated all drift as genuine athlete change. If the baseline was taken on an atypical day, every subsequent check-in triggered alerts as the athlete regressed to their true mean.

### What changed

The alert system now runs four diagnostics before rendering a verdict:

1. **Regression-to-mean detection.** If 70%+ of drifting subscales are moving toward the population centre (5.0), the system flags the drift as probable baseline noise and recommends re-establishing the baseline rather than intervening.

2. **Single-spike filtering.** A first threshold breach gets a cautious yellow flag, not a red alert. One bad week is noise. The system advises waiting for the next check-in.

3. **Sustained shift detection.** If multiple weeks exceed the threshold and the latest score has stabilised near the running average, the system identifies a genuine trajectory change and recommends reassessment.

4. **Mixed signal reporting.** When the evidence is ambiguous, the system reports the regression-to-mean percentage so the coach can judge whether the baseline or the athlete is the problem.

A baseline quality indicator appears the moment a participant is selected. It warns upfront if any subscale sits more than 3 points from the scale centre, since those scores are most susceptible to false drift alerts.

Four diagnostic metrics are displayed with every alert: regression-to-mean percentage, weeks over threshold, variation from running average, and maximum baseline deviation from centre.

### Why it matters

Repeated false reassessment alerts desensitise coaches. If the system cannot distinguish "the baseline was taken on a bad day" from "this athlete is declining," coaches will stop trusting the alerts. The diagnostic framework preserves alert credibility by only escalating when the evidence points to genuine change.

---

## 9. Assessment results now connect to trajectory

### What existed

The Assessment tab produced a type and profile. The Trajectory tab required selecting a simulated participant. The two were disconnected.

### What changed

The assessment results now include a "Track My Trajectory" button that sends the user's scores to the trajectory tab as a baseline. The trajectory system generates weekly check-ins from the assessment scores and runs the full coaching and alerting pipeline. Baseline quality warnings apply to assessment-derived baselines the same way they apply to simulated participants.

### Why it matters

The most practical use case for this system is: one athlete takes the assessment, sees their results, and tracks their trajectory over time. This path now works end-to-end.

---

## Recommendations for empirical readiness

The simulation now tests internal robustness. The following gaps remain between simulation validation and empirical credibility.

### Calibrate thresholds against real distributions

The current thresholds (6.46, 4.38, 5.5, 5.0) are theory-derived priors. When real athlete data arrives, compute the distribution of subscale scores and adjust thresholds so the four domain states distribute in clinically useful proportions. If 80% of athletes fall into two states, the thresholds are not discriminating well for that population. The threshold sensitivity panel makes this calibration straightforward.

### Validate type stability empirically

The simulation's test-retest analysis uses synthetic noise. Real test-retest data (same athletes, two assessments one week apart) would reveal whether the 50-trial synthetic stability estimates predict actual retest agreement. If synthetic stability of 85% corresponds to empirical stability of 60%, the noise model underestimates real measurement error.

### Anchor Big Five weights to an external instrument

The round-trip validation tests internal consistency of the weight matrix. It does not test whether the inferred Big Five percentiles correspond to scores on a validated Big Five instrument (e.g., BFI-2, NEO-PI-R). Administering both instruments to the same cohort would produce convergent validity evidence. Without this, the Big Five inference should carry a visible caveat in any user-facing surface.

### Run adversarial populations through the full pipeline

The simulation supports floor effects and acquiescence bias. Additional adversarial scenarios worth testing with real data:

- **Social desirability bias.** Athletes who present favourably (high satisfaction, low frustration across the board) may be masking genuine distress. The system should flag uniformly positive profiles as potential response bias, not as Thriving.
- **Response fatigue.** Athletes who rush through the assessment (low response time, low variance across items) produce noisy data. The system should flag low-variance response patterns and discount their stability estimates.
- **Cultural response styles.** Some populations avoid extreme responses (central tendency bias). The system should test whether the thresholds function when the effective response range narrows from 1-7 to 3-5.

### Establish predictive validity

The strongest defence against scrutiny is outcome prediction. Correlate domain states, archetypes, and trajectory alerts with external outcomes: burnout incidence, injury rates, performance metrics, coach ratings, and athlete retention. If Vulnerable classifications predict higher burnout incidence six weeks later, the system has predictive validity that no amount of internal simulation can provide. Without this evidence, the system describes patterns but does not prove they matter.

### Publish the methodology

Peer-reviewed publication of the factor structure, threshold calibration, and trajectory model would subject the system to external scrutiny before competitors or clients do. A pre-registration of the empirical validation study (hypotheses, sample size, analysis plan) would strengthen credibility further. The simulation code, validation gates, and this retrospective series provide the transparency that reviewers expect.

---

## Summary of changes

| Area | Before | After |
|---|---|---|
| Correlation matrix | Identity (independent subscales) | Primary from Chen et al. (2015), with 3 alternatives + 2 adversarial scenarios |
| Threshold sensitivity | None | Interactive sliders with real-time re-classification |
| Test-retest stability | Not measured | 50-trial per-participant stability with histograms and boundary analysis |
| Big Five validation | No external anchor | Round-trip recovery test with per-trait Pearson correlations |
| Belbin DOF | Not reported | Distinct combinations observed vs. theoretical maximum |
| Participant uncertainty | Not shown | Stability scores, threshold proximity warnings in detail panels |
| Trajectory subscales | Belonging only (2) | All domains (6), with per-domain drift and coaching |
| Reassessment alerts | Fixed threshold, no diagnosis | Regression-to-mean detection, single-spike filtering, sustained shift detection, baseline quality warnings |
| Assessment to trajectory | Disconnected | Direct "Track My Trajectory" link with full coaching pipeline |

---

## What to carry into the next iteration

1. **Thresholds are priors, not constants.** Treat every threshold as a hypothesis to be tested against empirical distributions and outcomes. The sensitivity panel exists for this purpose.
2. **Stability before labels.** Do not surface a classification to a user without a stability estimate. Unstable labels erode trust faster than missing labels.
3. **Diagnose the baseline, not just the drift.** When the system flags change, the first question should be "was the baseline representative?" not "what happened to the athlete?"
4. **Internal consistency is necessary but not sufficient.** Perfect simulation metrics prove the code works. Predictive validity proves the instrument works. The gap between these two is the empirical validation study.
