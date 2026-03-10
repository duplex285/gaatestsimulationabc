"""Belbin team-role inference for ABC Assessment.

Reference: abc-assessment-spec Section 2.6

Architecture: subscales (6 inputs) + Big Five percentiles (5 inputs) → roles.
The ABC domain structure selects the role cluster; Big Five traits
differentiate within each cluster.

Belbin's 9 roles are grouped into three clusters that map to ABC domains
(Aranzabal et al., 2022):

  Thinking (Craft):    Plant, Specialist, Monitor-Evaluator
  People (Belonging):  Coordinator, Teamworker, Resource Investigator
  Action (Ambition):   Shaper, Implementer, Completer-Finisher

Scoring: each role has a domain affinity (from satisfaction ranking) and
a Big Five trait alignment. The product gives a continuous role score.
Roles are restricted to the top two domain clusters (primary and secondary).
The tertiary cluster is excluded to reduce noise — adding a third cluster
would dilute signal without improving discriminant validity.

Roles above a threshold fire; the highest-scoring role always fires
(guaranteeing at least one role per participant). Multiple roles can apply.

Qualifier reflects trait strength: "natural" (≥ 60th percentile on the
role's key trait) or "manageable" (below 60th).

Subscale keys: a_sat, a_frust, b_sat, b_frust, c_sat, c_frust (0-10 scale).
Big Five keys: openness, conscientiousness, extraversion, agreeableness,
neuroticism (1-99 percentile scale).
"""

# Domain affinity weights by rank position.
# Primary domain gets full weight, secondary gets partial.
# Tertiary domain is excluded (affinity 0) to restrict roles to top two clusters.
DOMAIN_AFFINITY = {
    0: 1.0,  # primary (highest sat)
    1: 0.5,  # secondary
    2: 0.0,  # tertiary — excluded
}

# Role threshold: minimum score to fire (beyond the guaranteed top role).
ROLE_THRESHOLD = 0.30

# Trait percentile boundary for natural vs manageable qualifier.
NATURAL_THRESHOLD = 60.0

# Role definitions: domain anchor, differentiating Big Five trait, qualifiers.
ROLE_DEFS = [
    # Thinking cluster (Craft domain)
    {
        "role": "Plant",
        "domain": "craft",
        "trait": "openness",
        "qualifier_natural": "Creative",
        "qualifier_manageable": "Conceptual",
    },
    {
        "role": "Specialist",
        "domain": "craft",
        "trait": "conscientiousness",
        "qualifier_natural": "Deep Mastery",
        "qualifier_manageable": "Focused",
    },
    {
        "role": "Monitor-Evaluator",
        "domain": "craft",
        "trait": "neuroticism",
        "qualifier_natural": "Vigilant",
        "qualifier_manageable": "Analytical",
    },
    # People cluster (Belonging domain)
    {
        "role": "Teamworker",
        "domain": "belonging",
        "trait": "agreeableness",
        "qualifier_natural": "Anchor",
        "qualifier_manageable": "Supportive",
    },
    {
        "role": "Resource Investigator",
        "domain": "belonging",
        "trait": "extraversion",
        "qualifier_natural": "Networker",
        "qualifier_manageable": "Curious",
    },
    {
        "role": "Coordinator",
        "domain": "belonging",
        "trait": "conscientiousness",
        "qualifier_natural": "Balanced",
        "qualifier_manageable": "Structured",
    },
    # Action cluster (Ambition domain)
    {
        "role": "Shaper",
        "domain": "ambition",
        "trait": "extraversion",
        "qualifier_natural": "Inspiring",
        "qualifier_manageable": "Driving",
    },
    {
        "role": "Implementer",
        "domain": "ambition",
        "trait": "conscientiousness",
        "qualifier_natural": "Systematic",
        "qualifier_manageable": "Practical",
    },
    {
        "role": "Completer-Finisher",
        "domain": "ambition",
        "trait": "neuroticism",
        "qualifier_natural": "Quality Driven",
        "qualifier_manageable": "Thorough",
    },
]

# Map domain names to satisfaction subscale keys.
_DOMAIN_SAT_KEY = {
    "ambition": "a_sat",
    "belonging": "b_sat",
    "craft": "c_sat",
}

# Domain rank order (ties broken by this order).
_DOMAIN_ORDER = ["ambition", "belonging", "craft"]


def _rank_domains(subscales: dict[str, float]) -> dict[str, int]:
    """Rank domains by satisfaction score (0 = highest, 2 = lowest).

    Ties broken by domain order: ambition > belonging > craft.
    """
    sats = [(d, subscales[_DOMAIN_SAT_KEY[d]]) for d in _DOMAIN_ORDER]
    # Sort descending by score, stable sort preserves tie-break order.
    ranked = sorted(sats, key=lambda x: -x[1])
    return {domain: rank for rank, (domain, _) in enumerate(ranked)}


def _score_role(
    role_def: dict,
    domain_ranks: dict[str, int],
    big_five: dict[str, float],
) -> tuple[float, str]:
    """Compute role score and qualifier for a single role definition.

    Returns:
        (score, qualifier) where score = domain_affinity × trait_percentile / 100.
    """
    rank = domain_ranks[role_def["domain"]]
    affinity = DOMAIN_AFFINITY[rank]
    trait_pct = big_five[role_def["trait"]]
    score = affinity * trait_pct / 100.0

    if trait_pct >= NATURAL_THRESHOLD:
        qualifier = role_def["qualifier_natural"]
    else:
        qualifier = role_def["qualifier_manageable"]

    return score, qualifier


def infer_belbin_roles(
    subscales: dict[str, float],
    big_five: dict[str, float] | None = None,
) -> list[dict]:
    """Infer Belbin team roles from ABC subscales and Big Five percentiles.

    Reference: abc-assessment-spec Section 2.6

    Uses domain satisfaction ranking to determine cluster affinity, and
    Big Five percentiles to differentiate roles within each cluster.
    All roles are scored; those above ROLE_THRESHOLD fire. The highest-
    scoring role always fires (guaranteeing at least one role).

    Args:
        subscales: dict with keys a_sat, a_frust, b_sat, b_frust, c_sat,
            c_frust. Values on 0-10 scale.
        big_five: dict with keys openness, conscientiousness, extraversion,
            agreeableness, neuroticism. Values on 1-99 percentile scale.
            If None, computes Big Five from subscales internally.

    Returns:
        List of dicts, each with keys: role, qualifier, score.
    """
    if big_five is None:
        from src.python_scoring.big_five_inference import compute_big_five

        big_five = compute_big_five(subscales)

    domain_ranks = _rank_domains(subscales)

    # Score all roles.
    scored = []
    for role_def in ROLE_DEFS:
        score, qualifier = _score_role(role_def, domain_ranks, big_five)
        scored.append(
            {
                "role": role_def["role"],
                "qualifier": qualifier,
                "score": round(score, 4),
            }
        )

    # Sort descending by score.
    scored.sort(key=lambda r: -r["score"])

    # Select roles above threshold, always including the top role.
    matched = [scored[0]]
    for role in scored[1:]:
        if role["score"] >= ROLE_THRESHOLD:
            matched.append(role)

    return matched
