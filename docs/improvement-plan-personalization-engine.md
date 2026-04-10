# ABC Assessment Improvement Plan: From Research Instrument to Personalization Engine

**Date:** 2026-04-10
**Status:** Draft
**Depends on:** abc-assessment-spec.md, validity-argument.md, white-paper-outmatched-and-under-pressure-v2.md

---

## 0. What This Document Changes

This plan introduces capabilities that were either explicitly out of scope, implicitly deferred, or not conceived in any prior iteration of the simulator. The table below maps each new capability to its relationship with prior work.

### Genuinely new (not in any prior document)

| Capability | What's new | Why it didn't exist before |
|-----------|-----------|---------------------------|
| **Base rate engine** (`base_rate_engine.py`) | Demographic-stratified population priors from NCAA epidemiological data, applied to individual classifications via Bayes' Theorem | Prior iterations treated thresholds as fixed cutpoints. No document referenced population prevalence data or adjusted classifications by demographic group. The mental fatigue base rate research (NCAA SAHWS 2022-23, N=23,272) was compiled for this plan. |
| **Narrative engine** (`narrative_engine.py`) | Structured text generation: identity descriptions, reflection prompts, coaching conversation starters, growth narratives, transition stories | All prior iterations output scores, states, types, and signatures. No document specified language generation as a product output. The v2 retrospective classified trajectory patterns (Stable, Gradual Decline, etc.) as implicit narrative frames, but no system produced sentences an athlete or coach could use. |
| **Bayesian scorer** (`bayesian_scorer.py`) | Conjugate normal posterior updating: each measurement shifts the estimate, confidence grows over time, classification carries probability distributions instead of hard labels | IRT EAP scoring (gold-standard Phase 1) uses Bayesian posterior estimation for theta, but this is within a single measurement. No document proposed accumulating information across measurements via prior-to-posterior updating. The PRD mentioned "Bayesian prior from latest assessment anchors daily extraction" as future work (Phase 3) but never specified the mechanism. |
| **Transition engine** (`transition_engine.py`) | Classifies archetype shifts as growth, exploration, regression, or fluctuation; generates transition narratives; builds a growth hierarchy across the 8 patterns | Prior iterations treated type instability as a measurement problem to minimize (v2 retrospective: "classification instability is the biggest fragility"). This plan reframes transitions as the product: development made visible. No prior document proposed a transition taxonomy or growth hierarchy. |
| **Coach intelligence layer** (`coach_intelligence.py`) | Aggregates patterns across all athletes a coach has worked with; tracks intervention effectiveness; enables cross-sport and cross-team pattern recognition; portable across coaching changes | The ABQ+Coach spec (prd-second-game-criterion-integration.md) specified coach ratings as a validation criterion (3 domain ratings + concern flag). This plan extends coaches from data providers to intelligence consumers. No prior document proposed the coach's accumulated experience as a product feature. |
| **Post-career and cross-domain recontextualization** (`config/domain_contexts.yaml`) | Parallel domain framings for sport, professional, military, and transition contexts; item wording adapts while measurement model stays constant; longitudinal profile carries across life phases | Explicitly out of scope in all prior documents. The gold-standard plan, Phase Two plan, both PRDs, and validity argument all focus exclusively on the athlete population. Cross-domain expansion was never discussed. Post-career use was never mentioned. |
| **Threshold personalization** (enhancement to `bayesian_scorer.py`) | After 6+ measurements, population thresholds replaced by athlete-specific thresholds derived from their own posterior distribution | Prior iterations acknowledged threshold sensitivity (v2 retrospective built an interactive slider panel) and empirical derivation (Phase 2 ROC analysis), but always at the population level. No document proposed per-athlete threshold adaptation. |

### Extends or reframes existing work

| Capability | What existed | What this plan changes |
|-----------|-------------|----------------------|
| **6-item onboarding redesign** | PRD specified three tiers (6/12/24 items) with confidence scores (0.50/0.70/0.90). Phase 5b established supportable interpretations per tier. The 6-item tier was documented as supporting "directional signal only." | This plan enforces that finding: suppress archetype labels entirely at 6 items, show probability distributions over archetypes instead of point classifications, frame as invitation to full assessment. The mechanism (Bayesian posterior with weak likelihood) is new; the insight (6 items cannot support type labels) was already established. |
| **Base rate awareness** | v2 retrospective built regression-to-mean detection (recognizing that baseline variability is a population-level phenomenon). Phase 2 derived empirical thresholds via ROC analysis. The gold-standard plan noted that 28/44/28 type distribution is a mathematical ceiling, not a calibration failure. | This plan makes population base rates explicit inputs to classification, not just background context. The regression-to-mean detector addressed a consequence of base rate variability; the base rate engine addresses the cause. |
| **Trajectory and cascade model** | Gold-standard Phase 6 built the leading indicator detection engine: 5 trajectory types, Vulnerable-to-Distressed cascade, RCI-based change detection, alert optimization (81.1% sensitivity, 16.3% FPR, 1.5-timepoint lag). | This plan adds personalized cascade timing (individual Bayesian models replace population-level estimates) and narrative generation from trajectory patterns. The detection engine is unchanged; the interpretation layer is new. |
| **Classification instability handling** | v1 retrospective revised the type system (6 to 8 base patterns). v2 retrospective added confidence bands and stability scores. Phase 2b measured agreement rates (~67% per domain, ~31% for 24 types, ~50-55% for 8 patterns). Phase Two Workstream 4 simplified to 8 patterns + continuous frustration. | This plan stops treating instability as a problem to minimize and starts treating transitions as meaningful. The transition engine, growth hierarchy, and athlete self-narration prompts are all new. The underlying measurement (8 patterns, continuous frustration) is unchanged. |
| **Coach ratings integration** | ABQ+Coach spec defined the schema, endpoints, scoring service, and pairing logic for coach observations. Structured as a validation criterion (ROC analysis with N >= 200 paired datasets). | This plan extends coaches from criterion providers to intelligence consumers. The data collection infrastructure is unchanged. The aggregation, pattern recognition, and portability features are new. |

### Unchanged from prior iterations

| Component | Status | Source |
|----------|--------|--------|
| Scoring pipeline (10 steps) | No changes | abc-assessment-spec.md, scoring_pipeline.py |
| Item structure (36 items, 6 subscales) | No changes | phase-two-plan, implemented in python_scoring |
| Domain state classification logic | Thresholds unchanged (6.46/4.38); Bayesian wrapper added around them | domain_classification.py |
| Big Five weight matrix (v4) | No changes; empirical recalibration deferred to Phase B | big_five_inference.py |
| Belbin role inference | No changes | belbin_inference.py |
| Frustration signatures (6 patterns) | No changes | frustration_signatures.py |
| IRT infrastructure (GRM, EAP, SE) | No changes | irt_estimation.py, irt_simulation.py |
| ROC/Youden threshold derivation | No changes to method; base rate engine uses its outputs | threshold_derivation.py |
| Decision consistency framework | No changes | decision_consistency.py |
| Trajectory engine (RCI, pattern detection) | No changes to engine; narrative layer added on top | trajectory_engine.py |
| CFA/bifactor/method-factor models | No changes | factor_models.py |
| Measurement invariance testing | No changes | measurement_invariance.py |
| Population norming (T-scores, percentiles) | No changes | norming.py |
| Tier reliability (supportable interpretations) | No changes to analysis; onboarding UX enforces findings | tier_reliability.py |
| Test suite (493 tests) | New tests added for new modules; existing tests unchanged | tests/ |
| Validation thresholds config | No changes | config/validation_thresholds.yaml |

### What was explicitly deferred in prior documents and remains deferred

| Item | Originally deferred in | Still deferred because |
|------|----------------------|----------------------|
| MML parameter estimation | Gold-standard plan | Requires real response data |
| ESEM with target rotation | Gold-standard plan | CFA/bifactor addresses primary concerns |
| ABQ licensing confirmation | ABQ+Coach spec | Legal/commercial task, not technical |
| Physiological integration (cortisol, HPA) | Mentioned as future in gold-standard plan | Requires clinical partnership and IRB |
| Team-level analysis (team context items) | PRD ABC integration | Requires multiple athletes per team with assessments |
| Multi-language adaptation | Validity argument | Requires cultural review panel |
| Real-time monitoring systems | Not in scope | Beyond biweekly assessment cadence |

---

## 1. Strategic Reframe

The ABC assessment is not a diagnostic instrument. It is a personalization engine that serves two users across their entire careers:

1. **The athlete** develops language for their inner world and cultivates self-leadership. The tool stays with them long after their playing career ends.
2. **The coach** grows in their ability to support the mental side of sport. The tool stays with them regardless of team or sport.

The product starts in sport but expands to anyone in a high-stress, high-performance role: military, medicine, law enforcement, executive leadership. The underlying science (SDT's three basic psychological needs) is not sport-specific.

This reframe changes what we optimize for. Classification accuracy matters, but only insofar as it enables better conversations. The primary outputs are narratives, language, and patterns, not scores and labels.

---

## 2. Base Rate Integration: Mental Fatigue Epidemiology

### 2.1 The Problem

The current model classifies athletes into domain states (Thriving, Vulnerable, Mild, Distressed) using fixed thresholds without reference to population base rates. This means the model cannot answer: "Is this athlete's frustration score unusual, or is it typical for someone in their position?"

Without base rates, the model commits the base-rate fallacy (Section 3.2.8, OpenIntro Statistics, 4th ed., pp. 104-106): it treats individual scores as if they exist in a vacuum rather than within a population distribution.

### 2.2 Available Base Rates

Source: NCAA Student-Athlete Health and Wellness Study (2022-23, N=23,272); ACHA-NCHA (2018-19, N=9,057); ABQ meta-analysis (Madigan et al., 2022, 91 studies, N=21,012).

**Near-constant mental exhaustion (the prior for Distressed/Vulnerable states):**

| Population | Prevalence | Source |
|-----------|-----------|--------|
| All college athletes | ~25% | NCAA 2022-23 |
| Men | 16-22% | NCAA 2022-23 |
| Women | 35-38% | NCAA 2022-23 |
| LGBTQ+ athletes | 47-48% | NCAA 2022-23 |
| Trans/nonbinary athletes | 48% | NCAA 2022-23 |
| Athletes with financial stress | 58% | NCAA 2022-23 |
| Latinx athletes | 27% | NCAA 2022-23 |
| Black athletes | 24% | NCAA 2022-23 |
| White athletes | 23% | NCAA 2022-23 |

**Any recent mental exhaustion (broader threshold):**

| Population | Prevalence | Source |
|-----------|-----------|--------|
| Men | 49-71% | ACHA-NCHA 2018-21 |
| Women | 67-88% | ACHA-NCHA 2018-21 |

**ABQ exhaustion (continuous measure):**

| Metric | Value | Source |
|--------|-------|--------|
| Mean exhaustion score | 2.78/5.0 (SD=0.77) | ABQ studies, 2024 |
| Meta-analytic total ABQ | 2.29 (SD=0.40) | Madigan et al., 2022 |
| Clinical-level burnout | 6-12% | Various instruments |

**Critical caveat:** No peer-reviewed study has established a true epidemiological base rate for mental fatigue as defined in sport science (a psychobiological state from prolonged cognitive demand). The available data measures self-reported mental exhaustion, burnout, and related constructs. The ABC assessment measures need satisfaction and frustration, which overlap with but are conceptually distinct from these constructs.

### 2.3 Integration Spec

**New module:** `src/python_scoring/base_rate_engine.py`

**Purpose:** Adjust individual classifications by incorporating population-level priors. An athlete's Distressed classification should carry different weight depending on whether 16% or 48% of their demographic typically reports mental exhaustion.

**Architecture:**

```python
class BaseRateEngine:
    """
    Applies Bayesian prior adjustment to domain state classifications.
    
    P(truly distressed | ABC flags distressed) =
        P(ABC flags | truly distressed) * P(truly distressed)
        / P(ABC flags distressed)
    
    Where P(truly distressed) is the demographic-stratified base rate.
    """
    
    def __init__(self, base_rate_config: dict):
        self.base_rates = base_rate_config
    
    def get_prior(self, athlete_demographics: dict) -> dict:
        """
        Returns stratified base rate for each domain state.
        
        Demographics considered:
        - gender (male/female/nonbinary)
        - sexual_orientation (straight/lgbtq+)
        - race_ethnicity
        - financial_stress (low/moderate/high)
        - division (I/II/III)
        - sport_type (endurance/team/individual)
        - career_phase (active/transitioning/post-career)
        """
        pass
    
    def adjust_classification(
        self, 
        raw_state: str, 
        subscale_scores: dict, 
        prior: float,
        sensitivity: float,  # from ROC analysis
        specificity: float
    ) -> dict:
        """
        Returns adjusted posterior probability of each domain state,
        not just the raw classification.
        
        Output: {
            'raw_state': 'Distressed',
            'posterior_distressed': 0.43,
            'posterior_vulnerable': 0.31,
            'posterior_mild': 0.18,
            'posterior_thriving': 0.08,
            'confidence': 'moderate',
            'base_rate_used': 0.35,
            'demographic_factors': ['female', 'division_I']
        }
        """
        pass
```

**Config file:** `config/base_rates.yaml`

```yaml
# Population base rates for mental exhaustion / need frustration
# Sources: NCAA SAHWS 2022-23, ACHA-NCHA 2018-19, Madigan et al. 2022
# All values are priors; update with empirical ABC data as collected

data_source: literature_derived
last_updated: 2026-04-10

near_constant_exhaustion:
  overall: 0.25
  by_gender:
    male: 0.19
    female: 0.365
    nonbinary: 0.48
  by_sexual_orientation:
    straight: 0.22
    lgbtq_plus: 0.475
  by_race_ethnicity:
    white: 0.23
    black: 0.24
    latinx: 0.27
    other: 0.29
  by_financial_stress:
    low: 0.27
    high: 0.58
  by_division:
    d1: 0.245
    d2: 0.26
    d3: 0.26

# Future expansion: high-performance professional roles
# Placeholder priors to be populated from occupational health literature
professional_roles:
  military: null        # DoD resilience studies
  healthcare: null      # Maslach Burnout Inventory normative data
  law_enforcement: null # IACP wellness surveys
  executive: null       # DDO / Kegan & Lahey populations
```

### 2.4 How Base Rates Change the Product

**For the athlete:** Instead of "You are Distressed on Craft," the system says: "Your Craft frustration is elevated. Among athletes in your position, about 1 in 4 experience this level of mental exhaustion. This is common but not inevitable, and it responds to intervention."

**For the coach:** Instead of a binary flag, the coach sees: "This athlete's frustration score is in the 82nd percentile for female Division I athletes. Among LGBTQ+ athletes, this score would be at the 61st percentile. Context matters for interpreting this result."

**For the longitudinal model:** Base rates become the initial prior for each athlete. As measurements accumulate, the individual's own history replaces the population prior. After 6+ measurements, the athlete's personal trajectory carries more weight than the demographic base rate.

---

## 3. Narrative Layer

### 3.1 The Problem

The current pipeline outputs scores, states, types, and signatures. It does not output language. The athlete sees numbers and labels. The coach sees a dashboard. Neither receives words they can use in conversation.

### 3.2 Spec

**New module:** `src/python_scoring/narrative_engine.py`

**Purpose:** Generate personalized narrative text for each scoring output. Every number becomes a sentence. Every state becomes a paragraph. Every transition becomes a story.

**Narrative types:**

| Output | Athlete narrative | Coach narrative |
|--------|------------------|----------------|
| Archetype | Identity description: who you are at your best, what drives you, what to watch for | Pattern description: what this athlete needs, how to support them, common pitfalls |
| Domain state | Self-reflection prompt: what this state feels like, what questions to ask yourself | Conversation starter: how to open a dialogue, what to listen for |
| Frustration signature | Naming the experience: "This pattern is called Blocked Drive. It means..." | Intervention guidance: "Athletes with this signature typically respond to..." |
| State transition | Growth narrative: "You moved from Seeker to Artisan. This often happens when..." | Development tracking: "This athlete's transition pattern suggests..." |
| Trajectory | Self-awareness prompt: "Your Belonging satisfaction has risen steadily over 3 months. What changed?" | Trend alert: "This athlete's Craft frustration is rising. Historical pattern suggests..." |

**Narrative template structure:**

```python
@dataclass
class NarrativeTemplate:
    archetype: str
    domain_state: str
    audience: Literal["athlete", "coach"]
    
    identity_description: str      # Who you are
    current_state: str             # Where you are now
    growth_edge: str               # What to work on
    reflection_prompts: list[str]  # Questions to sit with
    conversation_starters: list[str]  # For coach-athlete dialogue
    
    # Longitudinal (populated after 3+ measurements)
    trajectory_narrative: str | None
    transition_history: str | None
    pattern_recognition: str | None
```

**Example output (athlete-facing, Pioneer archetype, Ambition Thriving, Belonging Vulnerable):**

> You lead with Ambition. You set goals that pull you forward, and your drive is genuine, not performative. Right now, your goal pursuit feels strong and autonomous.
> 
> Your Belonging score shows something worth paying attention to. Your relationships feel good on the surface, but frustration is building underneath. This pattern, called Conditional Belonging, often shows up when you feel you have to earn your place rather than simply occupy it.
>
> A question to sit with: "When was the last time I showed up to a teammate without trying to prove anything?"

### 3.3 Language Development Over Time

The narrative engine should track which prompts the athlete engages with (clicks, journaling responses, coach discussion notes) and adapt. Early narratives are explanatory ("This is what Pioneer means"). Later narratives are reflective ("You have been a Pioneer for 8 months. How has your relationship with ambition changed?"). Post-career narratives recontextualize ("The drive you brought to sport, where does it live now?").

---

## 4. Bayesian Scoring Model

### 4.1 The Problem

The current model treats each measurement as independent. A score of 4.0 on Craft satisfaction means the same thing whether it is the athlete's first measurement or their twentieth. It should not. An athlete with 10 prior measurements averaging 8.0 who suddenly scores 4.0 is in a fundamentally different situation than an athlete whose first-ever score is 4.0.

### 4.2 Spec

**New module:** `src/python_scoring/bayesian_scorer.py`

**Purpose:** Replace point-estimate scoring with posterior distributions that accumulate information across measurements.

**Architecture:**

```python
class BayesianScorer:
    """
    Maintains a posterior distribution for each subscale per athlete.
    
    First measurement: posterior = population prior (from base_rate_engine)
    Subsequent measurements: posterior updated via conjugate normal model
    
    The posterior mean becomes the "best estimate" of the athlete's true score.
    The posterior SD becomes the confidence band around that estimate.
    """
    
    def __init__(self, prior_mean: float, prior_sd: float):
        self.prior_mean = prior_mean
        self.prior_sd = prior_sd
        self.measurements = []
    
    def update(self, new_score: float, measurement_se: float) -> dict:
        """
        Conjugate normal update.
        
        posterior_mean = (prior_mean / prior_sd^2 + score / se^2) 
                       / (1/prior_sd^2 + 1/se^2)
        posterior_sd = sqrt(1 / (1/prior_sd^2 + 1/se^2))
        
        Returns:
        {
            'posterior_mean': float,
            'posterior_sd': float,
            'credible_interval_90': (float, float),
            'measurements_incorporated': int,
            'prior_weight': float,  # how much the prior still matters
            'data_weight': float    # how much the data dominates
        }
        """
        pass
    
    def classify_with_uncertainty(self, thresholds: dict) -> dict:
        """
        Instead of hard classification, returns probability of each state.
        
        P(Thriving) = P(sat > sat_threshold AND frust < frust_threshold)
        computed from the joint posterior distribution.
        """
        pass
```

**What this changes:**

| Measurement # | Prior weight | Data weight | Classification behavior |
|--------------|-------------|-------------|----------------------|
| 1 | ~80% | ~20% | Population base rate dominates. Labels are tentative. |
| 3 | ~50% | ~50% | Equal blend. Labels carry moderate confidence. |
| 6 | ~20% | ~80% | Individual history dominates. Labels are personalized. |
| 12+ | ~5% | ~95% | Almost entirely data-driven. Prior is a footnote. |

**For the athlete:** "Based on your first assessment and athletes like you, your Craft satisfaction is likely in the Thriving range (72% probability). After 3 more measurements, we will have a clearer picture."

**For the coach:** "This athlete's classification confidence is moderate (58%). Their scores sit near the threshold. Wait for the next measurement before intervening."

---

## 5. Transition Tracking and Growth Narratives

### 5.1 The Problem

Type stability of 50-55% on retest was treated as a weakness in the research framing. In the personalization framing, type shifts are the product. An athlete moving from Seeker to Artisan is not noise. It is development.

### 5.2 Spec

**New module:** `src/python_scoring/transition_engine.py`

**Purpose:** Track archetype transitions, classify them as growth/regression/fluctuation, and generate narratives.

**Transition classification:**

```python
class TransitionType(Enum):
    GROWTH = "growth"           # Movement toward greater need integration
    EXPLORATION = "exploration" # Lateral movement, trying new patterns
    REGRESSION = "regression"   # Movement toward fewer active needs
    FLUCTUATION = "fluctuation" # Noise: transition reversed within 2 measurements
    SUSTAINED = "sustained"     # Same type held for 3+ consecutive measurements

class TransitionEngine:
    def classify_transition(
        self, 
        previous_type: str, 
        current_type: str,
        posterior_confidence: float,
        measurement_count: int
    ) -> TransitionType:
        """
        Rules:
        - Growth: more domains active (e.g., Pioneer -> Captain, Artisan -> Integrator)
        - Exploration: same number of domains active, different ones (e.g., Pioneer -> Anchor)
        - Regression: fewer domains active (e.g., Integrator -> Artisan)
        - Fluctuation: reversed within 2 measurements OR confidence < 0.6
        - Sustained: same type for 3+ consecutive
        """
        pass
    
    def generate_transition_narrative(
        self,
        transition: TransitionType,
        previous_type: str,
        current_type: str,
        context: dict  # season phase, recent events, coach notes
    ) -> str:
        pass
```

**Growth hierarchy (ordered by number of active domains):**

```
Seeker (0) -> Pioneer/Anchor/Artisan (1) -> Captain/Architect/Mentor (2) -> Integrator (3)
```

**Transition map (which shifts are common vs. rare):**

To be populated empirically. Initial hypothesis based on SDT theory:
- Most common: Seeker -> single-domain type (first need activates)
- Common: single-domain -> dual-domain (second need develops)
- Uncommon: dual-domain -> Integrator (all three activate)
- Rare: Integrator -> single-domain (unless acute stressor)
- Flag for attention: any regression of 2+ levels (e.g., Integrator -> Pioneer)

### 5.3 Athlete self-narration

After each type transition, the athlete is prompted:

> "Your profile has shifted from Pioneer to Captain. This suggests your Belonging need has strengthened alongside your Ambition. Does this match your experience? What changed?"

Their response is stored and becomes part of their longitudinal narrative. Over time, the athlete builds a personal development story told in their own words, scaffolded by the assessment structure.

---

## 6. Coach Intelligence Layer

### 6.1 The Problem

A coach's insight grows with each athlete they support. The current system treats each athlete independently. It does not help the coach recognize patterns across athletes, teams, or seasons.

### 6.2 Spec

**New module:** `src/python_scoring/coach_intelligence.py`

**Purpose:** Aggregate patterns across all athletes a coach has worked with. Turn experience into explicit knowledge.

**Features:**

```python
class CoachIntelligence:
    def archetype_distribution(self, coach_id: str) -> dict:
        """
        "Of the 47 athletes you have coached, 12 were Pioneers, 
        8 were Integrators, 3 were Seekers..."
        """
        pass
    
    def frustration_patterns_by_context(self, coach_id: str) -> dict:
        """
        "Athletes entering Vulnerable states on Belonging in their 
        first month with a new team typically stabilize by measurement 4.
        Three of yours did not. Here is what was different."
        """
        pass
    
    def intervention_effectiveness(self, coach_id: str) -> dict:
        """
        "Your coaching interventions correlate with faster recovery 
        from Craft frustration (mean: 2.1 measurements vs population 3.4)."
        Requires coach to log interventions.
        """
        pass
    
    def cross_sport_insights(self, coach_id: str) -> dict:
        """
        When a coach moves sports:
        "In swimming, your athletes' Ambition frustration peaked mid-season.
        In basketball, it peaked during roster changes. Different triggers,
        same underlying pattern."
        """
        pass
```

**Portability:** The coach's intelligence profile travels with them. When they join a new team or switch sports, they bring their accumulated pattern recognition. The system learns from each new context and refines its suggestions.

---

## 7. Post-Career and Cross-Domain Recontextualization

### 7.1 The Problem

Ambition, Belonging, and Craft are currently framed for sport. But the needs they measure (autonomy, relatedness, competence) are universal per SDT. The platform should not expire when the athlete retires.

### 7.2 Spec

**New config:** `config/domain_contexts.yaml`

```yaml
contexts:
  sport:
    ambition:
      label: "Ambition"
      description: "Goal pursuit and autonomous motivation in sport"
      example_items: "How often did you feel excited about a goal you're working toward?"
    belonging:
      label: "Belonging"
      description: "Relationships and connection within your team"
      example_items: "How often did you feel genuinely heard by a teammate?"
    craft:
      label: "Craft"
      description: "Skill development and mastery in your sport"
      example_items: "How often did you lose track of time working on a specific skill?"
  
  professional:
    ambition:
      label: "Drive"
      description: "Goal pursuit and autonomous motivation in your career"
      example_items: "How often did you feel genuinely excited about a project you're leading?"
    belonging:
      label: "Connection"
      description: "Relationships and trust within your team or organization"
      example_items: "How often did you feel you could be honest with a colleague?"
    craft:
      label: "Mastery"
      description: "Skill development and competence in your professional domain"
      example_items: "How often did you lose track of time working on a complex problem?"
  
  transition:  # post-career athletes, career changers
    ambition:
      label: "Purpose"
      description: "Direction and meaning beyond sport"
      example_items: "How often did you feel a sense of direction about what comes next?"
    belonging:
      label: "Community"
      description: "Connection and identity beyond your team"
      example_items: "How often did you feel part of a group that knows you, not your athlete identity?"
    craft:
      label: "Growth"
      description: "Learning and competence in new domains"
      example_items: "How often did you feel challenged in a way that felt productive?"
  
  military:
    ambition:
      label: "Mission"
      description: "Purpose and autonomous commitment to objectives"
    belonging:
      label: "Unit Cohesion"
      description: "Trust and connection within your unit"
    craft:
      label: "Proficiency"
      description: "Tactical and technical skill development"
```

**Scoring engine change:** The underlying subscale structure (6 subscales, 0-10 normalized) remains identical across contexts. Only the item wording, narrative templates, and base rates change. An athlete's longitudinal profile carries across contexts because the measurement model is the same.

**Continuity narrative:** "Your need for Craft (now called Growth) has been your strongest domain for 4 years. In sport, it showed up as technical obsession. In your new career, it shows up as rapid skill acquisition. The need is the same. The expression changed."

---

## 8. Threshold Personalization

### 8.1 The Problem

Fixed thresholds (satisfaction >= 6.46, frustration >= 4.38) apply the same standard to every athlete. An athlete whose baseline satisfaction is 9.0 dropping to 6.5 is classified as Thriving, but they are in relative decline. An athlete whose baseline is 5.0 rising to 6.5 is also classified as Thriving, but they are improving. The fixed threshold misses both stories.

### 8.2 Spec

**Enhancement to `bayesian_scorer.py`:**

After 6+ measurements, replace population thresholds with personalized thresholds derived from the athlete's own posterior distribution.

```python
def personalized_thresholds(self, athlete_history: list[float]) -> dict:
    """
    Personalized threshold = athlete's posterior mean - 1.5 * posterior_sd
    
    An athlete with mean satisfaction of 8.5 (SD 0.8) has a personal
    "concern" threshold of 7.3, not the population 6.46.
    
    An athlete with mean satisfaction of 5.2 (SD 1.1) has a personal
    "concern" threshold of 3.55, not the population 6.46.
    
    This means:
    - High-baseline athletes get flagged earlier (their decline is real)
    - Low-baseline athletes don't get perpetually flagged (their normal is lower)
    """
    pass
```

**Guardrails:**
- Personalized thresholds cannot drop below an absolute floor (e.g., satisfaction < 3.0 is always concerning regardless of personal baseline).
- Personalized thresholds only activate after 6+ measurements (need sufficient data to estimate personal baseline).
- Population thresholds remain as the reference for cross-athlete comparison. Personalized thresholds are for within-athlete change detection.

---

## 9. 6-Item Onboarding Redesign

### 9.1 The Problem

The 6-item tier has 0.714 reliability and 50% interpretation confidence, but it is the first thing athletes see. It anchors self-perception on weak measurement.

### 9.2 Spec

**Remove archetype labels from the 6-item tier.** Replace with:

1. **Domain-level directional signals only.** "Your responses suggest Ambition is your strongest area right now. Belonging and Craft are still developing."

2. **Probability distribution over archetypes.** "Based on your initial responses, you are most likely a Pioneer (62%) or an Architect (28%). Take the full assessment for a clearer picture." This is the Bayesian posterior with a weak likelihood.

3. **Invitation framing.** "This is a starting point, not a label. Your profile will sharpen with each assessment."

4. **No frustration signatures at 6 items.** The measurement is too weak to detect nuanced patterns. Show only satisfaction-level directional signals.

---

## 10. Methods

### 10.1 Statistical Methods

This section documents the statistical and computational methods underlying each new module. All methods are standard in psychometrics and Bayesian statistics; citations to foundational references are provided.

#### 10.1.1 Bayesian Conjugate Normal Updating (bayesian_scorer.py)

**Method:** Conjugate normal-normal model for sequential estimation of latent trait scores.

**Mathematical formulation:**

Given a prior distribution $\theta \sim N(\mu_0, \sigma_0^2)$ and a new observation $x$ with known measurement error $\sigma_e^2$:

$$\mu_{\text{posterior}} = \frac{\mu_0 / \sigma_0^2 + x / \sigma_e^2}{1/\sigma_0^2 + 1/\sigma_e^2}$$

$$\sigma_{\text{posterior}}^2 = \frac{1}{1/\sigma_0^2 + 1/\sigma_e^2}$$

**Rationale:** The conjugate normal model is the simplest closed-form Bayesian update. It avoids MCMC sampling, making it computationally trivial for real-time scoring. The measurement error $\sigma_e^2$ comes from the IRT standard error (already computed in `irt_estimation.py` via EAP scoring).

**Prior specification:**
- First measurement: $\mu_0$ = population mean from `config/base_rates.yaml` (stratified by demographics); $\sigma_0$ = population SD from `config/norming_tables.yaml`
- Subsequent measurements: prior = previous posterior (sequential updating)

**Convergence behavior:** After $n$ measurements with equal measurement error, the prior weight decays as $1/(1 + n \cdot \sigma_0^2 / \sigma_e^2)$. With typical values ($\sigma_0 = 2.0$, $\sigma_e = 0.8$), the prior contributes less than 10% of the posterior after 6 measurements.

**Reference:** Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., & Rubin, D. B. (2013). *Bayesian Data Analysis* (3rd ed.). Chapman and Hall/CRC. Chapter 2.

#### 10.1.2 Base Rate Application via Bayes' Theorem (base_rate_engine.py)

**Method:** Application of Bayes' Theorem to adjust domain state classification probabilities using demographic-stratified population priors.

**Mathematical formulation:**

$$P(\text{State}_i \mid \text{Score}) = \frac{P(\text{Score} \mid \text{State}_i) \cdot P(\text{State}_i)}{\sum_{j} P(\text{Score} \mid \text{State}_j) \cdot P(\text{State}_j)}$$

Where:
- $P(\text{State}_i)$ = base rate prior for state $i$ from epidemiological data (Section 2.2)
- $P(\text{Score} \mid \text{State}_i)$ = likelihood from the score distribution within state $i$, estimated from simulation data or empirical data when available
- The denominator is the marginal probability of the observed score (law of total probability)

**Prior sources:**
- Near-constant mental exhaustion rates (NCAA SAHWS 2022-23, N=23,272) map to Distressed + Vulnerable states
- Any-recent mental exhaustion rates (ACHA-NCHA 2018-19, N=9,057) provide upper-bound priors
- ABQ exhaustion subscale means (Madigan et al., 2022, k=91, N=21,012) provide continuous frustration priors

**Likelihood estimation:** During simulation phase, likelihoods are estimated from the simulated score distributions within each domain state. During empirical phase, these are replaced with observed distributions from real athlete data.

**Stratification:** Priors are stratified by gender, sexual orientation, race/ethnicity, financial stress, division, and sport type. When multiple demographic factors apply, priors are combined via the most specific available stratum (not multiplied, to avoid independence assumptions that do not hold for intersecting identities).

**Reference:** Diez, D. M., Cetinkaya-Rundel, M., & Barr, C. D. (2019). *OpenIntro Statistics* (4th ed.). Section 3.2.8, pp. 104-108.

#### 10.1.3 Transition Classification (transition_engine.py)

**Method:** Deterministic classification of archetype transitions using a growth hierarchy, with confidence gating via posterior probability.

**Growth hierarchy:** Archetypes are ordered by the number of active domains (satisfaction >= 5.5):

| Level | Active domains | Archetypes |
|-------|---------------|------------|
| 0 | 0 | Seeker |
| 1 | 1 | Pioneer, Anchor, Artisan |
| 2 | 2 | Captain, Architect, Mentor |
| 3 | 3 | Integrator |

**Classification rules:**

| Transition | Rule |
|-----------|------|
| Growth | Level increases (e.g., Level 1 to Level 2) |
| Exploration | Level unchanged, different archetype (e.g., Pioneer to Anchor) |
| Regression | Level decreases (e.g., Level 3 to Level 1) |
| Fluctuation | Transition reversed within 2 measurements, OR posterior confidence < 0.60 |
| Sustained | Same archetype for 3+ consecutive measurements |

**Confidence gating:** Transitions are only classified as Growth, Exploration, or Regression when the Bayesian posterior confidence for both the previous and current archetype exceeds 0.60. Below this threshold, the transition is classified as Fluctuation regardless of direction. This prevents over-interpreting noise as meaningful change.

**Reference:** This classification system is original to Ero. The growth hierarchy follows from SDT's prediction that need satisfaction tends to broaden over development (Ryan & Deci, 2017, *Self-Determination Theory: Basic Psychological Needs in Motivation, Development, and Wellness*).

#### 10.1.4 Narrative Generation (narrative_engine.py)

**Method:** Template-based text generation with conditional logic driven by scoring outputs.

**Architecture:** Each narrative output is a function of:
1. Current archetype and domain states (determines template selection)
2. Posterior confidence (determines hedging language: "likely" vs. "clearly")
3. Measurement count (determines explanatory vs. reflective framing)
4. Transition history (determines growth narrative availability)
5. Audience (athlete vs. coach: determines vocabulary and action orientation)

**Template hierarchy:**
- Level 1: Archetype identity (8 templates per audience)
- Level 2: Domain state overlay (4 states x 3 domains = 12 modifiers per template)
- Level 3: Frustration signature (6 signature narratives per audience)
- Level 4: Transition narrative (5 transition types x 56 possible archetype pairs = up to 280 transition narratives, most generated from parameterized templates rather than hand-written)
- Level 5: Longitudinal reflection prompts (generated from trajectory pattern classification)

**Validation approach:** Narrative quality is validated through Phase D (Section 12.4): athlete engagement tracking, coach feedback, and A/B testing of framings.

#### 10.1.5 Coach Intelligence Aggregation (coach_intelligence.py)

**Method:** Descriptive statistics and pattern recognition across a coach's historical athlete data.

**Archetype distribution:** Frequency counts and proportions across all athletes the coach has worked with, segmented by sport, team, and time period.

**Frustration pattern analysis:** For each frustration signature, compute:
- Median recovery time (measurements from first detection to resolution)
- Recovery rate (proportion of flagged athletes who recover within 4 measurements)
- Coach's recovery rate vs. population recovery rate (paired comparison)

**Intervention effectiveness:** Requires coach-logged intervention events. Computes:
- Pre/post intervention slope change in frustration subscale (interrupted time series)
- Comparison to matched athletes without logged intervention (propensity score matching when N is sufficient; simple pre/post comparison when N is small)

**Cross-sport insights:** When a coach has data from 2+ sport contexts, compute:
- Archetype distribution differences across sports
- Frustration signature timing differences (e.g., mid-season vs. roster-change triggers)
- Common patterns that persist across contexts (coach's "signature" coaching challenges)

**Minimum data requirements:**
- Archetype distribution: 10+ athletes
- Frustration patterns: 20+ athletes with 3+ measurements each
- Intervention effectiveness: 10+ logged interventions with pre/post data
- Cross-sport insights: 10+ athletes per sport context

#### 10.1.6 Threshold Personalization

**Method:** Empirical Bayes shrinkage of individual thresholds toward population thresholds.

**Formulation:**

$$\tau_{\text{personal}} = \max\left(\mu_{\text{posterior}} - k \cdot \sigma_{\text{posterior}}, \tau_{\text{floor}}\right)$$

Where:
- $\mu_{\text{posterior}}$ = athlete's posterior mean from Bayesian scorer
- $\sigma_{\text{posterior}}$ = athlete's posterior SD
- $k$ = 1.5 (configurable; corresponds to roughly the 7th percentile of the athlete's personal distribution)
- $\tau_{\text{floor}}$ = absolute minimum threshold (3.0 for satisfaction, 7.0 for frustration) below/above which concern is always flagged

**Activation:** Personalized thresholds activate after 6+ measurements (posterior SD sufficiently narrow). Before 6 measurements, population thresholds apply.

**Dual reporting:** Both population-referenced and person-referenced classifications are reported. Population reference enables cross-athlete comparison. Person reference enables within-athlete change detection.

**Reference:** Morris, C. N. (1983). Parametric empirical Bayes inference: Theory and applications. *Journal of the American Statistical Association*, 78(381), 47-55.

### 10.2 Software Methods

#### 10.2.1 Module Dependencies

```
base_rate_engine.py
    <- config/base_rates.yaml
    <- config/norming_tables.yaml (existing)

bayesian_scorer.py
    <- base_rate_engine.py (for initial prior)
    <- irt_estimation.py (existing; for measurement SE)
    <- scoring_pipeline.py (existing; for raw scores)

transition_engine.py
    <- bayesian_scorer.py (for posterior confidence)
    <- type_derivation.py (existing; for archetype classification)

narrative_engine.py
    <- bayesian_scorer.py (for confidence language)
    <- transition_engine.py (for growth narratives)
    <- frustration_signatures.py (existing; for signature narratives)
    <- domain_classification.py (existing; for state narratives)
    <- config/narrative_templates.yaml (new)

coach_intelligence.py
    <- bayesian_scorer.py (for per-athlete posteriors)
    <- transition_engine.py (for transition patterns)
    <- narrative_engine.py (for coach-facing text)
```

#### 10.2.2 Testing Strategy

Each new module requires:

| Test type | Requirement | Coverage |
|-----------|------------|----------|
| Unit tests | All public methods | 100% of public API |
| Ground truth tests | Known-answer cases matching hand calculations | Bayesian update formula, Bayes' Theorem application, transition classification |
| Integration tests | Full pipeline with new modules | End-to-end scoring produces posterior distributions, narratives, and transitions |
| Property-based tests | Invariants that must hold | Posterior SD always decreases with more data; prior weight monotonically decreases; growth hierarchy is a total order |
| Regression tests | Existing 493 tests continue passing | No existing behavior changes |

**Test count estimate:** ~120 new tests across 5 new modules.

#### 10.2.3 Configuration Management

All new configuration files follow the existing pattern in `config/`:
- YAML format with `data_source` field (synthetic vs. literature_derived vs. empirical)
- `last_updated` timestamp
- Version-controlled in git
- Machine-readable for automated validation pipeline

New config files:
- `config/base_rates.yaml` (Section 2.3)
- `config/domain_contexts.yaml` (Section 7.2)
- `config/narrative_templates.yaml` (Section 3.2)

---

## 11. Mobile-Responsive Design

### 11.1 Current State

The existing dashboard (`outputs/site/index.html`) is a single HTML file (~285KB) with Chart.js visualizations. It has a basic responsive breakpoint at 768px that collapses the sidebar and stacks grid layouts. However, the mobile experience has significant gaps:

- Assessment form is desktop-optimized (small touch targets, no swipe navigation)
- Chart.js canvases do not adapt legend/label sizing for small screens
- Narrative text (new in this plan) has no mobile typography system
- No touch gesture support for chart interaction
- Tab navigation requires precise taps on small text
- No offline/PWA capability for athletes taking assessments in low-connectivity environments (gyms, fields)

### 11.2 Design Principles

The ABC assessment is primarily a mobile product. Athletes take assessments on their phones between training sessions. Coaches check dashboards on tablets at practice. Desktop is the secondary context (analysis, report generation, research).

**Mobile-first design:** All new components are designed for 320px minimum width and scaled up, not desktop-first and scaled down.

**Touch-first interaction:** Minimum touch target 44x44px (Apple HIG). Swipe navigation between assessment items. Pull-to-refresh for latest results.

**Progressive disclosure:** Show the narrative first. Scores and charts are available on tap/expand but do not compete with the primary message.

### 11.3 Breakpoint System

| Breakpoint | Target | Layout behavior |
|-----------|--------|----------------|
| < 375px | Small phones (iPhone SE) | Single column. Stacked cards. Abbreviated narratives. No charts inline (expandable). |
| 375-428px | Standard phones (iPhone 14/15) | Single column. Full narrative text. Inline sparkline charts. Bottom tab navigation. |
| 429-768px | Large phones, small tablets | Single column with wider cards. Inline charts at reduced size. Bottom tab navigation. |
| 769-1024px | Tablets (iPad) | Two-column layout. Side-by-side domain cards. Sidebar navigation returns. Charts at full size. |
| > 1024px | Desktop | Current dashboard layout. Three-column domain grid. Full sidebar with simulation controls. |

### 11.4 Component-Level Mobile Specs

#### 11.4.1 Assessment Form (Athlete-facing)

**Current:** Grid of Likert scale radio buttons, desktop-optimized.

**Mobile redesign:**

```
┌─────────────────────────┐
│  Question 3 of 36       │
│  ━━━━━━━━━░░░░░░░░░░░░  │  <- progress bar
│                         │
│  In the past two weeks, │
│  how often did you feel │
│  genuinely excited      │
│  about a goal?          │
│                         │
│  ┌───┐ ┌───┐ ┌───┐     │
│  │ 1 │ │ 2 │ │ 3 │     │  <- large touch targets (min 48x48px)
│  │   │ │   │ │   │     │
│  └───┘ └───┘ └───┘     │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐
│  │ 4 │ │ 5 │ │ 6 │ │ 7 │  <- 7-point Likert, 2 rows on small screens
│  │   │ │   │ │   │ │   │
│  └───┘ └───┘ └───┘ └───┘
│  Never        Very Often │
│                         │
│     ← swipe to advance →│
└─────────────────────────┘
```

**Interaction:**
- Swipe left/right to navigate between questions (with haptic feedback on iOS)
- Tap number to select; auto-advance to next question after 300ms delay
- Swipe down to see progress overview (which questions answered, estimated time remaining)
- Back button returns to previous question (does not lose answers)
- Answers persist locally (localStorage) so a closed browser does not lose progress

#### 11.4.2 Results View (Athlete-facing)

**Mobile layout (single column, narrative-first):**

```
┌─────────────────────────┐
│  Your Profile            │
│                         │
│  ┌─────────────────────┐│
│  │  🏹 Pioneer          ││  <- archetype card with domain color
│  │                     ││
│  │  You lead with      ││
│  │  Ambition. Your     ││  <- narrative paragraph, not scores
│  │  drive is genuine.  ││
│  └─────────────────────┘│
│                         │
│  ┌─── Ambition ────────┐│
│  │  Thriving (87%)     ││  <- confidence from Bayesian posterior
│  │  ██████████░░  8.2  ││  <- horizontal bar, score on right
│  └─────────────────────┘│
│  ┌─── Belonging ───────┐│
│  │  Vulnerable (62%)   ││
│  │  ███████░░░░░  6.8  ││
│  │                     ││
│  │  ⚠ Conditional      ││  <- frustration signature inline
│  │    Belonging         ││
│  └─────────────────────┘│
│  ┌─── Craft ───────────┐│
│  │  Developing         ││
│  │  ████░░░░░░░░  4.1  ││
│  └─────────────────────┘│
│                         │
│  ▼ Reflection prompts   │  <- expandable section
│  ▼ Detailed scores      │  <- expandable section
│  ▼ Trajectory (3+ meas) │  <- expandable section
│                         │
│  ┌─────────────────────┐│
│  │ Take Full Assessment ││  <- CTA if on 6-item tier
│  └─────────────────────┘│
└─────────────────────────┘
```

**Key decisions:**
- Narrative text is the primary content, not scores
- Scores appear as compact horizontal bars within domain cards
- Frustration signatures appear inline within the affected domain card (not a separate section)
- Detailed breakdowns, trajectory charts, and reflection prompts are in expandable accordions
- Confidence percentage shown next to state label (from Bayesian posterior)

#### 11.4.3 Coach Dashboard (Tablet-optimized)

**Tablet layout (769-1024px, landscape orientation):**

```
┌──────────┬──────────────────────────────┐
│ Athletes │  Selected: Jordan Mitchell    │
│          │                              │
│ ● Jordan │  Pioneer → Captain (Growth)  │  <- transition badge
│ ○ Taylor │                              │
│ ○ Sam    │  ┌────────┬────────┬────────┐│
│ ○ Alex   │  │Ambition│Belong. │ Craft  ││  <- 3-column domain grid
│          │  │Thriving│Vulner. │ Mild   ││
│ ──────── │  │  8.2   │  6.8   │  4.1   ││
│ Alerts(2)│  └────────┴────────┴────────┘│
│ ● Jordan │                              │
│ ● Sam    │  Narrative for coach:        │
│          │  "Jordan's Belonging..."     │
│          │                              │
│          │  ▼ Trajectory (chart)        │
│          │  ▼ Frustration history       │
│          │  ▼ Intervention log          │
└──────────┴──────────────────────────────┘
```

**Phone layout (< 768px):**
- Bottom tab bar: Athletes | Alerts | Insights | Settings
- Athletes tab: scrollable list with state badges, tap to expand
- Alerts tab: priority-sorted list of athletes needing attention
- Insights tab: coach intelligence summaries (archetype distribution, patterns)

#### 11.4.4 Charts on Mobile

**Chart.js responsive configuration:**

```javascript
const mobileChartConfig = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: window.innerWidth > 768,  // hide legends on mobile
      position: 'bottom',
      labels: { 
        font: { size: window.innerWidth < 428 ? 10 : 12 },
        boxWidth: 12,
        padding: 8
      }
    },
    tooltip: {
      enabled: true,
      mode: 'nearest',
      intersect: false,  // easier to trigger on touch
      bodyFont: { size: 14 },  // larger tooltip text for readability
    }
  },
  scales: {
    x: {
      ticks: { 
        font: { size: window.innerWidth < 428 ? 9 : 11 },
        maxRotation: 45  // angled labels on small screens
      }
    },
    y: {
      ticks: { 
        font: { size: window.innerWidth < 428 ? 9 : 11 }
      }
    }
  }
};
```

**Sparkline charts** for mobile (no axes, no legends, inline with text):
- Trajectory sparklines: 120x40px inline SVG showing last 6 measurements
- Frustration trend: single-line sparkline with color gradient (green to red)
- Used in athlete results view and coach athlete list

**Full charts** available in expandable sections with pinch-to-zoom support.

#### 11.4.5 Narrative Text Typography

```css
/* Mobile-first narrative typography */
.narrative-body {
  font-family: 'Georgia', serif;  /* matches existing type name styling */
  font-size: 1rem;                /* 16px base */
  line-height: 1.6;
  color: #2d3748;
  max-width: 65ch;                /* optimal reading width */
  padding: 0 1rem;
}

.narrative-body .highlight {
  font-weight: 600;
  color: #1a202c;
}

.reflection-prompt {
  font-style: italic;
  border-left: 3px solid #4299e1;  /* Belonging blue */
  padding-left: 1rem;
  margin: 1.5rem 0;
}

/* Tablet+ gets slightly larger text */
@media (min-width: 769px) {
  .narrative-body {
    font-size: 1.125rem;           /* 18px */
    padding: 0 2rem;
  }
}
```

### 11.5 Offline and Progressive Web App (PWA)

Athletes take assessments in environments with poor connectivity: gyms, practice fields, team buses. The assessment must work offline.

**Service worker strategy:**
- Cache assessment questions and scoring logic on first load
- Store responses in IndexedDB while offline
- Sync to server when connectivity returns
- Show "saved locally, will sync when online" confirmation
- Narrative templates cached for offline result display

**PWA manifest:**
- Installable on iOS and Android home screens
- App name: "ABC Assessment"
- Theme color: domain-adaptive (Ambition red, Belonging blue, Craft green based on athlete's primary domain)
- Splash screen with athlete's archetype icon

### 11.6 Accessibility Requirements

| Requirement | Standard | Implementation |
|------------|---------|----------------|
| Touch targets | WCAG 2.2 Target Size (2.5.8) | Minimum 44x44px for all interactive elements |
| Color contrast | WCAG 2.1 AA (1.4.3) | 4.5:1 minimum for body text, 3:1 for large text |
| Screen reader | WCAG 2.1 (4.1.2) | ARIA labels on all interactive elements, chart descriptions as alt text |
| Reduced motion | WCAG 2.1 (2.3.3) | `prefers-reduced-motion` media query disables animations |
| Dynamic content | WCAG 2.1 (4.1.3) | `aria-live` regions for score updates and narrative changes |
| Focus management | WCAG 2.1 (2.4.3) | Logical tab order; focus returns to trigger after accordion collapse |
| Text scaling | WCAG 2.1 (1.4.4) | All text in rem/em units; layout functional at 200% zoom |

---

## 12. Research-Driven Model Refinements

The following refinements are derived from the mental fatigue research corpus (50 papers reviewed in 00-Master-Summary.md) and the Grugan et al. (2024) ABQ validation study. Each refinement identifies what the research found, what it changes in the spec, and which module is affected.

### 12.1 Dual-Timescale Fatigue Model

**Research basis:** Muller et al. (2021, Nature Communications) identified two hidden fatigue states operating on different timescales. One is "recoverable" (restored by rest); the other is "unrecoverable" (accumulates with sustained work). Separate medial and lateral frontal regions track these states.

**What this changes:** The trajectory engine (Section 5) should classify frustration signals as acute or chronic, not just by trajectory shape.

**Implementation:** Add fatigue timescale classification to `transition_engine.py`:

```python
class FatigueTimescale(Enum):
    ACUTE = "acute"       # Single spike, likely recoverable with rest/schedule change
    CHRONIC = "chronic"   # Sustained trend, requires structural change in need satisfaction
    MIXED = "mixed"       # Acute spike on top of chronic trend

def classify_fatigue_timescale(
    frustration_history: list[float],
    window_short: int = 2,   # measurements (~4 weeks)
    window_long: int = 6     # measurements (~12 weeks)
) -> FatigueTimescale:
    """
    Acute: RCI exceeds threshold in short window but long-window trend is flat
    Chronic: Long-window slope is significantly negative (satisfaction) or positive (frustration)
    Mixed: Both conditions met simultaneously
    
    Reference: Muller et al. (2021), dual-state computational fatigue model
    """
    pass
```

**Narrative impact:** Acute frustration generates: "This looks like a spike, not a trend. A schedule change or recovery period may be enough." Chronic frustration generates: "This pattern has been building for weeks. The environment may need to change, not just the schedule."

### 12.2 Effort-Cost Reframing of Frustration

**Research basis:** Blain et al. (2016, PNAS), Pessiglione et al. (2025, Trends in Cognitive Sciences), Kok (2022, Brain and Cognition), Steward et al. (2025, Journal of Neuroscience), and Van Cutsem et al. (2017, Sports Medicine, systematic review of 11 studies) all converge: cognitive fatigue does not reduce capacity. It shifts cost-benefit calculations. Van Cutsem specifically found that mental fatigue impairs endurance performance through higher perceived exertion, not through physiological changes (heart rate, VO2, lactate all unaffected).

**What this changes:** The narrative engine should reframe frustration from "something is wrong" to "the cost of effort is rising relative to the reward." This is a more accurate and less stigmatizing frame.

**Narrative templates (update to Section 3.2):**

| Current framing | Research-informed reframing |
|----------------|---------------------------|
| "Your Craft frustration is elevated" | "The effort required for skill development feels higher than the reward right now" |
| "Your Ambition is in a Distressed state" | "Goal pursuit costs more energy than it returns. This is a signal about your environment, not your character" |
| "Frustration signature: Blocked Drive" | "Your motivation is intact but the path forward feels blocked. The mental cost of pushing through is rising" |

### 12.3 Self-Report Limitation Disclosure

**Research basis:** Pessiglione et al. (2025) argue explicitly that cognitive fatigue "is not transparently accessed via introspection." Massar et al. (2018) demonstrate effort-discounting paradigms as more valid fatigue markers. Randles et al. (2017, PLOS ONE, N=17,621) found minimal time-of-day performance variation despite expected depletion.

**What this changes:** The narrative engine should include a measurement limitations disclosure for athletes, and the coach dashboard should emphasize coach observations as complementary to (not redundant with) self-report.

**Athlete-facing disclosure (added to results view):**

> "These scores reflect how you perceive your motivation and frustration. Research shows that cognitive fatigue can shift your behavior, choosing lower-effort options, reduced endurance, before you consciously feel fatigued. If your coach or teammates notice changes you don't, that signal matters too."

**Coach-facing note:**

> "Self-report underestimates cognitive fatigue. Your behavioral observations (effort choices, endurance changes, decision quality) may detect fatigue before the athlete's scores shift. Use your ratings as an independent signal, not just a confirmation of the assessment."

### 12.4 Autonomy Paradox for High-Ambition Athletes

**Research basis:** Lee et al. (2025, Personality and Social Psychology Bulletin) found that daily decision-making autonomy triggers task reflexivity (cognitive processing about tasks), which causes next-day mental fatigue. This challenges a simple "more autonomy = better" reading of SDT.

**What this changes:** High Ambition satisfaction is currently treated as purely positive. The research reveals a hidden cost for athletes who carry heavy decision-making loads (team captains, athlete-leaders, senior players).

**Narrative addition for Ambition Thriving athletes (measurement 3+):**

> "Your Ambition satisfaction is strong. Athletes with high autonomy sometimes accumulate decision fatigue without noticing. A question to sit with: how much of your mental energy goes to decisions others could share?"

**Connection to existing Overinvestment Pattern (abc-assessment-spec.md, Section 2.2):** The autonomy paradox provides the theoretical basis for why overinvestment occurs. The Overinvestment Pattern detects it through cross-referencing daily cognitive signals. The narrative engine should connect these: when an Overinvestment Warning fires, the narrative should reference the autonomy paradox specifically.

### 12.5 Burnout Transmission Detection

**Research basis:** Shen et al. (2015, British Journal of Educational Psychology) demonstrated that teacher emotional exhaustion reduces students' perceived autonomy support, and teacher depersonalization negatively predicts students' autonomous motivation. Olafsen et al. (2017) and Niemiec et al. (2022) show need frustration spills across role boundaries.

**What this changes:** The coach intelligence layer (Section 6) should detect when multiple athletes under one coach show simultaneous frustration increases, as this pattern may signal coach-level rather than athlete-level distress.

**Implementation addition to `coach_intelligence.py`:**

```python
def detect_transmission_signal(
    self, 
    coach_id: str,
    window: int = 2  # measurement periods
) -> dict | None:
    """
    Flags when 3+ athletes under one coach show rising Belonging
    frustration in the same measurement window. 
    
    Returns None if no signal detected.
    Returns dict with:
      - affected_athletes: list of athlete IDs
      - domain: which domain shows correlated frustration
      - confidence: proportion of coach's athletes affected
      - narrative: "Three of your athletes' Belonging frustration 
        scores rose in the same window. This pattern sometimes 
        reflects changes in the coaching environment rather than 
        individual athlete experiences."
    
    Reference: Shen et al. (2015), burnout transmission model
    """
    pass
```

### 12.6 ESEM Validation Priority

**Research basis:** Grugan et al. (2024, Psychology of Sport & Exercise, N=914) found ESEM provided superior fit for the ABQ (CFI=.964, RMSEA=.093, SRMR=.027) over CFA (CFI=.853, RMSEA=.160, SRMR=.086). Cross-loadings were meaningful but interpretable. ABQ was approximately invariant across gender (n=377 female, n=532 male), sport type (n=344 individual, n=570 team), and age (n=416 under 18, n=498 over 18).

**What this changes:** The current validation framework uses CFA exclusively (gold-standard plan Phase 3). ESEM was listed as "deferred." Grugan et al. provide strong justification to prioritize it: if the ABQ (a simpler 15-item, 3-factor instrument) requires ESEM for adequate fit, the ABC (36-item, 6-factor) almost certainly does too. The ABC's satisfaction and frustration subscales within each domain likely have cross-loadings similar to the ABQ's RSA-SD overlap.

**Validation roadmap update:** Move ESEM from "deferred" to Phase A (Section 13.1). Specifically:
- Run both CFA and ESEM on Phase A pilot data (N >= 100)
- Compare fit indices using the same criteria as Grugan et al. (CFI > .90, TLI, RMSEA 90% CI < .08, SRMR < .08)
- If ESEM provides superior fit, adopt ESEM as the primary factor model for the ABC
- Test measurement invariance across gender and sport type using ESEM invariance methodology (alignment method per Asparouhov & Muthen, 2023, as used by Grugan et al.)

### 12.7 Motivation Profile Stability Calibration

**Research basis:** Fernet et al. (2020, European Journal of Work and Organizational Psychology, N=510) found motivation profiles were highly stable over 4 months via latent transition analysis. Gustafsson et al. (2018, Psychology of Sport & Exercise) found athletes with high autonomous AND controlled motivation had the lowest burnout on RSA and SD subscales. Lonsdale & Hodge (2011, Medicine & Science in Sports & Exercise, N=119) established temporal ordering: low self-determination preceded burnout, not the reverse.

**What this changes:** The current transition engine classifies archetype changes with a confidence threshold of 0.60. The research suggests profiles should be more stable than the current 50-55% retest agreement indicates. The discrepancy is likely measurement noise, not genuine instability.

**Implementation change:** Increase the confidence threshold for reporting transitions from 0.60 to 0.75 for changes occurring within 4 weeks (2 measurement periods). Maintain 0.60 for changes spanning 8+ weeks. The rationale: if Fernet et al. show 4-month stability in workplace motivation profiles, a 2-week type change in an athlete is more likely noise than signal.

```python
def confidence_threshold_for_window(self, weeks_elapsed: int) -> float:
    """
    Shorter windows require higher confidence to report a transition.
    
    Reference: Fernet et al. (2020), 4-month profile stability
    """
    if weeks_elapsed <= 4:
        return 0.75  # very high bar for rapid changes
    elif weeks_elapsed <= 8:
        return 0.65  # moderate bar
    else:
        return 0.60  # standard bar for longer-term changes
```

---

## 13. Validation Roadmap

### 13.1 Phase A: Empirical Pilot (target: 2026 Q3-Q4)
- N >= 100 athletes, one competitive season (minimum 6 biweekly measurements)
- Co-administer: BPNSFS (need satisfaction/frustration), ABQ (burnout), BFI-2 (Big Five)
- Coach ratings as external criterion
- **Goal:** Calibrate base rates, test threshold positions, validate Big Five inference against BFI-2

### 13.2 Phase B: Full Validation (target: 2027)
- N >= 300 athletes across 3+ sports, both genders, multiple divisions
- Full longitudinal tracking with trajectory analysis
- Measurement invariance testing across demographic groups
- **Goal:** Establish empirical thresholds, transition maps, and cascade model timing

### 13.3 Phase C: Cross-Domain Expansion (target: 2027-2028)
- Develop parallel item sets for professional/military/transition contexts
- Pilot with 50+ professionals in high-stress roles
- Collect occupational health base rates (Maslach Burnout Inventory normative data, military resilience surveys)
- **Goal:** Prove the measurement model generalizes beyond sport

### 13.4 Phase D: Narrative Validation (target: ongoing from Phase A)
- Track athlete engagement with narrative outputs (which prompts generate journaling, coach conversations)
- A/B test narrative framings for behavior change
- Collect coach feedback on intelligence layer utility
- **Goal:** The narratives drive behavior, not just the scores

---

## 14. Implementation Priority

| Priority | Module | Effort | Impact | Depends on |
|----------|--------|--------|--------|------------|
| 1 | `narrative_engine.py` | Medium | High: this is the product | Existing scoring pipeline |
| 2 | `base_rate_engine.py` + `config/base_rates.yaml` | Medium | High: enables Bayesian framing | Literature review (done) |
| 3 | `bayesian_scorer.py` | High | High: transforms longitudinal model | base_rate_engine |
| 4 | `transition_engine.py` | Medium | High: reframes type instability as growth | bayesian_scorer |
| 5 | 6-item onboarding redesign | Low | Medium: prevents anchoring on weak data | bayesian_scorer |
| 6 | `coach_intelligence.py` | High | High: but needs multi-athlete data | Phase A pilot |
| 7 | Threshold personalization | Medium | Medium: needs 6+ measurements per athlete | bayesian_scorer + Phase A |
| 8 | Cross-domain recontextualization | High | Long-term: new item sets required | Phase B validation |

---

## 15. Architecture Principle

Every improvement follows the same Bayesian logic:

1. **Start with a prior.** Population base rates, demographic stratification, or the athlete's own history.
2. **Collect evidence.** Each measurement is a likelihood function that updates the prior.
3. **Compute the posterior.** The current best estimate of who this athlete is, with explicit uncertainty.
4. **Generate narrative from the posterior.** Not from the raw score. The narrative reflects what we know, what we do not know, and how confidence has changed.
5. **Repeat.** The posterior from this measurement becomes the prior for the next.

The athlete's profile is never finished. It is always updating. This is what makes it a personalization engine rather than a test.
