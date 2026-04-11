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

## 7. Implementation Approach

### Phase 1: Dynamic narrative rules

Replace static archetype narratives with a rule-based generator that takes the profile code and frustration scores as input. No utility math visible. The rules encode the principles:

- Strengths: name the highest-satisfaction domain and describe how it shapes the archetype
- Watch-for: identify the highest-investment domain and describe the cost of losing it
- Growth edge: point toward the lowest-satisfaction, lowest-frustration domain (underdeveloped, not blocked). If lowest-satisfaction has high frustration, flag it as an active concern instead

### Phase 2: Frustration weighting

Apply the 1.5x frustration multiplier when computing which domain to highlight. This changes the growth edge for Vulnerable athletes: a domain with sat 7.0 and frust 6.0 has lower net value than the raw satisfaction score suggests.

### Phase 3: Check-in integration

Update the dynamic narrative after each check-in based on trajectory. The growth edge shifts as the athlete develops. The watch-for becomes predictive when the cascade pattern is detected.

### Phase 4: Coach team-level view

Aggregate individual utility profiles into a team distribution. Show the coach where the highest-return team-level intervention is.

---

## 8. What the Athlete Sees

**Before (static):**
> Type: Pioneer
> Strengths: Autonomy, goal clarity, competitive drive, forward momentum
> Watch for: May neglect relationships or skill depth in pursuit of goals
> Growth edge: Pick one relationship or one skill to invest in alongside your goals

**After (dynamic, Pioneer A with A:9.0, B:3.0, C:4.0):**
> Type: Pioneer
> Strengths: Your Ambition is exceptionally strong. You set direction and pursue it with conviction. This is rare and valuable.
> Watch for: Your motivation depends almost entirely on goal pursuit. If that is disrupted (injury, coaching change, role loss), you have little to fall back on. Belonging and Craft are not yet providing support.
> Growth edge: Belonging is your biggest opportunity right now. You are not frustrated here, just uninvested. One genuine connection would diversify your motivational foundation.

**After (dynamic, Pioneer B with A:7.0, B:5.5, C:2.0, C-frust:6.0):**
> Type: Pioneer
> Strengths: Your Ambition is activated and your Belonging is developing alongside it. You are building a broader base than most Pioneers.
> Watch for: Craft frustration is high (6.0) with low satisfaction (2.0). You feel blocked in skill development. This combination predicts disengagement from training if not addressed.
> Growth edge: Craft is not a growth opportunity right now, it is an active concern. The frustration needs to be addressed before investment can take hold. Talk to your coach about what is making skill development feel evaluative rather than developmental.

Same type. Different guidance. Driven by the scores, explained in plain language.

---

## 9. What This Does Not Do

- It does not require the athlete to understand utility theory, SDT, or statistics
- It does not replace the archetype system. The 8 types remain. The narratives within them become personalized
- It does not add new survey questions. The input is the same 36 items plus check-ins
- It does not create 125 separate narrative templates. It creates rules that generate narratives from score distributions
- It does not expose numbers to the athlete beyond what is already shown (subscale scores, domain states)
