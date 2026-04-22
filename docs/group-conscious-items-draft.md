# Group-Conscious Items Draft

Date: 2026-04-20
Status: Draft, pending expert review and cognitive pretesting
Source plan: improvement-plan-personalization-engine.md Section 16.5

## 1. Purpose

This document presents 5 items that operationalize the group-conscious stance from Chapter 53 of the Oxford Handbook of Self-Determination Theory (Thomaes et al.). Unlike the existing context-gap analysis, which compares an athlete's personal subscale scores to the same athlete's team-context subscale scores, these items measure what the athlete *perceives about other athletes' experience* and how strongly the athlete identifies with the team as a group.

The practical payoff: an athlete who is personally Thriving on Belonging but perceives that teammates are struggling, and who identifies strongly with the team, experiences empathic need-thwarting that existing measurements do not capture.

The items are paired with a team-level dispersion metric (computed across athletes, not per-athlete) that flags teams where need satisfaction is highly unequal across members, even when the team mean looks healthy.

These items are original to Ero. No licensed scale content is reproduced.

## 2. Design constraints

- **Cadence:** Biweekly, joins the core ABC form. Same cadence as regulatory style.
- **Placement:** Outside `REQUIRED_ITEMS`. Scored by a parallel module.
- **Stem:** "How often in the past two weeks did you..." (identical to the core bank).
- **Response scale:** 1 = Never, 4 = Sometimes, 7 = Very Often.
- **No reverse-scored items:** Five items across three distinct constructs (collective Ambition, collective Belonging, collective Craft, team identification). Reverse coding would compress information.
- **Collective-satisfaction items target perception.** The athlete is reporting what they perceive about teammates, not what teammates are actually reporting. The team-mean of teammates' own ABC responses is a separate signal that the dispersion metric consumes.

## 3. The 5 items

### 3.1 Perceived collective satisfaction

**AG1 (collective Ambition)**
"How often in the past two weeks did you sense that your teammates' goals were meaningful to them?"

- **Construct:** Perceived collective Ambition satisfaction.
- **Rationale:** Chapter 53 argues that group-level need satisfaction is a construct distinct from individual-level satisfaction. An athlete can personally feel their goals matter while perceiving that their teammates are going through the motions. AG1 captures the perceived-other axis.

**BG1 (collective Belonging)**
"How often in the past two weeks did you notice your teammates feeling connected to each other?"

- **Construct:** Perceived collective Belonging satisfaction.
- **Rationale:** Perceived relational quality among teammates, independent of the athlete's own relational experience. A relationally thriving athlete on an otherwise-fractured team will score differently than a relationally thriving athlete on a cohesive team.

**CG1 (collective Craft)**
"How often in the past two weeks did you see your teammates growing in their skills?"

- **Construct:** Perceived collective Craft satisfaction.
- **Rationale:** Perception of teammates' skill development. A team where peers are visibly improving is a different craft environment than one where peers feel stuck, regardless of the focal athlete's own development.

### 3.2 Team identification

Two items. Chapter 53 uses team identification as a moderator: the empathic effect of perceived collective need-thwarting scales with how strongly the athlete identifies with the team.

**TI1**
"How often in the past two weeks did this team's wins or losses feel personal to you?"

- **Construct:** Affective team identification.
- **Rationale:** Captures the felt connection between team outcomes and self. Athletes who emotionally register team events as personal events are more exposed to collective need-thwarting signals.

**TI2**
"How often in the past two weeks did you feel like a real member of this team, not just someone on the roster?"

- **Construct:** Cognitive team identification (membership salience).
- **Rationale:** Distinct from affective identification: an athlete can feel like a real member without every loss cutting personally. Separating the two allows us to tell "emotionally entangled" athletes from "structurally integrated" ones.

## 4. Scoring model

### 4.1 Per-domain collective satisfaction

Each collective-satisfaction item is scored independently on the 0-10 scale:

```
collective_score = ((raw_1_to_7 - 1) / 6) * 10
```

Level classification for narrative selection:

| Score | Level |
|-------|-------|
| >= 7.0 | high |
| >= 4.0 | moderate |
| < 4.0 | low |

### 4.2 Team identification

Mean of TI1 and TI2 on the 1-7 scale, normalized to 0-10. Same level bands.

### 4.3 Empathic risk flag

Fires per domain when:

```
team_identification_score >= 6.0  AND  collective_score[domain] < 4.0
```

Athletes who identify strongly with the team and perceive teammates' needs as thwarted on a given domain are exposed to empathic need-thwarting on that domain, independent of their own personal score. This is the detection Chapter 53 argues the current literature misses.

### 4.4 Evidence gates

Consistent with Section 17.5:

| Condition | Gate | Effect |
|-----------|------|--------|
| Collective-satisfaction item answered | Passes display for that domain | Score shown with level label |
| Both TI items answered | Team identification displayed | Score and level shown |
| Only one TI item answered | TI score shown with hedging | Recommendation gate fails |
| Either team identification or collective satisfaction missing on a domain | Empathic risk suppressed for that domain | Gate reason logged |

## 5. Team-level dispersion metric

The dispersion metric is separate from the group-conscious items. It takes a list of team members' ABC subscale scores and returns per-subscale standard deviations.

```
dispersion[a_sat] = stdev([a_sat for each athlete])
```

Interpretation bands on the 0-10 scale:

| SD | Interpretation |
|----|----------------|
| < 1.5 | Tight: team is experiencing this subscale similarly |
| 1.5 - 2.5 | Moderate spread |
| > 2.5 | High dispersion: perceived inequality is a risk factor in itself |

A team with mean `a_sat = 7.0` and SD `0.8` is a different team than one with the same mean and SD `3.0`. The second team has a split experience that is masked by the mean.

Minimum athletes for dispersion: 3. Below that, the SD is too noisy to interpret.

## 6. Empirical calibration open items

- Reliability of the single-item collective-satisfaction subscales. Single-item reliability is bounded; we may need to expand to two items per domain after Phase A if omega is weak.
- Convergent validity of team identification against an established scale (e.g., Leach et al. multi-component in-group identification, licensing permitting).
- Empirical calibration of the 6.0 / 4.0 empathic-risk thresholds against coach-rated team mental-health outcomes at season end.
- Dispersion thresholds (1.5, 2.5) are theoretical priors. Phase A team-level data will recalibrate.
- Multilevel analysis at Phase A to test Chapter 53's key empirical claim: does perceived collective dissatisfaction predict individual burnout trajectories beyond what personal need satisfaction explains?
