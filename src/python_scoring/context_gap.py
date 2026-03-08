"""Context gap analysis for ABC Assessment.

Reference: abc-assessment-spec Section 2.7

Formula: gap = team_score - personal_score (per subscale)
A gap below -1.5 on any SATISFACTION subscale flags a team context concern.
Frustration gaps are computed but never flagged.
"""

GAP_THRESHOLD = -1.5

SUBSCALE_KEYS = ("a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust")
SATISFACTION_KEYS = ("a_sat", "b_sat", "c_sat")


def compute_context_gaps(
    personal: dict[str, float],
    team: dict[str, float] | None = None,
) -> dict:
    """Compute per-subscale gaps between team and personal scores.

    Reference: abc-assessment-spec Section 2.7

    Returns dict with keys:
        gaps: dict of subscale -> gap value (team - personal)
        flagged: list of satisfaction subscale keys where gap < -1.5
    """
    if team is None:
        return {"gaps": {}, "flagged": []}

    gaps = {}
    flagged = []

    for key in SUBSCALE_KEYS:
        gaps[key] = team[key] - personal[key]

    for key in SATISFACTION_KEYS:
        if gaps[key] < GAP_THRESHOLD:
            flagged.append(key)

    return {"gaps": gaps, "flagged": flagged}
