"""Frustration signature detection for ABC Assessment.

Reference: abc-assessment-spec Section 2.5
Uses strict inequality (>) for all thresholds.

Pattern 1 — High sat + high frust (sat > 5.5, frust > 5.5) -> medium risk
  A: Blocked Drive, B: Conditional Belonging, C: Evaluated Mastery
Pattern 2 — Low sat + high frust (sat < 4.5, frust > 5.5) -> high risk
  A: Controlled Motivation, B: Active Exclusion, C: Competence Threat
"""

DOMAIN_PAIRS = {
    "ambition": ("a_sat", "a_frust"),
    "belonging": ("b_sat", "b_frust"),
    "craft": ("c_sat", "c_frust"),
}

HIGH_SAT_LABELS = {
    "ambition": "Blocked Drive",
    "belonging": "Conditional Belonging",
    "craft": "Evaluated Mastery",
}

LOW_SAT_LABELS = {
    "ambition": "Controlled Motivation",
    "belonging": "Active Exclusion",
    "craft": "Competence Threat",
}

HIGH_SAT_THRESHOLD = 5.5
LOW_SAT_THRESHOLD = 4.5
FRUST_THRESHOLD = 5.5


def detect_signatures(subscales: dict[str, float]) -> list[dict]:
    """Detect frustration signatures across all three domains.

    Reference: abc-assessment-spec Section 2.5

    Returns a list of dicts, each with keys: label, domain, risk.
    A person can have 0-3 signatures (one per domain at most, since the two
    patterns are mutually exclusive within a domain).
    """
    signatures = []
    for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
        sat = subscales[sat_key]
        frust = subscales[frust_key]

        if frust <= FRUST_THRESHOLD:
            continue

        if sat > HIGH_SAT_THRESHOLD:
            signatures.append(
                {
                    "label": HIGH_SAT_LABELS[domain],
                    "domain": domain,
                    "risk": "medium",
                }
            )
        elif sat < LOW_SAT_THRESHOLD:
            signatures.append(
                {
                    "label": LOW_SAT_LABELS[domain],
                    "domain": domain,
                    "risk": "high",
                }
            )

    return signatures
