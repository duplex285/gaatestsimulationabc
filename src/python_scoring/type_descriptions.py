"""Type and state descriptions for the ABC Assessment.

Reference: abc-assessment-spec Section 2.2 (domain states)
Reference: abc-assessment-spec Section 2.4 (motivational type derivation)

24 types = 8 base patterns × 3 frustration modifiers.

Base patterns from binary satisfaction threshold (6.46) per domain:
  Integrator (A↑B↑C↑), Captain (A↑B↑C↓), Architect (A↑B↓C↑),
  Mentor (A↓B↑C↑), Pioneer (A↑B↓C↓), Anchor (A↓B↑C↓),
  Artisan (A↓B↓C↑), Seeker (A↓B↓C↓).

Modifiers from frustrated-domain count (frust ≥ 4.38):
  Steady (0), Striving (1), Resolute (2-3).

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
            "Highest priority for intervention. The person is still engaged — "
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
            "thwarting — the most damaging state in SDT (Bartholomew et al., "
            "2011). Sustained thwarting predicts burnout, depressive symptoms, "
            "and dropout (Lonsdale & Hodge, 2011)."
        ),
        "fatigue": (
            "Severe fatigue risk. Chronic frustration without satisfaction "
            "triggers stress circuits that degrade executive function."
        ),
        "implication": (
            "Urgent intervention. Address the frustration source first — "
            "removing blockers beats adding positive experiences."
        ),
        "colour": "#E8563A",
    },
}

# ---------------------------------------------------------------------------
# 24 Motivational Type Descriptions
# ---------------------------------------------------------------------------
# 8 base patterns × 3 modifiers (Steady / Striving / Resolute)
#
# Base patterns use all three domains:
#   Integrator  (A↑B↑C↑) — all three needs activated
#   Captain     (A↑B↑C↓) — ambition + belonging strong, craft developing
#   Architect   (A↑B↓C↑) — ambition + craft strong, belonging developing
#   Mentor      (A↓B↑C↑) — belonging + craft strong, ambition developing
#   Pioneer     (A↑B↓C↓) — ambition leads, others developing
#   Anchor      (A↓B↑C↓) — belonging leads, others developing
#   Artisan     (A↓B↓C↑) — craft leads, others developing
#   Seeker      (A↓B↓C↓) — all three developing
#
# Modifiers from frustrated-domain count:
#   Steady   (0 frustrated) — sustainable flow
#   Striving (1 frustrated) — productive friction in one area
#   Resolute (2-3 frustrated) — persevering through multiple challenges

TYPE_DESCRIPTIONS = {
    # === INTEGRATOR (A↑ B↑ C↑) ===
    "Steady Integrator": {
        "tagline": "All systems flowing",
        "description": (
            "All three needs are activated with no frustrated domain. Ambition, "
            "belonging, and craft each contribute to a balanced, sustainable "
            "motivational profile. This is the rarest and most resilient pattern."
        ),
        "strengths": [
            "Versatility",
            "Balanced judgement",
            "Sustainable energy",
            "Cross-domain insight",
        ],
        "watch_for": "May spread attention too thin rather than deepening in one area.",
        "growth_edge": "Choose one domain to push from strong to exceptional.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "strong"},
    },
    "Striving Integrator": {
        "tagline": "Thriving on most fronts, one edge to smooth",
        "description": (
            "All three needs are activated but one domain carries frustration. "
            "The broad foundation is strong — the friction in one area is the "
            "development priority, not a crisis."
        ),
        "strengths": ["Broad competence", "Self-awareness", "Adaptive", "Resilient baseline"],
        "watch_for": "The frustrated domain may erode the others if left unaddressed.",
        "growth_edge": "Name the friction source. With this strong a base, targeted action works fast.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "strong"},
    },
    "Resolute Integrator": {
        "tagline": "Meeting every need despite the headwinds",
        "description": (
            "All three needs are activated but two or more domains carry "
            "frustration. Satisfaction is high across the board, yet the cost "
            "of maintaining it is also high. This is high performance under pressure."
        ),
        "strengths": [
            "Extraordinary resilience",
            "Refusal to drop standards",
            "Multi-front competence",
            "Determination",
        ],
        "watch_for": "Burnout risk is real. This pace is not sustainable without reducing friction.",
        "growth_edge": "Pick the highest-friction domain and address one specific blocker.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "strong"},
    },
    # === CAPTAIN (A↑ B↑ C↓) ===
    "Steady Captain": {
        "tagline": "Leading through people, sustainably",
        "description": (
            "Ambition and belonging are both activated with no frustrated domain. "
            "This person leads through connection — influencing others while "
            "maintaining relationships. Craft is the developing frontier."
        ),
        "strengths": [
            "People leadership",
            "Coalition-building",
            "Sustainable drive",
            "Relational intelligence",
        ],
        "watch_for": "Craft skills may plateau without deliberate investment.",
        "growth_edge": "Invest in one technical skill that deepens your leadership credibility.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "developing"},
    },
    "Striving Captain": {
        "tagline": "Leading through people, one edge under pressure",
        "description": (
            "Ambition and belonging are activated but one domain carries "
            "frustration. The leadership instinct and relational energy are "
            "strong — the friction is a signal, not a failure."
        ),
        "strengths": [
            "Resilient leadership",
            "Empathy under pressure",
            "Protective of team",
            "Results focus",
        ],
        "watch_for": "Friction in one area can spill into leadership decisions.",
        "growth_edge": "Separate the frustrated need from your leadership role. Address it on its own terms.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "developing"},
    },
    "Resolute Captain": {
        "tagline": "Leading through people despite multiple pressures",
        "description": (
            "Ambition and belonging are activated with multiple frustrated "
            "domains. This person maintains leadership and connection under "
            "significant strain. The commitment is real; so is the cost."
        ),
        "strengths": [
            "Fierce commitment",
            "Team loyalty under fire",
            "Inspirational persistence",
            "Emotional courage",
        ],
        "watch_for": "Multiple friction sources create compounding fatigue. Pace matters.",
        "growth_edge": "Accept help from the team you lead. Reciprocity sustains what willpower cannot.",
        "pattern": {"ambition": "strong", "belonging": "strong", "craft": "developing"},
    },
    # === ARCHITECT (A↑ B↓ C↑) ===
    "Steady Architect": {
        "tagline": "Building with ambition and skill",
        "description": (
            "Ambition and craft are both activated with no frustrated domain. "
            "This person builds strategically — combining drive with technical "
            "depth. Belonging is the developing frontier."
        ),
        "strengths": [
            "Strategic execution",
            "Technical vision",
            "Quality output",
            "Focused delivery",
        ],
        "watch_for": "May undervalue relationships or move too fast for consensus.",
        "growth_edge": "Bring one collaborator into your next project early.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "strong"},
    },
    "Striving Architect": {
        "tagline": "Building under one source of friction",
        "description": (
            "Ambition and craft are activated but one domain carries "
            "frustration. The strategic-technical combination is strong — "
            "the friction is targeted, not pervasive."
        ),
        "strengths": [
            "High standards under pressure",
            "Relentless delivery",
            "Technical rigour",
            "Self-driven",
        ],
        "watch_for": "Perfectionism under strain becomes paralysis.",
        "growth_edge": "Set a definition of done before starting. Standards should guide, not trap.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "strong"},
    },
    "Resolute Architect": {
        "tagline": "Building through multiple headwinds",
        "description": (
            "Ambition and craft are activated with multiple frustrated domains. "
            "Quality and drive persist despite significant opposition. This is "
            "tenacity applied to meaningful work."
        ),
        "strengths": [
            "Tenacity",
            "Resourcefulness",
            "Problem-solving under constraint",
            "Refusal to settle",
        ],
        "watch_for": "Persistent frustration without wins erodes even the strongest resolve.",
        "growth_edge": "Find one small win this week. Momentum is medicine for blocked ambition.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "strong"},
    },
    # === MENTOR (A↓ B↑ C↑) ===
    "Steady Mentor": {
        "tagline": "Growing others through expertise",
        "description": (
            "Belonging and craft are both activated with no frustrated domain. "
            "This person shares knowledge generously and builds others up through "
            "competence. Ambition is the developing frontier."
        ),
        "strengths": ["Teaching", "Knowledge sharing", "Patient guidance", "Trust-building"],
        "watch_for": "May avoid competitive settings that feel personally exposing.",
        "growth_edge": "Share your work with a wider audience. Expertise scales when visible.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "strong"},
    },
    "Striving Mentor": {
        "tagline": "Teaching through one source of tension",
        "description": (
            "Belonging and craft are activated but one domain carries "
            "frustration. The instinct to develop others through expertise "
            "remains strong despite the friction."
        ),
        "strengths": [
            "Resilient empathy",
            "Honest feedback",
            "Commitment to development",
            "Emotional stamina",
        ],
        "watch_for": "Giving too much to others while running on empty yourself.",
        "growth_edge": "Accept help from someone you've helped. Reciprocity is not weakness.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "strong"},
    },
    "Resolute Mentor": {
        "tagline": "Guiding others through shared struggle",
        "description": (
            "Belonging and craft are activated with multiple frustrated domains. "
            "This person persists in supporting others despite significant "
            "personal strain. The mentoring draws from hard-won experience."
        ),
        "strengths": [
            "Hard-won wisdom",
            "Authentic vulnerability",
            "Solidarity",
            "Teaching through experience",
        ],
        "watch_for": "Mentoring from a place of pain can blur boundaries.",
        "growth_edge": "Find a mentor for yourself. Even guides need guides.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "strong"},
    },
    # === PIONEER (A↑ B↓ C↓) ===
    "Steady Pioneer": {
        "tagline": "Ambition leading the way",
        "description": (
            "Ambition is the activated need with no frustrated domain. Drive "
            "and goal pursuit are strong; belonging and craft are developing. "
            "This person knows where they want to go."
        ),
        "strengths": ["Goal clarity", "Initiative", "Competitive edge", "Decisive action"],
        "watch_for": "Two developing domains leave a narrow motivational base.",
        "growth_edge": "Invest in one relationship or skill that supports your ambition.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "developing"},
    },
    "Striving Pioneer": {
        "tagline": "Ambition driving through friction",
        "description": (
            "Ambition is activated but one domain carries frustration. The "
            "drive is clear; the friction adds urgency. Two developing domains "
            "mean the growth opportunity is wide."
        ),
        "strengths": ["Urgency", "Risk tolerance", "Forward momentum", "Adaptability"],
        "watch_for": "Narrow activation plus friction creates intensity that others may find hard to match.",
        "growth_edge": "Slow down enough to bring someone along. Shared ambition travels further.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "developing"},
    },
    "Resolute Pioneer": {
        "tagline": "Ambition persisting through adversity",
        "description": (
            "Ambition is activated with multiple frustrated domains. This person "
            "pursues goals despite headwinds on multiple fronts. The persistence "
            "is remarkable; the strain is real."
        ),
        "strengths": [
            "Extraordinary persistence",
            "Anti-fragility",
            "Refusal to quit",
            "Self-reliance",
        ],
        "watch_for": "Grit without support is a finite resource.",
        "growth_edge": "Address the closest frustrated domain first. One less headwind changes everything.",
        "pattern": {"ambition": "strong", "belonging": "developing", "craft": "developing"},
    },
    # === ANCHOR (A↓ B↑ C↓) ===
    "Steady Anchor": {
        "tagline": "Belonging grounding everything",
        "description": (
            "Belonging is the activated need with no frustrated domain. "
            "Connection and relationships are strong; ambition and craft are "
            "developing. This person provides stability for others."
        ),
        "strengths": ["Relational stability", "Trust", "Empathy", "Team cohesion"],
        "watch_for": "Two developing domains mean personal growth may stall without intentional effort.",
        "growth_edge": "Use your relational strength to learn from someone you admire.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "developing"},
    },
    "Striving Anchor": {
        "tagline": "Belonging holding through friction",
        "description": (
            "Belonging is activated but one domain carries frustration. "
            "Connection remains strong despite the tension. The relational "
            "base provides resilience."
        ),
        "strengths": [
            "Emotional courage",
            "Loyalty under pressure",
            "Relational repair",
            "Supportiveness",
        ],
        "watch_for": "Absorbing others' stress while carrying your own friction.",
        "growth_edge": "Set one boundary this week. Belonging is stronger with limits.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "developing"},
    },
    "Resolute Anchor": {
        "tagline": "Belonging persisting through adversity",
        "description": (
            "Belonging is activated with multiple frustrated domains. This "
            "person maintains connection despite significant personal strain. "
            "The commitment to others is deep; the cost is high."
        ),
        "strengths": [
            "Moral courage",
            "Unbreakable commitment",
            "Principled loyalty",
            "Emotional endurance",
        ],
        "watch_for": "Fighting for belonging while multiple needs go unmet drains faster than any other pattern.",
        "growth_edge": "Seek one new connection outside the current context. Fresh soil grows new roots.",
        "pattern": {"ambition": "developing", "belonging": "strong", "craft": "developing"},
    },
    # === ARTISAN (A↓ B↓ C↑) ===
    "Steady Artisan": {
        "tagline": "Craft leading quietly",
        "description": (
            "Craft is the activated need with no frustrated domain. Technical "
            "depth and quality drive this person; ambition and belonging are "
            "developing. Mastery is the foundation."
        ),
        "strengths": [
            "Deep expertise",
            "Quality focus",
            "Independent mastery",
            "Patience with complexity",
        ],
        "watch_for": "Two developing domains may lead to isolation or missed opportunities.",
        "growth_edge": "Share one thing you've mastered. Teaching builds belonging from craft.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "strong"},
    },
    "Striving Artisan": {
        "tagline": "Craft deepening through friction",
        "description": (
            "Craft is activated but one domain carries frustration. The "
            "commitment to quality and mastery persists alongside the friction. "
            "The developing domains offer growth space."
        ),
        "strengths": [
            "Creative problem-solving",
            "Learning under pressure",
            "Unconventional methods",
            "Focus",
        ],
        "watch_for": "Friction plus narrow activation can feel isolating.",
        "growth_edge": "Find one collaborator who values what you build.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "strong"},
    },
    "Resolute Artisan": {
        "tagline": "Craft persisting despite the odds",
        "description": (
            "Craft is activated with multiple frustrated domains. This person "
            "creates and masters despite headwinds on multiple fronts. The "
            "work itself is the anchor."
        ),
        "strengths": [
            "Stubborn creativity",
            "Anti-fragility",
            "Resourcefulness",
            "Craft as refuge",
        ],
        "watch_for": "Using craft to avoid addressing frustrated needs.",
        "growth_edge": "Let the work bring you to people. Craft opens doors that ambition cannot.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "strong"},
    },
    # === SEEKER (A↓ B↓ C↓) ===
    "Steady Seeker": {
        "tagline": "Exploring without friction",
        "description": (
            "No domain is fully activated but none is frustrated either. This "
            "person is in an open, exploratory phase — unattached to any "
            "particular need. The canvas is blank."
        ),
        "strengths": ["Openness", "Low attachment", "Fresh perspective", "Ready to commit"],
        "watch_for": "Prolonged seeking without activation leads to drift.",
        "growth_edge": "Pick one domain and invest deliberately. Commitment creates momentum.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "developing"},
    },
    "Striving Seeker": {
        "tagline": "Searching with one edge of urgency",
        "description": (
            "No domain is fully activated but one carries frustration. "
            "The friction in one area creates urgency to find direction. "
            "The frustrated domain may point toward the most important need."
        ),
        "strengths": [
            "Self-awareness",
            "Urgency to grow",
            "Willingness to change",
            "Emotional honesty",
        ],
        "watch_for": "The frustration may be a compass — pointing toward what matters most.",
        "growth_edge": "Follow the friction. The domain that hurts may be the one that matters.",
        "pattern": {"ambition": "developing", "belonging": "developing", "craft": "developing"},
    },
    "Resolute Seeker": {
        "tagline": "Persevering through the fog",
        "description": (
            "No domain is fully activated and multiple carry frustration. "
            "This is the most challenging profile — low satisfaction and high "
            "friction across the board. But the person is still here."
        ),
        "strengths": [
            "Survival instinct",
            "Raw determination",
            "Nothing left to lose",
            "Capacity for transformation",
        ],
        "watch_for": "This profile requires immediate support. The risk of disengagement is highest here.",
        "growth_edge": "Start with the smallest possible win in any domain. One spark changes everything.",
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
