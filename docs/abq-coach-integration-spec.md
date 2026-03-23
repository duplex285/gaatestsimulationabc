# ABQ and Coach Rating Integration Specification

This document specifies how the Athlete Burnout Questionnaire (ABQ) and structured coach ratings integrate into the Ero platform (second-game). It covers Workstreams 2 and 3 from the Phase Two plan: database models, API endpoints, scoring services, administration schedules, and the ROC analysis pipeline that connects collected data back to the abc-assessment-simulation threshold derivation functions.

## 1. ABQ Integration Design

### 1.1 The ABQ instrument

The ABQ (Raedeke & Smith, 2001; validated by Grugan et al., 2024) contains 15 items scored on a 5-point Likert scale (1 = almost never, 5 = almost always). Three subscales of five items each:

| Subscale | Abbreviation | Items | Description |
|---|---|---|---|
| Reduced Sense of Accomplishment | RSA | 1, 5, 7, 13, 14 | Perceived failure to achieve sport goals |
| Emotional/Physical Exhaustion | EXH | 2, 4, 8, 10, 12 | Depletion from sport demands |
| Sport Devaluation | SD | 3, 6, 9, 11, 15 | Loss of interest and caring about sport |

Items 1 and 14 are reverse-scored. Higher subscale means indicate greater burnout.

Reliability: omega = .77 to .85 (Grugan et al., 2024). ESEM provides superior fit to CFA (CFI .964 vs .853). Measurement invariant across gender, sport type, and age.

### 1.2 ABQ items

The 15 items, grouped by subscale:

**RSA (Reduced Sense of Accomplishment):**
1. I am accomplishing many worthwhile things in sport. *(reverse-scored)*
5. I am not achieving much in sport.
7. I feel unsuccessful at sport.
13. I don't feel like I am achieving much in sport.
14. I feel successful at sport. *(reverse-scored)*

**EXH (Emotional/Physical Exhaustion):**
2. I feel so tired from training that I have trouble finding energy to do other things.
4. I feel overly tired from my sport participation.
8. I feel physically worn out from sport.
10. I feel exhausted by sport.
12. I am exhausted by the mental and physical demands of sport.

**SD (Sport Devaluation):**
3. The effort I spend in sport would be better spent doing other things.
6. I don't care as much about my sport performance as I used to.
9. I'm not into sport like I used to be.
11. I have negative feelings toward sport.
15. I don't care anymore about my sport.

### 1.3 Scoring logic

Reverse coding applies to items 1 and 14: `reversed = 6 - raw_value`.

Each subscale score is the mean of its five items (after reverse coding). Range: 1.0 to 5.0. Higher values indicate greater burnout.

Clinical interpretation thresholds (from Raedeke & Smith, 2001):
- Low burnout: subscale mean < 2.0
- Moderate burnout: 2.0 to 3.0
- High burnout: > 3.0

### 1.4 Database schema: ABQProfile model

Follows the same patterns as `ABCProfile` in `services/api/src/models/abc_profile.py`. Uses `Base`, `TimestampMixin`, UUID primary keys, and foreign key to `members.id`.

```python
# services/api/src/models/abq_profile.py

class ABQProfile(Base, TimestampMixin):
    """ABQ (Athlete Burnout Questionnaire) profile from monthly assessment."""

    __tablename__ = "abq_profiles"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    member_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Raw item responses stored for audit and re-scoring
    raw_responses: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Subscale means (1.0 to 5.0, after reverse coding)
    rsa: Mapped[float] = mapped_column(Float, nullable=False)  # Reduced Sense of Accomplishment
    exh: Mapped[float] = mapped_column(Float, nullable=False)  # Emotional/Physical Exhaustion
    sd: Mapped[float] = mapped_column(Float, nullable=False)   # Sport Devaluation

    # Composite burnout score (mean of three subscales)
    composite: Mapped[float] = mapped_column(Float, nullable=False)

    # Administration metadata
    administration_month: Mapped[str] = mapped_column(
        String(7), nullable=False, index=True,  # "2026-03" format
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    member: Mapped["Member"] = relationship("Member", backref="abq_profiles")

    __table_args__ = (
        Index("ix_abq_profiles_member_time_desc", "member_id", desc("timestamp")),
        # One ABQ per member per month
        Index("ix_abq_profiles_member_month", "member_id", "administration_month", unique=True),
    )
```

Key design decisions:
- `raw_responses` stores the full item-level data as JSON for re-scoring and psychometric analysis.
- `administration_month` enforces one ABQ per athlete per month via a unique composite index.
- `composite` stores the overall burnout mean for quick queries, though subscale-level analysis is primary.

### 1.5 Check-in template configuration

The ABQ uses the existing `CheckinTemplate` model. A seed script creates the ABQ template with its 15 items:

```python
abq_template = CheckinTemplate(
    name="Athlete Burnout Questionnaire (ABQ)",
    description="Monthly burnout assessment (Raedeke & Smith, 2001). 15 items, ~3 minutes.",
    questions=[
        {"id": "abq_1", "text": "I am accomplishing many worthwhile things in sport.",
         "type": "likert", "min": 1, "max": 5, "labels": ["Almost never", "Rarely", "Sometimes", "Frequently", "Almost always"],
         "subscale": "rsa", "reverse": True},
        {"id": "abq_2", "text": "I feel so tired from training that I have trouble finding energy to do other things.",
         "type": "likert", "min": 1, "max": 5, "labels": ["Almost never", "Rarely", "Sometimes", "Frequently", "Almost always"],
         "subscale": "exh", "reverse": False},
        # ... remaining 13 items follow the same structure
        {"id": "abq_14", "text": "I feel successful at sport.",
         "type": "likert", "min": 1, "max": 5, "labels": ["Almost never", "Rarely", "Sometimes", "Frequently", "Almost always"],
         "subscale": "rsa", "reverse": True},
        {"id": "abq_15", "text": "I don't care anymore about my sport.",
         "type": "likert", "min": 1, "max": 5, "labels": ["Almost never", "Rarely", "Sometimes", "Frequently", "Almost always"],
         "subscale": "sd", "reverse": False},
    ],
    is_active=True,
    season_type=None,  # administered year-round
)
```

The `questions` JSON structure includes `subscale` and `reverse` metadata so the scoring service can process responses without hardcoded item mappings.

### 1.6 ABQ scoring service

Located at `services/api/src/services/abq_service.py`. Follows the same service-class pattern as `ABCService`.

```python
# services/api/src/services/abq_service.py

# Item-to-subscale mapping
ABQ_SUBSCALES = {
    "rsa": ["abq_1", "abq_5", "abq_7", "abq_13", "abq_14"],
    "exh": ["abq_2", "abq_4", "abq_8", "abq_10", "abq_12"],
    "sd":  ["abq_3", "abq_6", "abq_9", "abq_11", "abq_15"],
}

# Reverse-scored items
REVERSE_ITEMS = {"abq_1", "abq_14"}


def reverse_code(value: int) -> int:
    """Reverse a 5-point Likert value: 1->5, 2->4, 3->3, 4->2, 5->1."""
    return 6 - value


def score_abq(responses: dict[str, int]) -> dict:
    """Compute ABQ subscale means from raw item responses.

    Args:
        responses: dict mapping item IDs (abq_1 through abq_15) to integer values (1-5)

    Returns:
        dict with rsa, exh, sd (subscale means), composite (overall mean),
        and scored_items (after reverse coding)
    """
    scored = {}
    for item_id, raw in responses.items():
        scored[item_id] = reverse_code(raw) if item_id in REVERSE_ITEMS else raw

    subscale_scores = {}
    for subscale, items in ABQ_SUBSCALES.items():
        values = [scored[item] for item in items if item in scored]
        subscale_scores[subscale] = round(sum(values) / len(values), 2) if values else None

    composite = round(
        sum(v for v in subscale_scores.values() if v is not None)
        / sum(1 for v in subscale_scores.values() if v is not None),
        2,
    )

    return {
        "rsa": subscale_scores["rsa"],
        "exh": subscale_scores["exh"],
        "sd": subscale_scores["sd"],
        "composite": composite,
        "scored_items": scored,
    }


class ABQService:
    """Read and write layer for ABQ profiles."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_abq(self, member_id: UUID, responses: dict[str, int]) -> ABQProfile:
        """Score and store an ABQ submission."""
        result = score_abq(responses)
        month_str = datetime.now(UTC).strftime("%Y-%m")

        profile = ABQProfile(
            member_id=member_id,
            raw_responses=responses,
            rsa=result["rsa"],
            exh=result["exh"],
            sd=result["sd"],
            composite=result["composite"],
            administration_month=month_str,
        )
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def get_latest(self, member_id: UUID) -> ABQProfile | None:
        """Get the most recent ABQ profile for a member."""
        result = await self.db.execute(
            select(ABQProfile)
            .where(ABQProfile.member_id == member_id)
            .order_by(ABQProfile.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(self, member_id: UUID, months: int = 12) -> list[ABQProfile]:
        """Get ABQ history for trend analysis."""
        cutoff = datetime.now(UTC) - timedelta(days=months * 30)
        result = await self.db.execute(
            select(ABQProfile)
            .where(ABQProfile.member_id == member_id, ABQProfile.timestamp >= cutoff)
            .order_by(ABQProfile.timestamp.desc())
        )
        return list(result.scalars().all())
```

### 1.7 API endpoints

New router at `services/api/src/routers/abq.py`, mounted as `/api/v1/abq`.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/abq/submit` | Athlete | Submit 15-item ABQ responses, returns scored profile |
| `GET` | `/api/v1/abq/me` | Athlete | Get latest ABQ profile |
| `GET` | `/api/v1/abq/me/history` | Athlete | Get ABQ history (default 12 months) |
| `GET` | `/api/v1/abq/leader/member/{member_id}` | Leader | Get athlete's ABQ history |
| `GET` | `/api/v1/abq/leader/team` | Leader | Get team ABQ summary (latest per member) |

Request schema for `POST /submit`:

```python
class ABQSubmitRequest(BaseModel):
    responses: dict[str, int] = Field(
        ...,
        description="Item responses: keys abq_1 through abq_15, values 1-5",
        min_length=15,
        max_length=15,
    )
```

Response schema:

```python
class ABQProfileResponse(BaseModel):
    id: str
    member_id: str
    rsa: float = Field(..., description="Reduced Sense of Accomplishment (1.0-5.0)")
    exh: float = Field(..., description="Emotional/Physical Exhaustion (1.0-5.0)")
    sd: float = Field(..., description="Sport Devaluation (1.0-5.0)")
    composite: float = Field(..., description="Overall burnout mean (1.0-5.0)")
    administration_month: str
    timestamp: datetime
```

### 1.8 Administration schedule

The ABQ is administered monthly, separate from the weekly ABC check-in cycle. Schedule logic:

- The platform prompts each athlete for ABQ completion once per calendar month.
- The ABQ prompt appears on the first Monday of each month (or the nearest active day).
- Athletes have a 7-day window to complete the ABQ before a reminder is sent.
- The unique index on `(member_id, administration_month)` prevents duplicate submissions.
- ABQ completion is optional but tracked. Non-completion after the reminder is logged for data completeness analysis.

The APScheduler job (in `services/api/src/core/scheduler.py`) triggers the monthly ABQ prompt:

```python
scheduler.add_job(
    trigger_monthly_abq,
    trigger="cron",
    day="1-7",
    day_of_week="mon",
    hour=9,
    id="monthly_abq_prompt",
)
```

### 1.9 Linking ABQ data to ABC data for ROC analysis

Each ABQ profile is linked to the athlete's ABC history through `member_id` and temporal proximity. The pairing logic:

1. For each ABQProfile, find the most recent ABCProfile for the same `member_id` within the preceding 7 days.
2. If no ABC profile exists within 7 days, the ABQ record is excluded from ROC analysis (unpaired).
3. The paired dataset contains: ABC subscale scores (0-100 scale) and ABQ subscale means (1.0-5.0 scale).

The ABC-to-ABQ mapping for criterion validation:

| ABC predictor (frustration subscale) | ABQ criterion | Binary classification | Direction |
|---|---|---|---|
| Craft Frustration score | RSA >= 3.0 | 1 = high RSA burnout | Higher CF predicts RSA burnout |
| Ambition Frustration score | SD >= 3.0 | 1 = high SD burnout | Higher AF predicts SD burnout |
| Total Frustration composite | EXH >= 3.0 | 1 = high EXH burnout | Higher total frustration predicts EXH |
| Ambition Satisfaction score | RSA >= 3.0 | 1 = high RSA burnout | Lower AS predicts RSA burnout (invert AS) |

The ABQ >= 3.0 cutoff for "high burnout" is the clinical benchmark from Raedeke & Smith (2001). This binary classification is the criterion variable for ROC analysis.


## 2. Coach Rating Integration Design

### 2.1 Rating items

Three structured items per athlete, completed weekly by the athlete's primary coach/leader:

| Item | Prompt | Scale | ABC domain validated |
|---|---|---|---|
| Ambition rating | "Rate this athlete's competitive drive and initiative this week." | 1-10 | Ambition Satisfaction activation |
| Belonging rating | "Rate this athlete's connection with teammates this week." | 1-10 | Belonging Satisfaction activation |
| Craft rating | "Rate this athlete's skill development effort this week." | 1-10 | Craft Satisfaction activation |

Optional concern flag:
- "I am concerned about this athlete's wellbeing." (yes/no boolean)
- When flagged: triggers comparison with ABC trajectory to test co-occurrence of coach concern and ABC decline.

### 2.2 Database schema: CoachRating model

```python
# services/api/src/models/coach_rating.py

class CoachRating(Base, TimestampMixin):
    """Structured coach observation ratings per athlete per week."""

    __tablename__ = "coach_ratings"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    member_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    coach_user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Structured ratings (1-10 scale)
    ambition_rating: Mapped[float] = mapped_column(Float, nullable=False)
    belonging_rating: Mapped[float] = mapped_column(Float, nullable=False)
    craft_rating: Mapped[float] = mapped_column(Float, nullable=False)

    # Concern flag
    concern_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    concern_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Week identifier for deduplication
    rating_week: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True,  # "2026-W12" ISO week format
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    member: Mapped["Member"] = relationship("Member", backref="coach_ratings")
    coach: Mapped["User"] = relationship("User", foreign_keys=[coach_user_id])

    __table_args__ = (
        # One rating per coach per athlete per week
        Index(
            "ix_coach_ratings_member_coach_week",
            "member_id", "coach_user_id", "rating_week",
            unique=True,
        ),
    )
```

Key design decisions:
- `coach_user_id` links to the `users` table (not members), because coaches are users with leader/coach roles.
- `rating_week` uses ISO week format ("2026-W12") to enforce one rating per athlete per week per coach.
- `concern_note` is optional free text that accompanies the boolean flag, giving coaches space to explain their concern without making the field mandatory.

### 2.3 Integration with the leader review flow

Coach ratings fit into the existing leader flow at `services/api/src/routers/leader.py`. The existing flow shows member lists, detail views, alerts, and trajectories. Coach ratings add a structured observation step.

The integration point is the leader's member detail view. When a leader views a member, the UI shows:
1. The existing signals, trends, and alerts (unchanged).
2. A "Weekly Rating" card that either shows the current week's rating (if submitted) or prompts the coach to submit one.
3. Rating history as a supplementary trend line on the member trajectory chart.

The concern flag, when triggered, generates an alert through the existing alert system (the `Alert` model in `services/api/src/models/alert.py`). The alert has `severity="info"`, `signal_type="coach_concern"`, and `message` populated from the coach's note.

### 2.4 API endpoints

Endpoints are added to the existing leader router or a new `/api/v1/coach-ratings` router.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/leader/member/{member_id}/rating` | Leader | Submit weekly rating for an athlete |
| `GET` | `/api/v1/leader/member/{member_id}/ratings` | Leader | Get rating history for an athlete |
| `GET` | `/api/v1/leader/ratings/pending` | Leader | List athletes without a rating this week |
| `GET` | `/api/v1/abq/leader/concern-alerts` | Leader | Get unresolved concern flags |

Request schema for `POST /rating`:

```python
class CoachRatingRequest(BaseModel):
    ambition_rating: float = Field(..., ge=1, le=10, description="Competitive drive and initiative")
    belonging_rating: float = Field(..., ge=1, le=10, description="Connection with teammates")
    craft_rating: float = Field(..., ge=1, le=10, description="Skill development effort")
    concern_flag: bool = Field(False, description="Wellbeing concern")
    concern_note: str | None = Field(None, max_length=500, description="Optional concern details")
```

Response schema:

```python
class CoachRatingResponse(BaseModel):
    id: str
    member_id: str
    coach_user_id: str
    ambition_rating: float
    belonging_rating: float
    craft_rating: float
    concern_flag: bool
    concern_note: str | None
    rating_week: str
    timestamp: datetime
```

### 2.5 Administration schedule

- Frequency: weekly, aligned with the existing ABC check-in cadence.
- The leader dashboard shows a "Pending Ratings" badge when athletes have not been rated for the current ISO week.
- Coaches can rate athletes at any point during the week. The unique index prevents duplicate submissions for the same week.
- Batch submission: the UI supports rating multiple athletes in sequence from the team list view, reducing friction.


## 3. ROC Analysis Pipeline

### 3.1 Purpose

The ROC analysis pipeline replaces synthetic thresholds with empirically derived cutoffs. It uses paired ABC + ABQ data and paired ABC + coach rating data to determine the ABC score values that best discriminate between burnout and non-burnout states.

### 3.2 Paired data extraction

A scheduled job (or manual script invocation) extracts paired datasets from the platform database:

**ABC-ABQ pairs:**
1. Query all `ABQProfile` records.
2. For each, find the nearest `ABCProfile` for the same `member_id` within 7 days prior.
3. Exclude unpaired records.
4. Output: CSV with columns `member_id, abc_ambition, abc_belonging, abc_craft, abc_ambition_sat, abc_ambition_frust, abc_belonging_sat, abc_belonging_frust, abc_craft_sat, abc_craft_frust, abq_rsa, abq_exh, abq_sd, abq_composite`.

**ABC-Coach pairs:**
1. Query all `CoachRating` records.
2. For each, find the nearest `ABCProfile` for the same `member_id` within 3 days (ratings and check-ins are both weekly, so temporal proximity is tighter).
3. Output: CSV with columns `member_id, abc_ambition, abc_belonging, abc_craft, coach_ambition, coach_belonging, coach_craft, concern_flag`.

### 3.3 Trigger conditions

The ROC analysis runs when paired dataset counts cross thresholds:

| Dataset | Minimum N | Rationale |
|---|---|---|
| ABC-ABQ pairs | 200 | Sufficient for stable AUC estimation with bootstrap CI |
| ABC-Coach pairs | 200 | Same statistical requirement |

A monitoring query checks counts weekly:

```sql
-- ABC-ABQ pair count
SELECT COUNT(*) FROM abq_profiles abq
JOIN LATERAL (
    SELECT id FROM abc_profiles abc
    WHERE abc.member_id = abq.member_id
      AND abc.timestamp BETWEEN abq.timestamp - INTERVAL '7 days' AND abq.timestamp
    ORDER BY abc.timestamp DESC
    LIMIT 1
) paired ON TRUE;
```

When the count reaches 200, the platform sends a notification to the admin dashboard and logs readiness for threshold derivation.

### 3.4 Connection to abc-assessment-simulation functions

The paired CSV exports feed directly into the existing threshold derivation functions in `abc-assessment-simulation/src/psychometric/threshold_derivation.py`:

1. **`compute_roc_curve(scores, criterion)`**: Takes continuous ABC scores and binary ABQ criterion (burnout vs. non-burnout).
2. **`youden_index_optimal_cutoff(fpr, tpr, thresholds)`**: Finds the Youden-optimal cutoff that maximises J = sensitivity + specificity - 1.
3. **`bootstrap_threshold_ci(scores, criterion, n_bootstrap=2000)`**: Produces 95% bootstrap confidence intervals around the optimal threshold.

The pipeline script (`scripts/derive_thresholds.py`, to be created) orchestrates these steps:

```
For each ABC-ABQ subscale pairing:
    1. Load paired data from CSV
    2. Create binary criterion: ABQ subscale >= 3.0 -> 1, else -> 0
    3. Call compute_roc_curve(abc_scores, criterion)
    4. Call youden_index_optimal_cutoff(fpr, tpr, thresholds)
    5. Call bootstrap_threshold_ci(abc_scores, criterion)
    6. Record: optimal_threshold, AUC, sensitivity, specificity, CI_lower, CI_upper
```

For coach ratings, the same pipeline applies but the criterion is defined differently:
- Concern flag = 1 as the binary criterion for each domain.
- Coach rating < 4 (out of 10) as an alternative binary criterion for domain-specific activation.

### 3.5 Output format

Results are written to `config/empirical_thresholds.yaml` in the abc-assessment-simulation repo:

```yaml
# Generated by scripts/derive_thresholds.py on 2026-XX-XX
# Source: N paired ABC-ABQ datasets from Ero platform
data_source: empirical
generation_date: "2026-XX-XX"
n_pairs: 247

thresholds:
  craft_frustration:
    criterion: "ABQ RSA >= 3.0"
    optimal_threshold: 62.3
    auc: 0.74
    sensitivity: 0.78
    specificity: 0.68
    youden_j: 0.46
    ci_lower: 58.1
    ci_upper: 66.9
    n: 247

  ambition_frustration:
    criterion: "ABQ SD >= 3.0"
    optimal_threshold: 58.7
    auc: 0.69
    sensitivity: 0.72
    specificity: 0.64
    youden_j: 0.36
    ci_lower: 53.2
    ci_upper: 63.8
    n: 247

  total_frustration:
    criterion: "ABQ EXH >= 3.0"
    optimal_threshold: 60.1
    auc: 0.71
    sensitivity: 0.75
    specificity: 0.66
    youden_j: 0.41
    ci_lower: 55.4
    ci_upper: 64.5
    n: 247

  ambition_satisfaction_activation:
    criterion: "Coach ambition_rating < 4"
    optimal_threshold: 45.2
    auc: 0.67
    # ... same structure

coach_rating_thresholds:
  ambition_activation:
    criterion: "coach_ambition_rating < 4"
    # ... same structure as above
  belonging_activation:
    criterion: "coach_belonging_rating < 4"
    # ...
  craft_activation:
    criterion: "coach_craft_rating < 4"
    # ...
```

Each threshold entry carries its derivation method, criterion variable, AUC, sensitivity, specificity, CI, and sample size. This satisfies APA Standard 5.8 (cut score method and rationale documented).

### 3.6 Convergence analysis

After both ABQ-derived and coach-derived thresholds are available, the pipeline computes convergence:
- Pearson correlation between ABQ-derived and coach-derived thresholds per domain.
- Agreement rate: proportion of athletes classified the same way by both criterion sources.
- Divergence analysis: cases where ABQ and coach ratings disagree are flagged for qualitative review.

Convergent evidence strengthens the validity argument. Divergent evidence identifies where self-report burnout (ABQ) and observable behavior (coach ratings) disagree, which is itself informative.


## 4. Data Flow Diagram

```
ATHLETE (weekly)                    COACH (weekly)                   MONTHLY
       |                                  |                              |
       v                                  v                              v
  ABC Check-in                    Coach Rating Form                 ABQ Assessment
  (9 Likert items)                (3 x 1-10 ratings                (15 Likert items)
       |                           + concern flag)                       |
       v                                  |                              v
  abc_extraction_service.py               |                     abq_service.py
  (rule-based / behavioral /              |                     (reverse code items
   LLM extraction)                        |                      1 and 14, compute
       |                                  |                      3 subscale means)
       v                                  v                              v
  +-----------+                  +---------------+              +------------+
  | ABCProfile|                  | CoachRating   |              | ABQProfile |
  | table     |                  | table         |              | table      |
  +-----------+                  +---------------+              +------------+
       |                                  |                              |
       |                                  |                              |
       +------ member_id ----------------+-------- member_id -----------+
       |                                  |                              |
       v                                  v                              v
  +------------------------------------------------------------------------+
  |                        Pairing Logic                                    |
  |  ABC-ABQ: match by member_id, ABCProfile within 7 days before ABQ     |
  |  ABC-Coach: match by member_id, ABCProfile within 3 days of rating    |
  +------------------------------------------------------------------------+
       |                                             |
       v                                             v
  ABC-ABQ paired CSV                          ABC-Coach paired CSV
       |                                             |
       +--------- N >= 200? -------------------------+
                      |
                      v
  +----------------------------------------------------------+
  |  abc-assessment-simulation threshold derivation pipeline  |
  |                                                           |
  |  1. compute_roc_curve(abc_scores, criterion_binary)       |
  |  2. youden_index_optimal_cutoff(fpr, tpr, thresholds)     |
  |  3. bootstrap_threshold_ci(scores, criterion, n=2000)     |
  +----------------------------------------------------------+
                      |
                      v
          config/empirical_thresholds.yaml
          (replaces synthetic thresholds)
                      |
                      v
  +----------------------------------------------------------+
  |  Ero platform consumes updated thresholds:               |
  |  - ABC type derivation uses empirical activation cutoffs  |
  |  - Alert system uses empirical frustration cutoffs        |
  |  - Dashboard displays confidence intervals                |
  +----------------------------------------------------------+
```

### 4.1 Concern flag alert flow

```
Coach submits rating with concern_flag = True
       |
       v
  CoachRating stored in database
       |
       v
  Alert created:
    severity = "info"
    signal_type = "coach_concern"
    member_id = rated athlete
    message = concern_note (or default text)
       |
       v
  Leader dashboard: alert appears in /leader/alerts feed
       |
       v
  Leader acknowledges or investigates
       |
       v
  System compares:
    - Recent ABC trajectory (declining?)
    - Recent ABQ score (elevated burnout?)
    - Coach concern timing vs. ABC pattern shift
       |
       v
  Co-occurrence analysis stored for ROC pipeline
```


## 5. Migration and Rollout Sequence

### Phase A: Schema and seed (week 1)

1. Create Alembic migration for `abq_profiles` table.
2. Create Alembic migration for `coach_ratings` table.
3. Seed the ABQ check-in template via `scripts/seed_dev_data.py`.
4. Register models in `services/api/src/models/__init__.py`.

### Phase B: Services and endpoints (week 2)

1. Implement `abq_service.py` with scoring and CRUD.
2. Implement `coach_rating_service.py` with submission and query logic.
3. Create `routers/abq.py` with athlete and leader endpoints.
4. Add coach rating endpoints to `routers/leader.py`.
5. Create Pydantic schemas in `schemas/abq.py` and `schemas/coach_rating.py`.

### Phase C: Scheduling and UI (week 3)

1. Add monthly ABQ prompt job to `core/scheduler.py`.
2. Add "Pending Ratings" badge logic to leader dashboard.
3. Build ABQ submission UI in SvelteKit (athlete-facing).
4. Build coach rating card in leader member detail view.
5. Regenerate Orval types from updated OpenAPI schema.

### Phase D: Pairing and export (week 4)

1. Build paired data export script (`scripts/export_paired_data.py`).
2. Build threshold derivation script (`scripts/derive_thresholds.py`) that calls the abc-assessment-simulation functions.
3. Add monitoring query for pair counts to admin dashboard.
4. Test full pipeline with synthetic data before deployment.


## 6. Open Questions

1. **ABQ licensing.** The ABQ is published in the literature and widely used in research. Confirm whether commercial platform use requires permission from Raedeke and Smith.

2. **ABQ item text.** The exact item wording should be verified against the published instrument. The items listed in Section 1.2 are from the published literature but should be confirmed against the original 2001 paper.

3. **Coach rating anchors.** The 1-10 scale needs defined anchors (e.g., 1 = "No engagement observed", 5 = "Typical engagement", 10 = "Exceptional engagement") to reduce rater variability.

4. **Multi-coach scenarios.** If an athlete has multiple coaches (e.g., head coach and position coach), should both rate independently? The current schema supports this via the unique index on `(member_id, coach_user_id, rating_week)`.

5. **ABQ clinical threshold.** The >= 3.0 cutoff for "high burnout" is conventional but not universally agreed upon. The ROC analysis itself will determine whether this cutoff produces adequate discrimination, and may suggest an alternative criterion boundary.
