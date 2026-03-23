# PRD: ABQ and Coach Rating Integration into the Second-Game Platform

## The problem

The ABC assessment's activation thresholds are synthetic. The current thresholds for satisfaction activation (6.46) and frustration activation (4.38) were derived from simulated data and literature benchmarks, not from observed relationships between ABC scores and real burnout outcomes. Without external criterion data, the platform cannot determine whether its alerts fire at the right ABC score values, whether its type classifications correspond to meaningful behavioural differences, or whether its frustration signatures predict genuine distress. Two validated criterion sources can close this gap: the Athlete Burnout Questionnaire (ABQ), a 15-item self-report measure of burnout, and structured weekly coach ratings that capture observable behaviour. Pairing these criterion measures with ABC scores enables ROC analysis to replace synthetic thresholds with empirically derived cutoffs.

## What this PRD covers

This PRD specifies three deliverables that connect criterion data collection to threshold derivation:

1. **ABQ integration**: monthly athlete self-report of burnout (15 items, three subscales), stored alongside ABC profiles and linked by member and time
2. **Coach rating integration**: weekly structured observations (three 1-to-10 ratings plus a concern flag), submitted through the leader dashboard
3. **ROC analysis pipeline**: paired data extraction, threshold derivation via Youden index, and output of empirical cutoffs with confidence intervals

---

## User stories

### Athletes

- As an athlete, I complete a 15-item ABQ assessment once per month so the platform can measure my burnout independently of my weekly check-ins.
- As an athlete, I can view my ABQ history to track my burnout trajectory over time.

### Coaches and leaders

- As a coach, I rate each athlete on three structured dimensions (ambition, belonging, craft) each week so the platform has an external behavioural signal alongside self-report data.
- As a coach, I can flag a wellbeing concern for any athlete during the rating process, which triggers an alert visible to all leaders.
- As a coach, I can see which athletes I have not yet rated this week so I can complete my ratings efficiently.

### Administrators and researchers

- As an admin, I can monitor the count of paired ABC-ABQ and ABC-coach datasets to know when the sample is large enough for threshold derivation.
- As an admin, I can trigger the ROC analysis pipeline once N >= 200 paired records exist and review the resulting empirical thresholds before they replace synthetic ones.
- As a researcher, I can export paired CSV datasets for independent psychometric analysis.

---

## Requirements by priority

### P0: must ship for criterion collection to begin

| ID | Requirement | Rationale |
|----|-------------|-----------|
| P0-1 | Create `abq_profiles` table with the schema specified in the integration spec | Stores scored ABQ data with subscale means, composite, raw responses, and a unique constraint on (member_id, administration_month) |
| P0-2 | Create `coach_ratings` table with the schema specified in the integration spec | Stores weekly structured ratings with a unique constraint on (member_id, coach_user_id, rating_week) |
| P0-3 | Implement ABQ scoring service: reverse-code items 1 and 14, compute three subscale means (RSA, EXH, SD) and composite | Scoring must match the validated algorithm from Raedeke and Smith (2001) |
| P0-4 | Build `POST /api/v1/abq/submit` endpoint accepting 15 item responses and returning scored profile | Athletes need a submission path |
| P0-5 | Build `POST /api/v1/leader/member/{member_id}/rating` endpoint accepting three ratings and optional concern flag | Coaches need a submission path |
| P0-6 | Build `GET /api/v1/abq/me` and `GET /api/v1/abq/me/history` for athlete self-service | Athletes should see their own burnout data |
| P0-7 | Build `GET /api/v1/leader/ratings/pending` listing athletes without a rating for the current ISO week | Coaches need to know who they have not rated |
| P0-8 | Enforce one ABQ per athlete per calendar month and one coach rating per athlete per coach per ISO week at the database level | Prevents duplicate data that would corrupt the paired dataset |

### P1: needed before ROC analysis can run

| ID | Requirement | Rationale |
|----|-------------|-----------|
| P1-1 | Build paired data extraction script: match each ABQProfile to the nearest ABCProfile within 7 days prior, by member_id | Produces the ABC-ABQ paired CSV required for ROC analysis |
| P1-2 | Build paired data extraction for coach ratings: match each CoachRating to the nearest ABCProfile within 3 days, by member_id | Produces the ABC-coach paired CSV |
| P1-3 | Build threshold derivation script calling `compute_roc_curve`, `youden_index_optimal_cutoff`, and `bootstrap_threshold_ci` from abc-assessment-simulation | Connects collected data to the existing psychometric functions |
| P1-4 | Output empirical thresholds to `config/empirical_thresholds.yaml` with AUC, sensitivity, specificity, Youden J, 95% CI, and sample size per threshold | Documents derivation method per APA Standard 5.8 |
| P1-5 | Add monitoring query to admin dashboard showing current ABC-ABQ and ABC-coach pair counts | Admins need to know when N >= 200 is reached |
| P1-6 | Monthly ABQ prompt: schedule via APScheduler on the first Monday of each month at 09:00, with a 7-day completion window and reminder | Drives ABQ completion rates |
| P1-7 | Concern flag alert: when a coach sets concern_flag = true, create an Alert record with severity "info" and signal_type "coach_concern" | Integrates coach observations into the existing alert system |

### P2: valuable after thresholds are derived

| ID | Requirement | Rationale |
|----|-------------|-----------|
| P2-1 | Convergence analysis: compute Pearson correlation and agreement rate between ABQ-derived and coach-derived thresholds per domain | Strengthens the validity argument through convergent evidence |
| P2-2 | ABQ submission UI in SvelteKit: 15-item Likert form with progress bar, results showing subscale interpretation | Athlete-facing experience for monthly assessment |
| P2-3 | Coach rating card in leader member detail view, with batch submission from the team list | Reduces friction for weekly rating workflow |
| P2-4 | "Pending Ratings" badge on the leader dashboard | Visual prompt to complete weekly ratings |
| P2-5 | `GET /api/v1/abq/leader/team` returning latest ABQ per member for team-level burnout overview | Gives coaches a team summary without viewing each athlete individually |
| P2-6 | Co-occurrence analysis: when a concern flag fires, compare against recent ABC trajectory and ABQ score to measure agreement between coach observation and self-report | Generates qualitative insight where criterion sources diverge |

---

## Data model summary

### ABQProfile

Stores one scored ABQ assessment per athlete per calendar month.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| member_id | UUID | FK to members, CASCADE, indexed |
| raw_responses | JSON | All 15 item responses for audit and re-scoring |
| rsa | float | Reduced Sense of Accomplishment mean (1.0 to 5.0) |
| exh | float | Emotional/Physical Exhaustion mean (1.0 to 5.0) |
| sd | float | Sport Devaluation mean (1.0 to 5.0) |
| composite | float | Mean of three subscale means |
| administration_month | varchar(7) | "2026-03" format, indexed |
| timestamp | datetime(tz) | Submission time |

**Key constraints**: unique composite index on (member_id, administration_month). Descending index on (member_id, timestamp) for latest-record lookup.

### CoachRating

Stores one structured observation per coach per athlete per ISO week.

| Column | Type | Purpose |
|--------|------|---------|
| id | UUID | Primary key |
| member_id | UUID | FK to members, CASCADE, indexed |
| coach_user_id | UUID | FK to users, CASCADE, indexed |
| ambition_rating | float | Competitive drive and initiative (1 to 10) |
| belonging_rating | float | Connection with teammates (1 to 10) |
| craft_rating | float | Skill development effort (1 to 10) |
| concern_flag | boolean | Wellbeing concern indicator, default false |
| concern_note | text | Optional free-text explanation |
| rating_week | varchar(10) | ISO week format "2026-W12", indexed |
| timestamp | datetime(tz) | Submission time |

**Key constraints**: unique composite index on (member_id, coach_user_id, rating_week).

---

## API endpoint summary

### ABQ endpoints (router: `/api/v1/abq`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/submit` | Athlete | Submit 15 item responses, returns scored ABQProfile |
| GET | `/me` | Athlete | Latest ABQ profile |
| GET | `/me/history` | Athlete | ABQ history (default 12 months) |
| GET | `/leader/member/{member_id}` | Leader | Athlete's ABQ history |
| GET | `/leader/team` | Leader | Latest ABQ per team member |

### Coach rating endpoints (router: `/api/v1/leader`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/member/{member_id}/rating` | Leader | Submit weekly rating (3 scores + concern flag) |
| GET | `/member/{member_id}/ratings` | Leader | Rating history for one athlete |
| GET | `/ratings/pending` | Leader | Athletes without a rating this week |
| GET | `/concern-alerts` | Leader | Unresolved concern flags |

---

## Success metrics

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Paired ABC-ABQ dataset size | N >= 200 | Count of ABQProfile records with a matching ABCProfile within 7 days prior |
| Paired ABC-coach dataset size | N >= 200 | Count of CoachRating records with a matching ABCProfile within 3 days |
| ROC discrimination (ABQ criterion) | AUC > 0.65 for each ABC-ABQ subscale pairing | ROC curve from `compute_roc_curve` |
| ROC discrimination (coach criterion) | AUC > 0.65 for each ABC-coach domain pairing | ROC curve from `compute_roc_curve` |
| ABQ monthly completion rate | >= 60% of active athletes per month | ABQProfile count vs active member count per administration_month |
| Coach weekly rating completion | >= 70% of athletes rated each ISO week | CoachRating count vs active member count per rating_week |
| Criterion convergence | Pearson r > 0.30 between ABQ-derived and coach-derived thresholds per domain | Convergence analysis output |

---

## Dependencies and risks

### Dependencies

| Dependency | Owner | Status | Impact if delayed |
|------------|-------|--------|-------------------|
| ABCProfile table and scoring pipeline in Ero | Existing | Shipped | Blocks all pairing logic |
| abc-assessment-simulation threshold derivation functions (`compute_roc_curve`, `youden_index_optimal_cutoff`, `bootstrap_threshold_ci`) | abc-assessment-simulation repo | Implemented | Blocks P1-3 (derivation script) |
| Member and User models with established relationships | Existing | Shipped | Blocks FK references in both new tables |
| Alert model and leader alert feed | Existing | Shipped | Blocks P1-7 (concern flag alerts) |
| APScheduler integration in `core/scheduler.py` | Existing | Shipped | Blocks P1-6 (monthly ABQ prompt) |
| CheckinTemplate model for ABQ item storage | Existing | Shipped | Blocks ABQ template seeding |
| Orval code generation for SvelteKit API types | Existing | Shipped | Blocks P2-2 and P2-3 (frontend work) |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **ABQ licensing uncertainty**: commercial platform use may require permission from Raedeke and Smith | Medium | High: could block ABQ deployment | Contact authors early. The ABQ is widely used in published research, but commercial use terms are unclear. Prepare a fallback plan using only coach ratings as the criterion source. |
| **Insufficient paired data**: if ABQ completion rates fall below 40% or temporal pairing windows are too narrow, N = 200 takes longer than expected | Medium | Medium: delays threshold derivation | Monitor completion rates from week 1. Widen the pairing window from 7 to 14 days if necessary (with documented sensitivity analysis). |
| **Coach rating variability**: without defined anchors on the 1-to-10 scale, inter-rater reliability may be poor | High | Medium: noisy criterion data weakens ROC analysis | Define rating anchors before launch (e.g., 1 = "No engagement observed", 5 = "Typical", 10 = "Exceptional"). Compute ICC after 50+ ratings to assess reliability. |
| **ABQ clinical threshold validity**: the >= 3.0 cutoff for "high burnout" is conventional but not universally agreed upon | Low | Medium: the binary criterion for ROC may misclassify borderline cases | The ROC analysis itself tests whether this cutoff produces adequate discrimination. If AUC is low, test alternative criterion boundaries (2.5, 3.5). |
| **Multi-coach disagreement**: athletes with multiple coaches may receive divergent ratings in the same week | Low | Low: the schema supports multiple coach ratings per athlete per week, but analysis must account for this | Aggregate multiple ratings per week (mean) in the pairing script. Flag high-disagreement cases for qualitative review. |

---

## Timeline recommendation

The integration spec defines four phases. The recommended calendar, assuming one engineer on backend and one on frontend:

| Phase | Scope | Duration | Deliverables |
|-------|-------|----------|--------------|
| A: Schema and seed | Alembic migrations for both tables, model registration, ABQ template seeding | Week 1 | `abq_profiles` and `coach_ratings` tables live in dev, ABQ check-in template seeded |
| B: Services and endpoints | ABQ scoring service, coach rating service, all P0 API endpoints, Pydantic schemas | Week 2 | All P0 endpoints passing integration tests |
| C: Scheduling and UI | Monthly ABQ prompt job, pending ratings badge, ABQ submission form (SvelteKit), coach rating card, Orval regeneration | Week 3 | Athletes can submit ABQ, coaches can submit ratings, prompts fire on schedule |
| D: Pairing and export | Paired data export scripts, threshold derivation script, admin monitoring query, synthetic data end-to-end test | Week 4 | Full pipeline tested with synthetic data, monitoring live in admin dashboard |

**After week 4**, the system collects data. Threshold derivation runs when both paired datasets reach N >= 200. At current projected team sizes (50 to 100 athletes, 5 to 10 coaches), reaching N = 200 ABC-ABQ pairs requires 3 to 5 months of collection (accounting for the monthly ABQ cadence and expected completion rates). ABC-coach pairs accumulate faster due to the weekly cadence: roughly 6 to 10 weeks.

---

## What this PRD does not cover

- **Threshold deployment to production.** Once empirical thresholds are derived, a separate review and deployment process updates the Ero platform's activation cutoffs. That process requires its own PRD.
- **Adaptive ABQ scheduling.** Future work could adjust ABQ frequency based on trajectory (more frequent for athletes showing rising frustration). This PRD uses fixed monthly cadence.
- **ABQ item wording verification.** The items listed in the integration spec are from the published literature. The exact wording must be verified against the original Raedeke and Smith (2001) paper before implementation.
- **Coach rating anchor definitions.** The integration spec notes the need for scale anchors. These should be defined before Phase C (UI build) but are a design task, not an engineering task.
- **CFA revalidation with real ABQ data.** The ABQ's psychometric properties (omega = .77 to .85, ESEM fit) are established in the literature. Revalidation on the platform's sample is desirable but not a prerequisite for criterion collection.
