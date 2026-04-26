# Self-Concordance Items Draft

Date: 2026-04-21
Status: Draft, pending expert review and cognitive pretesting
Source plan: improvement-plan-personalization-engine.md Section 16.7 (goal self-concordance)

## 1. Purpose

This document presents 4 items operationalizing the Self-Concordance Model (Sheldon & Houser-Marko, 2001; Sheldon & Goffredi, Chapter 17 of the Oxford Handbook of Self-Determination Theory). Self-concordance measures the degree to which an athlete's specific goal aligns with their core values and interests, scored along the Perceived Locus of Causality (PLOC) continuum from Ryan and Connell (1989).

Unlike the regulatory-style layer (Section 16.1), which measures regulation quality at the domain level (Ambition, Belonging, Craft as a whole), self-concordance is goal-specific. The athlete states a current primary goal and rates four reasons for pursuing it. The pattern across those four reasons defines whether the goal is autonomous (self-concordant) or controlled (non-concordant).

Self-concordance is a slowly-moving construct that benefits from biweekly tracking. Sheldon's longitudinal work shows that rising self-concordance predicts both goal attainment and well-being gains, while non-concordant goal pursuit can erode well-being even when objective progress is made.

These items are original to Ero. No licensed scale content is reproduced. The PLOC structure is academic public domain; the specific item wording is not.

## 2. Design constraints

- **Cadence:** Biweekly, joins the core ABC form. Self-concordance shifts slowly; biweekly is the minimum cadence to detect movement.
- **Placement:** Outside `REQUIRED_ITEMS`. Scored by a parallel module.
- **Goal text:** The athlete recalls or states their current primary goal at the top of the screen. The goal text itself is metadata, not scored. It is stored alongside the score for narrative reference and product display.
- **Stem:** "Thinking about a goal you are working on right now: how true is each of these reasons for pursuing it?"
- **Response scale:** 1 = Not true at all, 7 = Completely true. Agreement framing rather than behavioral frequency, because the question is about why a single goal is being pursued, not how often.
- **No reverse-scored items:** Each item maps to one PLOC dimension. Reverse coding would obscure which dimension drives the goal.
- **All four items presented together:** the athlete rates all four reasons for the same goal in the same screen. This is required for the autonomous-versus-controlled contrast to be valid.

## 3. The 4 items

### SC1 (external regulation)

"...because someone else (a coach, parent, or teammate) wants me to."

- **Construct:** External regulation, the most controlled end of the PLOC continuum.
- **Rationale:** Captures goals pursued for compliance with explicit external pressure. A high score here, alone or paired with introjection, signals that the goal is not self-owned.

### SC2 (introjected regulation)

"...because I would feel guilty, anxious, or disappointed in myself if I did not."

- **Construct:** Introjected regulation, internalized but still controlled.
- **Rationale:** Goals pursued under self-imposed pressure rather than freely chosen. Distinguished from external regulation by the source of pressure (internal versus external) but grouped with it on the controlled side of the continuum.

### SC3 (identified regulation)

"...because it matters to me personally."

- **Construct:** Identified regulation, the autonomous side of the continuum.
- **Rationale:** Goals pursued because the athlete has internalized their value. The goal is endorsed, even if the activity itself is not always enjoyable.

### SC4 (intrinsic regulation)

"...because I find the work itself interesting or rewarding."

- **Construct:** Intrinsic regulation, the most autonomous end of the continuum.
- **Rationale:** Goals pursued because the activity is inherently satisfying. Sheldon and Kasser (1995) found that intrinsic reasons are the strongest predictor of attainment-plus-well-being benefits.

## 4. Scoring model

Each item is scored independently on the 0-10 scale:

```
item_score = ((raw_1_to_7 - 1) / 6) * 10
```

Two composites:

```
autonomous = mean(SC3, SC4)    # identified + intrinsic
controlled = mean(SC1, SC2)    # external + introjected
```

Self-concordance score (signed):

```
self_concordance = autonomous - controlled    # range -10 (fully controlled) to +10 (fully autonomous)
```

Three-band classification:

| Condition | Label | Coach interpretation |
|-----------|-------|----------------------|
| `self_concordance >= 3.0` AND `autonomous >= 5.0` | `autonomous` | Goal is self-owned; protect the conditions that allow this |
| `self_concordance <= -3.0` AND `controlled >= 5.0` | `controlled` | Goal is pressure-driven; conversation about whether to keep, reframe, or release |
| Otherwise | `mixed` | Both autonomous and controlled reasons present, or signal too weak |

The 3.0 cutpoint reflects roughly half a Likert step on each dimension and matches the leaning thresholds used in the passion-quality layer.

## 5. Evidence gates

Consistent with Section 17.5:

| Condition | Gate | Effect |
|-----------|------|--------|
| All 4 items answered | Passes display + recommendation gates | Score and classification shown |
| 3 of 4 items answered, both subscales represented | Passes display only | Hedged narrative shown |
| Fewer than 3 items, OR one subscale empty | Fails display | Profile suppressed |
| All answered but classification is `mixed` | Passes display only | Hedged narrative |

## 6. Trajectory significance

Self-concordance is the only optional layer that benefits from longitudinal interpretation at the per-goal level. Sheldon's research suggests that movement matters more than absolute level: a goal that started as introjected and is moving toward identified regulation is a sign of internalization, even if the absolute self-concordance score is still mixed.

A trajectory module is not in scope for this slice. It is a Phase A or follow-up enhancement once enough biweekly cycles accumulate per athlete per goal.

## 7. Open items

- **Goal continuity across cycles.** Does the athlete state the same goal across cycles? Different goals? The product needs to capture goal identity (free-text or structured choice from prior goals) so that trajectories can be computed per goal, not per cycle. Out of scope here; flagged for product design.
- **Goal-domain mapping.** Which ABC domain (Ambition, Belonging, Craft) does the stated goal fall into? Tagging goals to domains would let self-concordance interact with the regulatory-style layer (which is per-domain). Optional Phase A enhancement.
- **Convergent validity against published self-concordance measures.** Sheldon's published instrument is in the public-domain academic literature; convergent comparison is a clean Phase A study.
- **Empirical calibration of the 3.0 cutpoint.** Theoretical prior; recalibrate against goal-attainment outcomes at season end.
- **Per-goal trajectory engine.** Separate slice. Requires goal continuity (above) plus a longitudinal scoring layer.
