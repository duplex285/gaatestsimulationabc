"""36-type derivation for ABC Assessment.

Reference: abc-assessment-spec Section 2.4

Steps:
1. Dominant domain = argmax(A-sat, B-sat, C-sat)
2. Primary Big Five trait = trait with largest |percentile - 50|
3. Direction = High if percentile >= 50, Low otherwise
4. Type = typeMap[domain][direction + trait]
"""

# Type map: domain -> (direction + trait) -> type name
# Reference: abc-assessment-spec Section 2.4
# These names come from the 36-type catalog in abc-typology.ts
TYPE_MAP = {
    "ambition": {
        "HighOpenness": "Visionary",
        "LowOpenness": "Traditionalist",
        "HighConscientiousness": "Achiever",
        "LowConscientiousness": "Improviser",
        "HighExtraversion": "Catalyst",
        "LowExtraversion": "Strategist",
        "HighAgreeableness": "Champion",
        "LowAgreeableness": "Challenger",
        "HighNeuroticism": "Striver",
        "LowNeuroticism": "Steady Hand",
        "HighIntegrator": "Integrator",
        "LowIntegrator": "Integrator",
    },
    "belonging": {
        "HighOpenness": "Bridge Builder",
        "LowOpenness": "Guardian",
        "HighConscientiousness": "Anchor",
        "LowConscientiousness": "Free Spirit",
        "HighExtraversion": "Connector",
        "LowExtraversion": "Observer",
        "HighAgreeableness": "Mentor",
        "LowAgreeableness": "Truth Teller",
        "HighNeuroticism": "Empath",
        "LowNeuroticism": "Rock",
        "HighIntegrator": "Integrator",
        "LowIntegrator": "Integrator",
    },
    "craft": {
        "HighOpenness": "Explorer",
        "LowOpenness": "Specialist",
        "HighConscientiousness": "Forge",
        "LowConscientiousness": "Tinkerer",
        "HighExtraversion": "Performer",
        "LowExtraversion": "Flow State",
        "HighAgreeableness": "Collaborator",
        "LowAgreeableness": "Lone Wolf",
        "HighNeuroticism": "Perfectionist",
        "LowNeuroticism": "Craftsman",
        "HighIntegrator": "Integrator",
        "LowIntegrator": "Integrator",
    },
}

DOMAIN_SAT_KEYS = {
    "ambition": "a_sat",
    "belonging": "b_sat",
    "craft": "c_sat",
}

TRAIT_NAMES = [
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
]


def get_dominant_domain(subscales: dict[str, float]) -> str:
    """Determine dominant domain: argmax of satisfaction scores.

    Reference: abc-assessment-spec Section 2.4
    Ties broken by domain order: ambition > belonging > craft.
    """
    domains = [
        ("ambition", subscales["a_sat"]),
        ("belonging", subscales["b_sat"]),
        ("craft", subscales["c_sat"]),
    ]
    return max(domains, key=lambda x: x[1])[0]


def get_primary_trait(big_five: dict[str, float]) -> tuple[str, str]:
    """Determine primary Big Five trait: largest |percentile - 50|.

    Reference: abc-assessment-spec Section 2.4
    Returns (trait_name, direction) where direction is "High" or "Low".
    """
    best_trait = None
    best_distance = -1.0

    for trait in TRAIT_NAMES:
        distance = abs(big_five[trait] - 50.0)
        if distance > best_distance:
            best_distance = distance
            best_trait = trait

    direction = "High" if big_five[best_trait] >= 50.0 else "Low"
    return (best_trait, direction)


def derive_type(
    subscales: dict[str, float],
    big_five: dict[str, float],
) -> dict[str, str]:
    """Derive the 36-type classification from subscales and Big Five.

    Reference: abc-assessment-spec Section 2.4
    Returns dict with type_name and type_domain.
    """
    domain = get_dominant_domain(subscales)
    trait, direction = get_primary_trait(big_five)

    trait_key = trait.capitalize()
    if trait_key == "Openness":
        lookup_key = f"{direction}Openness"
    elif trait_key == "Conscientiousness":
        lookup_key = f"{direction}Conscientiousness"
    elif trait_key == "Extraversion":
        lookup_key = f"{direction}Extraversion"
    elif trait_key == "Agreeableness":
        lookup_key = f"{direction}Agreeableness"
    elif trait_key == "Neuroticism":
        lookup_key = f"{direction}Neuroticism"
    else:
        lookup_key = f"{direction}Integrator"

    type_name = TYPE_MAP[domain].get(lookup_key, "Integrator")

    return {
        "type_name": type_name,
        "type_domain": domain,
    }
