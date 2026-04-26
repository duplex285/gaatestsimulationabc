# SME Review Packet: ABC Assessment Narrative Templates

**Date prepared:** 2026-04-20 (updated 2026-04-20 with circumplex, group-conscious, and gap-direction templates)
**Prepared for:** Paid consultant or advisor with subject-matter expertise in sport psychology, mental performance consulting, or adjacent clinical practice
**Prepared by:** Ero product team
**Review scope:** Narrative templates for seven ABC Assessment layers: passion-quality, overinvestment trigger, regulatory-style, regulation-erosion alert, coach-facing circumplex instrument (facet levels, dominant-approach summaries, and self-vs-athlete gap narratives), group-conscious team measurement (perceived collective satisfaction, team identification, empathic-risk alert, team-dispersion warnings), causality-orientations stratifier (autonomy, controlled, impersonal, mixed, emergent), and self-concordance (per-goal leanings plus the five-label trajectory engine across cycles).

---

## Contents

1. [Who this review is for](#1-who-this-review-is-for)
2. [What you are being asked to review](#2-what-you-are-being-asked-to-review)
3. [What you are not being asked to review](#3-what-you-are-not-being-asked-to-review)
4. [How the ABC Assessment works in one page](#4-how-the-abc-assessment-works-in-one-page)
5. [The new layers](#5-the-new-layers)
6. [Review rubric](#6-review-rubric)
7. [Templates to review: Passion quality](#7-templates-to-review-passion-quality)
8. [Templates to review: Overinvestment trigger](#8-templates-to-review-overinvestment-trigger)
9. [Templates to review: Regulatory style](#9-templates-to-review-regulatory-style)
10. [Templates to review: Regulation erosion](#10-templates-to-review-regulation-erosion)
11. [Open decision: ranking of amotivated vs introjected](#11-open-decision-ranking-of-amotivated-vs-introjected)
12. [Templates to review: Coach circumplex facet levels](#12-templates-to-review-coach-circumplex-facet-levels)
13. [Templates to review: Coach circumplex dominant approaches](#13-templates-to-review-coach-circumplex-dominant-approaches)
14. [Templates to review: Coach circumplex gap direction](#14-templates-to-review-coach-circumplex-gap-direction)
15. [Templates to review: Perceived collective satisfaction](#15-templates-to-review-perceived-collective-satisfaction)
16. [Templates to review: Team identification](#16-templates-to-review-team-identification)
17. [Templates to review: Empathic risk](#17-templates-to-review-empathic-risk)
18. [Templates to review: Team dispersion](#18-templates-to-review-team-dispersion)
19. [Templates to review: Causality orientations](#19-templates-to-review-causality-orientations)
20. [Templates to review: Self-concordance leanings](#20-templates-to-review-self-concordance-leanings)
21. [Templates to review: Self-concordance trajectory](#21-templates-to-review-self-concordance-trajectory)
22. [Deliverables we need from you](#22-deliverables-we-need-from-you)
23. [Logistics](#23-logistics)

---

## 1. Who this review is for

Ero builds a mental performance platform for athletes and coaches. The ABC Assessment is a proprietary psychometric instrument that measures athlete need satisfaction and frustration across three domains (Ambition, Belonging, Craft). The instrument draws on Self-Determination Theory and the Dualistic Model of Passion. It is not a licensed implementation of any existing scale; the items, scoring, and narrative layers are original to Ero.

We are shipping two new layers on top of the core instrument:

- **Passion quality** (quarterly): distinguishes harmonious from obsessive passion, replacing a prior rule-based "overinvestment" warning.
- **Regulatory style** (biweekly): per-domain classification of the quality of an athlete's motivation, plus a leading-indicator signal ("regulation erosion") for burnout risk.

Both layers produce athlete-facing and coach-facing narrative text. That text is what we are asking you to review.

## 2. What you are being asked to review

For each template, assess:

1. **Clinical appropriateness.** Is the language safe for an athlete to read without a clinician present? Does it avoid framings that could harm a vulnerable reader? Does the coach-facing text avoid prescriptive clinical language that a coach is not qualified to act on?
2. **Construct fidelity.** The internal construct label (e.g., "harmonious passion," "introjected regulation") is never shown to the user. But does the plain-language rendering accurately reflect what the construct means? Would a reader come away with a correct mental model?
3. **Tone.** Is it strengths-based and non-pathologizing, consistent with SDT's organismic stance? Does it avoid deficit framings that would alienate athletes?
4. **Cultural and demographic inclusivity.** Will the language land across gender, race, and competitive level? Any phrasing that implicitly assumes a dominant-culture athlete?
5. **Power dynamics.** The coach-facing text is read by someone with authority over the athlete. Does it channel that authority toward curiosity and care, not surveillance or control?
6. **The rank-ordering decision in Section 11.** A one-page memo asking for your adjudication on whether "amotivated" should sit below or above "introjected" in our autonomy ranking.

## 3. What you are not being asked to review

- **Item content.** The six passion items and six regulatory items are in a separate document (`docs/passion-items-draft.md`, `docs/regulatory-style-items-draft.md`) and go through a separate item-review cycle.
- **Scoring math or psychometric properties.** Factor structure, reliability, validity, and item-response theory are handled by the psychometric team.
- **Product architecture.** How scores flow through the pipeline is not relevant to this review.
- **Copy-editing at the grammar level.** We run automated readability checks (Flesch-Kincaid Grade 8 for athlete text, Grade 10 for coach text). Please focus on clinical and substantive issues, not typos or minor word choice.

## 4. How the ABC Assessment works in one page

- **Core instrument:** 36 Likert items (1-7) producing six subscales: satisfaction and frustration on each of Ambition (goal pursuit), Belonging (relationships), and Craft (skill development). Biweekly cadence during the season.
- **Core outputs:** Each domain is classified as Thriving, Vulnerable, Mild, or Distressed. The athlete also receives one of eight named archetypes (Integrator, Captain, Architect, Mentor, Pioneer, Anchor, Artisan, Seeker).
- **Passion layer (quarterly):** Six items distinguishing harmonious from obsessive passion, producing a leaning (harmonious, obsessive, mixed, uninvested, insufficient_signal, or not_computed).
- **Regulatory layer (biweekly):** Six items (two per domain) producing a per-domain autonomous-versus-controlled score and a four-way style classification (identified, conflicted, introjected, amotivated, or not_computed).
- **Derived signals:**
  - **Overinvestment trigger.** Fires when two or more domains are Thriving and optional daily recovery signals confirm strain. Passion leaning selects the narrative path (harmonious, obsessive, mixed, or insufficient evidence).
  - **Regulation erosion.** Fires when an athlete's regulatory style on one or more domains has moved downward on the autonomy ranking and is sustained. Acts as a leading indicator before satisfaction or frustration scores degrade.

Every user-facing surface is plain-language. Technical vocabulary ("bifactor," "introjected regulation," "Relative Autonomy Index," "omega") never appears in the narrative. All jargon is translated before rendering.

## 5. The new layers

**Passion quality** draws on Vallerand's Dualistic Model of Passion (2015, 2023). An athlete's engagement with sport can be harmonious (integrated with the rest of life, flexible) or obsessive (compulsive, identity-contingent, conflict-producing). Both types predict engagement. Harmonious passion predicts resilience; obsessive passion predicts burnout under adversity.

**Regulatory style** draws on Organismic Integration Theory (Deci & Ryan, 2000; Pelletier & Rocchi, 2023). Motivation quality runs along a continuum from external regulation through introjection to identification and integration. Autonomous regulation (identified, integrated) predicts well-being and persistence. Controlled regulation (introjected, external) predicts burnout and dropout.

**Regulation erosion** is a cross-measurement signal: when an athlete's regulatory quality moves from more autonomous to less autonomous and stays low, we alert before satisfaction or frustration scores degrade. Grounded in Lonsdale and Hodge (2011), who established that self-determination decline precedes burnout.

**Coach circumplex** is a separate instrument administered to the coach (self-rating) and to each athlete (rating of the coach). Twenty-four items across five facets: autonomy-support, structure, relatedness-support, controlling, chaos. Draws on the circumplex of coaching approaches (Aelterman et al., 2019, via Chapter 11) and the autonomy-supportive behaviors catalog in Chapter 25. Produces per-facet scores, a dominant-approach summary, and a self-versus-athlete gap analysis per facet.

**Group-conscious team measurement** draws on Chapter 53 (Thomaes et al., Group-Conscious BPNT). Five items measure the athlete's perception of collective need satisfaction across the three ABC domains plus their identification with the team. An empathic-risk flag fires when high team identification meets low perceived collective satisfaction. A separate team-level dispersion metric computes standard deviations across a roster's subscale scores, flagging teams where the mean hides a split experience.

## 6. Review rubric

For each template, please rate on the five-point scale below and leave a comment where any rating is 3 or lower.

| Dimension | 5 = Ship as-is | 4 = Minor edits | 3 = Needs rework | 2 = Major concerns | 1 = Do not ship |
|---|---|---|---|---|---|
| Clinical appropriateness | Safe as-is | One or two word swaps | Sentence-level revision | Concept-level revision | Pull from product |
| Construct fidelity | Accurate | Close enough | Partial mismatch | Misrepresents construct | Fundamentally wrong |
| Tone (strengths-based) | Strong | Acceptable | Neutral at best | Deficit-framed | Harmful |
| Cultural inclusivity | Inclusive | Inclusive with minor caveats | Some audiences excluded | Many audiences excluded | Discriminatory |
| Power dynamics (coach text) | Curiosity-first | Mostly curiosity | Mixed | Surveillance-framed | Enables coercion |

Also flag anything that falls outside these dimensions that you think we need to address before shipping.

## 7. Templates to review: Passion quality

Six leanings. Each has an athlete-facing summary plus a reflection prompt, and a coach-facing summary plus a conversation starter.

### 7.1 harmonious

**Trigger:** Athlete scores high on harmonious-passion items (integration with life, autonomous engagement, ability to step away) and low on obsessive-passion items. Indicates flexible, values-based commitment.

**Athlete summary.** Your drive stays in balance with the rest of your life. You can step back when you need to, and come back when you want to. That is a strong foundation.

**Athlete reflection prompt.** When was the last time you took a full day off without feeling like you were losing something?

**Coach summary.** The athlete can step away from sport without losing their sense of self. Drive is high and healthy. Protect recovery; do not restrict engagement.

**Coach conversation starter.** Ask what the athlete wants the training week to give them. A clear answer is a sign of flexible commitment.

### 7.2 obsessive

**Trigger:** Athlete scores high on obsessive-passion items (cognitive intrusion, distress when unable to engage, inter-domain conflict) and low on harmonious items.

**Athlete summary.** You find it hard to step away from sport, even when you need a break. The drive is real. It is also carrying a cost. That is worth a conversation.

**Athlete reflection prompt.** What does a day without training feel like for you right now? What do you notice in yourself?

**Coach summary.** The athlete has trouble stepping away from sport. Drive is high but it carries cost to other parts of life. An identity-level conversation is warranted, not a training adjustment.

**Coach conversation starter.** Ask what a week off would cost the athlete. Listen for whether the answer is about performance or about self.

### 7.3 mixed

**Trigger:** Both harmonious and obsessive passion are elevated. The athlete has intense commitment that is partly sustainable and partly costly.

**Athlete summary.** You bring intense commitment. Some of it lifts you. Some of it weighs on you. Both are real.

**Athlete reflection prompt.** Which parts of your training week give you energy, and which parts take it?

**Coach summary.** Both the healthy and the costly forms of commitment are elevated. Intensity is real. Check for underlying conflict before acting on the signal.

**Coach conversation starter.** Ask what the training week gives the athlete, and what it takes from them. Both answers matter.

### 7.4 uninvested

**Trigger:** Both harmonious and obsessive passion are low. Sport is not a strong motivational engine for this athlete right now.

**Athlete summary.** Sport is not a strong source of energy right now. That is not a problem to solve. It is a signal about where your drive sits today.

**Athlete reflection prompt.** What does pull on you right now, if not sport?

**Coach summary.** Sport is not carrying strong positive or negative charge for this athlete. Investigate other drivers before reading this as burnout.

**Coach conversation starter.** Ask what the athlete is looking forward to outside of sport. A flat answer here points to something broader.

### 7.5 insufficient_signal

**Trigger:** Responses are present but do not produce a confident leaning (balance between harmonious and obsessive is too close to zero to commit to one).

**Athlete summary.** Too early to say which way this is leaning. A few more check-ins will sharpen the picture.

**Athlete reflection prompt.** No action needed yet. Keep checking in.

**Coach summary.** Signal too weak to act on. Hold for another cycle.

**Coach conversation starter.** No action needed. Revisit after the next check-in.

### 7.6 not_computed

**Trigger:** Too few passion items answered to score (fewer than four of six).

**Athlete summary.** Not enough check-in answers yet to say how this is sitting for you.

**Athlete reflection prompt.** Complete the full check-in next time for a clearer read.

**Coach summary.** Not enough answers yet. Hold for another cycle.

**Coach conversation starter.** No action needed. Make sure the athlete completes the full check-in next cycle.

---

## 8. Templates to review: Overinvestment trigger

The overinvestment trigger fires when two or more ABC domains are in the Thriving state and either daily recovery signals confirm strain or no daily signals are available. The passion leaning then selects which narrative path runs.

### 8.1 harmonious path

**Trigger:** Thriving pattern present; passion leaning is harmonious. Healthy drive under load.

**Athlete text.** Your drive in training is strong right now. A rest day this week is part of the plan, not a setback.

**Coach text.** This athlete is pushing hard from a healthy place. Protect recovery without restricting engagement. A light week is maintenance, not demotion.

### 8.2 obsessive path

**Trigger:** Thriving pattern present; passion leaning is obsessive. High-risk pattern.

**Athlete text.** Your drive is high, and you are finding it hard to step back. That tension is worth a conversation, not a harder week.

**Coach text.** This athlete is pushing hard from a place of tension. A one-to-one that is not about performance is the action. Check whether they feel they can step back without losing standing on the team.

### 8.3 mixed path

**Trigger:** Thriving pattern present; passion is mixed (both harmonious and obsessive elevated).

**Athlete text.** You are pushing hard. Some of that is lifting you, some of it is costing you. Worth pausing to notice which is which.

**Coach text.** The athlete shows both healthy and costly commitment at once. Ask what the training week gives them, and what it takes from them.

### 8.4 insufficient_evidence path

**Trigger:** Thriving pattern present; passion leaning is unclear or not computable.

**Athlete text.** We do not have enough to say yet. Keep checking in.

**Coach text.** Thriving pattern is present but passion leaning is not clear yet. Watch for another cycle before acting.

### 8.5 not_triggered path

**Trigger:** No thriving pattern or daily signals indicate healthy recovery. Trigger does not fire.

**Athlete text.** Nothing flagged on the overinvestment side right now.

**Coach text.** No overinvestment trigger for this athlete in this cycle.

---

## 9. Templates to review: Regulatory style

Four styles plus a "not_computed" state. Each style renders per domain (Ambition, Belonging, Craft) because the wording substitutes the specific area of life being scored.

**Domain phrases used in rendering:**
- Ambition → athlete-facing: "your goals"; coach-facing: "goal pursuit"
- Belonging → athlete-facing: "your teammates"; coach-facing: "team relationships"
- Craft → athlete-facing: "your skills"; coach-facing: "skill development"

### 9.1 identified

**Trigger:** The athlete's autonomous-regulation items for a domain score high; controlled-regulation items score low. Drive in this domain is values-based.

**Athlete text (ambition).** You chase your goals because they genuinely matter to you. That is the strongest kind of drive. It holds up when things get hard.

**Athlete text (belonging).** You invest in your teammates because they genuinely matter to you. That is the strongest kind of drive. It holds up when things get hard.

**Athlete text (craft).** You work on your skills because they genuinely matter to you. That is the strongest kind of drive. It holds up when things get hard.

**Coach text (ambition).** In goal pursuit, the athlete's drive is values-based. It tends to hold up when things get hard. Keep offering reasons and choices. Avoid pressure tactics; they weaken ownership.

**Coach text (belonging).** In team relationships, the athlete's drive is values-based. It tends to hold up when things get hard. Keep offering reasons and choices. Avoid pressure tactics; they weaken ownership.

**Coach text (craft).** In skill development, the athlete's drive is values-based. It tends to hold up when things get hard. Keep offering reasons and choices. Avoid pressure tactics; they weaken ownership.

### 9.2 conflicted

**Trigger:** Both autonomous-regulation and controlled-regulation items score high. The athlete values this area and also feels pressure around it.

**Athlete text (ambition).** You chase your goals for real reasons, and also because you feel you have to. Both are true at the same time. That mix is workable, but the pressure side is worth naming.

**Athlete text (belonging).** You invest in your teammates for real reasons, and also because you feel you have to. Both are true at the same time. That mix is workable, but the pressure side is worth naming.

**Athlete text (craft).** You work on your skills for real reasons, and also because you feel you have to. Both are true at the same time. That mix is workable, but the pressure side is worth naming.

**Coach text (ambition).** The athlete values goal pursuit and also feels pressure here. The source of the pressure is worth naming in a one-to-one. When things get hard, the pressure side tends to break the engagement.

**Coach text (belonging).** The athlete values team relationships and also feels pressure here. The source of the pressure is worth naming in a one-to-one. When things get hard, the pressure side tends to break the engagement.

**Coach text (craft).** The athlete values skill development and also feels pressure here. The source of the pressure is worth naming in a one-to-one. When things get hard, the pressure side tends to break the engagement.

### 9.3 introjected

**Trigger:** Autonomous-regulation items score low; controlled-regulation items score high. Drive is obligation-based or image-based.

**Athlete text (ambition).** You chase your goals more out of pressure than out of want. That can still produce effort, but it tends to wear down. Worth a look at where the pressure is coming from.

**Athlete text (belonging).** You invest in your teammates more out of pressure than out of want. That can still produce effort, but it tends to wear down. Worth a look at where the pressure is coming from.

**Athlete text (craft).** You work on your skills more out of pressure than out of want. That can still produce effort, but it tends to wear down. Worth a look at where the pressure is coming from.

**Coach text (ambition).** In goal pursuit, the athlete's drive runs on obligation or image, not on real value. That is a thin foundation. A conversation about what the athlete actually wants from this part of their life is the action.

**Coach text (belonging).** In team relationships, the athlete's drive runs on obligation or image, not on real value. That is a thin foundation. A conversation about what the athlete actually wants from this part of their life is the action.

**Coach text (craft).** In skill development, the athlete's drive runs on obligation or image, not on real value. That is a thin foundation. A conversation about what the athlete actually wants from this part of their life is the action.

### 9.4 amotivated

**Trigger:** Both autonomous-regulation and controlled-regulation items score low. Neither values nor pressure is pulling the athlete in this domain.

**Athlete text (ambition).** You are not feeling much pull toward your goals right now, either from inside or from outside. That is worth noticing. It does not have to be a problem, but it is a signal.

**Athlete text (belonging).** You are not feeling much pull toward your teammates right now, either from inside or from outside. That is worth noticing. It does not have to be a problem, but it is a signal.

**Athlete text (craft).** You are not feeling much pull toward your skills right now, either from inside or from outside. That is worth noticing. It does not have to be a problem, but it is a signal.

**Coach text (ambition).** The athlete is disengaged in goal pursuit: neither values nor pressure is active. Investigate what changed. This is often an earlier warning than low satisfaction on its own.

**Coach text (belonging).** The athlete is disengaged in team relationships: neither values nor pressure is active. Investigate what changed. This is often an earlier warning than low satisfaction on its own.

**Coach text (craft).** The athlete is disengaged in skill development: neither values nor pressure is active. Investigate what changed. This is often an earlier warning than low satisfaction on its own.

### 9.5 not_computed

**Trigger:** One or both of the two regulatory items for a domain were not answered.

**Athlete text (ambition).** Not enough check-in answers yet for your goals. Complete both items next time for a clearer read.

**Athlete text (belonging).** Not enough check-in answers yet for your teammates. Complete both items next time for a clearer read.

**Athlete text (craft).** Not enough check-in answers yet for your skills. Complete both items next time for a clearer read.

**Coach text (ambition).** Not enough answers to read goal pursuit motivation this cycle. Ensure the athlete completes both items next time.

**Coach text (belonging).** Not enough answers to read team relationships motivation this cycle. Ensure the athlete completes both items next time.

**Coach text (craft).** Not enough answers to read skill development motivation this cycle. Ensure the athlete completes both items next time.

---

## 10. Templates to review: Regulation erosion

The erosion alert fires when an athlete's regulatory style in one or more domains has moved down the autonomy ranking across consecutive measurements and is sustained (not recovered). It is intended as a leading indicator, often firing before satisfaction and frustration scores degrade.

### 10.1 ambition

**Athlete text.** Something about your goals has shifted over the last few check-ins. The pull that was value-based is moving toward pressure-based. Worth a quiet look at what has changed around this part of your life.

**Coach text.** Motivation in goal pursuit is moving from values-based to pressure-based. This has shown up over the last two or three check-ins. The usual scores may still look healthy; this signal often moves first. A conversation that is not about performance is the action.

### 10.2 belonging

**Athlete text.** Something about your teammates has shifted over the last few check-ins. The pull that was value-based is moving toward pressure-based. Worth a quiet look at what has changed around this part of your life.

**Coach text.** Motivation in team relationships is moving from values-based to pressure-based. This has shown up over the last two or three check-ins. The usual scores may still look healthy; this signal often moves first. A conversation that is not about performance is the action.

### 10.3 craft

**Athlete text.** Something about your skills has shifted over the last few check-ins. The pull that was value-based is moving toward pressure-based. Worth a quiet look at what has changed around this part of your life.

**Coach text.** Motivation in skill development is moving from values-based to pressure-based. This has shown up over the last two or three check-ins. The usual scores may still look healthy; this signal often moves first. A conversation that is not about performance is the action.

---

## 11. Open decision: ranking of amotivated vs introjected

We ask you to adjudicate one design question: should `amotivated` sit below `introjected` in our autonomy ranking, or above it?

### 11.1 Why this matters

Our regulation-erosion detector uses an ordinal ranking of styles. When an athlete's style moves from a higher rank to a lower rank and stays there, the detector fires. The ordering determines which style transitions count as erosion.

**Current ordering (autonomy interpretation):**

| Rank | Style |
|------|-------|
| 3 | identified |
| 2 | conflicted |
| 1 | introjected |
| 0 | amotivated |

Under this ordering, moving from introjected to amotivated counts as further erosion.

**Alternative ordering (pathology interpretation):**

| Rank | Style |
|------|-------|
| 3 | identified |
| 2 | conflicted |
| 1 | amotivated |
| 0 | introjected |

Under this ordering, moving from amotivated back into introjected counts as erosion because the athlete has re-engaged under pressure.

### 11.2 Case for the autonomy interpretation (current)

Organismic Integration Theory locates amotivation at the non-autonomous extreme of the regulation continuum (Deci & Ryan, 2000, Fig. 2). It represents absence of regulation, whereas introjection represents controlled regulation. On a strict autonomy axis, amotivation is lower. An athlete moving from introjected to amotivated has given up rather than found self-determination.

### 11.3 Case for the pathology interpretation

Clinical outcomes often look better for amotivated athletes than for introjected athletes of comparable intensity. An athlete pushing hard under introjected regulation may be closer to burnout than an athlete who has disengaged but is recovering. Some SDT-fatigue literature (Toth-Kiraly et al., 2020; De Francisco et al., 2025) treats controlled motivation under high demands as the primary pathogen. Under this reading, introjected regulation is the bottom of the ranking and amotivation is closer to neutral.

### 11.4 What we need from you

A one-line decision plus a one-paragraph rationale. We will adopt your decision as the Phase A starting point and revisit once we have empirical data.

**Decision (circle one):**

- Keep the current autonomy interpretation (amotivated = 0, introjected = 1)
- Adopt the pathology interpretation (introjected = 0, amotivated = 1)
- Use both and fire erosion on the stricter of the two (please specify rule)

**Rationale (please keep under 150 words):**

---

## 12. Templates to review: Coach circumplex facet levels

Twenty templates total: five facets (autonomy-support, structure, relatedness-support, controlling, chaos) at four levels each (high, moderate, low, not_computed). All coach-facing; athletes do not see coach profiles directly.

### 12.1 Autonomy-support

**High.** Your athletes see you offering real choice, hearing them out, and explaining why. Keep watching for the moments when you move fast under pressure. That is where this slips.

**Moderate.** You give athletes some room to choose and some of the reasoning behind your calls, but not consistently. Pick one situation this week where you will name the reason out loud before you make the call.

**Low.** Your athletes are not experiencing much room for choice or input. The drills and decisions may still be right; the way they land is the issue. Start by asking one athlete for their read before a decision this week.

**Not_computed.** Not enough responses to read autonomy-support. Come back once the circumplex has more data.

### 12.2 Structure

**High.** Your athletes know what to expect from you. Expectations are clear, feedback is specific, and you follow through. The next edge is noticing when you push through a plan that is not working instead of adjusting it.

**Moderate.** Your structure is present but not consistent. One lever that usually moves this: make the goal of each session explicit in the first two minutes, every session, for a month.

**Low.** Your athletes are not getting clear expectations or specific feedback from you. Two habits usually fix this. State the goal of the session at the start. Name one specific thing in feedback, not a general judgment.

**Not_computed.** Not enough responses to read structure. Come back once the circumplex has more data.

### 12.3 Relatedness-support

**High.** Your athletes feel you care about them as people, not just as performers. That matters more than most coaches think. Protect it by guarding against days when you cut short the non-sport conversations.

**Moderate.** You show warmth sometimes and other times you stay on sport-only mode. Pick two athletes this week and ask each one something specific about their life outside sport.

**Low.** Your athletes are not experiencing you as someone who notices them beyond their performance. The fix is small and concrete: one non-sport question per athlete, one time per week, consistently.

**Not_computed.** Not enough responses to read relatedness-support. Come back once the circumplex has more data.

### 12.4 Controlling

**High.** Your athletes report pressure tactics from you: guilt, warmth withdrawal after a bad performance, or unfavorable comparisons. These tactics often work short-term and cost trust long-term. Pick one to catch yourself on this week.

**Moderate.** Controlling moments are showing up in your coaching. Not your whole style, more like episodes. Notice the trigger. Is it one athlete, one moment in the week, or one kind of pressure you are under?

**Low.** You are not showing much controlling behavior. Keep it that way when the season gets harder; this is the place pressure tactics tend to show up first.

**Not_computed.** Not enough responses to read controlling behavior. Come back once the circumplex has more data.

### 12.5 Chaos

**High.** Your athletes report inconsistency: changing plans without warning, dropped commitments, or reactions that shift day to day. This wears trust down quickly. Write down the next three commitments you make to an athlete and check you kept them.

**Moderate.** Chaos is showing up in patches. Often the source is one context: late-week practices, post-travel, high-stress weeks. Identify the pattern before trying to solve it.

**Low.** Your athletes experience you as consistent. That is a real strength that many coaches underestimate. Keep it.

**Not_computed.** Not enough responses to read consistency. Come back once the circumplex has more data.

---

## 13. Templates to review: Coach circumplex dominant approaches

Five summary templates that render based on where the coach's composite scores land in the need-supportive versus need-thwarting space. All coach-facing.

**Supportive.** Your profile sits in the need-supportive space. Athletes experience you as offering choice, structure, and warmth, with little pressure or chaos. The question for growth is not what to change, but which facet to deepen.

**Mixed.** Your profile is mixed: strong on support, and also showing meaningful pressure or chaos. Many coaches sit here. The work is to keep the support while naming the source of the controlling or inconsistent moments, one at a time.

**Under-structured.** Your profile shows neither strong support nor strong pressure. Athletes experience you as present but neutral. The fastest move is to add one facet of support: rationales, specific feedback, or a non-sport question per athlete each week.

**Thwarting.** Your profile currently sits in the need-thwarting space. Athletes experience more pressure or chaos than support. This is worth taking seriously as a coaching-development priority, not as a judgment. The fix is usually one behavior at a time, starting with whichever facet is highest.

**Not_computed.** Not enough of the circumplex is filled in to give a profile summary yet. Once more responses are in, this will surface.

---

## 14. Templates to review: Coach circumplex gap direction

Ten templates, fired only when the gap between the coach's self-rating and the athletes' aggregate rating on a facet exceeds the flagged threshold (two points on the 0-10 scale). Five facets x two directions. The "aligned" case has no narrative because the no-gap case does not require coaching feedback.

Definitions:
- `coach_higher` = the coach rates themselves higher on the facet than athletes rate the coach.
- `athlete_higher` = the athletes rate the coach higher than the coach rates themselves.

### 14.1 Autonomy-support

**Coach higher.** You see yourself as giving more choice and explanation than your athletes are reading. That gap is common and it is the place where one specific change (name the rationale out loud, or ask before deciding) tends to close it fast.

**Athlete higher.** Your athletes read more choice and explanation from you than you give yourself credit for. That is a hidden strength. Protect the habits that are producing it.

### 14.2 Structure

**Coach higher.** You see your expectations and feedback as clearer than they are landing for athletes. The fix is usually repetition: state the goal at the start, name one specific piece of feedback each time.

**Athlete higher.** Your athletes experience more clarity and follow-through from you than you are giving yourself credit for. Keep it.

### 14.3 Relatedness-support

**Coach higher.** You believe you are showing more care and interest in your athletes as people than they are feeling from you. This often closes with small signals: one non-sport question per athlete per week, consistently.

**Athlete higher.** Your athletes feel you care about them as people more than you realize. That is real trust. Keep investing in the small signals that are building it.

### 14.4 Controlling

**Coach higher.** You report using more pressure than athletes report feeling. That is unusual. Either you are self-critical, or athletes are not naming what they experience. Worth a conversation that makes it safer for them to say so.

**Athlete higher.** Your athletes experience more pressure from you than you realize. That is the most common blind spot in coaching. Pick one of the items your athletes rated high and watch yourself around it this week.

### 14.5 Chaos

**Coach higher.** You report more inconsistency in your coaching than your athletes experience. Unusual. Possibly they do not feel safe reporting, or you hold yourself to an exacting standard. Worth naming in a team conversation.

**Athlete higher.** Your athletes experience more inconsistency from you than you are aware of. This is often context-specific: late-week, post-travel, or high-stress moments. Identify the trigger before you try to solve it.

---

## 15. Templates to review: Perceived collective satisfaction

Twenty-four templates: three ABC domains (Ambition, Belonging, Craft) at four levels each (high, moderate, low, not_computed), for both athlete and coach audiences. The athlete reads about their own perception of teammates. The coach reads about the athlete's perception of teammates.

### 15.1 Ambition

**High / athlete.** You see your teammates chasing their own goals with meaning. That reads as a healthy team climate for drive.

**High / coach.** The athlete perceives their teammates' goals as meaningful to them. The team climate for drive is reading as healthy.

**Moderate / athlete.** Your teammates' goals land as meaningful to them some of the time. Mixed picture.

**Moderate / coach.** The athlete's read of teammates' goal-meaning is mixed. Watch for which athletes carry the signal.

**Low / athlete.** You are not seeing your teammates' goals as meaningful to them right now. That is worth noticing, even if your own drive is strong.

**Low / coach.** The athlete perceives teammates as disengaged from their own goals. Team climate for drive is a concern.

**Not_computed / athlete.** Not enough check-in data on the team climate for this.

**Not_computed / coach.** Insufficient data for this team climate signal.

### 15.2 Belonging

**High / athlete.** You notice your teammates feeling connected to each other. That is a strong team climate for belonging.

**High / coach.** The athlete perceives teammates as connected to each other. The team climate for belonging reads as healthy.

**Moderate / athlete.** Your teammates seem connected to each other some of the time. Not a full picture yet.

**Moderate / coach.** The athlete's read of team connection is mixed. Could be fault lines inside the group.

**Low / athlete.** You are not seeing strong connection among your teammates right now. That matters even if your own relationships are fine.

**Low / coach.** The athlete perceives teammates as disconnected from each other. Team climate for belonging is a concern.

**Not_computed / athlete.** Not enough check-in data on the team climate for this.

**Not_computed / coach.** Insufficient data for this team climate signal.

### 15.3 Craft

**High / athlete.** You see your teammates growing in their skills. That reads as a healthy team climate for craft.

**High / coach.** The athlete perceives teammates as developing. The team climate for skill growth reads as healthy.

**Moderate / athlete.** Some of your teammates seem to be growing, others less so. Mixed picture on skill development.

**Moderate / coach.** The athlete's read of team skill development is mixed. Worth looking at which athletes feel stuck.

**Low / athlete.** You are not seeing your teammates growing right now. Team climate for skill development is worth naming.

**Low / coach.** The athlete perceives teammates as stuck on skill development. Team climate for craft is a concern.

**Not_computed / athlete.** Not enough check-in data on the team climate for this.

**Not_computed / coach.** Insufficient data for this team climate signal.

---

## 16. Templates to review: Team identification

Eight templates: four levels (high, moderate, low, not_computed) for both audiences.

**High / athlete.** This team feels like your team. Wins and losses land personally, and you see yourself as a real member.

**High / coach.** The athlete identifies strongly with the team. That is a strength and also a pressure point: group events land harder when identification is this high.

**Moderate / athlete.** You feel like part of this team some of the time. The connection is there, but not deep.

**Moderate / coach.** The athlete's bond with the team is in the middle range. Group events land, but not as hard as they do for someone who feels fully part of the team.

**Low / athlete.** You are not feeling like a real member of this team right now. That is data, not a problem.

**Low / coach.** The athlete's team identification is low. Group events are unlikely to hit them as personal. Investigate whether this is by choice or by exclusion.

**Not_computed / athlete.** Not enough check-in data yet on how you are feeling about the team overall.

**Not_computed / coach.** Not enough data on how the athlete feels about the team yet.

---

## 17. Templates to review: Empathic risk

Two templates, one per audience. Fires when an athlete has high team identification and perceives collective need satisfaction as low on one or more domains.

**Athlete.** You care about this team, and you are seeing your teammates struggle in one or more areas. That carries a weight even when your own check-in looks okay. Worth naming with your coach.

**Coach.** This athlete identifies strongly with the team and perceives teammates as struggling. They are exposed to a kind of carry-load that their personal scores may not show. Check in on what they are absorbing for the group.

---

## 18. Templates to review: Team dispersion

Three templates, coach-only. Fires based on the standard deviation of subscale scores across a team's athletes, on the 0-10 scale.

**Tight (SD < 1.5 on most subscales).** Athletes on this team are experiencing things similarly. The team mean is the team. No hidden splits.

**Moderate (SD between 1.5 and 2.5).** Some spread across athletes on this team. Worth noticing which subscales show the spread; they are the places where the team mean hides a split.

**High (SD above 2.5).** High spread across athletes on one or more subscales. The team mean is not the team: some athletes are thriving, some are struggling. The split itself is the story.

---

## 19. Templates to review: Causality orientations

Twelve templates, six orientations at two audiences each. This layer is the annual trait-level instrument described in Section 5 (Causality Orientations). An athlete completes it at onboarding and once per year. The orientation does not change biweekly; the narrative surfaces only on the annual cycle or when the athlete asks.

Design note: the internal labels (autonomy, controlled, impersonal, mixed, emergent, not_computed) never appear in the text. The athlete and coach see plain-language descriptions of the underlying orientation and what it means for how the athlete reads situations.

### 19.1 Autonomy orientation

**Athlete.** You tend to move through situations from your own sense of what you want. When something does not fit, you adjust. That is a resilient way to operate. It does not make every situation easy, but it tends to hold up under pressure.

**Coach.** This athlete reads situations as opportunities for choice. They tolerate coaching-style variation well and respond to reasons and options. Pressure tactics will not help them more than with other athletes, and may cost more.

### 19.2 Controlled orientation

**Athlete.** You tend to read situations through what others expect from you. That can get a lot done. It also wears on you over time. Worth noticing when a choice is yours, not theirs.

**Coach.** This athlete reads situations as demands. They do well with clear expectations. They are also more exposed than other athletes to pressure tactics. Reasons, choice, and voice pay off more here than elsewhere.

### 19.3 Impersonal orientation

**Athlete.** Situations often feel like they happen to you rather than through you. That is a read, not a fact. It shifts when one small thing in your week starts going to plan. Start with one controllable piece and build from there.

**Coach.** This athlete reads situations as beyond their own influence. They are at higher risk of checking out. They also respond less to pressure or choice alone. Start with structure and small, steady wins. Build choice in later.

### 19.4 Mixed orientation

**Athlete.** You do not lean clearly one way. Sometimes you read situations as yours to shape, sometimes as something pushing on you. That is normal and tells you less than a clearer pattern would. Worth watching which one shows up when things get hard.

**Coach.** The athlete does not show one clear pattern. How you coach them will depend on which lens is active in the moment. Watch under pressure. That is when the dominant lens usually shows up.

### 19.5 Emergent (no clear orientation)

**Athlete.** No clear pattern is showing up yet. That is not a problem. A year or two of check-ins will sharpen the picture.

**Coach.** No clear orientation is reading from the data. This is common at first administration. Revisit at the next annual cycle.

### 19.6 Not computed (insufficient responses)

**Athlete.** Not enough answers yet to read how you tend to approach situations. Complete the full screen at the next annual check-in.

**Coach.** Not enough data to score orientation. Ensure the full screen is completed at the next annual administration.

---

## 20. Templates to review: Self-concordance leanings

Eight templates, four leanings at two audiences each. This layer is a per-cycle, per-goal assessment. The athlete names a current goal (the goal text is stored but not shown here; the narratives refer to "this goal" generically) and rates four reasons for pursuing it. The pattern across those four reasons places the goal in one of four bands:

- **Autonomous:** the goal is pursued because it matters to the athlete and the work itself is interesting.
- **Controlled:** the goal is pursued out of pressure, obligation, or image-management.
- **Mixed:** both autonomous and pressure-based reasons are present.
- **Not computed:** fewer than three items answered, or one subscale is empty.

### 20.1 Autonomous

**Athlete.** This goal is yours. You are pursuing it because it matters to you and because the work itself draws you in. That kind of goal tends to hold up across setbacks and tends to lift well-being as you make progress on it.

**Coach.** The athlete's reasons for this goal are values-based and interest-based. Goals like this hold up under setback and tend to drive both performance and well-being. Protect the conditions that allow this; do not tie it to external rewards or pressure.

### 20.2 Controlled

**Athlete.** You are pursuing this goal more because of pressure than because it fits you. Pressure goals can produce real effort, but progress on them does not lift well-being the way self-chosen goals do. Worth a look at whether to keep, reframe, or release this one.

**Coach.** The athlete's reasons here are pressure-based or obligation-based. Even if the athlete makes progress, the well-being lift will be smaller than for a self-chosen goal. A conversation about whether to keep, reshape, or step away from the goal is the action.

### 20.3 Mixed

**Athlete.** You hold both kinds of reasons for this goal. Some of them fit you, some are pressure. That is workable. The pressure side is worth naming because it tends to grow under stress.

**Coach.** The athlete's reasons for this goal mix self-chosen and pressure-based. Watch under stress; the pressure side tends to take over. Help the athlete name the source of the pressure so it can be addressed directly.

### 20.4 Not computed (insufficient responses)

**Athlete.** Not enough answers yet to read how this goal is sitting with you. Complete all four reasons next cycle for a clearer read.

**Coach.** Not enough data on the athlete's reasons for this goal. Ensure all four reasons are completed next cycle.

---

## 21. Templates to review: Self-concordance trajectory

Ten templates, five labels at two audiences each. This layer reads the athlete's self-concordance scores across at least three cycles on the same goal and names the pattern.

Design note: Sheldon's empirical work (Self-Concordance Model) treats *movement* of self-concordance across time as a stronger predictor of goal attainment and well-being than any single cycle's absolute level. This is why the trajectory layer exists and why the narratives focus on direction and change rather than level.

- **Becoming more autonomous:** reasons are shifting from pressure-based to values-based.
- **Becoming more controlled:** reasons are drifting from values-based to pressure-based.
- **Stable:** reasons are holding steady.
- **Oscillating:** reasons swing between cycles without a clear direction.
- **Insufficient data:** fewer than three scored cycles on this goal.

### 21.1 Becoming more autonomous

**Athlete.** Your reasons for this goal are moving in a healthy direction over the last few check-ins. The goal is becoming more yours. Keep noticing what is drawing you in.

**Coach.** The athlete's reasons for this goal are shifting from pressure-based to values-based across recent cycles. Internalization is happening. Protect the conditions that are letting it happen; do not add external rewards or pressure now.

### 21.2 Becoming more controlled

**Athlete.** Your reasons for this goal are shifting toward pressure over the last few check-ins. Worth a quiet look at what changed. Sometimes the goal is right and the context is off.

**Coach.** The athlete's reasons for this goal are drifting from values-based to pressure-based across recent cycles. This is an early signal that often shows up before engagement drops. A non-performance conversation about the goal itself is the action.

### 21.3 Stable

**Athlete.** Your reasons for this goal are holding steady across the last few check-ins. That is the most common pattern and tells you the goal is settled, for now.

**Coach.** The athlete's reasons for this goal are stable across recent cycles. No movement to act on. Revisit when a new goal is set or context changes.

### 21.4 Oscillating

**Athlete.** Your reasons for this goal swing from cycle to cycle. That can mean the goal is contested for you, or that the context around it keeps changing. Worth a closer look at what is driving the swings.

**Coach.** The athlete's reasons for this goal swing across recent cycles without a clear direction. The goal may be contested or the context around it unstable. Ask what changes between weeks where the goal feels theirs and weeks where it does not.

### 21.5 Insufficient data

**Athlete.** Not enough check-ins on this goal yet to read a trend. Two more cycles will give a useful picture.

**Coach.** Not enough cycles on this goal to compute a trajectory. Revisit after at least three completed check-ins on the same goal.

---

## 22. Deliverables we need from you

For each template:

1. Rubric scores (1-5) on the five dimensions in Section 6.
2. A one-line comment on any dimension scored 3 or lower.
3. Optional: suggested alternative wording. We will not adopt it verbatim without checking it against our readability targets and banned-term list, but it helps us understand what you mean.

Plus:

4. Your decision on Section 11 (rank ordering) with a short rationale.
5. A one-paragraph summary of any themes you noticed across templates (for example, a consistent issue with coach-facing tone, or a pattern in how a specific construct is represented).
6. A go / hold / block verdict on the overall packet: "Go" means fine to ship with or without minor edits; "Hold" means material revisions needed before ship; "Block" means a fundamental issue we need to discuss before fixing anything.

Format is flexible. A marked-up version of this document with inline comments works. A separate spreadsheet with template IDs and scores works. A narrative memo works. Your preference.

## 23. Logistics

**Estimated review time:** 12 to 16 hours for a thorough first pass across all ten template families (passion, overinvestment, regulatory, erosion, circumplex facet, circumplex approach, circumplex gap, group-conscious, causality, self-concordance plus trajectory), including the Section 11 rank-ordering memo and summary comments. We are happy to split this into two or three engagements if that is easier to schedule.

**Compensation:** By agreement with the Ero team.

**Preferred deliverable date:** Within two weeks of accepting the engagement, unless otherwise negotiated.

**Confidentiality:** The templates and product plans in this packet are pre-public. We will send a short mutual NDA separately if you prefer that format; otherwise please treat the contents as confidential through your deliverable date.

**Contact for questions during review:** Listed in the cover email. We welcome clarifying questions. If something in the packet reads as ambiguous, assume that is a signal we need to clarify before shipping, and flag it explicitly.

**About the reviewer:** We are particularly interested in engaging a reviewer who has worked directly with college or elite-youth athletes, has training in Self-Determination Theory or adjacent motivational frameworks, and has experience translating clinical or research vocabulary into coach-facing and athlete-facing communication. Certification as a Certified Mental Performance Consultant (CMPC) or equivalent is ideal but not required if depth of applied experience is present.

Thank you for your time and care. This packet exists because we want the language we put in front of athletes and coaches to be as strong as the science underneath it.
