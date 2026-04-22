# Passion-Quality Items Draft

Date: 2026-04-20
Status: Draft, pending expert review and cognitive pretesting
Source plan: improvement-plan-personalization-engine.md Section 16.2

## 1. Purpose

This document presents 6 new items measuring the quality of an athlete's passion for their sport, drawing on the Dualistic Model of Passion (Vallerand, 2015, Ch. 19 in the Oxford Handbook of Self-Determination Theory). The items split into two three-item subscales: Harmonious Passion (HP) and Obsessive Passion (OP). They replace the current heuristic overinvestment rule with a validated construct.

These items are original to ABC. No licensed DMP scale content is reproduced.

## 2. Design constraints

- **Cadence:** Quarterly, not biweekly. Passion quality moves slowly.
- **Placement:** Outside the core 36-item bank. Does not change `REQUIRED_ITEMS`.
- **Stem:** "How often in the past three months did you..."
- **Response scale:** 1 = Never, 4 = Sometimes, 7 = Very Often. Matches the core bank.
- **No reverse-scored items:** With only six items and two independent subscales, reverse coding would compress information. The subscales are independent by construction, not a single bipolar dimension.
- **Independence:** An athlete can score high on both (intense, conflicted), high on one only, or low on both (uninvested). Scoring respects this.

## 3. The 6 items

### 3.1 Harmonious Passion (HP1, HP2, HP3)

**HP1**
"How often in the past three months did your sport fit well alongside the other things that matter in your life?"

- **Construct:** Life-domain integration, absence of conflict.
- **Rationale:** Harmonious passion is defined by integration with the rest of life, not withdrawal from it. HP1 targets the structural criterion: the activity and other valued domains coexist without friction.

**HP2**
"How often in the past three months did you engage with your sport because you genuinely wanted to, not because you felt you had to?"

- **Construct:** Volitional engagement, autonomous internalization.
- **Rationale:** The central marker of harmonious passion is that engagement is chosen, not driven. HP2 directly taps the autonomous-versus-controlled quality of the engagement motive.

**HP3**
"How often in the past three months were you able to step away from sport when you needed to, without feeling like you were losing part of yourself?"

- **Construct:** Flexible disengagement, identity non-contingency.
- **Rationale:** Harmonious passion preserves the athlete's ability to disengage without identity threat. HP3 distinguishes athletes whose identity is expressed through sport from those whose identity is captured by it.

### 3.2 Obsessive Passion (OP1, OP2, OP3)

**OP1**
"How often in the past three months did you find it hard to stop thinking about your sport even when you wanted a break?"

- **Construct:** Cognitive intrusion, inability to disengage mentally.
- **Rationale:** Obsessive passion is marked by persistent activation of the activity even during recovery. OP1 captures the mental side of the inability to step away.

**OP2**
"How often in the past three months did you feel tense or uneasy when you were unable to train?"

- **Construct:** Negative affect during disengagement, affective dependency.
- **Rationale:** Obsessive passion predicts negative affect during forced disengagement (injury, rest, travel). OP2 captures the affective signature of compulsive engagement.

**OP3**
"How often in the past three months did your commitment to sport create friction with other parts of your life?"

- **Construct:** Inter-domain conflict, spillover cost.
- **Rationale:** Obsessive passion is distinguished from harmonious passion by the cost it imposes on other life domains. OP3 captures the behavioral footprint of that cost.

## 4. Scoring model

Two subscale means on the 1-7 scale:

```
hp_mean = mean(HP1, HP2, HP3)
op_mean = mean(OP1, OP2, OP3)
```

Both normalized to 0-10:

```
hp_score = ((hp_mean - 1) / 6) * 10
op_score = ((op_mean - 1) / 6) * 10
```

Balance score (direction and magnitude of leaning):

```
balance = hp_score - op_score    # range: -10 (fully obsessive) to +10 (fully harmonious)
```

Leaning classification:

| Condition | Leaning | Coach action |
|-----------|---------|--------------|
| `balance >= 2.0` AND `hp_score >= 5.0` | `harmonious` | Protect recovery without restricting engagement |
| `balance <= -2.0` AND `op_score >= 5.0` | `obsessive` | Address identity capture and life balance |
| Both `hp_score >= 5.0` AND `op_score >= 5.0` | `mixed` | Intensity is real; check for underlying conflict |
| `hp_score < 5.0` AND `op_score < 5.0` | `uninvested` | Not a passion issue; look elsewhere for drive |
| Otherwise | `insufficient_signal` | Gather more measurements before acting |

## 5. Evidence gates

Consistent with improvement-plan-personalization-engine.md Section 17.5:

| Condition | Gate | Effect |
|-----------|------|--------|
| Fewer than 4 of 6 items answered | Fails display gate | Construct not computed |
| 4 or 5 of 6 items answered | Passes display gate, fails recommendation gate | Shown with hedged language; no coach alert |
| All 6 items answered, `abs(balance) < 1.0` | Passes display gate only | Shown as "pattern still forming" |
| All 6 items answered, `abs(balance) >= 2.0`, clear leaning | Passes recommendation gate | Drives narrative selection and coach routing |

## 6. Empirical calibration open items

The above thresholds are theoretical priors. Phase A pilot data will recalibrate:

- Subscale reliability (McDonald's omega) per subscale at n >= 100.
- Empirical balance-score cutpoints against coach-rated life-balance concerns.
- Convergent validity against validated passion measures in a subset (licensing dependent).
- Test-retest stability across the quarterly cadence.
