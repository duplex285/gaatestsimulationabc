"""Domain state classification for ABC Assessment.

Reference: abc-assessment-spec Section 2.2
Threshold: 5.5 on the 0-10 normalized scale.

| Satisfaction | Frustration | State      |
|-------------|-------------|------------|
| >= 5.5      | < 5.5       | Thriving   |
| >= 5.5      | >= 5.5      | Vulnerable |
| < 5.5       | < 5.5       | Dormant    |
| < 5.5       | >= 5.5      | Distressed |
"""

THRESHOLD = 5.5

DOMAIN_PAIRS = {
    "ambition": ("a_sat", "a_frust"),
    "belonging": ("b_sat", "b_frust"),
    "craft": ("c_sat", "c_frust"),
}


def classify_domain_state(sat: float, frust: float) -> str:
    """Classify a single domain into one of four states.

    Reference: abc-assessment-spec Section 2.2
    """
    high_sat = sat >= THRESHOLD
    high_frust = frust >= THRESHOLD

    if high_sat and not high_frust:
        return "Thriving"
    if high_sat and high_frust:
        return "Vulnerable"
    if not high_sat and not high_frust:
        return "Dormant"
    return "Distressed"


def classify_all_domains(subscales: dict[str, float]) -> dict[str, str]:
    """Classify all three domains from subscale scores.

    Reference: abc-assessment-spec Section 2.2
    Returns dict with keys: ambition, belonging, craft.
    Values are one of: Thriving, Vulnerable, Dormant, Distressed.
    """
    result = {}
    for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
        result[domain] = classify_domain_state(
            subscales[sat_key],
            subscales[frust_key],
        )
    return result
