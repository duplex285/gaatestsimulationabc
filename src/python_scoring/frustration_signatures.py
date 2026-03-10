"""Frustration signature detection for ABC Assessment.

Reference: abc-assessment-spec Section 2.5
Uses split thresholds aligned with domain classification:
  Satisfaction threshold: 6.46
  Frustration threshold:  4.38

Pattern 1 — High sat + high frust (sat >= 6.46, frust >= 4.38) -> medium risk
  A: Blocked Drive, B: Conditional Belonging, C: Evaluated Mastery
Pattern 2 — Low sat + high frust (sat < 6.46, frust >= 4.38) -> high risk
  A: Controlled Motivation, B: Active Exclusion, C: Competence Threat

No gap zone: every participant with frust >= 4.38 receives a signature.
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

SAT_THRESHOLD = 6.46
FRUST_THRESHOLD = 4.38


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

        if frust < FRUST_THRESHOLD:
            continue

        if sat >= SAT_THRESHOLD:
            signatures.append(
                {
                    "label": HIGH_SAT_LABELS[domain],
                    "domain": domain,
                    "risk": "medium",
                }
            )
        else:
            signatures.append(
                {
                    "label": LOW_SAT_LABELS[domain],
                    "domain": domain,
                    "risk": "high",
                }
            )

    return signatures
