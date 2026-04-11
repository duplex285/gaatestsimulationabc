# Expected Utility Framework for ABC Assessment

**Date:** 2026-04-11
**Status:** Plan (not yet implemented)
**Depends on:** improvement-plan-personalization-engine.md, abc-assessment-spec.md

---

## 1. What This Does

The ABC assessment classifies athletes into 8 archetypes. Each archetype has strengths, watch-fors, and a growth edge. Today, those are static: every Pioneer gets the same text.

This framework makes them dynamic. Two Pioneers with different score distributions get different guidance, because their scores tell us different things about what they value, what they risk losing, and where a small investment would matter most.

The athlete never sees utility theory. They see:

> "Your Ambition is your anchor. Belonging is where a small shift would make the biggest difference right now."

The math underneath produces that sentence. The sentence is the product.

---

## 2. How It Works

### 2.1 The score distribution tells us preferences

An athlete's satisfaction and frustration scores across Ambition, Belonging, and Craft are not just numbers. They reveal what the athlete values and where they invest their energy.

- A Pioneer with A-Sat 9.0 values goal pursuit intensely. A threat to Ambition (rising frustration, declining satisfaction) costs them more than the same shift in a domain they are less invested in.
- A Pioneer with A-Sat 6.5 has Ambition activated but not dominant. They are closer to the type boundary. Their profile is less settled.

The distribution shape, not just the type label, drives the personalization.

### 2.2 Frustration costs more than satisfaction delivers

SDT research shows an asymmetry: need frustration predicts burnout, depression, and disengagement at a rate that exceeds what need satisfaction predicts for engagement and motivation (Bartholomew et al., 2011; Lonsdale et al., 2009). The dark pathway is not the absence of the bright one.

In practical terms: a 1-point rise in frustration is worse than a 1-point drop in satisfaction. An athlete with Belonging satisfaction 7.0 and frustration 6.0 looks fine on the satisfaction score alone. The frustration tells a different story. The system should weight that frustration more heavily when generating watch-fors and growth edges.

The multiplier is approximately 1.5-2.0x, based on the finding that frustration accounts for up to 74% of variance in burnout (Lonsdale et al., 2009).

### 2.3 Small investments matter most where the score is lowest

An athlete with Craft satisfaction at 3.0 benefits more from a skill development session than an athlete with Craft satisfaction at 8.0 benefits from the same session. The return on investment is higher when the score is low, because the psychological need is most responsive when it is least satisfied.

This is diminishing returns: the first unit of satisfaction gained is worth more than the tenth. The implication for the growth edge: always point toward the domain where the athlete sits on the steepest part of the curve.

### 2.4 Having multiple domains satisfied is more than the sum

An Integrator (all three domains active) is more resilient than three single-domain specialists combined. When one domain dips temporarily, the other two provide a buffer. This integration bonus means the system should value maintaining breadth, not just maximizing any single domain.

---

## 3. What Changes for the Athlete

### 3.1 Dynamic strengths

Current (static): Every Integrator sees "Versatility, Balanced judgment, Cross-domain insight, Broad competence."

Dynamic: The strengths reflect which domains are actually strongest and how balanced they are.

| Integrator profile | Dynamic strengths |
|-------------------|-------------------|
| A:9.0, B:6.2, C:6.0 | "Your Ambition drives the team forward. Your Belonging and Craft provide a stable foundation, though they are closer to the threshold. Your strength is that you lead from the front without losing connection." |
| A:6.5, B:6.5, C:6.5 | "Your balance is genuine. No single domain dominates. Your strength is consistency: you hold steady when specialists burn hot and cold." |
| A:7.0, B:8.5, C:6.2 | "Your Belonging is your anchor. People trust you because you invest in relationships first. Your Ambition and Craft are active but secondary to the relational core." |

Same archetype. Different narrative. Driven by the score distribution.

### 3.2 Dynamic watch-fors

The watch-for is personalized based on what the athlete risks losing.

The principle: your highest-satisfaction domain is your biggest asset and your biggest vulnerability. If it drops, the psychological cost is higher than if a lower domain drops, because you have organized your identity around it.

| Pioneer profile | Dynamic watch-for |
|----------------|-------------------|
| A:9.0, B:3.0, C:4.0 | "Your Ambition is carrying your motivation. If goal pursuit is disrupted (coaching change, injury, loss of starting role), the impact will hit harder than you expect because Belonging and Craft are not yet strong enough to buffer it." |
| A:7.0, B:5.5, C:2.0 | "Your Craft is underdeveloped. If you hit a performance plateau, you may lack the intrinsic interest in skill development to push through it. The risk is that declining performance erodes your Ambition from below." |

### 3.3 Dynamic growth edge

The growth edge points toward the domain where a small investment has the largest return. This is where the score is lowest but frustration is not yet high, meaning the athlete is underinvested, not blocked.

| Profile | Growth edge |
|---------|------------|
| A:8.0, B:3.0, C:5.0 (frustration all low) | "Belonging is your biggest opportunity. You are not blocked here, you just have not invested yet. One genuine connection with a teammate would shift this domain more than any amount of goal-setting would shift your already-strong Ambition." |
| A:8.0, B:3.0, C:5.0 (B-frust: 7.0) | "Belonging is low AND frustrated. This is not a growth opportunity, it is an active problem. Something in your team environment is making connection feel costly. Start there before investing elsewhere." |

The distinction matters: low satisfaction with low frustration is "underdeveloped" (growth opportunity). Low satisfaction with high frustration is "actively blocked" (urgent concern). The growth edge adapts.

---

## 4. What Changes for the Coach

### 4.1 Team distribution insight

The coach sees all athletes on one diagram. The expected utility framework adds: where is the highest-return coaching investment across the team?

If 8 of 44 athletes have Belonging satisfaction below 4.0, a team-wide Belonging activity (shared meals, structured partner work, team building) has higher total return than 8 individual conversations, because the per-athlete cost is lower and the aggregate benefit is larger.

If only 1 athlete has Craft below 4.0 while the rest are above 6.0, individual attention is warranted because a team-wide skill session does not address an individual gap.

### 4.2 Coach-profile-to-distribution match

The coach takes the assessment too. If the coach is a Pioneer (Ambition-dominant), and the team distribution shows low Belonging across the roster, the system can surface: "Your coaching emphasis on goal pursuit may not be reaching athletes whose primary need is connection. Consider whether your approach is reinforcing the distribution you see."

This is not a judgment. It is pattern recognition. The coach's profile is not wrong. It creates predictable blind spots, and the system makes those visible.

---

## 5. How the Check-ins Refine This Over Time

The initial assessment gives a point-in-time distribution. The check-ins reveal how the distribution moves.

**What the check-ins add to the utility picture:**

1. **Which domain is most volatile?** High volatility means the athlete's investment in that domain is unstable. The growth edge should not point toward a volatile domain (the athlete is already wrestling with it). It should point toward the most stable low domain.

2. **Is frustration leading or lagging?** The cascade model (frustration rises before satisfaction drops) tells us which domain is about to shift. The watch-for becomes predictive: "Your Craft frustration has risen for 3 weeks while satisfaction is still holding. This pattern often precedes a satisfaction drop. Pay attention here."

3. **Has the growth edge changed?** If the athlete acts on the initial growth edge (invests in Belonging), the check-ins will show Belonging satisfaction rising. The growth edge should then shift to the next-highest-return domain automatically. The system evolves with the athlete.

---

## 6. The 125-Profile Code as Input

The simulator already computes a 125-combination profile code (5 satisfaction levels per domain: Very High, High, Medium, Low, Very Low). This code (e.g., "4-3-5" meaning A:High, B:Medium, C:Very High) is the input to the dynamic narrative generator.

The mapping:

```
Type (8 archetypes)          --> frame (who you are)
Profile code (125 combos)    --> specifics (where you sit within that frame)
Frustration scores (0-10)    --> risk (what to watch for)
Score-to-utility curve       --> priority (where to invest)
Check-in trajectory          --> change (what is shifting)
```

The type is stable (changes slowly, requires high confidence). The profile code and frustration scores change with each measurement. The narrative regenerates each time, producing personalized output that evolves with the athlete.

---

## 7. The Four Sections

Drawing on Kegan and Lahey's Deliberately Developmental Organizations (DDO) framework, the participant narrative has four sections. Each is generated dynamically from the score distribution, personality descriptors, and team role behaviors. No trait names, scale names, or technical labels are shown to the athlete.

### 7.1 Overview

One paragraph that names who the athlete is in plain language. It draws from the archetype, the personality descriptors (translated from Big Five percentiles into behavioral language), and the team role behaviors (translated from Belbin roles into what the person actually does). It names what is working and what is not, without using any psychometric vocabulary.

### 7.2 Strengths (DDO: Edge, Developmental Aspirations)

These are the athlete's natural patterns described as behaviors, not traits. Each strength is something the athlete does, not something they score. The strengths are drawn from:

- The highest-satisfaction domain (what energizes them)
- The personality descriptors (how they show up)
- The team role behaviors (what they contribute to others)

The language is specific and personal. "You create safety for others without needing to be asked" is a strength. "High agreeableness" is not.

### 7.3 What to Watch For (DDO: Groove, Developmental Practices)

These are the patterns that could undermine the athlete if left unattended. They are drawn from:

- Frustration scores (where effort feels costly)
- The gap between satisfaction and frustration within a domain (the Vulnerable pattern)
- The proximity of key scores to classification thresholds

The language reframes frustration as information, not failure. "You are not avoiding your craft because you do not care. You are avoiding it because the feedback you are getting feels like judgment" is a watch-for. "Craft frustration is high (6.11)" is not.

### 7.4 Growth Opportunities (DDO: Home, Developmental Communities)

These are specific, actionable invitations for vulnerability and depth. They are drawn from:

- The lowest-satisfaction domain that is not already frustrated (where investment has the highest return)
- The relationship between the athlete's relational strength and their other domains (can Belonging carry Ambition or Craft development?)
- The personality descriptors (how this athlete learns best)

The language is concrete and relational. "Use one of those relationships to say out loud what you are struggling with in your sport" is an opportunity. "Invest in Belonging" is not.

### 7.5 Resonance Check

After the athlete reads their narrative:

> **Does this sound like you?** Your response helps us learn. If something feels off, that is useful.
> [ Yes, this resonates ] [ Some of it ] [ Not really ]

If the athlete selects "Some of it" or "Not really," the system flags which section did not land. This feedback enters the trajectory: the inference is off for this person, and the next reassessment should probe the flagged domain more carefully. The model learns from disagreement, not just from scores.

---

## 8. Narrative Examples

### 8.1 Anchor (B-Sat 5.83, B-Frust 3.33, A-Sat 3.33, A-Frust 5.83, C-Sat 4.17, C-Frust 6.11)

**Overview:**
You are someone people turn to. You are naturally warm, cooperative, and genuinely interested in others. Your team roles reflect this: you anchor the group, you connect people who would not otherwise talk, and you bring structure without making it feel rigid. That is your foundation. Right now, your relationships are the one area where you feel more satisfied than frustrated. Goal pursuit and skill development both feel heavier than they should.

**Strengths:**
- You create safety for others without needing to be asked. This is not something you perform. It is how you operate.
- You are curious about people. You ask questions and remember the answers. That builds loyalty that most people have to work much harder to earn.
- You organize without controlling. People follow your lead because you make things clearer, not because you demand compliance.
- You are emotionally steady. When things get tense around you, you do not amplify it. That is rarer than you think.

**What to Watch For:**
- Goal pursuit feels like obligation right now, not choice. When you set goals, ask whether they are yours or someone else's. If you cannot tell the difference, that is the problem.
- Skill development feels evaluative. You are not avoiding your craft because you do not care. You are avoiding it because the feedback you are getting feels like judgment. Pay attention to who is giving the feedback and how.
- Your relationships are the one thing holding steady, but they are closer to the edge than they look. Do not sacrifice what is working to perform in areas that feel punishing.

**Growth Opportunities:**
- You already have people who trust you. Use one of those relationships to say out loud what you are struggling with in your sport. Not the physical part. The motivation part. That conversation is where direction starts.
- You may not naturally build structure for yourself, even though you do it well for others. Make a small plan for yourself the way you would for a teammate. Not a big one. A small one.
- Pick one skill you are curious about, not one you are supposed to improve. Curiosity is how you learn best. Obligation shuts it down for someone like you.

> **Does this sound like you?** [ Yes, this resonates ] [ Some of it ] [ Not really ]

### 8.2 Pioneer A (A-Sat 9.0, A-Frust 2.0, B-Sat 3.0, B-Frust 2.5, C-Sat 4.0, C-Frust 3.0)

**Overview:**
You know where you are going. You set direction and move toward it with conviction. You are independent, assertive, and energized by challenge. Right now, goal pursuit is the engine that drives everything. Relationships and skill development are quieter parts of your life, not because they do not matter, but because your attention flows to what challenges you most.

**Strengths:**
- You set goals that are yours, not someone else's. That independence is the foundation of sustained motivation.
- You bring energy to the room. People notice your drive, and it raises the standard around you.
- You are not easily knocked off course. When things go wrong, you recalibrate and keep moving.
- You are comfortable with discomfort. Competition sharpens you rather than draining you.

**What to Watch For:**
- Your motivation depends almost entirely on goal pursuit. If that is disrupted, whether by injury, a coaching change, or losing a starting role, the impact will hit harder than you expect. You do not have a backup source of motivation right now.
- You may be so focused on the next objective that you miss what the people around you are offering. Relationships are not a distraction from your goals. They are the infrastructure that supports them when things get hard.

**Growth Opportunities:**
- Belonging is not something you are frustrated about. It is just something you have not invested in. One genuine connection with a teammate, not a strategic alliance, would change the shape of your experience without costing you any of your drive.
- You bring structure to your goals naturally. Try bringing that same clarity to one relationship. What would it look like to pursue a friendship with the same intention you bring to your training?

> **Does this sound like you?** [ Yes, this resonates ] [ Some of it ] [ Not really ]

### 8.3 Pioneer B (A-Sat 7.0, A-Frust 3.0, B-Sat 5.5, B-Frust 2.0, C-Sat 2.0, C-Frust 6.0)

**Overview:**
You have direction and you are building connections alongside it. That combination is stronger than most. But skill development feels like a wall right now. You care about getting better, but something about the process feels punishing rather than productive.

**Strengths:**
- You pursue goals with genuine autonomy. Your drive comes from inside, not from pressure.
- You are developing relationships alongside your ambition. Most people with your drive neglect that. You are not.
- You are emotionally present. You show up for your teammates, not just for your performance.

**What to Watch For:**
- Working on your craft feels like being judged rather than learning. That is not about your ability. It is about the environment around skill development. Pay attention to whether the feedback you receive is designed to help you or to evaluate you.
- The gap between how much you care about your craft (the frustration tells you that you care) and how little satisfaction it gives you is unsustainable. Something needs to change in how you are developing, not whether you are developing.

**Growth Opportunities:**
- Tell your coach what kind of feedback helps you and what kind shuts you down. That is not weakness. It is self-knowledge.
- Find one aspect of your craft where you feel curious, not obligated. Start there. Curiosity survives failure. Obligation does not.
- Your Belonging is nearly activated. One more step, being honest with a teammate about what you are struggling with, would give you a second foundation to stand on.

> **Does this sound like you?** [ Yes, this resonates ] [ Some of it ] [ Not really ]

---

## 9. Layout

The dynamic narrative occupies the left panel of the participant detail view. The raw scores, subscale bars, classification confidence, and team role assignments stay on the right panel. The left tells the story. The right shows the evidence.

```
┌─────────────────────────┬──────────────────────────┐
│                         │                          │
│  OVERVIEW               │  SUBSCALE SCORES (0-10)  │
│  [paragraph]            │  [bars]                  │
│                         │                          │
│  STRENGTHS              │  MOTIVATIONAL PROFILE    │
│  [bullets]              │  [domain states]         │
│                         │                          │
│  WHAT TO WATCH FOR      │  CLASSIFICATION          │
│  [bullets]              │  CONFIDENCE              │
│                         │  [stability metrics]     │
│  GROWTH OPPORTUNITIES   │                          │
│  [bullets]              │  TEAM ROLES              │
│                         │  [badges]                │
│  ─────────────────────  │                          │
│  Does this sound like   │  FRUSTRATION SIGNATURES  │
│  you? [Yes] [Some] [No] │  [badges]                │
│                         │                          │
└─────────────────────────┴──────────────────────────┘
```

The raw item responses (AS1: 1, AS2: 1, etc.) move to a collapsible detail section below, available for inspection but not prominent.

---

## 10. Implementation Approach

### Phase 1: Dynamic narrative rules

Replace static archetype narratives with a rule-based generator. Inputs: archetype, 125-profile code, 6 frustration scores, Big Five percentiles (as behavioral descriptors), Belbin roles (as behavioral descriptors). No psychometric vocabulary in the output.

### Phase 2: Frustration weighting

Apply the 1.5x frustration multiplier when selecting which domain to highlight in Watch For and Growth Opportunities. Low satisfaction + low frustration = growth opportunity (underdeveloped, not blocked). Low satisfaction + high frustration = urgent concern (the environment needs to change, not the athlete).

### Phase 3: Resonance feedback loop

Add the "Does this sound like you?" prompt after the narrative. Track responses in the trajectory. Disagreement flags the inference for review at the next reassessment.

### Phase 4: Check-in integration

Update the dynamic narrative after each check-in. Growth opportunities shift as the athlete develops. Watch-fors become predictive when the cascade pattern is detected.

### Phase 5: Coach team-level view

Aggregate individual narratives into a team distribution. Show the coach where the highest-return team-level investment is, using the same plain language.

---

## 11. What This Does Not Do

- It does not require the athlete to understand utility theory, SDT, Big Five, Belbin, or any psychometric framework
- It does not replace the archetype system. The 8 types remain. The narratives within them become personalized
- It does not add new survey questions. The input is the same 36 items plus check-ins
- It does not create 125 separate narrative templates. It creates rules that generate narratives from score distributions
- It does not expose trait names, scale names, or technical labels to the athlete
- It does not present disagreement as error. If the athlete says "not really," the system learns from that
