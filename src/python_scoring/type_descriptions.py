"""Type and state descriptions for the ABC Assessment.

Reference: abc-assessment-spec Section 2.4 (motivational type derivation)
Reference: Phase 2b decision consistency analysis (archetype revision rationale)

8 base patterns with continuous frustration reporting.

Base patterns from binary satisfaction threshold (5.5) per domain:
  Integrator (A strong, B strong, C strong)
  Captain (A strong, B strong, C developing)
  Architect (A strong, B developing, C strong)
  Mentor (A developing, B strong, C strong)
  Pioneer (A strong, B developing, C developing)
  Anchor (A developing, B strong, C developing)
  Artisan (A developing, B developing, C strong)
  Seeker (A developing, B developing, C developing)

Frustration is reported as continuous scores per domain rather than
as a categorical modifier (Steady/Striving/Resolute). This preserves
all information without the classification instability that Phase 2b
identified (~31% type agreement with 24 categories).

All names are strengths-based.
"""

# ---------------------------------------------------------------------------
# Domain State Descriptions
# ---------------------------------------------------------------------------

DOMAIN_STATE_DESCRIPTIONS = {
    "Thriving": {
        "label": "Thriving",
        "condition": "Satisfaction >= 6.46, Frustration < 4.38",
        "summary": "This need is met with minimal obstruction.",
        "science": (
            "When a basic psychological need is satisfied without significant "
            "frustration, people experience vitality, intrinsic motivation, and "
            "psychological growth (Deci & Ryan, 2000). Low frustration distinguishes "
            "genuine thriving from the brittle high performance of the Vulnerable "
            "state. Sustained need satisfaction predicts lower burnout, higher "
            "engagement, and greater persistence (Lonsdale & Hodge, 2011)."
        ),
        "fatigue": (
            "Low fatigue risk. Satisfaction replenishes cognitive resources while "
            "low frustration avoids the rumination that drains them."
        ),
        "implication": (
            "No intervention needed. Protect the conditions enabling this state. "
            "Monitor for early signs of rising frustration."
        ),
        "colour": "#3ABF5E",
    },
    "Vulnerable": {
        "label": "Vulnerable",
        "condition": "Satisfaction >= 6.46, Frustration >= 4.38",
        "summary": "This need is met, but at a cost. High frustration signals strain.",
        "science": (
            "Need frustration harms wellbeing even when need satisfaction is high "
            "(Vansteenkiste & Ryan, 2013). This is the 'successful but suffering' "
            "pattern. High satisfaction and high frustration together create "
            "unsustainable tension. Without intervention, frustration erodes "
            "satisfaction and the trajectory shifts toward Distressed."
        ),
        "fatigue": (
            "High fatigue risk. The person spends cognitive resources on two fronts: "
            "performing the task and suppressing the frustration that accompanies it."
        ),
        "implication": (
            "Highest priority for intervention. The person is still engaged, "
            "the window to act is now."
        ),
        "colour": "#F5A623",
    },
    "Mild": {
        "label": "Mild",
        "condition": "Satisfaction < 6.46, Frustration < 4.38",
        "summary": "This need is neither fulfilled nor actively blocked. It sits idle.",
        "science": (
            "Low satisfaction without frustration suggests the need goes unengaged "
            "rather than thwarted. In SDT terms this resembles amotivation (Deci & "
            "Ryan, 2000). Prolonged dormancy in a core need predicts gradual "
            "disengagement and reduced wellbeing (Bartholomew et al., 2011)."
        ),
        "fatigue": (
            "Moderate fatigue risk from understimulation. Without engagement, "
            "the mind lacks the intrinsic reward that sustains attention."
        ),
        "implication": (
            "Lower urgency. Explore whether the environment offers opportunities "
            "to engage this need."
        ),
        "colour": "#A0A0A0",
    },
    "Distressed": {
        "label": "Distressed",
        "condition": "Satisfaction < 6.46, Frustration >= 4.38",
        "summary": "This need is unmet and actively blocked.",
        "science": (
            "Low satisfaction and high frustration together constitute need "
            "thwarting, the most damaging state in SDT (Bartholomew et al., "
            "2011). Sustained thwarting predicts burnout, depressive symptoms, "
            "and dropout (Lonsdale & Hodge, 2011)."
        ),
        "fatigue": (
            "Severe fatigue risk. Chronic frustration without satisfaction "
            "triggers stress circuits that degrade executive function."
        ),
        "implication": (
            "Urgent intervention. Address the frustration source first: "
            "removing blockers beats adding positive experiences."
        ),
        "colour": "#E8563A",
    },
}

# ---------------------------------------------------------------------------
# 8 Motivational Type Descriptions
# ---------------------------------------------------------------------------
# Base patterns use all three domains. Frustration is reported continuously.

TYPE_DESCRIPTIONS = {
    "Integrator": {
        "tagline": "All three needs activated",
        "description": (
            "All three needs are engaged. Ambition, belonging, and craft each "
            "contribute to a balanced motivational profile. This is the broadest "
            "and most resilient pattern. Frustration levels determine whether this "
            "balance is sustainable or under strain."
        ),
        "strengths": [
            "Versatility",
            "Balanced judgement",
            "Cross-domain insight",
            "Broad competence",
        ],
        "watch_for": (
            "May spread attention too thin rather than deepening in one area. "
            "If frustration is high across domains, burnout risk is real despite "
            "high satisfaction."
        ),
        "growth_edge": "Choose one domain to push from strong to exceptional.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "strong"},
    },
    "Captain": {
        "tagline": "Leading through people",
        "description": (
            "Ambition and belonging are both activated. This person leads through "
            "connection, influencing others while maintaining relationships. "
            "Craft is the developing frontier."
        ),
        "strengths": [
            "People leadership",
            "Coalition-building",
            "Relational intelligence",
            "Results focus",
        ],
        "watch_for": (
            "Craft skills may plateau without deliberate investment. "
            "If frustration is concentrated in the developing domain, it signals "
            "a skill gap that undermines leadership credibility."
        ),
        "growth_edge": "Invest in one technical skill that deepens your leadership credibility.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "developing"},
    },
    "Architect": {
        "tagline": "Building with ambition and skill",
        "description": (
            "Ambition and craft are both activated. This person builds "
            "strategically, combining drive with technical depth. Belonging "
            "is the developing frontier."
        ),
        "strengths": [
            "Strategic execution",
            "Technical vision",
            "Quality output",
            "High standards",
        ],
        "watch_for": (
            "May undervalue relationships or move too fast for consensus. "
            "If belonging frustration is high, isolation compounds the risk."
        ),
        "growth_edge": "Bring one collaborator into your next project early.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "strong"},
    },
    "Mentor": {
        "tagline": "Growing others through expertise",
        "description": (
            "Belonging and craft are both activated. This person shares knowledge "
            "generously and builds others up through competence. Ambition is the "
            "developing frontier."
        ),
        "strengths": [
            "Teaching",
            "Knowledge sharing",
            "Patient guidance",
            "Trust-building",
        ],
        "watch_for": (
            "May avoid competitive settings that feel personally exposing. "
            "If ambition frustration is high, it signals blocked goal pursuit "
            "that mentoring cannot address alone."
        ),
        "growth_edge": "Share your work with a wider audience. Expertise scales when visible.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "strong"},
    },
    "Pioneer": {
        "tagline": "Ambition leading the way",
        "description": (
            "Ambition is the primary activated need. Drive and goal pursuit are "
            "strong; belonging and craft are developing. This person knows where "
            "they want to go."
        ),
        "strengths": [
            "Goal clarity",
            "Initiative",
            "Competitive edge",
            "Decisive action",
        ],
        "watch_for": (
            "Two developing domains leave a narrow motivational base. "
            "High frustration in developing domains signals that ambition alone "
            "cannot sustain engagement."
        ),
        "growth_edge": "Invest in one relationship or skill that supports your ambition.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "developing"},
    },
    "Anchor": {
        "tagline": "Belonging grounding everything",
        "description": (
            "Belonging is the primary activated need. Connection and relationships "
            "are strong; ambition and craft are developing. This person provides "
            "stability for others."
        ),
        "strengths": [
            "Relational stability",
            "Trust",
            "Empathy",
            "Team cohesion",
        ],
        "watch_for": (
            "Two developing domains mean personal growth may stall without "
            "intentional effort. If frustration is high while belonging is strong, "
            "the person may be absorbing others' stress."
        ),
        "growth_edge": "Use your relational strength to learn from someone you admire.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "developing"},
    },
    "Artisan": {
        "tagline": "Craft leading quietly",
        "description": (
            "Craft is the primary activated need. Technical depth and quality "
            "drive this person; ambition and belonging are developing. Mastery "
            "is the foundation."
        ),
        "strengths": [
            "Deep expertise",
            "Quality focus",
            "Independent mastery",
            "Patience with complexity",
        ],
        "watch_for": (
            "Two developing domains may lead to isolation or missed opportunities. "
            "If belonging frustration is high, the isolation is not chosen."
        ),
        "growth_edge": "Share one thing you have mastered. Teaching builds belonging from craft.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "strong"},
    },
    "Seeker": {
        "tagline": "All three needs developing",
        "description": (
            "No domain is fully activated. This person is in an open, exploratory "
            "phase. The frustration levels determine whether this is peaceful "
            "exploration or distressed searching: low frustration suggests openness, "
            "high frustration signals urgent unmet needs."
        ),
        "strengths": [
            "Openness",
            "Fresh perspective",
            "Willingness to change",
            "Capacity for transformation",
        ],
        "watch_for": (
            "Prolonged seeking without activation leads to drift. "
            "High frustration across domains requires immediate support; "
            "the risk of disengagement is highest here."
        ),
        "growth_edge": "Pick one domain and invest deliberately. Commitment creates momentum.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "developing"},
    },
}


def get_type_description(type_name: str) -> dict | None:
    """Look up a type description by name.

    Reference: abc-assessment-spec Section 2.4
    """
    return TYPE_DESCRIPTIONS.get(type_name)


def get_state_description(state: str) -> dict | None:
    """Look up a domain state description by name.

    Reference: abc-assessment-spec Section 2.2
    """
    return DOMAIN_STATE_DESCRIPTIONS.get(state)
