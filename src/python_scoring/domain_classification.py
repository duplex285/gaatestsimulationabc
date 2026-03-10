"""Domain state classification for ABC Assessment.

Reference: abc-assessment-spec Section 2.2
Split thresholds on the 0-10 normalized scale:
  Satisfaction threshold: 6.46
  Frustration threshold:  4.38

These sit between discrete score boundaries (scores spaced 0.417 apart)
to counteract argmax selection bias and within-domain anticorrelation.

| Satisfaction | Frustration | State      |
|-------------|-------------|------------|
| >= 6.46     | < 4.38      | Thriving   |
| >= 6.46     | >= 4.38     | Vulnerable |
| < 6.46      | < 4.38      | Mild    |
| < 6.46      | >= 4.38     | Distressed |
"""

SAT_THRESHOLD = 6.46
FRUST_THRESHOLD = 4.38

DOMAIN_PAIRS = {
    "ambition": ("a_sat", "a_frust"),
    "belonging": ("b_sat", "b_frust"),
    "craft": ("c_sat", "c_frust"),
}


def classify_domain_state(sat: float, frust: float) -> str:
    """Classify a single domain into one of four states.

    Reference: abc-assessment-spec Section 2.2
    Uses split thresholds: sat >= 6.46, frust >= 4.38.
    """
    high_sat = sat >= SAT_THRESHOLD
    high_frust = frust >= FRUST_THRESHOLD

    if high_sat and not high_frust:
        return "Thriving"
    if high_sat and high_frust:
        return "Vulnerable"
    if not high_sat and not high_frust:
        return "Mild"
    return "Distressed"


def classify_all_domains(subscales: dict[str, float]) -> dict[str, str]:
    """Classify all three domains from subscale scores.

    Reference: abc-assessment-spec Section 2.2
    Returns dict with keys: ambition, belonging, craft.
    Values are one of: Thriving, Vulnerable, Mild, Distressed.
    """
    result = {}
    for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
        result[domain] = classify_domain_state(
            subscales[sat_key],
            subscales[frust_key],
        )
    return result
