# Measuring What Athletes Need, Not What They Are: A Simulation-Validated Framework for Longitudinal Motivational Assessment

**White Paper**
March 2026

---

## Abstract

Most psychometric tools in sport classify athletes into fixed types based on single-session questionnaires. This approach treats personality as stable and context as irrelevant. Self-Determination Theory (SDT) offers a different premise: athletes have three basic psychological needs (autonomy, competence, relatedness) whose satisfaction and frustration shift with their environment. A framework that measures these shifts over time would predict burnout, disengagement, and role behaviour more accurately than static trait assessment.

This paper presents a simulation-validated psychometric framework, the ABC Assessment, that operationalises SDT's three needs as six subscales: satisfaction and frustration for Ambition (autonomy-directed goal pursuit), Belonging (relational connection), and Craft (skill-directed competence). The simulator generates synthetic populations, scores them through a ten-step pipeline, and validates the resulting type system, domain classifications, frustration signatures, and team role inferences against quantitative gates. The purpose of the simulator is to stress-test the framework's structural properties before exposing it to real respondents, so that the first empirical study begins with a measurement instrument whose psychometric architecture has already been verified.

---

## 1. The problem with point-in-time personality assessment in sport

Personality assessment in sport rests on a familiar assumption: measure an athlete's traits once, classify them, and use the classification to guide coaching. The Big Five model (Costa & McCrae, 1992), the Myers-Briggs Type Indicator (Myers et al., 1998), and Belbin's Team Role inventory (Belbin, 2010) all follow this pattern. Each captures something real about individual differences. None captures how those differences change when the environment changes.

SDT challenges this assumption directly. Deci and Ryan (2000) showed that three basic psychological needs, autonomy, competence, and relatedness, are universal across cultures and contexts, and that the degree to which an environment satisfies or frustrates these needs predicts wellbeing, motivation quality, and performance. Vansteenkiste and Ryan (2013) demonstrated that satisfaction and frustration are partially independent constructs: an athlete can feel competent and simultaneously frustrated in their competence development. Bartholomew et al. (2011) found that need frustration predicts ill-being (burnout, depressive symptoms, physical symptoms) independently of need satisfaction and more strongly than low satisfaction alone.

These findings have three consequences for assessment design:

1. **Satisfaction and frustration must be measured separately.** A single score per need conflates two independent signals. An athlete scoring 6 out of 10 on "belonging" could be moderately satisfied with low frustration (the "Mild" state) or highly satisfied with high frustration (the "Vulnerable" state). These demand different coaching responses.

2. **Assessment must be repeated.** A single measurement captures the current state of need fulfilment, not the person's stable tendencies. Stable tendencies emerge only from repeated measurement across contexts (Sheldon et al., 1997). A longitudinal instrument that tracks need satisfaction and frustration over weeks and months reveals patterns that point-in-time tools cannot detect.

3. **Types should describe current motivational shape, not fixed personality.** If needs shift, types should shift with them. Movement between types is informative, not an error. An athlete who moves from "Resolute Pioneer" (high ambition, multiple frustrated domains) to "Steady Pioneer" (high ambition, no frustrated domains) has reduced frustration without changing their motivational orientation. This is progress. A static type system would miss it entirely.

The ABC Assessment framework addresses all three consequences. But before testing it with real athletes, the framework's structural properties, whether the scoring pipeline produces the intended distributions, whether all types are reachable, whether downstream inferences (domain states, frustration signatures, team roles) behave as designed, must be verified. That is the simulator's purpose.

---

## 2. Why simulate before measuring

### 2.1 The cost of discovering structural flaws in the field

Psychometric validation typically follows a linear path: design the instrument, administer it, analyse the results, revise, repeat. Each cycle requires recruiting participants, collecting data, and running confirmatory analyses. When structural flaws emerge (a type that no respondent can reach, a threshold that creates a dead zone, a downstream inference that amplifies upstream bias), the entire cycle repeats.

Simulation inverts this sequence. A parametric model generates thousands of synthetic respondents whose subscale scores follow known distributions. The scoring pipeline processes these respondents identically to how it would process real data. If the pipeline produces unintended biases, unreachable types, or unstable role distributions, the simulator reveals them before any real athlete answers a single question.

This matters for three reasons:

**Structural completeness.** The ABC framework derives 24 named archetypes from a two-layer system: 125 granular profiles (five satisfaction levels per domain, 5 x 5 x 5) collapsed into 24 human-readable types (eight base patterns crossed with three frustration modifiers). Each of these 24 types must be reachable by plausible response patterns. Each of the 125 profiles must map unambiguously to exactly one archetype. The simulator verifies both properties across populations of 1,000 to 10,000 synthetic respondents.

**Threshold calibration.** The framework uses three layers of thresholds, each serving a different purpose: domain state classification (satisfaction >= 6.46, frustration >= 4.38), type activation (satisfaction >= 5.5), and frustration modifier counting (frustration >= 5.0). These thresholds interact. A change in the domain state threshold alters the proportion of "Thriving" versus "Vulnerable" athletes. A change in the type activation threshold shifts which base patterns dominate. The simulator reveals these interactions before they distort real-world classifications.

**Downstream amplification.** The scoring pipeline feeds subscale scores into Big Five trait inference, which feeds into Belbin team role assignment. Small biases in subscale distributions compound through these layers. The simulator discovered, for example, that a 0.40 negative correlation between within-domain satisfaction and frustration caused the "Steady Integrator" type to dominate at 5.9% (the target ceiling was 5.7%). Removing the correlation and tuning the generative means corrected the distribution. This interaction would have been invisible in a small-sample pilot study.

### 2.2 What simulation cannot do

Simulation validates structure, not content. It confirms that the scoring pipeline produces the intended distributions, that all classification paths are reachable, and that downstream inferences behave as designed. It does not confirm that the question items measure what they claim to measure. Content validity, the question of whether "I feel confident pursuing the goals that matter most to me" actually captures ambition satisfaction, requires real respondents and confirmatory factor analysis on empirical data.

The simulator uses the lavaan package in R (Rosseel, 2012) to run confirmatory factor analysis on synthetic data generated from the hypothesised six-factor structure. This confirms that the statistical machinery works (all fit indices pass: CFI >= 0.95, TLI >= 0.95, RMSEA <= 0.06, SRMR <= 0.08) but does not confirm that the factor structure holds in real populations. The CFA on real data is the next step, and the simulator ensures that when that step arrives, the measurement instrument's architecture is already sound.

---

## 3. The ABC Assessment framework

### 3.1 Theoretical grounding

The framework maps SDT's three basic needs to three domains accessible to athletes:

| Domain | SDT Root | What It Captures |
|--------|----------|------------------|
| **Ambition** | Autonomy + goal-directed competence | The quality of goal pursuit: whether striving feels self-directed and meaningful, or pressured and hollow |
| **Belonging** | Relatedness | The quality of connection: whether relationships feel authentic and unconditional, or conditional and isolating |
| **Craft** | Skill-directed competence | The quality of mastery engagement: whether skill development feels autonomous and satisfying, or evaluated and coerced |

The relabelling from SDT's technical terms to Ambition, Belonging, and Craft serves two purposes. First, it increases face validity for athletes, who understand "ambition" and "belonging" without training in motivation science. Second, it separates competence into two distinct expressions: goal-directed competence (captured in Ambition, the drive to achieve) and skill-directed competence (captured in Craft, the drive to master). This distinction matters because an athlete can feel competent at achieving results while feeling incompetent at developing skills, or vice versa. SDT's single "competence" construct conflates these (Deci & Ryan, 2000).

Each domain is measured on two subscales: satisfaction (need fulfilment) and frustration (need thwarting). This follows Vansteenkiste and Ryan's (2013) dual-process model and Chen et al.'s (2015) validation of the Basic Psychological Need Satisfaction and Frustration Scale, which demonstrated that satisfaction and frustration load on distinct factors rather than opposite ends of a single continuum.

### 3.2 Instrument structure

The full instrument contains 24 items: four per subscale, six subscales (A-Sat, A-Frust, B-Sat, B-Frust, C-Sat, C-Frust). Each item uses a seven-point Likert scale (1 = Strongly Disagree, 7 = Strongly Agree). The fourth item in each subscale is reverse-scored (recoded as 8 minus the raw response) to detect acquiescence bias.

Three assessment tiers allow the instrument to function at different stages of a longitudinal relationship:

| Tier | Items | Items per Subscale | Use Case | Confidence |
|------|-------|--------------------|----------|------------|
| Onboarding | 6 | 1 | First encounter; directional signal | 0.50 |
| Standard | 12 | 2 | First two weeks; provisional type | 0.70 |
| Full | 24 | 4 | Two to three months; validated profile | 0.90 |

The tiered design reflects a core premise: longitudinal assessment earns trust over time. An athlete completing a six-item onboarding assessment receives an immediate insight ("You're a Steady Architect") that demonstrates the platform's value. The standard assessment, prompted within two weeks, sharpens the profile. The full assessment, at two to three months, produces reliable subscale means against which all prior signals can be calibrated. This progressive approach differs from instruments that demand 30 to 60 minutes of a new user's time before delivering any value.

### 3.3 Scoring pipeline

The simulator implements the same ten-step pipeline that the production system will use. Each step is deterministic: identical inputs produce identical outputs.

**Step 1: Reverse-score.** Items AS4, AF4, BS4, BF4, CS4, CF4 are recoded as (8 - raw response). This ensures all items within a subscale are directionally aligned.

**Step 2: Subscale means.** Average the (reverse-scored where applicable) items within each subscale to produce six raw means on the 1.0 to 7.0 scale.

**Step 3: Normalise.** Convert each subscale mean to a 0 to 10 scale: score = (mean - 1) x 10 / 6. This places thresholds at interpretable positions and allows percentage-based communication ("Your ambition satisfaction is 7.2 out of 10").

**Step 4: Domain state classification.** Cross each domain's satisfaction and frustration scores against two thresholds (satisfaction >= 6.46, frustration >= 4.38) to assign one of four states:

- **Thriving:** high satisfaction, low frustration. The need is met and the environment does not obstruct it.
- **Vulnerable:** high satisfaction, high frustration. The need is met but the environment also thwarts it. This is the "successful but suffering" state that Vansteenkiste and Ryan (2013) identified as a precursor to burnout.
- **Mild:** low satisfaction, low frustration. The need is neither met nor thwarted. This corresponds to amotivation (Deci & Ryan, 2000).
- **Distressed:** low satisfaction, high frustration. The need is unmet and actively thwarted. Bartholomew et al. (2011) linked sustained need thwarting to burnout, depressive symptoms, and dropout.

The thresholds (6.46 and 4.38) are positioned between discrete score boundaries on the normalised scale to prevent classification artefacts caused by the seven-point Likert resolution.

**Step 5: Type derivation.** A two-layer system classifies each athlete:

*Layer 1: 125 profiles.* Each domain's satisfaction score is classified into five levels (Very High >= 8.0, High >= 6.0, Medium >= 4.0, Low >= 2.0, Very Low < 2.0). The profile code (e.g. "4-3-5") captures the granular motivational shape.

*Layer 2: 24 archetypes.* Eight base patterns are derived by applying a binary threshold (satisfaction >= 5.5) to each domain, producing 2^3 = 8 combinations (e.g. Integrator: all three strong; Seeker: all three developing). Three frustration modifiers count how many domains have frustration >= 5.0: Steady (zero), Striving (one), Resolute (two or three). The archetype name combines modifier and base: "Striving Architect."

The activation threshold (5.5) sits below the domain state threshold (6.46) because activation precedes full satisfaction. A need can be engaged and energising without yet reaching the "Thriving" level. The frustration modifier threshold (5.0) sits above the domain state frustration threshold (4.38) because the modifier asks how many domains carry notable frustration, not whether the domain is clinically distressed.

**Step 6: Frustration signature detection.** When a domain's frustration reaches 4.38, the system flags a named pattern:

| Condition | Ambition | Belonging | Craft | Risk |
|-----------|----------|-----------|-------|------|
| High sat + high frust | Blocked Drive | Conditional Belonging | Evaluated Mastery | Medium |
| Low sat + high frust | Controlled Motivation | Active Exclusion | Competence Threat | High |

These signatures translate SDT's theoretical predictions (Bartholomew et al., 2011; Vansteenkiste & Ryan, 2013) into coaching-actionable language. "Conditional Belonging" tells a coach something specific: the athlete feels connected but senses that connection depends on performance. "Active Exclusion" tells a different story: the athlete feels disconnected and actively shut out.

**Steps 7-10** infer Big Five personality percentiles (internal validation only, not user-facing), Belbin team roles (using a cluster-affinity architecture mapped from Aranzabal et al., 2022), dominant domain, and context gaps between personal and team-level scores. These downstream inferences are detailed in Section 4.

---

## 4. Simulation architecture and validation

### 4.1 Population generation

The simulator generates synthetic populations using a multivariate normal model. Each simulated athlete receives six z-scores (one per subscale), transformed through a correlation matrix and converted to item-level responses on the 1-7 Likert scale.

**Key design choices:**

*Independent subscales.* The production simulator uses an identity correlation matrix (all six subscales fully independent). Early iterations used empirically motivated correlations (e.g. -0.40 within-domain satisfaction-frustration correlation, drawn from Chen et al., 2015), but these introduced systematic type biases. An independent model produces an unbiased baseline distribution: no type combination is structurally favoured over any other. Real population correlations will emerge from empirical data.

*Tuned generative means.* The z-means for each subscale are offset from zero to compensate for two structural asymmetries:

- Satisfaction z-mean = +0.24: compensates for reverse-scoring pulling item means below the type activation threshold (5.5).
- Frustration z-mean = -0.31: compensates for the Resolute modifier's structural advantage. With three independent Bernoulli trials (each domain either frustrated or not), the probability of two or more successes (Resolute) exceeds the probability of exactly zero (Steady) or exactly one (Striving) when the per-trial probability is near 0.5. Shifting the frustration mean downward reduces the per-trial probability, flattening the modifier distribution.

*Item-level noise.* Each item receives independent Gaussian noise (SD = 0.3 x noise multiplier) to simulate within-subscale response variability. Items are clamped to [1, 7] and rounded to integers. This preserves the discrete structure of Likert data.

### 4.2 Validation gates

The simulator checks every run against quantitative gates derived from psychometric standards and the framework's design requirements:

| Gate | Criterion | Source |
|------|-----------|--------|
| CFA fit: CFI | >= 0.95 | Hu & Bentler (1999) |
| CFA fit: TLI | >= 0.95 | Hu & Bentler (1999) |
| CFA fit: RMSEA | <= 0.06 | Hu & Bentler (1999) |
| CFA fit: SRMR | <= 0.08 | Hu & Bentler (1999) |
| Cronbach's alpha per subscale | >= 0.70 | Nunnally (1978) |
| Type coverage | All 24 types present, none > 15% | Design requirement |
| Big Five inter-trait correlation | |r| < 0.30 | Gosling et al. (2003) |
| Belbin role coverage | All 9 roles present | Design requirement |
| Cross-seed stability | < 3% SD across seeds | Design requirement |
| Scoring correlation (R vs Python) | r = 1.000 | Implementation verification |

The R validation (using lavaan; Rosseel, 2012) and the Python scoring engine produce identical subscale scores (Pearson r = 1.000 across all six subscales on shared test data). This cross-language verification ensures that the production scoring engine faithfully implements the validated pipeline.

### 4.3 Biases discovered and corrected

The simulator's primary value lies in the biases it revealed before any real data was collected:

**Resolute Seeker dominance.** Early simulations centred subscale means at the population midpoint (z = 0). Because the midpoint falls below the type activation threshold (5.5), most simulated athletes had all three domains classified as "Developing," producing the Seeker base pattern. Frustration scores near the midpoint gave each domain approximately 50% probability of exceeding the modifier threshold (5.0), making Resolute (two or more frustrated domains) the most probable modifier. Resolute Seeker reached 10.8% of the population against a target ceiling of 5.7%. Tuning z-means corrected this without introducing domain-specific bias.

**Steady Integrator dominance.** A negative within-domain satisfaction-frustration correlation (-0.40) meant that high satisfaction reliably predicted low frustration. This boosted the Integrator (all domains strong) and Steady (zero frustrated domains) combination to 5.9%. Removing the correlation (switching to an identity matrix) eliminated the bias. The decision to use independent subscales is conservative: it assumes nothing about real-world correlations and produces the flattest possible type distribution.

**Belbin role concentration.** Three compounding biases distorted the team role distribution:

1. *Tie-breaking bias.* Domain satisfaction scores from seven-point Likert data frequently tied. A stable sort consistently ranked Ambition first, inflating Action-cluster roles (Shaper, Implementer, Completer-Finisher). Adding random jitter (< 0.001) before ranking corrected the 38% vs 33% Ambition-primary imbalance.

2. *Big Five variance asymmetry.* Each Big Five trait's weight vector has a different L2 norm, producing different variances in the inferred z-scores. Neuroticism, with the smallest weights, had the tightest percentile distribution, suppressing Neuroticism-dependent roles (Monitor-Evaluator, Completer-Finisher). Dividing each trait's z-score by its weight vector's standard deviation equalised trait variance.

3. *Mean bias from z-offsets.* The satisfaction z-mean (+0.24) and frustration z-mean (-0.31) shifted Big Five trait means away from the population centre. Extraversion (loaded heavily on satisfaction) was boosted; Neuroticism (loaded on frustration) was suppressed. Post-hoc population centering (shifting each trait's mean percentile to 50) corrected this, followed by recomputation of all Belbin role scores with the centred percentiles.

None of these biases would have been visible in a pilot study with 50 to 100 real respondents. The simulator's ability to generate 10,000 respondents per run exposed distributional distortions that small samples would have absorbed as noise.

### 4.4 Structural ceiling on type flatness

A mathematical constraint limits how flat the type distribution can be. The frustration modifier uses three independent Bernoulli trials (one per domain). The probabilities of zero, one, and two-or-more successes cannot all equal one-third simultaneously. At the optimal per-trial probability (approximately 0.29), the maximum achievable flatness is approximately 5.7% per type (compared to the theoretical uniform of 4.17% = 1/24). The simulator confirmed that the tuned z-means achieve this ceiling within statistical noise across repeated runs.

---

## 5. Downstream inferences

### 5.1 Big Five personality inference

The framework infers Big Five personality percentiles from the six subscales using a covariance-aware weight matrix. This is not a Big Five instrument; it is a mapping from motivational need states to personality-trait approximations, used for two purposes: (a) internal validation against established personality benchmarks (Gosling et al., 2003), and (b) differentiation of Belbin team roles within domain clusters. Big Five scores are never displayed to end users.

The weight matrix was optimised to produce near-zero inter-trait correlations (|r| < 0.02 in simulation) and balanced primary-trait distribution (approximately 20% of the population leading on each trait). Each weight has a theoretical anchor:

- **Openness** loads positively on Craft satisfaction (+0.52) and Craft frustration (+0.33): curious, tolerant of creative friction, independent of social belonging (Belonging satisfaction -0.36).
- **Conscientiousness** loads negatively on Craft frustration (-0.45): disciplined athletes experience low friction in skill development.
- **Extraversion** loads on Ambition satisfaction (+0.47) and Belonging satisfaction (+0.27): assertive, socially energised.
- **Agreeableness** loads on Belonging satisfaction (+0.43) and negatively on Ambition satisfaction (-0.23): cooperative, low in competitive assertion.
- **Neuroticism** loads on Belonging frustration (+0.41) and Ambition frustration (+0.24): relational and goal-directed distress.

### 5.2 Belbin team role inference

The framework maps Belbin's nine team roles (Belbin, 2010) through a two-stage architecture inspired by Aranzabal et al.'s (2022) finding that Belbin roles cluster into three groups (Thinking, People, Action) that correspond to the ABC domains (Craft, Belonging, Ambition):

*Stage 1: Cluster selection.* Each athlete's three domain satisfaction scores are ranked. The top two domains determine which role clusters are active (primary affinity = 1.0, secondary = 0.5, tertiary = 0.0). Excluding the tertiary cluster reduces noise from the weakest domain signal.

*Stage 2: Within-cluster differentiation.* Each role within an active cluster is scored as (domain affinity) x (Big Five trait percentile / 100). The relevant Big Five trait differentiates roles within the same cluster (e.g. within the People cluster: Teamworker uses Agreeableness, Resource Investigator uses Extraversion, Coordinator uses Conscientiousness). Roles scoring above 0.30 are assigned; the highest-scoring role always fires regardless of threshold.

This architecture treats team roles as dynamic expressions of current need states, not fixed traits. When an athlete's ABC profile shifts (e.g. Belonging satisfaction rises, moving Belonging from tertiary to secondary), their Belbin roles shift accordingly. This aligns with Belbin's (2010) own observation that individuals' role preferences change with context and team composition.

---

## 6. Areas for additional research

### 6.1 Empirical factor structure validation

The six-factor structure (three domains, each split into satisfaction and frustration) has been validated on synthetic data using CFA. The next step is confirmatory factor analysis on real respondent data. Key questions: Does the six-factor model fit better than a three-factor model (collapsing satisfaction and frustration)? Do the within-domain satisfaction-frustration correlations match Chen et al.'s (2015) findings for the BPNSFS? Does the factor structure hold across sports, competitive levels, and cultural contexts?

### 6.2 Threshold calibration with empirical data

All thresholds (domain state: 6.46/4.38; type activation: 5.5; modifier: 5.0) were calibrated against simulated distributions. Empirical data may reveal that natural response distributions cluster differently from the parametric model, requiring threshold adjustment. Item Response Theory (IRT) analysis on real data would identify optimal cut points based on empirical item difficulty and discrimination parameters (Embretson & Reise, 2000).

### 6.3 Longitudinal stability and sensitivity to change

The framework assumes that type changes across repeated assessments reflect genuine shifts in motivational state, not measurement noise. Test-retest reliability studies are needed to establish: (a) the minimum interval at which type changes carry signal (weekly, fortnightly, monthly); (b) the effect size of environmental changes (coaching interventions, team restructuring, competition cycles) on subscale scores; and (c) whether the tiered assessment structure (onboarding, standard, full) produces convergent type assignments as item count increases.

### 6.4 Predictive validity for athlete outcomes

The framework's practical value depends on whether ABC types and domain states predict outcomes that matter to coaches and athletes: burnout risk, performance trajectories, retention, and response to coaching interventions. Bartholomew et al. (2011) established that need frustration predicts ill-being in sport; the question is whether the ABC Assessment's operationalisation of frustration (through the frustration subscales and signatures) predicts these outcomes with greater specificity than general need measures.

### 6.5 Big Five weight matrix validation

The weight matrix that maps six subscales to Big Five percentiles was optimised for internal consistency (low inter-trait correlations, balanced distributions) rather than external validity. Administering both the ABC Assessment and a validated Big Five instrument (e.g. the BFI-2; Soto & John, 2017) to the same sample would reveal whether the inferred percentiles correlate with directly measured traits and, if so, at what strength.

### 6.6 Belbin role dynamics

The cluster-affinity architecture predicts that Belbin roles shift when ABC states shift. Longitudinal data from teams using the ABC Assessment would test this prediction: do athletes' observed team behaviours change in the direction predicted by their role reassignment? This question connects the psychometric framework to observable performance and team dynamics, bridging the gap between self-report measurement and behavioural validity.

### 6.7 Cross-cultural applicability

SDT's three basic needs have been validated across cultures (Chen et al., 2015), but the ABC relabelling (Ambition, Belonging, Craft) and the question items' language may carry cultural connotations. "Ambition" connotes individualistic striving in some cultures and collective aspiration in others. Item wording should be tested for measurement invariance across at least three cultural contexts before the instrument is deployed internationally.

### 6.8 Adaptive item selection

The three-tier structure (6, 12, 24 items) uses fixed item sets. An adaptive approach using computerised adaptive testing (CAT; van der Linden & Glas, 2000) could select items dynamically based on prior responses, achieving the same measurement precision with fewer items. This would be particularly valuable for the daily check-in context, where shorter assessments reduce respondent burden and increase completion rates.

---

## References

Aranzabal, A., Epelde, E., & Artetxe, M. (2022). Team formation on the basis of Belbin's roles: A reassessment with a modified scale. *Assessment & Evaluation in Higher Education, 47*(8), 1231-1245.

Bartholomew, K. J., Ntoumanis, N., Ryan, R. M., Bosch, J. A., & Thogersen-Ntoumani, C. (2011). Self-determination theory and diminished functioning: The role of interpersonal control and psychological need thwarting. *Personality and Social Psychology Bulletin, 37*(11), 1459-1473.

Belbin, R. M. (2010). *Team roles at work* (2nd ed.). Butterworth-Heinemann.

Chen, B., Vansteenkiste, M., Beyers, W., Boone, L., Deci, E. L., Van der Kaap-Deeder, J., Duriez, B., Lens, W., Matos, L., Mouratidis, A., Ryan, R. M., Sheldon, K. M., Soenens, B., Van Petegem, S., & Verstuyf, J. (2015). Basic psychological need satisfaction, need frustration, and need strength across four cultures. *Motivation and Emotion, 39*(2), 216-236.

Costa, P. T., Jr., & McCrae, R. R. (1992). *Revised NEO Personality Inventory (NEO-PI-R) and NEO Five-Factor Inventory (NEO-FFI) professional manual.* Psychological Assessment Resources.

Deci, E. L., & Ryan, R. M. (2000). The "what" and "why" of goal pursuits: Human needs and the self-determination of behavior. *Psychological Inquiry, 11*(4), 227-268.

Embretson, S. E., & Reise, S. P. (2000). *Item response theory for psychologists.* Lawrence Erlbaum Associates.

Gosling, S. D., Rentfrow, P. J., & Swann, W. B., Jr. (2003). A very brief measure of the Big-Five personality domains. *Journal of Research in Personality, 37*(6), 504-528.

Hu, L., & Bentler, P. M. (1999). Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives. *Structural Equation Modeling, 6*(1), 1-55.

Myers, I. B., McCaulley, M. H., Quenk, N. L., & Hammer, A. L. (1998). *MBTI manual: A guide to the development and use of the Myers-Briggs Type Indicator* (3rd ed.). Consulting Psychologists Press.

Nunnally, J. C. (1978). *Psychometric theory* (2nd ed.). McGraw-Hill.

Rosseel, Y. (2012). lavaan: An R package for structural equation modeling. *Journal of Statistical Software, 48*(2), 1-36.

Sheldon, K. M., Ryan, R. M., & Reis, H. T. (1997). What makes for a good day? Competence and autonomy in the day and in the person. *Personality and Social Psychology Bulletin, 22*(12), 1270-1279.

Soto, C. J., & John, O. P. (2017). The next Big Five Inventory (BFI-2): Developing and assessing a hierarchical model with 15 facets to enhance bandwidth, fidelity, and predictive power. *Journal of Personality and Social Psychology, 113*(1), 117-143.

van der Linden, W. J., & Glas, C. A. W. (Eds.). (2000). *Computerized adaptive testing: Theory and practice.* Kluwer Academic Publishers.

Vansteenkiste, M., & Ryan, R. M. (2013). On psychological growth and vulnerability: Basic psychological need satisfaction and need frustration as a unifying principle. *Journal of Psychotherapy Integration, 23*(3), 263-280.
