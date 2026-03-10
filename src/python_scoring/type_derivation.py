"""Motivational type derivation for ABC Assessment.

Reference: abc-assessment-spec Section 2.4

Two-layer type system:

Layer 1 — 125 Profile Combinations
  Each domain's satisfaction is classified into 5 levels (Very High, High,
  Medium, Low, Very Low). The profile is the combination of all three levels.
  5 × 5 × 5 = 125 possible profiles. This is the granular view — no domain
  is excluded. Every person's relationship with all three needs is captured.

Layer 2 — 24 Named Archetypes
  For human-readable labelling, profiles are grouped into 24 types:
    8 base patterns × 3 frustration modifiers.

  Base patterns use a binary threshold (sat >= 6.46) per domain:
    (A_strong, B_strong, C_strong) → 2^3 = 8 patterns.
    Each pattern has a name that describes the full A-B-C shape.

  Modifiers count how many domains have frust >= 4.38:
    0 frustrated = Steady (sustainable flow)
    1 frustrated = Striving (productive friction in one area)
    2-3 frustrated = Resolute (persevering through multiple challenges)

  All names are strengths-based.

Ties in domain ranking (for Belbin compatibility) broken by domain order:
ambition > belonging > craft.
"""

# ---------------------------------------------------------------------------
# Layer 1: 5-level satisfaction classification
# ---------------------------------------------------------------------------

# Thresholds for 5 satisfaction levels on the 0-10 scale.
# Each band is ~2 points wide, aligned to discrete score boundaries.
SAT_LEVEL_THRESHOLDS = [
    ("Very High", 8.0),
    ("High", 6.0),
    ("Medium", 4.0),
    ("Low", 2.0),
]
SAT_LEVEL_DEFAULT = "Very Low"

# Numeric codes for profile: 5=Very High, 4=High, 3=Medium, 2=Low, 1=Very Low
SAT_LEVEL_CODES = {
    "Very High": 5,
    "High": 4,
    "Medium": 3,
    "Low": 2,
    "Very Low": 1,
}

ALL_SAT_LEVELS = ["Very High", "High", "Medium", "Low", "Very Low"]

# ---------------------------------------------------------------------------
# Layer 2: 24 named archetypes
# ---------------------------------------------------------------------------

# Binary threshold: Strong (sat >= 5.5) or Developing (sat < 5.5)
# This is the point where a need moves from "more developing than not" to
# "more activated than not." It sits below the domain state threshold (6.46)
# because activation precedes full satisfaction — a need can be engaged
# without yet thriving.
SAT_THRESHOLD = 5.5

# Frustration threshold for modifier count.
# Counts domains where frustration >= 5.0 (scale midpoint).
# This is separate from the domain state frust threshold (4.38) because the
# modifier asks how many domains carry *notable* frustration, not whether the
# domain is clinically distressed.
FRUST_THRESHOLD = 5.0

# 8 base patterns: (A_strong, B_strong, C_strong) -> base name
# Each name describes the full three-domain shape.
BASE_PATTERNS = {
    (True, True, True): "Integrator",  # all three needs activated
    (True, True, False): "Captain",  # ambition + belonging strong, craft developing
    (True, False, True): "Architect",  # ambition + craft strong, belonging developing
    (False, True, True): "Mentor",  # belonging + craft strong, ambition developing
    (True, False, False): "Pioneer",  # ambition leads, others developing
    (False, True, False): "Anchor",  # belonging leads, others developing
    (False, False, True): "Artisan",  # craft leads, others developing
    (False, False, False): "Seeker",  # all three developing
}

# 3 modifiers from frustrated-domain count
MODIFIER_THRESHOLDS = {
    0: "Steady",  # no frustrated domains — sustainable
    1: "Striving",  # one frustrated domain — productive friction
}
MODIFIER_DEFAULT = "Resolute"  # 2-3 frustrated domains — persevering

# All valid type names
ALL_TYPE_NAMES = {
    f"{mod} {base}" for base in BASE_PATTERNS.values() for mod in ["Steady", "Striving", "Resolute"]
}

# Domain order for tie-breaking
_DOMAIN_ORDER = ["ambition", "belonging", "craft"]

# Map domain names to subscale keys
_DOMAIN_SAT_KEY = {
    "ambition": "a_sat",
    "belonging": "b_sat",
    "craft": "c_sat",
}
_DOMAIN_FRUST_KEY = {
    "ambition": "a_frust",
    "belonging": "b_frust",
    "craft": "c_frust",
}


def classify_sat_level(sat_score: float) -> str:
    """Classify a satisfaction score into one of 5 levels.

    Levels: Very High (>=8.0), High (>=6.0), Medium (>=4.0),
            Low (>=2.0), Very Low (<2.0).

    Reference: abc-assessment-spec Section 2.4
    """
    for level_name, threshold in SAT_LEVEL_THRESHOLDS:
        if sat_score >= threshold:
            return level_name
    return SAT_LEVEL_DEFAULT


def compute_profile(subscales: dict[str, float]) -> dict:
    """Compute the 125-combination satisfaction profile.

    Returns dict with:
        levels: {ambition: str, belonging: str, craft: str}
        codes: {ambition: int, belonging: int, craft: int}
        profile_code: str like "4-3-5" (A:High, B:Medium, C:Very High)

    Reference: abc-assessment-spec Section 2.4
    """
    levels = {}
    codes = {}
    for domain in _DOMAIN_ORDER:
        sat = subscales[_DOMAIN_SAT_KEY[domain]]
        level = classify_sat_level(sat)
        levels[domain] = level
        codes[domain] = SAT_LEVEL_CODES[level]

    code_str = f"{codes['ambition']}-{codes['belonging']}-{codes['craft']}"
    return {"levels": levels, "codes": codes, "profile_code": code_str}


def get_dominant_domain(subscales: dict[str, float]) -> str:
    """Determine dominant domain: argmax of satisfaction scores.

    Ties broken by domain order: ambition > belonging > craft.

    Reference: abc-assessment-spec Section 2.4
    """
    domains = [(d, subscales[_DOMAIN_SAT_KEY[d]]) for d in _DOMAIN_ORDER]
    return max(domains, key=lambda x: x[1])[0]


def _get_base_pattern(subscales: dict[str, float]) -> str:
    """Map satisfaction scores to one of 8 base patterns."""
    a_strong = subscales["a_sat"] >= SAT_THRESHOLD
    b_strong = subscales["b_sat"] >= SAT_THRESHOLD
    c_strong = subscales["c_sat"] >= SAT_THRESHOLD
    return BASE_PATTERNS[(a_strong, b_strong, c_strong)]


def _get_modifier(subscales: dict[str, float]) -> str:
    """Count frustrated domains and return modifier."""
    frust_count = sum(subscales[_DOMAIN_FRUST_KEY[d]] >= FRUST_THRESHOLD for d in _DOMAIN_ORDER)
    return MODIFIER_THRESHOLDS.get(frust_count, MODIFIER_DEFAULT)


def derive_type(subscales: dict[str, float]) -> dict:
    """Derive motivational type from all 6 subscale scores.

    Reference: abc-assessment-spec Section 2.4

    Returns dict with:
        type_name: str — one of 24 named archetypes
        type_domain: str — dominant satisfaction domain
        profile: dict — 125-combination profile (levels, codes, profile_code)
    """
    profile = compute_profile(subscales)
    base = _get_base_pattern(subscales)
    modifier = _get_modifier(subscales)
    dominant = get_dominant_domain(subscales)

    return {
        "type_name": f"{modifier} {base}",
        "type_domain": dominant,
        "profile": profile,
    }
