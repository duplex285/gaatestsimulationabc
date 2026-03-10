# PRD: ABC Psychometric Assessment Integration into Ero

## The problem

Ero extracts ABC signals indirectly, through weighted proxy questions and LLM inference. This approach captures longitudinal patterns well but lacks a validated direct measurement of need satisfaction and frustration. The simulation dashboard has now validated a six-subscale psychometric model (Ambition, Belonging, Craft, each split into satisfaction and frustration) with a two-layer type system (125 profiles, 24 archetypes), Belbin role inference, and frustration signatures. Ero needs this instrument to establish reliable baselines at onboarding, strengthen profiles at key milestones, and anchor the indirect extraction pipeline against ground-truth scores.

## What this PRD covers

Three workstreams integrate the validated ABC Assessment into the Ero platform:

1. **Data layer**: new models, migrations, and scoring service for the six-subscale instrument
2. **Assessment flow**: three-tier questionnaire (onboarding, standard, full) delivered through the existing check-in interface
3. **Scoring pipeline alignment**: bridging the current 0-100 three-dimension ABC system with the new 0-10 six-subscale model

---

## 1. Data layer: models, migrations, scoring

### 1.1 New `ABCAssessment` model

The current `ABCProfile` stores three scores (ambition, belonging, craft on 0-100) derived from check-in proxies. The validated instrument produces six subscale scores on 0-10. These are different constructs and must coexist.

**Table: `abc_assessments`**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | UUID | Primary key |
| `member_id` | UUID | FK to `members`, CASCADE |
| `tier` | varchar(20) | `onboarding`, `standard`, `full` |
| `responses` | JSONB | Raw item responses (item_id: 1-7 Likert) |
| `a_sat` | float | Ambition satisfaction (0-10) |
| `a_frust` | float | Ambition frustration (0-10) |
| `b_sat` | float | Belonging satisfaction (0-10) |
| `b_frust` | float | Belonging frustration (0-10) |
| `c_sat` | float | Craft satisfaction (0-10) |
| `c_frust` | float | Craft frustration (0-10) |
| `type_name` | varchar(50) | 24-archetype name (e.g. "Steady Architect") |
| `profile_code` | varchar(10) | 125-profile code (e.g. "4-3-5") |
| `dominant_domain` | varchar(20) | argmax of sat scores |
| `domain_states` | JSONB | Per-domain state (Thriving/Vulnerable/Mild/Distressed) |
| `frustration_sigs` | JSONB | Active frustration signatures with risk level |
| `confidence` | float | Tier-dependent: onboarding 0.5, standard 0.7, full 0.9 |
| `timestamp` | datetime | When submitted |
| `created_at` | datetime | Record creation |
| `updated_at` | datetime | Last update |

**Indexes:**
- `(member_id, timestamp DESC)` for latest-assessment lookup
- `(member_id, tier)` for tier-specific history

**Relationship to `ABCProfile`:** Each assessment submission also generates an `ABCProfile` record by converting the six subscales to the existing three-dimension 0-100 format (see Section 3). This keeps all downstream consumers (archetype service, leader dashboard, cognitive coach) working without changes.

### 1.2 Scoring service: `abc_assessment_service.py`

Port the validated Python scoring engine (`src/python_scoring/`) into `services/api/src/services/abc_assessment_service.py`.

**Functions:**

| Function | Input | Output |
|----------|-------|--------|
| `score_responses(responses, tier)` | dict of item_id: value (1-7) | dict with six subscales, type_name, profile_code, domain_states, frustration_sigs |
| `submit_assessment(db, member_id, tier, responses)` | raw Likert answers | Stored `ABCAssessment` + generated `ABCProfile` |
| `get_latest_assessment(db, member_id)` | member lookup | Most recent assessment of any tier |
| `get_assessment_history(db, member_id, tier=None)` | optional tier filter | List of past assessments |

**Scoring pipeline (identical to validated simulation):**

1. Reverse-score items AS4, AF4, BS4, BF4, CS4, CF4: `8 - raw`
2. Compute subscale means (average of available items per subscale)
3. Normalise to 0-10: `(mean - 1) * 10 / 6`
4. Classify domain states using split thresholds (sat >= 6.46, frust >= 4.38)
5. Derive type: 8 base patterns (sat >= 5.5 binary) x 3 frustration modifiers (frust >= 5.0 count)
6. Generate 125-profile code (5 sat levels per domain)
7. Detect frustration signatures (frust >= 4.38: high sat = medium risk, low sat = high risk)

**Confidence by tier:**
- Onboarding (1 item per subscale): 0.50. Enough for a directional signal, not reliable for type assignment.
- Standard (2 items per subscale): 0.70. Adequate for provisional type and domain states.
- Full (4 items per subscale): 0.90. Validated subscale means, reliable type assignment.

### 1.3 Migration

One Alembic migration creates the `abc_assessments` table. No changes to existing tables. The `ABCProfile` table gains no new columns; it receives records through the bridge function in Section 3.

---

## 2. Assessment flow: three-tier questionnaire

### 2.1 Where assessments live in the user journey

Assessments are delivered through the existing check-in interface. They are special check-in types, not a separate product surface.

| Tier | When | Trigger | Duration |
|------|------|---------|----------|
| **Onboarding** | First or second check-in after signup | Onboarding flow, `onboarding_step` progression | ~2 min (6 items) |
| **Standard** | Within first two weeks | Prompted after 5-7 daily check-ins | ~4 min (12 items) |
| **Full** | 2-3 months on platform | Prompted after 30+ check-ins | ~8 min (24 items) |

The onboarding assessment replaces or supplements the current baseline calibration questionnaire. It gives the athlete an immediate insight ("You're a Steady Architect") that builds trust and shows the platform's value from the first interaction.

### 2.2 Question items

All 24 items are defined in the simulation dashboard and validated against the six-factor CFA structure. The items measure need satisfaction and frustration through self-report, adapted from the Basic Psychological Need Satisfaction and Frustration Scale for sport and performance contexts.

**Item structure per subscale (4 items each):**

| Subscale | Item 1 (tier 1) | Item 2 (tier 2) | Items 3-4 (tier 3) |
|----------|-----------------|-----------------|---------------------|
| A-Sat | Goal confidence | Progress feeling | Path clarity, realism (R) |
| A-Frust | Feeling held back | Effort doubt | External blocks, clear path (R) |
| B-Sat | Connection | Support and understanding | Authenticity, outsider (R) |
| B-Frust | Exclusion | Lack of acceptance | Conditional relationships, full acceptance (R) |
| C-Sat | Competence | Learning | Challenge-readiness, out of depth (R) |
| C-Frust | Judged not developed | Lack of opportunity | Punishment for mistakes, supportive environment (R) |

(R) = reverse-scored. Each subscale's fourth item is reverse-scored to detect acquiescence bias.

### 2.3 API endpoints

Add to the existing `/checkins` router or create a new `/assessments` router. The latter is cleaner because assessments have a different response structure from daily check-ins.

**New router: `/api/v1/assessments`**

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/questions/{tier}` | GET | Path: tier (onboarding/standard/full) | List of question objects with id, text, subscale, domain, reverse flag |
| `/` | POST | `{tier, responses: [{item_id, value}]}` | Scored assessment with type, profile, domain states, frustration sigs |
| `/latest` | GET | | Most recent assessment (any tier) |
| `/history` | GET | Query: `tier` (optional), `limit` (default 10) | List of past assessments |

**POST `/assessments/` response shape:**

```json
{
  "id": "uuid",
  "tier": "standard",
  "subscales": {
    "a_sat": 7.22, "a_frust": 3.61,
    "b_sat": 5.83, "b_frust": 4.17,
    "c_sat": 8.06, "c_frust": 2.50
  },
  "type_name": "Steady Architect",
  "profile_code": "4-3-5",
  "dominant_domain": "craft",
  "domain_states": {
    "ambition": "Thriving",
    "belonging": "Mild",
    "craft": "Thriving"
  },
  "frustration_signatures": [],
  "confidence": 0.70,
  "description": {
    "tagline": "Building with purpose and precision",
    "strengths": ["Systems thinking", "Independent execution", ...],
    "growth_edge": "Investing in collaborative relationships...",
    "pattern": {"ambition": "strong", "belonging": "developing", "craft": "strong"}
  },
  "timestamp": "2026-03-09T14:30:00Z"
}
```

### 2.4 Frontend: assessment in the check-in flow

**Member route:** `/member/checkin/assessment/[tier]`

The assessment page uses the same layout as the daily check-in but with a different question set and results display. Components needed:

| Component | Purpose |
|-----------|---------|
| `AssessmentTierPicker.svelte` | Card selector for onboarding/standard/full |
| `AssessmentForm.svelte` | Question list with 7-point Likert scale, progress bar |
| `AssessmentResults.svelte` | Type card, domain state badges, strengths, growth edge, frustration signals |
| `AssessmentHistory.svelte` | Timeline of past assessments with type changes |

**Design principles:**
- The Likert scale uses 1-7 (not 1-10 like daily check-ins). The label change from "Strongly disagree" to "Strongly agree" must be clear.
- Results should feel like a reveal, not a report. Show the archetype name and tagline prominently, then unfold detail (domain states, strengths, growth edge).
- For onboarding, emphasise that this is a first impression: "Your profile will sharpen as we learn more about you."
- For full assessment, show comparison to previous assessments if available.

### 2.5 Prompting the assessment

The home card system (`home_service.py`) generates assessment prompts at the right moments:

| Card | Condition | Priority |
|------|-----------|----------|
| "Complete your first assessment" | `onboarding_step < 2` and no onboarding assessment | Critical (top of feed) |
| "Strengthen your profile" | 5-7 check-ins completed, no standard assessment | High |
| "Take your full assessment" | 30+ check-ins, no full assessment (or last full > 90 days) | Medium |
| "Your profile has evolved" | Latest assessment type differs from latest check-in type | Low (informational) |

---

## 3. Scoring pipeline alignment

### 3.1 The bridge: six subscales to three dimensions

The existing `ABCProfile` model stores three scores (0-100). The new instrument produces six scores (0-10). The bridge function converts between them so all current consumers keep working.

**Conversion logic:**

```python
def subscales_to_abc_profile(subscales: dict) -> dict:
    """Convert 6 subscales (0-10) to 3 dimensions (0-100)."""
    return {
        "ambition": subscales["a_sat"] * 10,      # 0-10 → 0-100
        "belonging": subscales["b_sat"] * 10,
        "craft": subscales["c_sat"] * 10,
    }
```

This maps satisfaction scores to the existing dimension scores. Frustration is a separate construct that the current `ABCProfile` does not capture; it flows through domain states and frustration signatures instead.

**Why satisfaction only:** The current three-dimension model treats each ABC dimension as a single continuum. The six-subscale model splits each into satisfaction (need fulfilment) and frustration (need thwarting). These are partially independent: an athlete can feel satisfied and frustrated in the same domain (the "Vulnerable" state). Mapping frustration into the single-dimension model would conflate distinct signals. Satisfaction is the closer proxy to what the current system measures.

### 3.2 Replacing the extraction pipeline (phased)

The current extraction pipeline (rule-based weights, behavioural scoring, LLM enrichment) infers ABC from proxy questions. The validated instrument measures ABC directly. Over time, the instrument should become the anchor and the extraction pipeline should calibrate against it.

**Phase 1 (this PRD): coexistence.** Assessments and daily check-ins produce independent `ABCProfile` records. The assessment record has higher confidence (0.5-0.9 depending on tier) than rule-based extraction (0.70). The `extraction_method` field on `ABCProfile` gains a new value: `assessment`.

**Phase 2 (future): calibration.** Once enough athletes have both assessment scores and daily check-in histories, the rule-based extraction weights can be recalibrated against the instrument's ground truth. The current weights (motivation x 0.30 + autonomy x 0.30 + challenge_threat x 0.20 + competence x 0.20 for ambition) are educated guesses; real data will reveal the true mapping.

**Phase 3 (future): unified scoring.** The daily check-in extractions and periodic assessments feed into a single longitudinal ABC model. The assessment establishes the baseline and periodic recalibration; daily check-ins track movement between assessments. A Bayesian prior from the latest assessment anchors the daily extraction, reducing noise.

### 3.3 Type system alignment

The current Ero codebase uses a 36-type system (12 types per domain, classified by nearest-neighbour on a 3D ABC space). The validated simulation uses a 24-type system (8 base patterns x 3 frustration modifiers). These are different classification schemes.

**Resolution:** The 24-type system replaces the 36-type system. The 36 types were designed before the satisfaction/frustration split was validated. The 24-type system captures frustration as a first-class dimension through the modifier (Steady/Striving/Resolute), which the 36-type system cannot express. The 36-type classification code in `framework_vocab.py` and `abc_archetype_service.py` should be updated to use the new system.

**Migration path:**
1. Add the 24 type definitions to `framework_vocab.py` alongside the existing 36.
2. Update `abc_archetype_service.py` to use the new classification when the source is an assessment (`extraction_method = 'assessment'`).
3. Update `ABCProfileCard.svelte`, `ArchetypeBadge.svelte`, and `ArchetypeDistribution.svelte` to render 24 types.
4. Deprecate the 36-type system once all athletes have at least one assessment.

### 3.4 Belbin role update

The current Belbin implementation uses direct ABC weight mappings (e.g. Shaper: A=0.6, B=0.1, C=0.3). The validated model uses a cluster-affinity architecture: domain satisfaction ranking selects the top two clusters (Thinking/People/Action), and Big Five percentiles differentiate roles within each cluster.

**This is a future workstream.** The current Belbin mapping works adequately for the existing system. The cluster-affinity model requires Big Five inference, which depends on six subscale scores. Once most athletes have assessment-derived subscale scores, the Belbin calculation can switch to the validated method. For now, the dashboard simulation demonstrates the target architecture.

---

## 4. What changes in existing code

### 4.1 Backend changes

| File | Change | Scope |
|------|--------|-------|
| `models/abc_assessment.py` | **New file.** SQLAlchemy model for `abc_assessments` table. | New |
| `services/abc_assessment_service.py` | **New file.** Scoring pipeline (reverse-score, subscale means, normalise, type derivation, domain states, frustration sigs). | New |
| `routers/assessments.py` | **New file.** REST endpoints for questions, submission, history. | New |
| `schemas/assessment.py` | **New file.** Pydantic request/response models. | New |
| `core/framework_vocab.py` | Add 24-type definitions (8 base patterns, 3 modifiers, type descriptions). Keep 36-type for backward compatibility until deprecated. | Edit |
| `services/abc_extraction_service.py` | Add `extraction_method = 'assessment'` path. Bridge function to generate `ABCProfile` from assessment subscales. | Edit |
| `services/checkin_service.py` | No changes in Phase 1. Assessment submission is a separate endpoint, not routed through check-in submission. | None |
| `routers/abc.py` | Add optional `include_assessments` query param to `/me/history`. | Edit |
| `main.py` | Register new router. | Edit |

### 4.2 Frontend changes

| File/Component | Change | Scope |
|----------------|--------|-------|
| `routes/member/checkin/assessment/` | **New route.** Assessment tier picker, form, results. | New |
| `components/abc/AssessmentResults.svelte` | **New component.** Type reveal card with domain states, strengths, growth edge. | New |
| `components/abc/AssessmentHistory.svelte` | **New component.** Timeline showing type changes across assessments. | New |
| `components/abc/ABCProfileCard.svelte` | Update to show assessment-derived type alongside check-in-derived type. Add confidence indicator. | Edit |
| `components/abc/ArchetypeBadge.svelte` | Support 24-type names and colour scheme (by base pattern, not domain). | Edit |
| `components/onboarding/` | Add assessment tier to onboarding flow after baseline calibration. | Edit |
| `queries/assessments.ts` | **New file.** TanStack Query hooks for assessment endpoints. | New |
| `api/generated/` | Regenerate via Orval after backend endpoints are added. | Regenerate |

### 4.3 Database migration

One migration file:
- Create `abc_assessments` table with indexes
- No changes to existing tables

---

## 5. What this PRD does not cover

- **Big Five inference from subscales.** The weight matrix is validated in simulation but is internal only. No user-facing Big Five display is planned.
- **Belbin cluster-affinity switch.** The current ABC-weight Belbin mapping continues until sufficient assessment data exists.
- **Adaptive item selection.** Future tiers could use IRT (Item Response Theory) to select the most informative questions dynamically. This requires real response data.
- **Team-level assessment items.** The simulation includes 6 team context items (30 total). These are excluded from the individual assessment for now. Team context analysis becomes relevant when multiple team members have assessment data.
- **Recalibration of extraction weights.** Phase 2 work that depends on collecting paired data (assessment scores + daily check-in responses from the same athletes).
- **CFA revalidation with real data.** The R/lavaan validation used simulated data. Real respondent data should confirm the six-factor structure before the instrument is treated as clinically validated.

---

## 6. Implementation sequence

| Step | Dependency | Effort |
|------|------------|--------|
| 1. Create `ABCAssessment` model + migration | None | Small |
| 2. Port scoring service from simulation | Step 1 | Medium |
| 3. Build assessment router + schemas | Steps 1-2 | Medium |
| 4. Add 24-type definitions to `framework_vocab.py` | None | Small |
| 5. Build assessment form component (SvelteKit) | Step 3 | Medium |
| 6. Build results display component | Steps 3-4 | Medium |
| 7. Wire into onboarding flow | Steps 5-6 | Small |
| 8. Add home card prompts for standard and full tiers | Steps 5-6 | Small |
| 9. Regenerate Orval types | Step 3 | Small |
| 10. Update ABC profile card to show assessment type | Steps 3-4 | Small |

Steps 1-4 are backend and can run in parallel with steps 5-6 (frontend). Steps 7-10 depend on both tracks completing.

---

## 7. Success criteria

| Metric | Target | How measured |
|--------|--------|-------------|
| Onboarding completion | 80%+ of new users complete the onboarding assessment | `abc_assessments` count vs new `members` count |
| Standard assessment uptake | 50%+ of users who complete onboarding take the standard within 14 days | Tier funnel analysis |
| Full assessment uptake | 30%+ of active users (30+ check-ins) complete the full assessment | Tier funnel analysis |
| Type stability | Full assessment type matches simulation distribution (no type > 15%) | Type distribution query on real data |
| Extraction calibration lift | Rule-based extraction correlation with assessment scores improves from baseline after Phase 2 recalibration | Pearson r between daily extraction and nearest assessment |
| User trust signal | Users who complete onboarding assessment have higher 7-day retention than those who skip | Cohort analysis |
