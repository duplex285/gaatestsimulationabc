---
layout: default
title: Audit Checklist
---

# Audit Checklist

A structured checklist for external reviewers. Use this to organize your evaluation; file your responses as GitHub issues on this repository or via direct email to the project owner.

---

## A. For psychometricians

### A.1 Measurement model

- [ ] Is the bifactor result (omega_h = 0.246, ECV = 0.061 on synthetic data) correctly interpreted as "no dominant general factor across the three needs," or does it suggest a different problem (item fragmentation, weak factor structure)?
- [ ] Is the planned bifactor-ESEM 1-G vs 2-G test (WI-8) the correct way to resolve whether ABC measures one bipolar fulfillment continuum or two distinct sat/frust constructs? Toth-Kiraly et al. (2018) ran this test on the BPNSFS; ABC plans the same.
- [ ] Is the ESEM approximation route (factor_analyzer + Procrustes target rotation + EwC respecification in semopy) defensible for Phase A with N >= 100 to 300? Or should the plan move to `rpy2` + `lavaan` for full ML ESEM immediately?
- [ ] Are the proposed S-1 anchor candidates (Belonging satisfaction per Sanchez-Oliva 2017 pattern, OR Zhang 2020 augmented bifactor with general-content items) appropriate?

### A.2 LPA model selection

- [ ] Is the five-criterion convention (ABIC elbow + BIC/CAIC/ABIC weighted majority + aLMR/BLRT + interpretability + entropy >= 0.70) the correct decision rule for ABC?
- [ ] Given the literature cap of k = 4 to 5 for SDT motivation profiles at any plausible sample size, is the decision to keep ABC's eight a-priori archetypes as a theoretical taxonomy (Decision-2) defensible? Should the typology be reduced?
- [ ] Are bifactor factor scores the right LPA indicators (per Howard 2020, Fernet 2020), or should ABC use raw subscales for transparency?

### A.3 Reverse-item design

- [ ] Are the proposed item rewrites in [new-items-draft-v2.md](new-items-draft-v2.html) correctly classified as "negated regulars" rather than "polar opposites" per Kam, Meyer & Sun (2021)?
- [ ] Is the trade-off between content variety (polar opposites carry richer semantic content) and methodological cleanliness (negated regulars avoid the logical-response artifact) appropriately resolved?
- [ ] Should the plan include a hybrid Phase A (some subscales with polar-opposite reverses, others with negated-regular reverses, then test) instead of fully committing to negated regulars?

### A.4 Effect-size benchmarks

- [ ] Are the pre-registered effect-size targets in [validity-argument.md](validity-argument.html) Section (d) appropriate? Specifically:
  - ABC frust composite x ABQ burnout: r = .50 to .65 (Bartholomew 2011 r = .46; Vasconcellos 2020 r = .53)
  - Within-domain sat-frust: r = -.20 to -.40 (Bartholomew 2011 r = -.21 to -.27)
  - Coach IBQ x ABC sat: r = .35 to .55 (Vasconcellos 2020 r = .57 minus cross-rater discount)

### A.5 Difference scores and categorization

- [ ] Is the planned replacement of `gap = team_score - personal_score` with polynomial regression and response surface analysis (WI-9, per Edwards 2001) appropriately scoped?
- [ ] Is the 2x2 domain-state classifier (Thriving/Vulnerable/Mild/Distressed) appropriately reframed as a display layer rather than the primary analytic unit (per Edwards 2001 Myth 4)?

### A.6 Cascade hypothesis

- [ ] Is the reframing of the 1.5-timepoint frustration-leads-satisfaction lag as a falsifiable hypothesis (rather than an asserted parameter) appropriate?
- [ ] Are the five competing hypotheses in `abc-assessment-spec.md` Section 2.9 (parallel, frustration-leads, satisfaction-leads, reciprocal feedback, asymmetric transition) the right candidates to compare in Phase A?

### A.7 Sample size and power

- [ ] Is the Phase A target N >= 100 (feasibility pilot, with all bifactor-ESEM analyses deferred to Phase B with N >= 500) defensible?
- [ ] What minimum N would you require for ABC to claim publishable factor structure evidence?

---

## B. For sport psychologists

### B.1 Item content

- [ ] Inspect the 36 current items in [new-items-draft.md](new-items-draft.html). Do they describe athlete experience accurately?
- [ ] Inspect the ten revised items in [new-items-draft-v2.md](new-items-draft-v2.html). Do the revisions improve construct fidelity to active thwarting (frustration items) and to literal negation (reverse items) without losing sport relevance?
- [ ] Are the named agents in the revised frustration items (coach, training plan, teammates) the correct sources of thwarting in the elite and college athlete populations ABC targets?
- [ ] Does AF1 ("did your coach or training plan stop you from pursuing what you wanted to work on") capture the autonomy-thwarting experience that NCAA scholarship constraints, professional contract obligations, and team selection produce?

### B.2 Sport-specific gaps

- [ ] Is the proposed new item BF7 ("teammates seem resentful or dismissive when you performed well") tapping a real and important phenomenon in athletic environments?
- [ ] Are there sport-relevant constructs the 36 items still do not cover? Examples flagged by the literature review:
  - Performance pressure vs personal challenge distinction
  - Coach-source vs teammate-source belonging support (currently lumped)
  - Identity foreclosure (athletic-identity narrowness)
  - Injury and rehabilitation context
  - Selection pressure (NCAA roster, scholarship contingencies)

### B.3 Cultural and developmental accessibility

- [ ] Does the language work for athletes across competitive levels (recreational, collegiate, elite, professional)?
- [ ] Does the language work across sport types (team sport, individual sport, judged vs scored sport)?
- [ ] Does the language work for non-native English speakers and athletes from non-Western sporting cultures? Items flagged for sensitivity review:
  - BF5 ("deliberately leave you out") - athletes may struggle to judge intent vs effect
  - BS6 (revised) - individual-sport athletes may interpret "things going well" differently
  - CF6 (revised) - cultures with absolute coach authority may have floor effects

### B.4 Goal content (Aspiration Index supplement)

- [ ] Inspect the [Aspiration Index supplement](aspiration-index-supplement.html). Are the 6 items (3 intrinsic, 3 extrinsic) the right operationalization of Kasser & Ryan (1996) for athletes?
- [ ] Should ASP4 ("earning a significant income") trigger socially desirable underreporting in NCAA athletes (where amateurism rules apply)? If so, how should the wording change?
- [ ] Is the championship item (ASP7) reliably classifiable as intrinsic OR extrinsic, or does it depend on the athlete's framing?

### B.5 Coach circumplex IBQ alignment

- [ ] Per Decision-7, ABC adopts the Rocchi 2017 IBQ 6x4 structure as the spine for the coach-rated need support instrument and extends with sport-specific items. Is this the right approach?
- [ ] Should the IBQ stem be changed from "The people in my life..." to specify coach vs teammates separately, to enable dyadic-source decomposition?

### B.6 Athlete-facing reports

- [ ] Are the eight archetype names (Pacesetter, Anchor, Builder, Captain, Architect, Mentor, Integrator, Seeker) appropriate for athlete self-discovery? Do they avoid stigmatizing labels?
- [ ] Should ABC athlete-facing reports always show the continuous (sat, frust) coordinates alongside the categorical label (per WI-9 reframing)?
- [ ] Is the "Vulnerable" label (high sat + high frust = "successful but suffering") appropriate, or does it pathologize athletes who are performing well?

### B.7 Practitioner workflows

- [ ] How would you, as a sport psychologist or applied practitioner, use ABC outputs in a session with an athlete?
- [ ] What additional information would you need (e.g., comparison to team norms, change since last administration, confidence bounds) to make ABC actionable?

---

## C. Cross-disciplinary

### C.1 Strategic positioning

- [ ] Is ABC's positioning as a "first-of-its-kind athlete mental performance platform" (per `abc-assessment-spec.md` Strategic Context) defensible given the existing instruments (BPNSFS, PNTS, ABQ, MWMS adapted to sport)? What does ABC add that those do not?
- [ ] Is the longitudinal-Bayesian architecture (per `improvement-plan-personalization-engine.md` Section 15) genuinely novel, or has it been done elsewhere?

### C.2 Open work and risks

- [ ] What is the single most important methodological risk to the ABC validity claim that this audit package does not adequately address?
- [ ] What additional empirical work (beyond the planned Phase A) would you require before recommending ABC for use in elite-athlete settings?

---

## D. Filing your review

**Format.** A document or structured email organized by the section letters above (A.1, A.2, ...). Include item-level comments where applicable.

**Where to send.**
- GitHub issues on this repository (preferred for transparency)
- Direct email to the project owner

**Acknowledgement.** Reviewers willing to be acknowledged in publications will be listed in `docs/external-review-package.md` with affiliation and date of review.

**Conflict of interest.** Please declare any consulting relationships, financial interests, or competing instruments.

---

## E. Decision authority

The project owner has final decision authority. Reviewer comments will be:
1. Addressed in writing in `docs/literature-review-activity-log.md` issue log
2. Either accepted (with revisions made and documented) OR explicitly rejected (with rationale)

Reviewers do NOT have veto power over implementation decisions, but their concerns will be answered in writing. The audit serves transparency and methodological discipline, not gatekeeping.
