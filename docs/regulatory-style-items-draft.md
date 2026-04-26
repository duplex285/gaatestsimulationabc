# Regulatory-Style Items Draft

Date: 2026-04-20
Status: Draft, pending expert review and cognitive pretesting
Source plan: improvement-plan-personalization-engine.md Section 16.1

## 1. Purpose

This document presents 6 new items measuring the regulatory quality of an athlete's engagement in each of the three ABC domains. The items draw on Organismic Integration Theory (Deci & Ryan, 2000; Pelletier & Rocchi, Ch. 3 in the Oxford Handbook of Self-Determination Theory), which distinguishes qualitatively different reasons for pursuing an activity along a continuum from external regulation through introjection, identification, integration, and intrinsic motivation.

The six items sit outside the core 36-item bank and produce three new subscales, one per domain. They do not modify the satisfaction or frustration scores. They add a quality-of-engagement layer that answers a different question: given how much the athlete is investing, *why* are they investing.

These items are original to ABC. No licensed scale content is reproduced.

## 2. Design constraints

- **Cadence:** Biweekly, same as the core bank. Motivational quality moves on the same cycle as need satisfaction; keeping both on the same form simplifies analysis.
- **Placement:** Outside `REQUIRED_ITEMS`. Scored by a parallel module (`regulatory_style.py`), not the core pipeline.
- **Two items per domain:** One item taps autonomous regulation (identified/integrated), one taps controlled regulation (introjected/external). With two items per domain, the instrument supports a four-way classification (identified, conflicted, introjected, amotivated) rather than the full five-way OIT continuum. The full continuum requires at least four items per domain and is deferred to a future expansion if Phase A reliability justifies it.
- **Stem:** "How often in the past two weeks did you..." (identical to the core bank).
- **Response scale:** 1 = Never, 4 = Sometimes, 7 = Very Often.
- **No reverse-scored items:** Each item measures a distinct motivational quality, not inverse endpoints of one dimension. Reverse coding would collapse information.

## 3. The 6 items

### 3.1 Ambition

**AR1 (autonomous regulation)**
"How often in the past two weeks did you pursue your goals because they genuinely matter to who you are?"

- **Construct:** Identified/integrated regulation in goal pursuit.
- **Rationale:** Taps the sense that goals are self-endorsed and aligned with personal values, the marker of autonomous motivation in OIT. Distinct from satisfaction (am I making progress) and frustration (am I blocked). The question is about origin of the drive.

**AR2 (controlled regulation)**
"How often in the past two weeks did you pursue your goals because you would feel guilty, ashamed, or anxious if you did not?"

- **Construct:** Introjected/external regulation in goal pursuit.
- **Rationale:** Taps the sense that goals are pursued to avoid internal or external sanction. OIT treats this as internally controlled motivation, which empirically predicts burnout more strongly than external regulation alone. Pairing with AR1 on the same form supports a clean autonomous-versus-controlled contrast.

### 3.2 Belonging

**BR1 (autonomous regulation)**
"How often in the past two weeks did you invest in relationships on this team because you genuinely care about the people?"

- **Construct:** Identified/integrated regulation in relational engagement.
- **Rationale:** Relational investment can be autonomous (care-driven) or controlled (keep-up-appearances, avoid-exclusion). BR1 captures the autonomous pole.

**BR2 (controlled regulation)**
"How often in the past two weeks did you invest in relationships on this team because you felt you had to keep up appearances or avoid being excluded?"

- **Construct:** Introjected/external regulation in relational engagement.
- **Rationale:** Captures the image-management and exclusion-avoidance motives that produce surface-level connection without the sustainability of autonomous investment.

### 3.3 Craft

**CR1 (autonomous regulation)**
"How often in the past two weeks did you work on your skills because improving them is important to who you are as an athlete?"

- **Construct:** Identified/integrated regulation in skill development.
- **Rationale:** Skill work driven by identity alignment and personal value, distinct from the performance feel that drives satisfaction scores.

**CR2 (controlled regulation)**
"How often in the past two weeks did you work on your skills because you worried about what coaches, teammates, or rivals would think if you did not?"

- **Construct:** Introjected/external regulation in skill development.
- **Rationale:** Skill work driven by evaluation concern. Pairs with CR1 to distinguish athletes whose craft is an identity project from those whose craft is a reputation-protection project.

## 4. Scoring model

Two subscale means per domain on the 1-7 scale, normalized to 0-10:

```
autonomous_score = ((item_auto - 1) / 6) * 10
controlled_score = ((item_ctrl - 1) / 6) * 10
rai              = autonomous_score - controlled_score    # -10 (fully controlled) to +10 (fully autonomous)
```

Dominant-style classification per domain:

| autonomous_score | controlled_score | Dominant style | Coach interpretation |
|------------------|------------------|----------------|----------------------|
| >= 5.0 | < 5.0 | `identified` | Values-driven; sustainable under setback |
| >= 5.0 | >= 5.0 | `conflicted` | Values present but so is pressure; watch for fracture under stress |
| < 5.0 | >= 5.0 | `introjected` | Driven by obligation or image; fragile under setback |
| < 5.0 | < 5.0 | `amotivated` | Neither values nor pressure; engagement is hollow |

Note on language: the labels above are internal. User-facing text uses plain-language equivalents per Section 17.4 (values-driven, pushed-and-pulled, pressure-driven, disengaged).

## 5. Evidence gates

Consistent with improvement-plan-personalization-engine.md Section 17.5 and matching the passion-quality pattern:

| Condition | Gate | Effect |
|-----------|------|--------|
| Both items in a domain answered | Passes display gate for that domain | Style shown with hedged language |
| One item missing in a domain | Fails display gate for that domain | Domain suppressed, no style shown |
| Both items answered and both scores at or above 2.0 points from the threshold | Passes recommendation gate for that domain | Style drives narrative selection |
| Both answered but either score within 1.0 point of the threshold | Passes display gate only | Style shown with "pattern still forming" framing |

Gates are per-domain, not global. An athlete can have identified regulation on Ambition with recommendation-gate passing and amotivated regulation on Craft with only display-gate passing in the same cycle.

## 6. Regulation erosion: a cross-measurement signal

A new signal fires when an athlete's dominant style on any domain moves down the autonomy ranking across two or more consecutive measurements. The ranking is ordinal:

- `identified` (most autonomous) = 3
- `conflicted` = 2
- `introjected` = 1
- `amotivated` = 0

An erosion event fires when the rank decreases by at least 1 between consecutive measurements on any domain, sustained for at least two measurements (so a single-cycle drop with recovery is not flagged). This is a leading indicator of burnout that the existing frustration-based cascade cannot see: regulatory quality can erode while satisfaction and frustration scores are still within the healthy range. Lonsdale & Hodge (2011) established the temporal ordering empirically.

## 7. Empirical calibration open items

The thresholds and the rank encoding above are theoretical priors. Phase A pilot data will recalibrate:

- Subscale reliability (McDonald's omega) at n >= 100 per domain. With only two items per subscale, reliability bounds are tight; the Phase A result determines whether the instrument needs to expand to four items per domain.
- Convergent validity against a validated OIT measure (Sport Motivation Scale or Behavioral Regulation in Sport Questionnaire, licensing permitting).
- Test-retest stability across the biweekly cadence.
- Empirical RAI cutpoints against coach-rated motivation quality at season end.
- Predictive validity: does the regulation-erosion signal predict ABQ burnout scores at the end of season?
