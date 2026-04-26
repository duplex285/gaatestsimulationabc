# New Items Draft v2: ABC Assessment Item Revisions

**Date:** 2026-04-25
**Supersedes:** `new-items-draft.md` (v1, dated 2026-03-22) for items flagged below.
**Status:** Draft for SME review. Pending: at least one sport psychologist and one SDT researcher rate each revised item on (a) construct fidelity to active thwarting, (b) Kam et al. (2021) classification (regular vs negated regular vs polar opposite), (c) cultural accessibility, (d) sport-specificity.

---

## 1. Why this revision exists

Two findings from the 2026-04-25 literature review (`docs/howard-2024-implementation-plan.md` Literature Review v2) require item-level changes:

**Bartholomew et al. (2011) Psychological Need Thwarting Scale framework.** Frustration items must describe ACTIVE THWARTING by named agents, not internal dissatisfaction. The four existing items AF1, AF2, BF1, CF3 drift toward dissatisfaction language and risk loading with low-satisfaction items in CFA. Bartholomew's Study 3 fit (RCFI = .96, RNNFI = .94, SRMR = .04, RMSEA = .07) and the asymmetric paths in his SEM (frustration uniquely predicts exhaustion; satisfaction uniquely predicts vitality) depend on this construct distinction.

**Kam, Meyer & Sun (2021) logical response perspective.** Items can be classified as regular ("I am tall"), polar opposite ("I am short"), negated regular ("I am not tall"), or negated polar opposite ("I am not short"). Their N = 529 height study showed that mid-trait respondents logically disagree with both regular and polar-opposite items. Polar opposites and their negations form a separate factor from regulars and their negations. Mixing keying within a subscale (the Murphy 2023 fix already in v1) does not eliminate this artifact. Six existing reverse items (AS6, AF6, BS6, BF6, CS6, CF6) are polar opposites and need rewriting as negated regulars.

This revision targets ten items total. Five existing forward items (AF1, AF2, BF1, CF3) and five reverse items (AS6, AF6, BS6, BF6, CS6, CF6) are revised. One new item (BF7) is added per Bartholomew's relatedness-thwarting item R4 (teammate envy).

---

## 2. Item revisions

### 2.1 Forward frustration items (Bartholomew 2011 alignment)

#### AF1 Ambition Frustration

**Current text.** "How often in the past two weeks did you feel like you were held back?"

**Issue.** Passive voice. No agent named. "Held back" reads as low satisfaction (perceived restriction) rather than active thwarting (named external force).

**Revised text.** "How often in the past two weeks did your coach or training plan stop you from pursuing what you wanted to work on?"

**Bartholomew alignment.** Maps to PNTS A1 ("I feel prevented from making choices with regard to the way I train") and A3 ("I feel forced to follow training decisions made for me"). Names the agent (coach or training plan). Names the action (stop you from pursuing). Names the object (what you wanted to work on, capturing the volitional content of autonomy).

**Kam classification.** Regular (no negation; describes the presence of thwarting).

#### AF2 Ambition Frustration

**Current text.** "How often in the past two weeks did you feel like you were going through the motions without knowing why?"

**Issue.** Reads as anhedonia or amotivation. No external agent. The phrase "without knowing why" describes an internal state of meaning loss, not an external thwarting event.

**Revised text.** "How often in the past two weeks did training feel like something done to you rather than something you chose?"

**Bartholomew alignment.** Maps to PNTS A2 ("I feel pushed to behave in certain ways"). The phrase "done to you rather than something you chose" foregrounds the involuntary, externally-imposed nature of the experience. The agent is implicit (the team, the system) but the action (done to you) is concrete.

**Kam classification.** Regular.

#### BF1 Belonging Frustration

**Current text.** "How often in the past two weeks did you feel like you had to perform a version of yourself to fit in?"

**Issue.** Self-monitoring and impression-management language. Captures internal performance of self, not external rejection. Mid-trait athletes may feel general social adjustment without active exclusion.

**Revised text.** "How often in the past two weeks did teammates or coaches signal that you would not be accepted as you are?"

**Bartholomew alignment.** Maps to PNTS R1 ("I feel I am rejected by those around me") and R2 ("I feel others can be dismissive of me"). Names the agents (teammates or coaches). Names the action (signal). Names the object (would not be accepted as you are, capturing conditional regard).

**Kam classification.** Regular.

#### CF3 Craft Frustration

**Current text.** "How often in the past two weeks did you feel like feedback on your skill was more about judgment than improvement?"

**Issue.** Agent ambiguous (whose feedback?). The passive construction obscures the source.

**Revised text.** "How often in the past two weeks did your coaches give feedback that focused on judging you rather than helping you develop?"

**Bartholomew alignment.** Maps to PNTS C2 ("There are times when I am told things that make me feel incompetent"). Names the agent (your coaches). Names the action (give feedback). The contrastive frame (judging vs helping develop) directly invokes the evaluative climate construct.

**Kam classification.** Regular.

### 2.2 Reverse items (Kam et al. 2021 alignment)

The principle: rewrite each reverse item as a "negated regular" (literally negate the corresponding forward item) rather than as a "polar opposite" (describe the opposite construct in positive language). Per Kam, negated regulars load with regulars; polar opposites load with negated polar opposites and form a separate method factor among mid-trait respondents.

#### AS6 Ambition Satisfaction (reverse-keyed)

**Current text.** "How often in the past two weeks did you feel like your competitive goals no longer mattered to you?"

**Issue.** Polar opposite. "No longer mattered" is the opposite construct (mattering vs not-mattering as distinct cognitive states), not a literal negation of "mattered."

**Revised text.** "How often in the past two weeks did you NOT feel that your competitive goals mattered to you?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

#### AF6 Ambition Frustration (reverse-keyed)

**Current text.** "How often in the past two weeks did you feel that your training environment encouraged you to pursue your own competitive ambitions?"

**Issue.** Polar opposite. The current item describes a positive coaching climate (need support), not the absence of frustration. Positively-keyed sat content placed inside a frust subscale is the precise design pattern Kam flags.

**Revised text.** "How often in the past two weeks did you NOT feel that your training environment supported your competitive ambitions?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

#### BS6 Belonging Satisfaction (reverse-keyed)

**Current text.** "How often in the past two weeks did you feel that you could only be close to your teammates when things were going well in your sport?"

**Issue.** Polar opposite. The current item describes a conditional pattern (closeness contingent on performance). It introduces a substantively different construct (conditional regard) into the satisfaction subscale rather than negating the satisfaction content.

**Revised text.** "How often in the past two weeks did you NOT feel close to your teammates?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

**Note.** The conditional-regard construct (originally in BS6 v1) is theoretically important but should be measured separately as a Belonging *frustration* item, not buried inside a satisfaction reverse. Consider adding it to BF subscale as BF8 in a future revision.

#### BF6 Belonging Frustration (reverse-keyed)

**Current text.** "How often in the past two weeks did you feel that your teammates accepted you even when you made mistakes or underperformed?"

**Issue.** Polar opposite. Describes positive social acceptance (need support content) inside a frust subscale.

**Revised text.** "How often in the past two weeks did you NOT feel that your teammates accepted you?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

#### CS6 Craft Satisfaction (reverse-keyed)

**Current text.** "How often in the past two weeks did you feel stuck at your current skill level, unable to progress?"

**Issue.** Polar opposite. "Stuck at current skill level" is a different construct (stagnation) than the negation of competence growth.

**Revised text.** "How often in the past two weeks did you NOT feel that you were getting better at your skills?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

**Note.** The stagnation construct (originally in CS6 v1) is theoretically important and could be retained as a separate experimental item (CS7) for empirical comparison with the negated regular.

#### CF6 Craft Frustration (reverse-keyed)

**Current text.** "How often in the past two weeks did your coaches create opportunities for you to practise and improve at your own pace?"

**Issue.** Polar opposite. Describes positive coaching support (need support content) inside a frust subscale.

**Revised text.** "How often in the past two weeks did your coaches NOT give you opportunities to practise at your own pace?"

**Kam classification.** Negated regular.

**Reverse-scoring formula.** recoded score = 8 - raw score (unchanged).

### 2.3 New item

#### BF7 Belonging Frustration (new, forward-scored)

**Text.** "How often in the past two weeks did teammates seem resentful or dismissive when you performed well?"

**Justification.** Maps to PNTS R4 ("I feel some of the athletes around me are envious when I achieve success"). Sport-specific belonging-thwarting experience absent from the current ABC item set. The current B-Frust subscale captures exclusion, conditional acceptance, and rejection but does not capture the inverted-success experience: performance well that triggers social withdrawal rather than support.

**Construct.** Active relational thwarting via peer envy or success-conditional withdrawal. This is theoretically distinct from BF5 (deliberate exclusion) because BF5 captures exclusion at baseline; BF7 captures exclusion triggered specifically by success.

**Kam classification.** Regular.

**Subscale impact.** Adding BF7 makes the B-Frust subscale 7 items (4 forward including BF7, 2 reverse, plus the existing 4 forward). Two ways to handle:
- (a) Promote BF7 to position 5 in B-Frust and demote the existing BF5 to position 7. Recompute IRT parameters.
- (b) Keep BF7 as an experimental item collected alongside the core 36; drop or retain after Phase A loadings analysis.

Recommend (b) for Phase A; promote to (a) in v3 if loading >= 0.60.

---

## 3. Updated subscale layout

After this revision, the 36-item core remains 36 items (no net add unless BF7 is promoted). The reverse-coded items per subscale are unchanged (positions 4 and 6). Item content is changed for ten items.

| Subscale | Item 1 | Item 2 | Item 3 | Item 4 (R) | Item 5 | Item 6 (R) |
|---|---|---|---|---|---|---|
| A-Sat | (unchanged) | (unchanged) | (unchanged) | (unchanged) | AS5 | **AS6 revised** |
| A-Frust | **AF1 revised** | **AF2 revised** | (unchanged) | (unchanged) | AF5 | **AF6 revised** |
| B-Sat | (unchanged) | (unchanged) | (unchanged) | (unchanged) | BS5 | **BS6 revised** |
| B-Frust | **BF1 revised** | (unchanged) | (unchanged) | (unchanged) | BF5 | **BF6 revised** |
| C-Sat | (unchanged) | (unchanged) | (unchanged) | (unchanged) | CS5 | **CS6 revised** |
| C-Frust | (unchanged) | (unchanged) | **CF3 revised** | (unchanged) | CF5 | **CF6 revised** |

Plus one experimental item: BF7 (teammate envy, forward, peer-source belonging thwarting).

---

## 4. Reverse-scoring summary (unchanged from v1)

| Subscale | Reverse-coded items | Total items | Forward items |
|---|---|---|---|
| A-Sat | AS4, AS6 | 6 | AS1, AS2, AS3, AS5 |
| A-Frust | AF4, AF6 | 6 | AF1, AF2, AF3, AF5 |
| B-Sat | BS4, BS6 | 6 | BS1, BS2, BS3, BS5 |
| B-Frust | BF4, BF6 | 6 | BF1, BF2, BF3, BF5 (+BF7 experimental) |
| C-Sat | CS4, CS6 | 6 | CS1, CS2, CS3, CS5 |
| C-Frust | CF4, CF6 | 6 | CF1, CF2, CF3, CF5 |

Reverse-scoring formula: recoded = 8 - raw.

---

## 5. Tradeoffs surfaced

**Reduced content variety.** All six negated-regular reverse items now read "did NOT feel...". This is repetitive across the instrument. Kam's framework predicts the trade improves measurement; Murphy's earlier critique was partly about wording monotony. The hybrid mitigation is to alternate negated-regular and polar-opposite reverse items across subscales (not within), then test in Phase A which type loads more cleanly. This v2 takes the conservative path of negating all six.

**Construct content lost.** The polar-opposite reverse items in v1 were carrying additional content (conditional regard in BS6, stagnation in CS6, supportive climate in AF6 and CF6). Some of this content is theoretically important. Where lost, this v2 recommends adding the construct as a separate forward item in the matched subscale (e.g., BS6's conditional regard becomes a candidate B-Frust item; CS6's stagnation becomes a candidate experimental C-Sat item).

**SME review timeline.** All ten revised items require expert review before Phase A administration. Estimated cycle: 4 to 6 weeks with two SDT researchers and two sport psychologists. The threshold for acceptance: at least 3 of 4 reviewers rate each revised item >= 4 on a 1 to 5 scale for (a) construct fidelity and (b) Kam classification correctness.

---

## 6. Test specification for the v2 instrument

After Phase A administration (target N >= 100 feasibility, N >= 500 for full bifactor analyses):

**Item-level checks (Kam diagnostic).**
1. Forward-only and reverse-only subscale correlations: r >= 0.60 (after sign reversal). Below 0.60 suggests logical-response artifact or genuine bidimensionality.
2. Factor mixture model across trait-level subgroups: tests whether factor structure differs at low vs mid vs high trait. If yes, confirm artifact.
3. Method-factor B-CFA: orthogonal method factor for the 12 reverse items. Compare to without-method-factor model. Method factor loadings > 0.20 suggest residual artifact.

**Construct-level checks (Bartholomew diagnostic).**
1. Within-domain sat-frust correlations: target r = -0.20 to -0.40. More negative than -0.55 suggests bipolar collapse (run WI-8 1-G B-ESEM). Less negative than -0.10 suggests sat and frust measure unrelated constructs.
2. Asymmetric paths in SEM: frust composite uniquely predicts ABQ burnout with beta = .30 to .50; sat composite uniquely predicts vitality with beta = .30 to .50; cross-paths smaller.
3. Frustration items load on need-specific frust factors with lambda >= 0.50 in ESEM; loadings on the matched sat factor < 0.30.

**Bipolar-vs-unipolar test (WI-8 global).** 1-G versus 2-G B-ESEM per Toth-Kiraly et al. 2018. Decision rule: if 1-G fits at least as well as 2-G (Delta-BIC < 10 favoring 2-G is not enough; need Delta-BIC > 10 favoring 1-G) and G-factor loadings show the bipolar pattern, adopt 1-G.

---

## 7. References

- Bartholomew, K. J., Ntoumanis, N., Ryan, R. M., & Thogersen-Ntoumani, C. (2011). Psychological need thwarting in the sport context. *Journal of Sport and Exercise Psychology*, 33(1), 75-102.
- Kam, C. C. S., Meyer, J. P., & Sun, S. (2021). Why do people agree with both regular and reversed items? A logical response perspective. *Assessment*, 28(4), 1110-1124.
- Murphy, J., Swann, C., Peoples, G. E., & Gucciardi, D. F. (2023). The BPNSFS probably does not validly measure need frustration. *Motivation and Emotion*, 47, 899-919.
- Toth-Kiraly, I., Morin, A. J. S., Bothe, B., Orosz, G., & Rigo, A. (2018). Investigating the multidimensionality of need fulfillment: A bifactor exploratory structural equation modeling representation. *Structural Equation Modeling*, 25(2), 267-286.
