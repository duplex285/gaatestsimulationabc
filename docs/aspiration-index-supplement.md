# Aspiration Index Supplement (WI-15)

**Date:** 2026-04-25
**Status:** Draft for SME review.
**Purpose:** Add a 6-item goal-content supplement to ABC for Phase A subsample (n ~ 100 of N >= 500). Operationalizes Kasser & Ryan (1996) and Martela et al. (2019) intrinsic-vs-extrinsic aspiration distinction as an interaction layer with the Ambition subscale.

---

## 1. Why this supplement

The Ambition subscale (A_sat, A_frust) measures need satisfaction in goal pursuit. It does not measure goal CONTENT. Kasser & Ryan (1996) and Martela et al. (2019) established that intrinsic aspirations (mastery, growth, affiliation) correlate with self-actualization and vitality, while extrinsic aspirations (financial, fame, image) correlate with anxiety and ill-being even controlling for intrinsic aspirations and even when extrinsic goals are attained. Two athletes with identical A_sat scores but different aspiration profiles likely have different downstream burnout trajectories.

The hypothesis: athletes high on extrinsic-relative-to-intrinsic aspirations show steeper burnout cascades for the same A_frust score. This is testable as an A_sat x Aspiration Index interaction.

This supplement is OPTIONAL and administered to a subset of Phase A participants (target n ~ 100). The core 36-item ABC instrument is unchanged.

## 2. Items

Six items on a 1 to 7 importance scale (1 = "not at all important to me", 7 = "extremely important to me"). Stem: "How important is each of the following to you in your sport career?"

### 2.1 Intrinsic aspirations (3 items)

| Code | Construct | Item |
|---|---|---|
| ASP1 | Mastery | "Becoming the best version of myself in my sport, regardless of external recognition" |
| ASP2 | Growth | "Developing as a person through the challenges my sport presents" |
| ASP3 | Affiliation / community | "Building deep, lasting relationships with teammates and coaches" |

### 2.2 Extrinsic aspirations (3 items)

| Code | Construct | Item |
|---|---|---|
| ASP4 | Financial | "Earning a significant income from my sport" |
| ASP5 | Recognition / fame | "Being widely recognized or admired for my athletic achievements" |
| ASP6 | Image | "Being seen as physically impressive or attractive because of my athletic ability" |

### 2.3 Ambivalent / boundary item (optional, not scored)

This item could be intrinsic (championship as a marker of mastery) or extrinsic (championship as social recognition). Use only for cognitive pretesting, not scored.

| Code | Item |
|---|---|
| ASP7 | "Winning a major championship in my sport" |

## 3. Scoring

| Score | Formula |
|---|---|
| Intrinsic Aspiration Score | mean(ASP1, ASP2, ASP3), range 1 to 7 |
| Extrinsic Aspiration Score | mean(ASP4, ASP5, ASP6), range 1 to 7 |
| Relative Intrinsic | Intrinsic - Extrinsic, range -6 to +6 |

Per Kasser & Ryan (1996), the *relative* intrinsic score is the most predictive of well-being, more than absolute intrinsic or extrinsic. Athletes who place HIGHER importance on intrinsic than extrinsic aspirations show better outcomes.

**Note on difference scores.** This is a difference score and inherits the Edwards (2001) Myth 1 reliability problem (see WI-9). Future iteration: replace with polynomial regression of outcomes on Intrinsic + Extrinsic + Intrinsic^2 + Intrinsic*Extrinsic + Extrinsic^2 per Edwards 2001. For Phase A, the simple difference is acceptable as a preliminary indicator.

## 4. Hypotheses for Phase A

H1 (replication): Athletes with higher Relative Intrinsic show lower ABQ burnout total scores (target r = -0.20 to -0.40, per Kasser & Ryan 1996 effect sizes in non-athlete populations, discounted for measurement noise).

H2 (incremental validity): Relative Intrinsic predicts ABQ burnout incrementally beyond ABC subscale composites. ΔR² > 0.03 in hierarchical regression after controlling for A_sat, B_sat, C_sat, A_frust, B_frust, C_frust.

H3 (interaction; primary novel hypothesis): Relative Intrinsic moderates the A_sat to burnout relationship. Specifically, athletes with high A_sat AND extrinsic-dominant aspirations show steeper burnout slopes than athletes with high A_sat AND intrinsic-dominant aspirations.

H4 (Ambition specificity): Relative Intrinsic correlates more strongly with A_sat (target r = 0.15 to 0.30) than with B_sat or C_sat (target r < 0.10). This establishes the supplement's discriminant validity within ABC.

## 5. Cognitive pretesting protocol

Administer to 5 to 10 athletes from diverse sports and competitive levels. Probe:
- Do athletes interpret "best version of myself" (ASP1) as mastery or as competitive ranking?
- Does ASP3 read as same construct as ABC's Belonging items?
- Does ASP4 trigger socially desirable underreporting in NCAA athletes (where amateurism rules apply)?
- Does ASP7 (championship) read as intrinsic or extrinsic?

If athletes consistently misinterpret an item, revise. If ASP7 cannot be reliably classified, drop it from the supplement.

## 6. References

- Kasser, T., & Ryan, R. M. (1996). Further examining the American dream: Differential correlates of intrinsic and extrinsic goals. *Personality and Social Psychology Bulletin*, 22(3), 280-287.
- Martela, F., Bradshaw, E. L., & Ryan, R. M. (2019). Expanding the map of intrinsic and extrinsic aspirations using network analysis and multidimensional scaling: Examining four new aspirations. *Frontiers in Psychology*, 10, 2174.
- Edwards, J. R. (2001). Ten difference score myths. *Organizational Research Methods*, 4, 265-287.
- Bradshaw, E. L., Sahdra, B. K., Ciarrochi, J., et al. (2020). A configural approach to aspirations. *Journal of Personality and Social Psychology*, 120(1), 226.
