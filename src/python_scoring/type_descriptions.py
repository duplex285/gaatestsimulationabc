"""Type and state descriptions for the ABC Assessment.

Reference: abc-assessment-spec Section 2.2 (domain states)
Reference: abc-assessment-spec Section 2.4 (36-type derivation)

The 36-type system classifies each person by:
  1. Dominant domain (Ambition, Belonging, Craft)
  2. Primary Big Five trait direction (High/Low x 5 traits)
  3 x 10 = 30 trait-based types + Integrator = 31 unique types

Type names are defined here as the single source of truth. To rename
a type, change it in TYPE_DESCRIPTIONS and in type_derivation.TYPE_MAP.

Theoretical foundations:
  - Self-Determination Theory (Deci & Ryan, 2000): autonomy, relatedness,
    competence as basic psychological needs
  - ABC mapping: Ambition ≈ autonomy, Belonging ≈ relatedness, Craft ≈ competence
  - Big Five personality traits (Costa & McCrae, 1992)
  - Frustration as distinct from low satisfaction (Vansteenkiste & Ryan, 2013)
"""

# ---------------------------------------------------------------------------
# Domain State Descriptions
# ---------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 2.2
#
# The four states arise from crossing satisfaction (high/low) with frustration
# (high/low) at the 5.5 threshold on the 0-10 scale. This dual-continuum
# model follows Vansteenkiste & Ryan (2013), who demonstrated that need
# frustration is not simply the absence of need satisfaction — it is a
# distinct psychological experience with independent effects on wellbeing.

DOMAIN_STATE_DESCRIPTIONS = {
    "Thriving": {
        "label": "Thriving",
        "condition": "Satisfaction >= 5.5, Frustration < 5.5",
        "summary": "This need is being actively met with minimal obstruction.",
        "science": (
            "Self-Determination Theory predicts that when a basic psychological "
            "need is satisfied without significant frustration, people experience "
            "vitality, intrinsic motivation, and psychological growth (Deci & Ryan, "
            "2000). The absence of frustration distinguishes genuine thriving from "
            "the brittle high performance seen in the Vulnerable state. Longitudinal "
            "research shows that sustained need satisfaction predicts lower burnout, "
            "higher engagement, and greater persistence (Lonsdale & Hodge, 2011)."
        ),
        "implication": (
            "No intervention needed. Protect the conditions enabling this state. "
            "Monitor for early signs of rising frustration that could shift the "
            "person toward Vulnerable."
        ),
        "colour": "#3ABF5E",
    },
    "Vulnerable": {
        "label": "Vulnerable",
        "condition": "Satisfaction >= 5.5, Frustration >= 5.5",
        "summary": "This need is being met, but at a cost. High frustration signals strain.",
        "science": (
            "Vansteenkiste & Ryan (2013) showed that need frustration has "
            "independent negative effects on wellbeing even when need satisfaction "
            "is high. This is the 'successful but suffering' pattern: a person "
            "achieves outcomes but experiences controlling pressures, conditional "
            "approval, or excessive self-criticism along the way. The coexistence "
            "of high satisfaction and high frustration creates psychological "
            "tension that is unsustainable. Without intervention, the typical "
            "trajectory is toward Distressed as frustration erodes satisfaction."
        ),
        "implication": (
            "Highest priority for intervention. The person is still engaged — "
            "the window to act is now. Identify the source of frustration: "
            "external pressure, interpersonal conflict, or self-imposed standards."
        ),
        "colour": "#F5A623",
    },
    "Dormant": {
        "label": "Dormant",
        "condition": "Satisfaction < 5.5, Frustration < 5.5",
        "summary": "This need is neither fulfilled nor actively blocked. It sits idle.",
        "science": (
            "Low satisfaction without frustration suggests the need is not being "
            "engaged rather than being thwarted. In SDT terms, this resembles "
            "amotivation — the person neither pursues nor is blocked from pursuing "
            "this need (Deci & Ryan, 2000). Dormancy is not inherently harmful in "
            "the short term; people naturally prioritise different needs at different "
            "times. However, prolonged dormancy in a core need predicts gradual "
            "disengagement and reduced wellbeing (Bartholomew et al., 2011)."
        ),
        "implication": (
            "Lower urgency than Vulnerable or Distressed. Explore whether the "
            "person's environment offers opportunities to engage this need. "
            "Dormancy in Belonging, for example, may reflect isolation rather "
            "than contentment."
        ),
        "colour": "#A0A0A0",
    },
    "Distressed": {
        "label": "Distressed",
        "condition": "Satisfaction < 5.5, Frustration >= 5.5",
        "summary": "This need is unmet and actively blocked. The person is struggling.",
        "science": (
            "The combination of low satisfaction and high frustration represents "
            "need thwarting — the most psychologically damaging state in SDT "
            "(Bartholomew et al., 2011). The person is not merely missing "
            "fulfilment; they experience active obstruction of a basic need. "
            "Research links sustained need thwarting to burnout, depressive "
            "symptoms, ill-being, and dropout (Lonsdale & Hodge, 2011). Unlike "
            "Dormancy, Distress involves active suffering and tends to be "
            "self-reinforcing: frustration undermines the motivation needed "
            "to seek satisfaction."
        ),
        "implication": (
            "Urgent intervention. The self-reinforcing nature of this state "
            "means delay makes recovery harder. Address the frustration source "
            "first — removing blockers is more effective than adding positive "
            "experiences when a person is actively thwarted."
        ),
        "colour": "#E8563A",
    },
}

# ---------------------------------------------------------------------------
# 36-Type Descriptions
# ---------------------------------------------------------------------------
# Each type is the intersection of a dominant domain and a primary Big Five
# trait direction. The description explains WHY this combination produces
# distinctive behaviour, grounded in what the domain and trait each contribute.
#
# Structure per type:
#   tagline     - one phrase that captures the essence
#   description - 2-3 sentences explaining the pattern
#   strengths   - what this person brings at their best
#   watch_for   - where this pattern can become a liability
#   growth_edge - development focus
#   domain      - primary domain (ambition / belonging / craft)
#   trait       - primary Big Five trait and direction

TYPE_DESCRIPTIONS = {
    # === AMBITION DOMAIN ===
    "Visionary": {
        "tagline": "Sees the path others haven't imagined yet",
        "description": (
            "Driven by ambition and high openness, the Visionary pursues goals that "
            "challenge convention. They are energised by possibility and draw motivation "
            "from reimagining what success looks like rather than following established routes."
        ),
        "strengths": ["Strategic imagination", "Comfort with ambiguity", "Inspires new directions"],
        "watch_for": "May chase novelty at the expense of execution. Ideas outpace follow-through.",
        "growth_edge": "Pair vision with structure — partner with implementers or build personal systems for finishing.",
        "domain": "ambition",
        "trait": "High Openness",
    },
    "Traditionalist": {
        "tagline": "Builds ambition on proven ground",
        "description": (
            "Ambition-dominant with low openness, the Traditionalist pursues goals through "
            "established methods. They find motivation in mastering known frameworks rather "
            "than inventing new ones, and bring reliability to ambitious endeavours."
        ),
        "strengths": ["Consistent execution", "Institutional knowledge", "Risk-aware planning"],
        "watch_for": "May resist necessary change or dismiss unconventional approaches too quickly.",
        "growth_edge": "Experiment with one unfamiliar method per quarter. Discomfort is data, not danger.",
        "domain": "ambition",
        "trait": "Low Openness",
    },
    "Achiever": {
        "tagline": "Turns ambition into disciplined results",
        "description": (
            "High ambition combined with high conscientiousness produces someone who sets "
            "clear goals and methodically works toward them. The Achiever thrives on measurable "
            "progress and takes deep satisfaction in completing what they start."
        ),
        "strengths": ["Goal execution", "Self-discipline", "Dependable output under pressure"],
        "watch_for": "May over-index on productivity and neglect relationships or creative exploration.",
        "growth_edge": "Define success beyond output. Practice unstructured time without guilt.",
        "domain": "ambition",
        "trait": "High Conscientiousness",
    },
    "Improviser": {
        "tagline": "Pursues ambition through agility, not plans",
        "description": (
            "Ambition-driven but low in conscientiousness, the Improviser adapts quickly and "
            "thrives in dynamic environments. They advance toward goals by seizing opportunities "
            "rather than following predetermined plans."
        ),
        "strengths": ["Rapid adaptation", "Opportunistic problem-solving", "Thrives in chaos"],
        "watch_for": "May struggle with long-term projects that require sustained, systematic effort.",
        "growth_edge": "Build one reliable routine. Consistency in small things frees energy for big ones.",
        "domain": "ambition",
        "trait": "Low Conscientiousness",
    },
    "Catalyst": {
        "tagline": "Rallies others around ambitious goals",
        "description": (
            "High ambition meets high extraversion. The Catalyst advances their goals by "
            "energising the people around them. They are natural mobilisers who create momentum "
            "through enthusiasm and social influence."
        ),
        "strengths": ["Team energiser", "Persuasive communication", "Creates urgency and buy-in"],
        "watch_for": "May dominate airtime or push pace beyond what others can sustain.",
        "growth_edge": "Listen longer before rallying. The best catalyst knows when not to react.",
        "domain": "ambition",
        "trait": "High Extraversion",
    },
    "Strategist": {
        "tagline": "Advances ambition through quiet calculation",
        "description": (
            "Ambition-dominant with low extraversion, the Strategist works behind the scenes. "
            "They think several moves ahead and prefer influence through positioning rather "
            "than persuasion."
        ),
        "strengths": [
            "Long-range planning",
            "Independent judgement",
            "Calm under political pressure",
        ],
        "watch_for": "May withhold ideas that need to be heard, or be overlooked despite strong contributions.",
        "growth_edge": "Share thinking earlier and more often. Visibility is not vanity — it's leverage.",
        "domain": "ambition",
        "trait": "Low Extraversion",
    },
    "Champion": {
        "tagline": "Pursues goals that serve others",
        "description": (
            "High ambition paired with high agreeableness. The Champion channels drive toward "
            "collective benefit. They advocate fiercely for shared causes and find personal "
            "meaning in advancing others alongside themselves."
        ),
        "strengths": ["Advocate for others", "Builds coalitions", "Trusted with authority"],
        "watch_for": "May sacrifice personal needs to maintain harmony or avoid appearing selfish.",
        "growth_edge": "Pursue something purely for yourself. Self-interest is not selfishness.",
        "domain": "ambition",
        "trait": "High Agreeableness",
    },
    "Challenger": {
        "tagline": "Competes to win, not to please",
        "description": (
            "Ambition-driven with low agreeableness, the Challenger is direct, competitive, "
            "and unafraid of friction. They push hard for results and hold others to high "
            "standards without worrying about being liked."
        ),
        "strengths": ["Direct feedback", "Competitive drive", "Holds high standards"],
        "watch_for": "May create unnecessary conflict or alienate potential allies.",
        "growth_edge": "Distinguish between challenging ideas and challenging people. The best opponents build respect.",
        "domain": "ambition",
        "trait": "Low Agreeableness",
    },
    "Striver": {
        "tagline": "Driven by ambition, fuelled by pressure",
        "description": (
            "High ambition combined with high neuroticism. The Striver is intensely motivated "
            "but carries anxiety about falling short. Their emotional sensitivity to failure "
            "creates urgency that often produces remarkable output — at a personal cost."
        ),
        "strengths": ["High effort under pressure", "Anticipates problems", "Never complacent"],
        "watch_for": "Burnout risk is high. The internal pressure that drives performance also erodes recovery.",
        "growth_edge": "Separate effort from worth. Rest is not failure — it is maintenance.",
        "domain": "ambition",
        "trait": "High Neuroticism",
    },
    "Steady Hand": {
        "tagline": "Ambitious without the anxiety",
        "description": (
            "Ambition-dominant with low neuroticism, the Steady Hand pursues goals with "
            "emotional stability. They maintain composure during setbacks and rarely let "
            "pressure distort their judgement."
        ),
        "strengths": [
            "Calm under pressure",
            "Consistent performance",
            "Reassures others in uncertainty",
        ],
        "watch_for": "May appear disengaged or indifferent when calm is mistaken for apathy.",
        "growth_edge": "Show investment visibly. Others need to see that you care, not just that you cope.",
        "domain": "ambition",
        "trait": "Low Neuroticism",
    },
    # === BELONGING DOMAIN ===
    "Bridge Builder": {
        "tagline": "Connects different worlds through relationships",
        "description": (
            "Belonging-dominant with high openness, the Bridge Builder forms connections across "
            "diverse groups. They are drawn to people unlike themselves and create understanding "
            "between communities that would otherwise stay separate."
        ),
        "strengths": [
            "Cross-boundary relationships",
            "Cultural fluency",
            "Creates unexpected alliances",
        ],
        "watch_for": "May spread too thin across groups without deepening any single relationship.",
        "growth_edge": "Invest deeply in a few relationships, not broadly in many. Depth builds trust.",
        "domain": "belonging",
        "trait": "High Openness",
    },
    "Guardian": {
        "tagline": "Protects the bonds that matter most",
        "description": (
            "Belonging-focused with low openness, the Guardian values loyalty, tradition, and "
            "the preservation of established relationships. They create safety by maintaining "
            "norms and defending group cohesion."
        ),
        "strengths": ["Loyalty", "Group stability", "Protects team culture"],
        "watch_for": "May resist newcomers or new ideas that threaten familiar dynamics.",
        "growth_edge": "Welcome one outsider perspective per cycle. New voices strengthen what you protect.",
        "domain": "belonging",
        "trait": "Low Openness",
    },
    "Anchor": {
        "tagline": "The reliable centre that holds relationships together",
        "description": (
            "High belonging with high conscientiousness. The Anchor shows care through "
            "consistent follow-through — remembering commitments, showing up reliably, and "
            "holding the group to its shared agreements."
        ),
        "strengths": [
            "Reliable presence",
            "Follow-through on commitments",
            "Maintains group structure",
        ],
        "watch_for": "May become rigid about norms or resentful when others don't match their reliability.",
        "growth_edge": "Flexibility is not unreliability. Sometimes the most caring thing is to bend.",
        "domain": "belonging",
        "trait": "High Conscientiousness",
    },
    "Free Spirit": {
        "tagline": "Belongs on their own terms",
        "description": (
            "Belonging-dominant but low in conscientiousness, the Free Spirit values connection "
            "without constraint. They resist rigid social structures and thrive in relationships "
            "that allow spontaneity and individual expression."
        ),
        "strengths": ["Authentic presence", "Social spontaneity", "Makes groups feel alive"],
        "watch_for": "May frustrate others by being unreliable or dismissing group commitments.",
        "growth_edge": "Honour one small promise consistently. Freedom and reliability are not enemies.",
        "domain": "belonging",
        "trait": "Low Conscientiousness",
    },
    "Connector": {
        "tagline": "Builds and energises social networks",
        "description": (
            "High belonging meets high extraversion. The Connector actively builds and maintains "
            "wide social networks. They draw energy from bringing people together and are often "
            "the first person others turn to for introductions."
        ),
        "strengths": [
            "Network building",
            "Social energy",
            "Creates introductions and opportunities",
        ],
        "watch_for": "May prioritise breadth over depth, or exhaust themselves maintaining too many ties.",
        "growth_edge": "Nurture silence in relationships. Not every connection needs active maintenance.",
        "domain": "belonging",
        "trait": "High Extraversion",
    },
    "Observer": {
        "tagline": "Understands the group by watching, not performing",
        "description": (
            "Belonging-focused with low extraversion, the Observer contributes to relationships "
            "through attentive listening and careful reading of social dynamics. They notice what "
            "others miss and offer insight at critical moments."
        ),
        "strengths": ["Social perception", "Thoughtful responses", "Detects unspoken tension"],
        "watch_for": "May withdraw too far and become invisible to the group they care about.",
        "growth_edge": "Voice one observation per meeting. The group needs what you see.",
        "domain": "belonging",
        "trait": "Low Extraversion",
    },
    "Mentor": {
        "tagline": "Invests in others' growth through relationship",
        "description": (
            "High belonging paired with high agreeableness. The Mentor finds deep fulfilment in "
            "supporting others' development. They create psychologically safe spaces where people "
            "feel comfortable being vulnerable and asking for help."
        ),
        "strengths": ["Psychological safety", "Develops others", "Patient guidance"],
        "watch_for": "May neglect their own needs or avoid giving hard feedback to preserve the relationship.",
        "growth_edge": "Caring sometimes means being uncomfortable. The kindest feedback is honest feedback.",
        "domain": "belonging",
        "trait": "High Agreeableness",
    },
    "Truth Teller": {
        "tagline": "Values honesty over harmony",
        "description": (
            "Belonging-dominant with low agreeableness, the Truth Teller is loyal but blunt. "
            "They show care by speaking directly rather than softening messages, believing that "
            "real relationships survive hard truths."
        ),
        "strengths": ["Radical honesty", "Cuts through groupthink", "Trusted for candour"],
        "watch_for": "May damage relationships by mistiming or over-delivering difficult feedback.",
        "growth_edge": "Soften the delivery, not the message. Truth lands better when the listener feels safe.",
        "domain": "belonging",
        "trait": "Low Agreeableness",
    },
    "Empath": {
        "tagline": "Feels the room before anyone speaks",
        "description": (
            "High belonging combined with high neuroticism. The Empath has heightened emotional "
            "sensitivity that makes them acutely attuned to others' feelings. They detect "
            "distress early and respond with genuine compassion."
        ),
        "strengths": ["Emotional attunement", "Early conflict detection", "Compassionate response"],
        "watch_for": "May absorb others' emotions to the point of personal depletion. Boundaries blur.",
        "growth_edge": "Distinguish between feeling for someone and feeling as someone. Empathy needs a boundary.",
        "domain": "belonging",
        "trait": "High Neuroticism",
    },
    "Rock": {
        "tagline": "Steady, present, unshakeable in relationships",
        "description": (
            "Belonging-focused with low neuroticism. The Rock provides emotional stability "
            "to the people around them. They remain calm during interpersonal crises and offer "
            "a grounding presence that others rely on."
        ),
        "strengths": ["Emotional stability", "Calming presence", "Reliable in crisis"],
        "watch_for": "May be so steady that others never learn to regulate their own emotions.",
        "growth_edge": "Show vulnerability occasionally. Strength includes letting others support you.",
        "domain": "belonging",
        "trait": "Low Neuroticism",
    },
    # === CRAFT DOMAIN ===
    "Explorer": {
        "tagline": "Learns by wandering into the unknown",
        "description": (
            "Craft-dominant with high openness, the Explorer develops skill by pursuing "
            "curiosity rather than curriculum. They are drawn to novel problems and unfamiliar "
            "tools, and they grow fastest when the territory is uncharted."
        ),
        "strengths": [
            "Creative problem-solving",
            "Rapid skill acquisition",
            "Comfortable with the unknown",
        ],
        "watch_for": "May abandon skill development before reaching mastery, always chasing the next thing.",
        "growth_edge": "Go deep on one skill before moving on. Mastery requires the discipline to stay.",
        "domain": "craft",
        "trait": "High Openness",
    },
    "Specialist": {
        "tagline": "Goes deeper than anyone else in a single domain",
        "description": (
            "Craft-focused with low openness, the Specialist builds expertise through narrow, "
            "sustained focus. They prefer depth over breadth and take pride in knowing their "
            "subject more thoroughly than anyone around them."
        ),
        "strengths": ["Deep expertise", "Technical authority", "Trusted for precision"],
        "watch_for": "May resist learning adjacent skills or dismiss approaches outside their specialty.",
        "growth_edge": "Explore one adjacent field. Depth gains power when it connects to breadth.",
        "domain": "craft",
        "trait": "Low Openness",
    },
    "Forge": {
        "tagline": "Shapes raw skill into refined output through discipline",
        "description": (
            "High craft satisfaction paired with high conscientiousness. The Forge treats skill "
            "development as a systematic practice. They set standards, track progress, and "
            "produce consistently high-quality work through rigorous self-management."
        ),
        "strengths": ["Quality standards", "Systematic improvement", "Reliable craftsmanship"],
        "watch_for": "May become inflexible about process or resistant to feedback that disrupts their system.",
        "growth_edge": "Let the work be messy in early stages. Premature polish kills experimentation.",
        "domain": "craft",
        "trait": "High Conscientiousness",
    },
    "Tinkerer": {
        "tagline": "Learns by taking things apart",
        "description": (
            "Craft-dominant but low in conscientiousness, the Tinkerer develops skills through "
            "unstructured experimentation. They learn by doing, breaking, and rebuilding — "
            "often producing novel solutions that structured approaches would miss."
        ),
        "strengths": [
            "Experimental learning",
            "Unconventional solutions",
            "Comfortable with failure",
        ],
        "watch_for": "May produce inconsistent output or struggle to document and reproduce their best work.",
        "growth_edge": "Write down what works. Your experiments have more value when others can learn from them.",
        "domain": "craft",
        "trait": "Low Conscientiousness",
    },
    "Performer": {
        "tagline": "Brings skill to life in front of an audience",
        "description": (
            "High craft satisfaction combined with high extraversion. The Performer develops "
            "skill partly through public practice — teaching, presenting, demonstrating. They "
            "refine their craft by explaining it to others and thrive when their work is visible."
        ),
        "strengths": [
            "Teaching through demonstration",
            "Engaging presentations",
            "Makes expertise accessible",
        ],
        "watch_for": "May optimise for audience reaction rather than genuine quality improvement.",
        "growth_edge": "Practice in private sometimes. Not all growth needs an audience.",
        "domain": "craft",
        "trait": "High Extraversion",
    },
    "Flow State": {
        "tagline": "Does their best work in deep solitude",
        "description": (
            "Craft-focused with low extraversion. Flow State enters deep concentration more "
            "easily than most people and produces their best work during uninterrupted solo "
            "sessions. They experience skill development as an intrinsically rewarding, "
            "private practice."
        ),
        "strengths": ["Deep focus", "Sustained concentration", "High-quality solo output"],
        "watch_for": "May resist collaboration or become invisible to the team during deep work periods.",
        "growth_edge": "Share work-in-progress, not just finished products. Collaboration sharpens craft.",
        "domain": "craft",
        "trait": "Low Extraversion",
    },
    "Collaborator": {
        "tagline": "Builds skill through partnership",
        "description": (
            "High craft satisfaction paired with high agreeableness. The Collaborator grows "
            "through shared work — pair programming, co-authoring, joint problem-solving. "
            "They elevate both their own skills and their partners' through generous exchange."
        ),
        "strengths": ["Pair work", "Knowledge sharing", "Elevates team capability"],
        "watch_for": "May depend on others to drive direction or avoid independent technical decisions.",
        "growth_edge": "Take a solo project to completion. Prove to yourself you can build alone.",
        "domain": "craft",
        "trait": "High Agreeableness",
    },
    "Lone Wolf": {
        "tagline": "Masters craft through independent work",
        "description": (
            "Craft-dominant with low agreeableness. The Lone Wolf develops skill independently "
            "and trusts their own judgement over group consensus. They produce distinctive work "
            "because they are willing to disagree with conventional approaches."
        ),
        "strengths": [
            "Independent judgement",
            "Original solutions",
            "Uncompromising quality standards",
        ],
        "watch_for": "May reject valid feedback or create knowledge silos that hurt the team.",
        "growth_edge": "Invite one reviewer before shipping. Independence is not infallibility.",
        "domain": "craft",
        "trait": "Low Agreeableness",
    },
    "Perfectionist": {
        "tagline": "Driven to mastery by the fear of falling short",
        "description": (
            "High craft satisfaction combined with high neuroticism. The Perfectionist produces "
            "exceptional work because their internal standards are relentlessly high. Their "
            "anxiety about inadequacy pushes them to refine and polish beyond what others "
            "would consider sufficient."
        ),
        "strengths": ["Exceptional attention to detail", "High quality output", "Self-correcting"],
        "watch_for": "May delay shipping indefinitely, paralysed by the gap between output and ideal.",
        "growth_edge": "Define 'good enough' before starting. Perfection is the enemy of completion.",
        "domain": "craft",
        "trait": "High Neuroticism",
    },
    "Craftsman": {
        "tagline": "Quietly excellent, unbothered by the noise",
        "description": (
            "Craft-focused with low neuroticism. The Craftsman builds skill with patience and "
            "emotional steadiness. They handle setbacks in their work without spiralling and "
            "maintain consistent quality because their mood does not fluctuate with results."
        ),
        "strengths": ["Consistent quality", "Resilient to setbacks", "Patient skill development"],
        "watch_for": "May lack urgency or appear indifferent to deadlines and external standards.",
        "growth_edge": "Channel calm into speed occasionally. Some situations reward urgency over patience.",
        "domain": "craft",
        "trait": "Low Neuroticism",
    },
    # === CROSS-DOMAIN ===
    "Integrator": {
        "tagline": "Balanced across all needs, no single drive dominates",
        "description": (
            "The Integrator has no single dominant domain or extreme personality trait. They "
            "distribute energy evenly across ambition, belonging, and craft. This balance "
            "makes them adaptable generalists who move fluidly between roles."
        ),
        "strengths": ["Versatility", "Balanced perspective", "Bridges specialised team members"],
        "watch_for": "May lack the intensity needed to break through in any single area.",
        "growth_edge": "Identify which need matters most right now. Temporary focus sharpens general skill.",
        "domain": "any",
        "trait": "Balanced",
    },
}


def get_type_description(type_name: str) -> dict | None:
    """Look up a type description by name.

    Reference: abc-assessment-spec Section 2.4

    Returns dict with tagline, description, strengths, watch_for,
    growth_edge, domain, trait. Returns None if type_name not found.
    """
    return TYPE_DESCRIPTIONS.get(type_name)


def get_state_description(state: str) -> dict | None:
    """Look up a domain state description by name.

    Reference: abc-assessment-spec Section 2.2

    Returns dict with label, condition, summary, science, implication,
    colour. Returns None if state not found.
    """
    return DOMAIN_STATE_DESCRIPTIONS.get(state)
