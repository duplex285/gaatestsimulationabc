# ABC Assessment & Scoring Engine — Product Spec

## Strategic Context

ABC is Ero's proprietary psychometric model. It draws on the scientific literature around Self-Determination Theory (Deci & Ryan, 2000) and Deliberately Developmental Organizations (Kegan & Lahey, 2016), but it is not a licensed implementation of either. The instrument, scoring engine, type system, and trajectory model are original to Ero. This matters for four reasons.

**No licensing dependencies.** SDT-based instruments (BPNSFS, PNSE) and DDO diagnostic tools carry usage restrictions and academic licensing expectations. ABC uses the same underlying science — three basic psychological needs, the satisfaction/frustration distinction — but wraps it in an original measurement framework (behavioural frequency items, the six-subscale structure, the 36-type derivation) that Ero owns outright. We reference the science. We do not redistribute someone else's instrument.

**Built on the strongest evidence in the field.** A comprehensive review of 50 studies across 170 million research papers (Consensus, 2026) rates the evidence that need satisfaction reduces burnout at 9/10 and controlled motivation increasing vulnerability at 8/10. These are the two highest-confidence claims in the entire SDT-fatigue literature. The ABC model's six-subscale structure — measuring satisfaction and frustration separately per domain — is directly aligned with these findings. Multiple meta-analyses confirm large effect sizes across healthcare, education, and athletics (Slemp et al., 2024; Fernet et al., 2012; Lonsdale et al., 2009). The science is settled on the core mechanism. What remains is building a proprietary instrument that operationalises it for continuous longitudinal measurement — which is what ABC does.

**Defensible efficacy claims.** Most competitors in the athlete wellness space make vague claims about "mental performance" backed by no psychometric evidence. By computationally validating ABC before empirical deployment — proving the factor structure recovers, the scoring pipeline preserves signal, the type system is stable, and the trajectory model detects real change — Ero can make specific, evidence-backed claims that competitors cannot. "Our model has been validated through confirmatory factor analysis with fit indices exceeding gold-standard thresholds" is a statement no current competitor in this space can make.

**De-risked empirical investment.** A real-world validation study (300+ athletes, one season, parallel administration of established instruments) costs significant time and money. Running the simulation validation first proves the math works, identifies which model parameters are fragile, and sizes the empirical study precisely. If the simulation surfaces structural problems, we fix them computationally — not after recruiting 300 athletes and discovering the instrument doesn't work.

**Filling a documented research gap.** The SDT-fatigue literature has a conspicuous hole: cognitive fatigue in athletes is the least-studied intersection across all populations and outcomes (marked "GAP" in the systematic review coverage matrix). Healthcare, education, and student populations all have multiple studies. Athletes have strong burnout research but almost no work on cognitive fatigue specifically. Ero's combined daily cognitive signals (Cognitive Load, Recovery Slope, Stressor Stacking) plus biweekly ABC assessment is positioned to fill this gap with real longitudinal data. This is not just a product feature — it is a publishable research contribution that positions Ero as the empirical leader in a space where competitors have no data at all.

---

## Problem

The current ABC system derives scores indirectly from daily check-in data using rule-based extraction. This produces single-dimension scores (Ambition, Belonging, Craft on a 0-100 scale) without separating satisfaction from frustration. The theoretical framework requires six subscales (satisfaction + frustration per domain), measured through behavioural frequency questions with temporal anchors. Without that split, the system cannot detect the most important state: the Vulnerable athlete who appears fine on satisfaction but is accumulating frustration.

## What Gets Built

A standalone ABC Assessment instrument administered biweekly, a scoring engine that produces six subscales, and UI surfaces for both players and coaches. The 36-type system, frustration signatures, Belbin inference, and context gap analysis all flow from the six subscale scores. The entire pipeline is validated computationally before production deployment.

---

## 1. The Instrument

### 1.1 Item Structure

30 items total on a 1-7 behavioural frequency scale (1 = Never, 4 = Sometimes, 7 = Very Often):

- **24 core items** (4 per subscale x 6 subscales) measuring the individual
- **6 team items** (1 per subscale) measuring the team environment

Each subscale has 3 forward-scored and 1 reverse-scored item. Items are shuffled across domains to prevent gaming.

All items use a temporal anchor: "In the past two weeks..." or "Since your last check-in..."

### 1.2 Subscale Map

| Subscale | Code | Items | What it captures |
|----------|------|-------|-----------------|
| Ambition Satisfaction | `A-sat` | AS1, AS2, AS3, AS4 (rev) | Goal pursuit feels autonomous and meaningful |
| Ambition Frustration | `A-frust` | AF1, AF2, AF3, AF4 (rev) | Goal pursuit feels controlled, blocked, or pointless |
| Belonging Satisfaction | `B-sat` | BS1, BS2, BS3, BS4 (rev) | Relationships feel authentic and supportive |
| Belonging Frustration | `B-frust` | BF1, BF2, BF3, BF4 (rev) | Relationships feel conditional or performative |
| Craft Satisfaction | `C-sat` | CS1, CS2, CS3, CS4 (rev) | Skill development feels engaging and autonomous |
| Craft Frustration | `C-frust` | CF1, CF2, CF3, CF4 (rev) | Skill development feels stalled or evaluated |

### 1.3 Example Items

| Code | Item |
|------|------|
| AS1 | "How often in the past two weeks did you feel genuinely excited about a goal you're working toward?" |
| AF2 | "How often in the past two weeks did you feel like you were going through the motions without knowing why?" |
| BS3 | "How often in the past two weeks did you have a conversation with a teammate where you felt genuinely heard?" |
| BF1 | "How often in the past two weeks did you feel like you had to perform a version of yourself to fit in?" |
| CS2 | "How often in the past two weeks did you lose track of time working on a specific skill?" |
| CF3 | "How often in the past two weeks did you feel like feedback on your skill was more about judgment than improvement?" |

### 1.4 Cadence

- **Default**: Every 2 weeks during competitive season
- **High-stress**: Weekly during postseason, exam weeks, roster changes (coach-configurable)
- **Minimum viable**: 3 measurement points before trajectory estimation begins

---

## 2. Scoring Engine

### 2.1 Pipeline

```
Raw responses (1-7)
  -> Reverse-score items (8 - r)
  -> Subscale means (1.0 - 7.0)
  -> Normalize to 0-10: ((mean - 1) / 6) * 10
  -> Domain state classification (Thriving / Vulnerable / Mild / Distressed)
  -> Big Five inference (weight matrix -> percentile)
  -> 36-type derivation (dominant domain x primary Big Five trait)
  -> Frustration signature detection
  -> Belbin role inference
  -> Context gap (team vs personal)
  -> Trajectory + volatility (after 3+ measurements)
```

### 2.2 Domain State Classification

Threshold: 5.5 on the 0-10 normalized scale.

| Satisfaction | Frustration | State | Risk |
|-------------|-------------|-------|------|
| >= 5.5 | < 5.5 | **Thriving** | Low |
| >= 5.5 | >= 5.5 | **Vulnerable** | Medium — appears fine but environment is eroding |
| < 5.5 | < 5.5 | **Mild** | Low-medium — disengaged, low salience |
| < 5.5 | >= 5.5 | **Distressed** | High — need actively frustrated |

**The Overinvestment Pattern.** Research shows that highly self-determined individuals can overinvest effort under chronic demands, leading to resource depletion even when their needs appear well-met (Towair et al., 2025; Mobarak et al., 2024). In ABC terms: an athlete who shows sustained high satisfaction across two or more domains (Thriving on both Ambition and Craft, for example) while daily cognitive signals show declining Recovery Slope or rising Cognitive Load may be in an overinvestment state. Their needs are satisfied — so satisfied they cannot stop pushing — but their recovery capacity is eroding.

This pattern is invisible to the ABC assessment alone. It emerges only when the biweekly ABC data is cross-referenced with the daily cognitive signals. The system flags an **Overinvestment Warning** when:

- 2+ domains are Thriving (satisfaction >= 7.0, frustration < 3.0) for 2+ consecutive assessments
- AND daily Cognitive Load signal averages > 70 over the same period
- AND daily Recovery Slope signal averages < 40 over the same period

This is a coach-only alert. The player sees Thriving. The coach sees Thriving plus a recovery concern. The intervention is not to reduce satisfaction — it is to protect recovery.

### 2.3 Big Five Inference

Weight matrix applied to centred subscale scores. Each non-N trait anchors
on its most theoretically defensible ABC domain using a template of three
magnitude tiers (primary/secondary/tertiary). L2 norms are equal by
construction (~0.54 for O/E/A, ~0.56 for C). No post-hoc normalisation.

Domain anchors: O → Craft, C → Craft + Belonging, E → Ambition, A → Belonging, N → all frustration.

| Trait | A-sat | A-frust | B-sat | B-frust | C-sat | C-frust |
|-------|-------|---------|-------|---------|-------|---------|
| Openness | 0.15 | -0.10 | 0.22 | -0.16 | 0.35 | -0.25 |
| Conscientiousness | 0.15 | -0.16 | 0.30 | -0.22 | 0.28 | -0.22 |
| Extraversion | 0.35 | -0.25 | 0.22 | -0.16 | 0.15 | -0.10 |
| Agreeableness | 0.15 | -0.10 | 0.35 | -0.25 | 0.22 | -0.16 |
| Neuroticism | -0.18 | 0.33 | -0.18 | 0.33 | -0.18 | 0.33 |

Steps:
1. Centre each subscale: `(score - 5) / 5` (yields roughly -1.0 to +1.0)
2. Dot product with weight row
3. Convert to percentile: `50 + z * 30`, clamped to [1, 99]

These weights are theoretical priors. The simulation validation (Section 11) tests their sensitivity and identifies which weights are robust versus fragile. Empirical recalibration follows in Phase F.

### 2.4 36-Type Derivation

1. **Dominant domain** = `argmax(A-sat, B-sat, C-sat)`
2. **Primary Big Five trait** = trait with largest `|percentile - 50|`
3. **Direction** = High if percentile >= 50, Low otherwise
4. **Lookup** = `typeMap[domain][direction + trait]`

Produces a named type (e.g., "Mentor", "Forge", "Flow State") with tagline, description, strengths, contribution, and growth edge. The full 36-type catalog already exists in `apps/web/src/lib/data/abc-typology.ts`.

### 2.5 Frustration Signatures

| Pattern | Condition | Label | Risk |
|---------|-----------|-------|------|
| High sat + high frust | sat > 5.5, frust > 5.5 | Blocked Drive / Conditional Belonging / Evaluated Mastery | Medium |
| Low sat + high frust | sat < 4.5, frust > 5.5 | Controlled Motivation / Active Exclusion / Competence Threat | High |

### 2.6 Belbin Role Inference

Rule-based, checked in order (multiple can apply):

| Condition | Role | Qualifier |
|-----------|------|-----------|
| A-sat > 6.5 AND B-sat > 6.0 | Shaper | Inspiring |
| A-sat > 6.5 (B-sat <= 6.0) | Shaper | Driving |
| C-sat > 7.0 AND C-frust < 3.0 | Specialist | Deep Mastery |
| B-sat > 7.0 AND B-frust < 3.0 | Teamworker | Anchor |
| A-sat > 5.0 AND B-sat > 5.0 AND C-sat > 5.0 | Coordinator | Balanced |
| A-frust > 6.0 OR B-frust > 6.0 | Monitor-Evaluator | Vigilant |
| No match | Resource Investigator | Seeking |

Existing mappings in `apps/web/src/lib/data/abc-belbin.ts` remain as the type-to-Belbin reference. This rule engine adds a dynamic, score-driven layer.

### 2.7 Context Gap

```
gap = team_score - personal_score  (per subscale)
```

A gap below -1.5 on any satisfaction subscale flags a **team context concern**: the team environment significantly undermines a need the person meets elsewhere.

### 2.8 Trajectory & Volatility (3+ measurements)

**Trajectory (slope)**: OLS regression of subscale scores over most recent 3-5 measurement points.

```
slope = sum((t_i - t_mean)(y_i - y_mean)) / sum((t_i - t_mean)^2)
```

- Negative slope on any satisfaction subscale = yellow flag
- Positive slope on any frustration subscale = yellow flag
- Two or more simultaneous flags = red flag

**Volatility**: Within-person standard deviation across recent measurements. High volatility (SD > 2.0 on 0-10 scale) signals need fragility regardless of mean.

**Composite risk score**:

```
risk = w1 * |negative sat slope|
     + w2 * |positive frust slope|
     + w3 * (10 - sat level)
     + w4 * frust level
     + w5 * volatility
```

Initial weights equal. Recalibrate as outcome data accumulates.

### 2.9 Reciprocal Effects and Causal Interpretation

The trajectory model treats declining satisfaction and rising frustration as leading indicators of burnout. This is supported by Lonsdale & Hodge (2011), who established through longitudinal design that declining self-determination preceded increases in burnout. However, the same study found evidence for reciprocal effects: chronic exhaustion also undermines subsequent motivation and need satisfaction.

This means a declining ABC trajectory could be either:
1. **A leading indicator** — the need environment is deteriorating, and burnout will follow if nothing changes.
2. **A lagging indicator** — the athlete is already burned out from other causes (overtraining, life stress, injury), and the declining ABC scores are a consequence.

The system handles this ambiguity in two ways:

**Cross-referencing with daily signals.** If daily cognitive signals (Readiness, Stress Response, Recovery Slope) declined *before* ABC scores declined, the ABC trajectory is more likely a lagging indicator — the burnout came first. If ABC scores declined while daily signals were still stable, the ABC trajectory is more likely a leading indicator — the need environment is eroding, and performance decline will follow. The system timestamps both signal streams and can reconstruct the temporal ordering.

**Intervention guidance, not diagnosis.** The coach-facing UI presents trajectory flags as "attention signals" rather than diagnoses. The frustration signature cards include language like "This pattern is associated with..." rather than "This athlete is burning out because..." The system surfaces the signal and suggests where to look. The coach determines the cause through conversation with the athlete. This is consistent with the literature's recommendation that ABC data should drive inquiry, not replace clinical judgment.

---

## 3. Data Model Changes

### 3.1 New Tables

**`abc_assessments`** — stores each completed assessment

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| member_id | UUID FK -> members | |
| responses | JSONB | Raw item responses `{AS1: 6, AF1: 3, ...}` |
| a_sat | float | Ambition satisfaction (0-10) |
| a_frust | float | Ambition frustration (0-10) |
| b_sat | float | Belonging satisfaction (0-10) |
| b_frust | float | Belonging frustration (0-10) |
| c_sat | float | Craft satisfaction (0-10) |
| c_frust | float | Craft frustration (0-10) |
| team_a_sat | float | Team context A-sat |
| team_a_frust | float | Team context A-frust |
| team_b_sat | float | Team context B-sat |
| team_b_frust | float | Team context B-frust |
| team_c_sat | float | Team context C-sat |
| team_c_frust | float | Team context C-frust |
| domain_states | JSONB | `{ambition: "thriving", belonging: "vulnerable", craft: "mild"}` |
| big_five | JSONB | `{openness: 62, conscientiousness: 74, ...}` |
| type_name | varchar(50) | 36-type name ("Mentor", "Forge", etc.) |
| type_domain | varchar(20) | Dominant domain |
| frustration_signatures | JSONB | `["blocked_drive", "conditional_belonging"]` |
| belbin_roles | JSONB | `[{role: "Shaper", qualifier: "Inspiring"}]` |
| context_gaps | JSONB | `{a_sat: -2.1, b_frust: 0.3, ...}` |
| completed_at | timestamptz | |
| created_at | timestamptz | |

Indexed on `(member_id, completed_at DESC)`.

**`abc_assessment_templates`** — the item bank

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | |
| code | varchar(10) | Item code (AS1, BF3, etc.) |
| subscale | varchar(10) | `a_sat`, `b_frust`, etc. |
| context | varchar(10) | `personal` or `team` |
| text | text | Question text |
| reverse_scored | boolean | |
| active | boolean | |
| sort_order | int | Display order (shuffled) |

### 3.2 Existing Model — ABCProfile

The existing `abc_profiles` table (single ambition/belonging/craft scores derived from check-ins) stays as-is. It serves a different purpose: lightweight, daily, rule-based extraction from check-in data. The new `abc_assessments` table is the longitudinal instrument with the full six-subscale model.

The relationship: `abc_profiles` = fast daily signal. `abc_assessments` = deep biweekly measurement. Both feed into the player and coach views, but the 36-type system, frustration signatures, and trajectory analysis run off `abc_assessments`.

---

## 4. API Endpoints

### Player-facing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/abc/assessment/current` | Get current open assessment (or null) |
| POST | `/api/v1/abc/assessment/submit` | Submit completed assessment (30 responses) |
| GET | `/api/v1/abc/assessment/history` | Past assessments with scores, types, states |
| GET | `/api/v1/abc/profile/me` | Latest scored profile (type, Big Five, Belbin, states) |
| GET | `/api/v1/abc/trajectory/me` | Trajectory slopes + volatility + risk (requires 3+ assessments) |

### Coach-facing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/leader/abc/assessments` | All members' latest assessments |
| GET | `/api/v1/leader/abc/member/{id}` | Single member's full ABC detail |
| GET | `/api/v1/leader/abc/member/{id}/trajectory` | Member trajectory + risk |
| GET | `/api/v1/leader/abc/team/composition` | Team composition balance, variance, complementarity |
| GET | `/api/v1/leader/abc/team/risks` | Members with active frustration signatures or red flags |
| GET | `/api/v1/leader/abc/team/context-gaps` | Members where team environment undermines personal needs |
| POST | `/api/v1/leader/abc/assessment/trigger` | Push an assessment to one or all members |

---

## 5. Player Experience

### 5.1 Assessment Flow

**Entry point**: Notification every two weeks — "Your ABC check-in is ready." Tapping opens a full-screen flow.

**Screen 1 — Intro**
- "This takes about 3 minutes."
- "Think about the past two weeks — on and off the field."
- Progress bar showing 0/30.

**Screen 2-7 — Questions (5 items per screen)**
- One question at a time within each screen, or grouped by 5 with a vertical layout.
- 1-7 slider or button row per question. Labels only on endpoints (Never / Very Often) and midpoint (Sometimes).
- Items shuffled across domains. No domain labels visible to the player.
- Progress bar advances.

**Screen 8 — Submission**
- "Thanks. Your results are ready."
- Tap to view results.

### 5.2 Results — "Your ABC Profile" (new tab on `/member/typology`)

**Top card — Your Type**
- Type name large (e.g., "Mentor"), tagline below ("Grows others' skill").
- Domain badge: colour-coded Ambition / Belonging / Craft pill.
- If the type changed since last assessment, a subtle "Previously: Forge" note.

**Middle section — Domain States**
Three horizontal bars, one per domain. Each bar shows:
- Satisfaction score (left-aligned, filled green-to-amber gradient).
- Frustration score (right-aligned, filled grey-to-red gradient).
- State label in the centre: Thriving / Vulnerable / Mild / Distressed, colour-coded.

Visual example (Belonging):
```
 Satisfaction ████████░░  7.2    [Vulnerable]    5.8  ░░██████ Frustration
```

This is the key view that makes the satisfaction/frustration split tangible. A player sees at a glance which domain is Thriving and which is under pressure.

**Bottom section — What This Means**

Short, plain-language paragraphs generated per domain state. Examples:

- **Thriving (Craft)**: "Your skill development feels engaging and self-directed right now. You're in a good place to take on new challenges."
- **Vulnerable (Belonging)**: "You have real connections on this team, but something about them feels conditional lately. That tension is worth paying attention to."
- **Distressed (Ambition)**: "Your goals feel unclear or imposed right now. That can drain motivation. Consider talking to your coach about what you actually want to work toward."

No clinical language. No scores exposed beyond the visual bars. The player sees states and guidance, not numbers.

### 5.3 Trajectory View (after 3+ assessments)

Available on `/member/typology` as a "Trends" tab.

**Per-domain sparkline** showing satisfaction and frustration scores over time (separate lines, same chart). The slope direction is annotated: arrow up/down with "improving" / "declining" / "stable".

**Volatility indicator**: A small badge per domain — "Stable", "Some variation", "High variation" — colour-coded green/amber/red.

**No risk score exposed to the player.** The composite risk score is coach-only. Players see trends and states, not risk labels.

### 5.4 Big Five & Belbin (existing views, enhanced)

The existing `/member/typology` page already shows the 36-type detail, personality insights, and Belbin mapping. These views stay but now pull from `abc_assessments` instead of `abc_profiles` when assessment data is available.

**Change**: The `PersonalityInsights` component currently shows Big Five traits without explanation of where they come from. Add a one-liner: "These traits are inferred from your ABC profile pattern. They reflect how you tend to express your needs, not fixed personality."

---

## 6. Coach Experience

### 6.1 Team ABC Dashboard (enhanced `/leader/abc`)

**Existing components stay**: TeamABCHeatmap, DDOScoreCard, ArchetypeDistribution, TeamPatternCard, BelbinRoleMap, TeamVectorMap.

**New: Domain State Summary**

A 3x4 grid showing how many members are in each state per domain:

```
              Thriving  Vulnerable  Mild  Distressed
 Ambition        5          3          2          2
 Belonging       4          4          1          3
 Craft           6          2          3          1
```

Cells are colour-coded. Clicking a cell filters the member list below to show those members. This is the coach's primary triage view — "I have 3 members Distressed on Belonging. Who are they?"

**New: Risk Panel**

A sorted list of members with active flags:
- Red flags (2+ simultaneous negative slopes) at top.
- Yellow flags (single negative sat slope or positive frust slope) next.
- Frustration signatures (Blocked Drive, Active Exclusion, etc.) with labels.
- Context gaps > -1.5 flagged with "Team environment concern."

Each row: member name, avatar, flag type, affected domain(s), and a "View" link to the member detail.

### 6.2 Member ABC Detail (enhanced `/leader/member/[id]`)

**Existing**: ABC profile card, archetype predictions, intervention card, trend chart.

**New: Six-Subscale View**

Same satisfaction/frustration bar visualisation as the player sees, but with:
- Numeric scores visible (coaches see the numbers).
- Domain state labels.
- Historical comparison: "2 weeks ago: Thriving -> now: Vulnerable" with direction arrow.

**New: Trajectory Chart**

A line chart with 6 lines (one per subscale) over all available measurement points. Coaches can toggle lines on/off. Slope annotations on hover. Volatility badges per subscale.

**New: Frustration Signature Card**

If active signatures are detected:
- Signature name (e.g., "Conditional Belonging")
- Plain-language explanation: "Jordan has strong team connections, but something about those connections feels performance-contingent. After a poor performance, watch for social withdrawal."
- Suggested action: "Have a 1:1 conversation that is explicitly not about performance."

**New: Context Gap Card**

If any gap exceeds -1.5:
- "Belonging-satisfaction is 2.1 points lower in the team context than personally. The team environment is undermining this player's relational needs."
- This tells the coach the problem is environmental, not individual.

### 6.3 Assessment Management

**Trigger Assessments**: Button on the team dashboard to push an assessment to all members or a specific member. Coach sets the deadline (default: 3 days).

**Completion Tracker**: Shows which members have completed the current cycle and which haven't. Nudge button to send a reminder notification.

**Cadence Settings**: In `/leader/settings`, configure default cadence (biweekly/weekly) and high-stress override windows.

---

## 7. Notification Flow

| Event | Recipient | Channel | Message |
|-------|-----------|---------|---------|
| Assessment due | Player | Push + in-app | "Your ABC check-in is ready. Takes ~3 minutes." |
| Assessment reminder (24h before deadline) | Player | Push | "Reminder: Your ABC check-in closes tomorrow." |
| Assessment completed | Coach | In-app | "Jordan Williams completed their ABC check-in." |
| Red flag detected | Coach | Push + in-app | "Alert: Jordan Williams has declining trends in 2+ domains." |
| Frustration signature detected | Coach | In-app | "Jordan Williams: Conditional Belonging pattern detected." |
| Context gap detected | Coach | In-app | "Jordan Williams: team environment concern on Belonging." |

---

## 8. What Does NOT Change

- **Daily check-ins** stay as-is. They feed the cognitive signals engine (Readiness, Focus, Stress, etc.) and the lightweight `abc_profiles` (single-score extraction).
- **Existing abc_profiles table** stays. The rule-based daily extraction continues to power the home dashboard cards and daily signal views.
- **Existing 36-type catalog** (`abc-typology.ts`) stays. The scoring engine now feeds it with assessment-derived scores instead of (or in addition to) check-in-derived scores.
- **Existing Belbin mappings** (`abc-belbin.ts`) stay as the type-to-role reference. The new rule engine adds a dynamic, score-driven layer alongside it.

---

## 9. Implementation Sequence

### Phase 0 — Simulation Validation (prerequisite)

Computational validation of the ABC model before any production code is written. This phase proves the instrument's psychometric structure is sound, identifies fragile parameters, and sizes the future empirical study. Full methodology in Section 11.

**Deliverables:**
- Confirmed 6-factor structure (CFA fit indices exceeding gold-standard thresholds)
- Scoring pipeline certification (correlation with ground truth >= 0.85)
- Big Five weight sensitivity report (which weights are robust, which need empirical priority)
- Type system stability report (test-retest >= 85%, boundary sensitivity analysis)
- Longitudinal detection thresholds (minimum measurement points, smallest detectable change)
- Power analysis for the empirical study (exact N and T requirements)
- Robustness profile (failure modes under faking, careless responding, missing data)

**Gate**: If the 6-factor model does not fit significantly better than a 3-factor model in simulation, the satisfaction/frustration split is not structurally supported and the item pool must be revised before proceeding to Phase A. No production code is written against a model that fails its own internal validation.

### Phase A — Instrument + Scoring Engine (backend)

1. Create `abc_assessment_templates` table and seed the 30 items.
2. Create `abc_assessments` table with Alembic migration.
3. Build `ABCAssessmentService` with the full scoring pipeline (subscale means, normalisation, domain states, Big Five inference, type derivation, frustration signatures, Belbin rules, context gaps).
4. Build API endpoints (player + coach).
5. Regenerate Orval types.

### Phase B — Player Assessment Flow (frontend)

1. Build the assessment flow (intro, questions, submit, results).
2. Add the domain state bars to `/member/typology`.
3. Add the "What This Means" plain-language section.
4. Wire the 36-type view to use assessment scores when available.

### Phase C — Coach Views (frontend)

1. Add the domain state summary grid to `/leader/abc`.
2. Add the risk panel with flags and signatures.
3. Add the six-subscale view and trajectory chart to `/leader/member/[id]`.
4. Add frustration signature and context gap cards.
5. Build assessment trigger and completion tracker.

### Phase D — Trajectory Engine (backend + frontend)

1. Build trajectory calculation (OLS slope, volatility, composite risk) — requires 3+ assessments, so this ships after players have used the instrument for 6+ weeks.
2. Add trajectory sparklines to player view.
3. Add trajectory chart and risk scoring to coach view.
4. Build red/yellow flag notification triggers.

### Phase E — Early Empirical Validation (first season)

First deployment with real athletes. This is not the full validation study — it is an instrumented launch designed to collect the data needed for Phase F while delivering value to users.

1. Deploy the assessment to 3-5 partner teams (target: 100-150 athletes).
2. Collect 6-8 biweekly measurement points across one competitive season.
3. At season start and end, administer the BFI-2 (Big Five) alongside the ABC assessment to a volunteer subset (n=50+).
4. At season end, collect outcome measures: coach-rated engagement, retention status, self-reported burnout (ABQ).
5. Compute within-team norms (subscale means, SDs, percentile tables).
6. Compare empirical factor structure to the simulation predictions from Phase 0.

### Phase F — Model Recalibration + Norming (ongoing)

1. Compute empirical Big Five regression weights from Phase E data. Replace the theoretical weight matrix with calibrated coefficients.
2. Recalibrate the composite risk score weights using outcome data (which trajectory patterns actually predicted burnout/disengagement).
3. Build cross-team percentile norms as additional teams deploy (target: 5-10 teams, 200-400 athletes by end of year 2).
4. Publish a technical report documenting the model's psychometric properties — convergent validity, discriminant validity, predictive validity, reliability. This becomes the evidence base for efficacy claims.

---

## 10. Relationship to Existing Systems

```
Daily check-in (5 inputs, every day)
  -> Cognitive signals (Readiness, Focus, Stress, etc.)  [fast, shallow]
  -> abc_profiles (single A/B/C scores, rule-based)      [fast, shallow]

ABC Assessment (30 items, every 2 weeks)
  -> abc_assessments (6 subscales, Big Five, type, etc.) [deep, longitudinal]
  -> Frustration signatures, Belbin roles, context gaps
  -> Trajectory + risk scoring (after 3+ assessments)

Cross-system signals:
  -> Overinvestment Warning (ABC Thriving + daily signals declining)
  -> Causal ordering (which signal stream moved first)
```

### Why two systems, not one

Recent computational and neuroscientific models (Herlambang et al., 2021; Kok, 2022; Matthews et al., 2023) show that mental fatigue is not resource depletion — it reflects shifts in how the brain allocates effort based on perceived goal value. This means cognitive performance and motivational need states are two views of the same underlying process, operating at different timescales.

The daily cognitive signals (Readiness, Focus Stability, Cognitive Load, Recovery Slope) capture the **momentary effort-allocation layer** — how the athlete's brain is regulating effort right now, today, based on sleep, stress, energy, and perceived demands. These signals fluctuate day to day and respond to acute events.

The biweekly ABC assessment captures the **motivational environment layer** — whether the athlete's psychological needs are being met or frustrated by their context. These scores move slowly, over weeks, and reflect structural conditions (coaching style, team culture, role clarity) rather than daily state.

The two layers interact. When need satisfaction is high and stable (ABC Thriving), the daily effort-allocation system has a strong motivational foundation — the athlete allocates effort efficiently and recovers well. When need frustration rises (ABC Vulnerable or Distressed), the motivational foundation erodes, and daily signals begin to degrade: Cognitive Load increases as the athlete spends mental resources managing frustration rather than performing; Recovery Slope declines as stress becomes chronic rather than acute.

The cross-reference is where the insight lives:
- **ABC stable, daily signals declining** = acute stressor (overtraining, poor sleep, exam week). Intervention: recovery-focused, short-term.
- **ABC declining, daily signals stable** = motivational environment eroding. Intervention: need-targeted, environmental. Daily performance hasn't suffered yet, but it will.
- **ABC declining, daily signals declining** = compounding crisis. Both systems confirm the problem. Highest urgency.
- **ABC Thriving, daily signals declining** = overinvestment paradox. The athlete is pushing because they're so motivated — and they're burning out because of it. Intervention: protect recovery without reducing satisfaction.

Both feed the AI agents. The Cognitive Coach uses daily signals for in-session skill routing. The Intervention Engine uses assessment trajectories for proactive risk-based recommendations. When both systems agree on a risk pattern, the intervention confidence is highest.

---

## 11. Simulation Validation Plan

Computational validation of the ABC model's psychometric properties, run before any production deployment. The simulation proves the model is structurally sound and testable — that the math works, the factor structure recovers, and a future empirical study has a high probability of producing interpretable results. Full detail in `abc-simulation-validation-plan.md`.

### 11.1 Latent Structure Specification

Define the ground truth: six continuous latent factors (A-sat, A-frust, B-sat, B-frust, C-sat, C-frust) with an inter-factor correlation matrix derived from the SDT literature.

Expected correlations:
- Within-domain satisfaction/frustration: r = -0.40 to -0.60 (related but separable)
- Cross-domain satisfactions: r = 0.20 to 0.40 (moderate positive)
- Cross-domain frustrations: r = 0.25 to 0.45 (frustration generalises)
- Cross-domain sat/frust: r = -0.10 to -0.25 (weak negative)

Define a target factor loading matrix: each item loads >= 0.55 on its intended factor, < 0.20 on all others.

### 11.2 Synthetic Response Generation

Generate 10,000 simulated participants from the latent model. For each participant:
1. Draw latent factor scores from the multivariate normal distribution.
2. Multiply by the loading matrix, add residual noise.
3. Discretise to the 1-7 Likert scale using threshold-based mapping.
4. Apply reverse-scoring corruption for the 6 reversed items.

Produce two datasets: a clean set (no noise) and a realistic set with careless responders (5-10%), acquiescence bias (10-15%), extreme responding (5%), and missing data (2-5%).

### 11.3 Psychometric Evaluation

**Internal consistency**: Cronbach's alpha and McDonald's omega per subscale. Target: alpha >= 0.75 for all six subscales.

**Confirmatory Factor Analysis**: Fit the 6-factor model and compare against 3-factor (sat/frust collapsed), 2-factor (all sat vs all frust), and 1-factor alternatives.

| Index | Good Fit | Acceptable Fit |
|-------|----------|----------------|
| CFI | >= 0.95 | >= 0.90 |
| TLI | >= 0.95 | >= 0.90 |
| RMSEA | <= 0.06 | <= 0.08 |
| SRMR | <= 0.06 | <= 0.08 |

The 6-factor model must fit significantly better than all alternatives. This is the test of the satisfaction/frustration distinction — the model's central structural claim.

**Discriminant validity**: Constrain within-domain sat/frust correlation to -1.0 and show the constrained model fits significantly worse. This confirms satisfaction and frustration are separable constructs, not inverse endpoints.

### 11.4 Scoring Pipeline Verification

Run the production scoring pipeline on simulated data and correlate outputs with known ground truth.

| Metric | Target |
|--------|--------|
| Pearson r (computed vs true, per subscale) | >= 0.85 |
| Spearman rho (rank preservation) | >= 0.90 |
| Domain state classification accuracy | >= 80% overall |
| Vulnerable state sensitivity | >= 75% |

Repeat on the noisy dataset. Acceptable degradation: correlations drop by no more than 0.10, accuracy drops by no more than 10 points.

### 11.5 Big Five Inference Stress Test

Generate ground truth Big Five scores correlated with ABC latent scores at theoretically expected magnitudes. Run the inference model and evaluate:

- **Recovery accuracy**: r >= 0.40 between inferred and true per trait (moderate recovery acceptable at this stage — the weights are theoretical priors)
- **Discriminant validity**: each inferred trait correlates most strongly with its corresponding true trait, with diagonal >= 0.15 above off-diagonal
- **Weight sensitivity**: perturb each weight +/-20% and measure output change. Weights where output shifts > 10 percentile points are flagged for empirical priority.
- **Edge cases**: extreme ABC profiles (all 0 or all 10) produce differentiable, non-degenerate Big Five estimates.

### 11.6 Type Derivation Stability

Classify all 10,000 simulated participants and evaluate:

- **Distribution**: no type captures < 1% (unreachable) or > 10% (attractor). Integrator fallback captures < 2%.
- **Boundary sensitivity**: what percentage of participants are within "flip distance" of a different type (domain margin < 0.5 or trait margin < 3 percentile points). Target: < 30%.
- **Test-retest stability**: add small random noise to responses and reclassify. Target: >= 85% type retention.
- **Profile distinctiveness**: adjacent types (same domain, different Big Five) differ by >= 0.5 SD on differentiating subscales.

### 11.7 Longitudinal Sensitivity

Simulate 2,000 participants across 8 measurement points with five trajectory profiles:
- Stable (40%): constant with measurement noise
- Gradual decline (20%): one satisfaction subscale decreases 0.15 SD per point
- Gradual rise (20%): one frustration subscale increases 0.15 SD per point
- Acute event (10%): stable until point 5, then 1.0 SD shift
- Volatile (10%): high within-person variance (SD = 0.8)

**Detection targets** (by measurement point 5):
- Decline detection sensitivity >= 0.80
- Rise detection sensitivity >= 0.80
- Stability specificity >= 0.80
- Frustration signature lead time: triggers >= 1 measurement point before Distressed state

Compute the minimum detectable slope at each measurement occasion (3 through 8) with 80% power and alpha = 0.05.

### 11.8 Power Analysis

Size the future empirical study. For each hypothesis:

| Hypothesis | What it tests | Expected minimum N | Minimum T |
|-----------|--------------|-------------------|-----------|
| H1: Factor structure | 6-factor CFA fits better than alternatives | 200-300 | 1 |
| H2: Sat/frust separability | Within-domain correlation != -1.0 | 150-200 | 1 |
| H3: Big Five convergence | ABC predicts BFI-2 scores (R >= 0.40) | 200-300 | 1+ |
| H4: Trajectory prediction | Slopes predict burnout/disengagement (AUC >= 0.70) | 150-250 | 5+ |
| H5: Incremental validity | Trajectories add predictive power beyond single Big Five score | 250-400 | 5+ |

Multiply required N by 1.4 to account for attrition and careless responding.

### 11.9 Adversarial Testing

- **Faking resistance**: shift satisfaction +1.5, frustration -1.5. Does the 6-factor structure survive? Do frustration signatures still trigger?
- **Careless responding detection**: test long-string analysis, intra-individual variability, person-total correlation, Mahalanobis distance. What percentage of careless responders are caught?
- **Missing data robustness**: at what missing-data rate (5%, 10%, 15%, 20%) does scoring correlation with true scores drop below 0.70?
- **Scale compression**: test 18-item (3 per subscale) and 12-item (2 per subscale) versions. What is the shortest version that still meets psychometric standards?

### 11.10 Simulation Outputs and Decision Gates

| Output | Gate Criterion | If Failed |
|--------|---------------|-----------|
| 6-factor CFA fit | CFI >= 0.95, RMSEA <= 0.06 | Revise items before proceeding |
| Sat/frust separability | 6-factor fits significantly better than 3-factor | Satisfaction/frustration split is not supported — fundamental redesign required |
| Scoring pipeline correlation | r >= 0.85 with ground truth | Debug scoring math |
| Vulnerable state sensitivity | >= 75% | Adjust threshold (5.5) or item content |
| Big Five recovery | r >= 0.40 per trait | Identify which weights are fragile; flag for empirical priority |
| Type test-retest stability | >= 85% | Add confidence bands or reduce type granularity |
| Trajectory detection | Sensitivity >= 0.80 by point 5 | Increase measurement frequency or item count |
| Faking resistance | 6-factor structure survives | Add validity scale or redesign items for indirect measurement |

---

## 12. Competitive Position

The simulation validation is not just a technical exercise. It establishes ABC as a proprietary, evidence-based psychometric model that Ero owns and competitors cannot replicate.

### The evidence base ABC stands on

The SDT-fatigue literature provides unusually strong support for the core mechanism ABC operationalises. A systematic review of 50 studies (drawn from 170 million papers) rates the key claims:

| Claim | Evidence Strength | Source |
|-------|------------------|--------|
| Need satisfaction reduces burnout risk | 9/10 — Strong | Slemp et al., 2024; Fernet et al., 2012; Lonsdale et al., 2009 |
| Controlled motivation increases exhaustion vulnerability | 8/10 — Strong | De Francisco et al., 2025; Toth-Kiraly et al., 2020 |
| Motivation type mediates stressor impact on fatigue | 7/10 — Moderate | Towair et al., 2025; Toth-Kiraly et al., 2020 |
| Mental fatigue reflects motivational shifts, not resource loss | 6/10 — Moderate | Herlambang et al., 2021; Kok, 2022; Matthews et al., 2023 |
| High self-determination can lead to overinvestment | 5/10 — Moderate | Towair et al., 2025; Mobarak et al., 2024 |
| Reciprocal effects: burnout undermines future motivation | 4/10 — Emerging | Lonsdale & Hodge, 2011 |

The top two claims — the ones ABC's entire architecture rests on — have the strongest evidence in the field. This is not a speculative model built on weak correlations. It is an operationalisation of the most replicated findings in motivation science.

### What Ero can say after Phase 0 (simulation)

- "Our ABC model has been validated through confirmatory factor analysis against gold-standard fit thresholds."
- "Our six-subscale structure — measuring both satisfaction and frustration per domain — has been computationally confirmed as a better model than collapsing to three dimensions."
- "Our type classification system has been tested for stability and boundary sensitivity."
- "We have quantified the minimum data needed to detect meaningful psychological change."

### What Ero can say after Phases E-F (empirical)

- "ABC scores correlate with established SDT measures at r = [X], confirming construct validity."
- "ABC trajectories predict athlete burnout [X] weeks before it manifests, with AUC = [Y]."
- "Our model explains [X]% of variance in athlete retention beyond what traditional personality assessments capture."
- "We are the first platform to produce longitudinal data on cognitive fatigue in athletes — a documented gap in the research literature."

### What competitors can say

- Most: nothing. No psychometric validation, no published evidence, no documented methodology.
- A few: "We use validated SDT scales" — meaning they license someone else's instrument and have no proprietary model.

### The moat

Ero builds and owns the science, not just the software. The validation path creates compounding advantage:

1. **Simulation** (Phase 0) — proves the model's structure is sound. Competitors would need to build their own instrument and validate it from scratch.
2. **Empirical validation** (Phases E-F) — produces real psychometric data (convergent validity, predictive validity, reliability coefficients). This data is proprietary to Ero.
3. **Technical report** — published evidence base that enables specific efficacy claims. Competitors cannot make these claims without doing the same work.
4. **Longitudinal dataset** — every season of ABC assessment data across every partner team builds Ero's norming database. Cross-team norms, sport-specific percentile tables, and calibrated risk weights all improve with scale. A competitor entering the market two years later starts with zero data against Ero's thousands of ABC profiles.
5. **Research gap ownership** — cognitive fatigue in athletes is the least-studied intersection in the SDT-fatigue literature. Ero's combined daily signals + biweekly ABC data is the first system positioned to fill it. Publishing on this gap — even a technical white paper, not a peer-reviewed journal article — positions Ero as the empirical authority in a space where no one else has data.

---

## 13. Mathematical Foundations

This section catalogues every mathematical method required across the simulation, scoring engine, empirical validation, and production analytics. Each method is tied to the specific problem it solves.

### 13.1 Simulation & Structural Validation

These methods prove the ABC model's factor structure is sound before any real data is collected.

**Multivariate normal sampling.** The simulation generates synthetic response data from a population-level covariance matrix. Each simulated respondent is a draw from a multivariate normal distribution parameterised by a mean vector μ (6 × 1, one per subscale) and a covariance matrix Σ (6 × 6, encoding inter-subscale correlations). The key formula:

```
X ~ N(μ, Σ)    where X ∈ ℝ⁶
```

Σ is constructed from the factor loading matrix Λ and unique variance matrix Θ: `Σ = ΛΛᵀ + Θ`. This is the fundamental equation of the common factor model — it defines the relationship between observed scores and latent constructs.

**Factor loading matrices.** Each of the 24 core items loads on one of six latent factors (the subscales). The loading matrix Λ (24 × 6) encodes how strongly each item reflects its subscale. Target loadings are 0.6–0.8 for primary loadings, < 0.3 for cross-loadings. Reverse-scored items carry negative loadings before recoding.

**Ordinal discretisation.** Raw continuous draws are discretised to the 1–7 response scale using threshold vectors. For each item, six thresholds τ₁...τ₆ partition the continuous distribution into seven bins. The thresholds are calibrated to produce realistic response distributions (slight positive skew for satisfaction items, slight negative skew for frustration items).

**Confirmatory Factor Analysis (CFA).** The core structural test. CFA fits the hypothesised six-factor model to the simulated (and later, real) data and evaluates fit. The model specifies which items load on which factors and constrains cross-loadings to zero. Key equations:

```
Σ_model = ΛΦΛᵀ + Θ
```

Where Φ (6 × 6) is the inter-factor correlation matrix, Λ is the loading matrix, and Θ is the diagonal matrix of unique variances. The estimation minimises the discrepancy between Σ_model and the observed covariance matrix Σ_observed.

**Estimator: WLSMV** (Weighted Least Squares, Mean and Variance adjusted). Standard maximum likelihood assumes continuous, normally distributed variables. Likert-scale items (1–7) violate this. WLSMV operates on polychoric correlations (the estimated continuous correlations underlying ordinal responses) and produces corrected chi-square statistics. This is the gold-standard estimator for ordinal psychometric data.

**Fit indices and their thresholds:**

| Index | Formula concept | Gold standard | Acceptable |
|-------|----------------|---------------|------------|
| CFI (Comparative Fit Index) | 1 − (χ²_model − df_model) / (χ²_null − df_null) | ≥ 0.95 | ≥ 0.90 |
| TLI (Tucker-Lewis Index) | Penalises model complexity more than CFI | ≥ 0.95 | ≥ 0.90 |
| RMSEA (Root Mean Square Error of Approximation) | √((χ²/df − 1) / (N − 1)) | ≤ 0.06 | ≤ 0.08 |
| SRMR (Standardised Root Mean Residual) | √(mean of squared standardised residuals) | ≤ 0.08 | ≤ 0.10 |

**Model comparison (chi-square difference test).** The simulation must prove six factors fit better than three (collapsing satisfaction and frustration). The test statistic:

```
Δχ² = χ²_restricted − χ²_full
Δdf = df_restricted − df_full
p = 1 − CDF_χ²(Δχ², Δdf)
```

For WLSMV, the standard chi-square difference is not valid — a scaled difference test (DIFFTEST in Mplus, or the Satorra-Bentler correction) must be used.

Additionally, AIC and BIC provide information-theoretic model comparison: lower values indicate better fit after penalising for complexity.

**Monte Carlo power analysis.** Determines the minimum sample size needed to detect the six-factor structure with adequate power. The simulation runs CFA at sample sizes from 100 to 2,000 and plots the proportion of replications where all fit indices meet thresholds. The target: ≥ 80% power (conventional threshold). This directly sizes the empirical study.

**Perturbation and sensitivity analysis.** Tests which model parameters are fragile. Each parameter (loading, cross-loading, inter-factor correlation, threshold) is systematically perturbed by ±10-20%, and the change in fit indices is recorded. Parameters where small perturbations cause large fit degradation are flagged for empirical priority — these are the numbers that must be estimated precisely from real data.

### 13.2 Scoring Engine

These methods convert raw item responses into the scores, types, and trajectories that surface in the product.

**Subscale scoring.** Each subscale mean is the arithmetic mean of its four items (after reverse-coding):

```
subscale_score = (1/4) Σᵢ itemᵢ     where i ∈ {1,2,3,4}
reverse_coded = 8 − raw_score        for reverse items
```

**Domain states.** Each subscale score is classified against a 5.5 threshold (on the 1–7 scale):

| Satisfaction | Frustration | State |
|-------------|-------------|-------|
| ≥ 5.5 | < 5.5 | Thriving |
| ≥ 5.5 | ≥ 5.5 | Vulnerable |
| < 5.5 | < 5.5 | Mild |
| < 5.5 | ≥ 5.5 | Distressed |

The Vulnerable state — high satisfaction masking high frustration — is the clinically important detection that requires the six-subscale split.

**Big Five inference via weight matrix.** The 36-type system derives approximate personality trait scores from ABC subscales using a linear mapping:

```
T = W · S
```

Where S (6 × 1) is the subscale score vector, W (5 × 6) is the empirically calibrated weight matrix mapping subscales to Big Five traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism), and T (5 × 1) is the estimated trait vector. The dominant trait from T determines the type suffix within each domain.

Initial weights come from the theoretical mapping (e.g., Craft-Satisfaction loads on Openness and Conscientiousness). Phase E calibrates W empirically by administering a validated Big Five instrument alongside ABC and running multiple regression:

```
T_observed = W_calibrated · S + ε
W_calibrated = (SᵀS)⁻¹SᵀT_observed
```

With k-fold cross-validation (k=5) to prevent overfitting.

**Trajectory analysis (OLS regression).** Trend detection uses ordinary least squares on the time series of each subscale:

```
score_t = β₀ + β₁t + ε_t
```

Where β₁ is the slope (rate of change per assessment period). A slope is flagged as meaningful when |β₁| exceeds a minimum effect size threshold and reaches statistical significance (p < 0.05). Minimum window: 3 assessments (6 weeks).

**Volatility.** Standard deviation of scores within the trajectory window:

```
volatility = √((1/(n-1)) Σ(scoreᵢ − mean)²)
```

High volatility with a flat slope indicates instability without directional change — a distinct risk pattern from steady decline.

**Composite risk score.** Combines slope and volatility into a single trajectory risk metric:

```
risk = w₁ · |negative_slope| + w₂ · volatility + w₃ · frustration_level
```

Weights (w₁, w₂, w₃) are initially set to equal and recalibrated empirically once outcome data (e.g., dropout, injury, burnout diagnosis) is available.

**Overinvestment detection.** Cross-system check combining daily signals with ABC:

```
overinvestment_flag = (A_sat ≥ 5.5 OR C_sat ≥ 5.5)
                      AND recovery_slope < threshold
                      AND cognitive_load > threshold
```

This catches the athlete whose high satisfaction masks physiological depletion — the "burning bright before burning out" pattern documented in the SDT-fatigue literature.

### 13.3 Empirical Validation

These methods apply once real athlete data is collected (Phases E–F).

**Convergent and discriminant validity.** Pearson correlations between ABC subscales and established SDT measures (BPNSFS). Expected: r ≥ 0.50 for convergent pairs (e.g., A-sat with Autonomy Satisfaction), r < 0.30 for discriminant pairs (e.g., A-sat with Relatedness Frustration). The correlation matrix is tested against these patterns.

**Internal consistency (Cronbach's α and McDonald's ω).** Reliability of each four-item subscale:

```
α = (k / (k-1)) · (1 − Σσ²ᵢ / σ²_total)
```

Where k = 4 (items per subscale). Target: α ≥ 0.70. McDonald's omega (ω) is preferred for congeneric models where loadings are unequal — it uses the CFA loadings directly rather than assuming tau-equivalence.

**Predictive validity (ROC/AUC).** Tests whether ABC trajectories predict future outcomes (burnout, dropout, performance decline). For binary outcomes:

```
AUC = P(score_positive > score_negative)
```

An AUC of 0.70+ indicates clinically useful prediction. The composite risk score from 13.2 serves as the predictor; outcome occurrence within 4–8 weeks serves as the criterion.

**Cross-lagged panel models (CLPM / RI-CLPM).** Tests reciprocal effects between daily signals and biweekly ABC scores. The Random-Intercept Cross-Lagged Panel Model separates within-person dynamics from stable between-person differences:

```
ABC_t = ρ₁ · ABC_{t-1} + β₁ · DailySignal_{t-1} + u_t
DailySignal_t = ρ₂ · DailySignal_{t-1} + β₂ · ABC_{t-1} + v_t
```

Where ρ values are autoregressive paths (stability) and β values are cross-lagged paths (directional influence). If β₁ > β₂, daily signals drive ABC changes. If β₂ > β₁, ABC changes drive daily signals. The RI-CLPM variant adds random intercepts to control for trait-level confounding — essential because athletes who are generally high on Ambition will be high at every time point, inflating cross-lagged paths in the standard CLPM.

**Multilevel modelling.** Athletes are nested within teams, and repeated measurements are nested within athletes. Ignoring this nesting inflates standard errors and produces false positives. The two-level model:

```
Level 1 (within-athlete): score_ti = β₀ᵢ + β₁ᵢ · time_ti + ε_ti
Level 2 (between-athlete): β₀ᵢ = γ₀₀ + γ₀₁ · team_contextᵢ + u₀ᵢ
```

This partitions variance into within-person change, between-person differences, and team-level effects. The Intraclass Correlation Coefficient (ICC) from the null model determines how much variance sits at each level — if team-level ICC is substantial, team norms and team-context gap analysis are empirically justified.

**Measurement invariance (multi-group CFA).** Tests whether ABC measures the same constructs across groups (sport type, gender, competitive level). Four progressive levels:

1. **Configural** — same factor structure across groups
2. **Metric** — same factor loadings (Δ CFI < 0.01)
3. **Scalar** — same item intercepts (enables mean comparisons)
4. **Strict** — same residual variances (rarely achieved, not required)

If scalar invariance fails for a group, ABC scores cannot be compared across that grouping variable. Sport-specific norms would be needed instead of universal norms.

**Latent growth curve models.** For modelling trajectories at the latent level rather than observed scores:

```
score_ti = intercept_i + slope_i · time_t + ε_ti
intercept_i ~ N(μ_intercept, σ²_intercept)
slope_i ~ N(μ_slope, σ²_slope)
```

This estimates average trajectories (μ values) while allowing individual variation (σ² values). Covariates (team context, sport type, training load) can predict individual intercepts and slopes, answering questions like "do athletes in higher-context-gap teams show steeper frustration trajectories?"

### 13.4 Production Analytics

Methods that run in the live product, not just in validation studies.

**Z-score normalisation (population norming).** Raw subscale scores are converted to population-relative scores:

```
z = (score − μ_population) / σ_population
```

Initial norms use simulation-derived distributions. As real data accumulates, norms are updated per sport, gender, and competitive level (assuming measurement invariance holds for those groupings). Percentile ranks are derived from the cumulative normal distribution.

**Careless responding detection (Mahalanobis distance).** Identifies athletes who respond randomly or without engagement:

```
D² = (x − μ)ᵀ Σ⁻¹ (x − μ)
```

Where x is the response vector, μ is the expected mean vector, and Σ is the expected covariance matrix. D² follows a chi-square distribution with k degrees of freedom. Responses with D² exceeding the 97.5th percentile are flagged for review. Additional checks: response time < 30 seconds (too fast), zero variance across items (straight-lining), inconsistency between forward and reverse items on the same subscale.

**Changepoint detection.** Identifies acute shifts in ABC trajectories that differ from gradual trends. The CUSUM (Cumulative Sum) method tracks cumulative deviations from the running mean:

```
S_t = max(0, S_{t-1} + (x_t − μ₀ − k))
```

Where k is the allowable slack and μ₀ is the target mean. An alarm triggers when S_t exceeds threshold h. This catches sudden drops (e.g., a relationship rupture causing Belonging to fall from 6.2 to 3.8 in one assessment) that trend-based analysis would smooth over.

**Empirically calibrated composite weights.** The initial equal-weight risk score (Section 13.2) is recalibrated once outcome data exists, using logistic regression:

```
P(outcome) = σ(w₁ · slope + w₂ · volatility + w₃ · frustration + w₀)
```

Where σ is the sigmoid function. The fitted weights replace the equal-weight defaults. The model is validated with leave-one-team-out cross-validation to ensure weights generalise across teams.

### 13.5 Implementation Stack

| Method | Library | Phase |
|--------|---------|-------|
| Multivariate sampling | `numpy.random.multivariate_normal` | Simulation |
| Factor loading / covariance matrices | `numpy` linear algebra | Simulation |
| Ordinal discretisation | `numpy` threshold binning | Simulation |
| CFA (WLSMV) | `semopy` or `lavaan` via `rpy2` | Simulation + Empirical |
| Model comparison | `scipy.stats.chi2` (scaled diff test) | Simulation |
| Monte Carlo power | Custom loop over CFA fits | Simulation |
| Subscale means, reverse coding | `numpy` / Python stdlib | Scoring engine |
| OLS trajectory slopes | `numpy.polyfit` or `statsmodels.OLS` | Scoring engine |
| Big Five weight matrix | `numpy` matrix multiplication | Scoring engine |
| Weight calibration (regression) | `scikit-learn.linear_model` | Empirical |
| ROC / AUC | `scikit-learn.metrics` | Empirical |
| Cross-lagged panel models | `semopy` or `lavaan` via `rpy2` | Empirical |
| Multilevel models | `statsmodels.MixedLM` | Empirical |
| Measurement invariance | `lavaan` via `rpy2` (multi-group CFA) | Empirical |
| Latent growth curves | `lavaan` via `rpy2` | Empirical |
| Z-score norming | `scipy.stats.norm` | Production |
| Mahalanobis distance | `scipy.spatial.distance.mahalanobis` | Production |
| Changepoint detection | `ruptures` or custom CUSUM | Production |
| Logistic calibration | `scikit-learn.linear_model.LogisticRegression` | Production |

### 13.6 Mathematical Dependencies Between Phases

The mathematics is not a grab-bag — each phase produces inputs that subsequent phases consume.

```
Simulation
  └─ Factor loadings Λ, thresholds τ → define the data-generating model
  └─ CFA fit indices → prove structure before collecting real data
  └─ Power analysis → sizes the empirical study (N, measurement occasions)

Scoring Engine
  └─ Subscale means → domain states → type classification
  └─ Weight matrix W → Big Five inference → 36-type derivation
  └─ OLS slopes + volatility → trajectory risk → alerts

Empirical Validation
  └─ Convergent validity (r values) → confirms ABC measures what it claims
  └─ Calibrated W matrix → replaces theoretical Big Five weights
  └─ RI-CLPM β values → establishes direction of daily ↔ biweekly effects
  └─ Measurement invariance → determines whether universal or sport-specific norms
  └─ ICC from multilevel models → validates team-context gap analysis

Production Analytics
  └─ Norming distributions (μ, σ per population) → percentile ranks
  └─ Calibrated risk weights → replace equal-weight defaults
  └─ Changepoint detection → acute alert system
  └─ Mahalanobis screening → data quality assurance
```

Every method listed here either produces a number the product displays, proves a structural claim that enables an efficacy statement, or sizes a study that de-risks empirical investment. Nothing is included for mathematical sophistication alone.
