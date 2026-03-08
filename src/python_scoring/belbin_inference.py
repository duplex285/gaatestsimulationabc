"""Belbin team-role inference for ABC Assessment.

Reference: abc-assessment-spec Section 2.6

Rule-based inference evaluated in order; multiple roles can apply.
All rules use strict inequality (>) per spec.

Belbin's 9 team roles mapped to ABC subscale conditions:

| Condition                                    | Role                  | Qualifier      |
|----------------------------------------------|-----------------------|----------------|
| C-sat > 6.5 AND C-frust < 4.0 AND A-sat < 5 | Plant                 | Creative       |
| A-sat > 6.5 AND B-sat > 6.0                 | Shaper                | Inspiring      |
| A-sat > 6.5 AND B-sat <= 6.0                | Shaper                | Driving        |
| C-sat > 7.0 AND C-frust < 3.0               | Specialist            | Deep Mastery   |
| B-sat > 7.0 AND B-frust < 3.0               | Teamworker            | Anchor         |
| A-sat > 5.0 AND B-sat > 5.0 AND C-sat > 5.0 | Coordinator           | Balanced       |
| A-frust > 6.0 OR B-frust > 6.0              | Monitor-Evaluator     | Vigilant       |
| C-sat > 5.5 AND A-sat > 5.5 AND C-frust < 4 | Implementer           | Systematic     |
| C-sat > 6.0 AND C-frust > 5.0               | Completer-Finisher    | Quality Driven |
| No match                                     | Resource Investigator | Seeking        |

Plant: High craft creativity (high C-sat, low C-frust) without strong ambition drive —
  the idea generator who works from mastery rather than goal pursuit.
Implementer: Turns plans into action — needs both craft satisfaction and ambition
  satisfaction with low craft frustration, the disciplined executor.
Completer-Finisher: High craft standards coupled with frustration about quality —
  the person who notices every gap and won't ship until it's right.

Subscale keys: a_sat, a_frust, b_sat, b_frust, c_sat, c_frust (0-10 scale).
"""

BELBIN_RULES = [
    {
        "condition": lambda s: s["c_sat"] > 6.5 and s["c_frust"] < 4.0 and s["a_sat"] < 5.0,
        "role": "Plant",
        "qualifier": "Creative",
    },
    {
        "condition": lambda s: s["a_sat"] > 6.5 and s["b_sat"] > 6.0,
        "role": "Shaper",
        "qualifier": "Inspiring",
    },
    {
        "condition": lambda s: s["a_sat"] > 6.5 and s["b_sat"] <= 6.0,
        "role": "Shaper",
        "qualifier": "Driving",
    },
    {
        "condition": lambda s: s["c_sat"] > 7.0 and s["c_frust"] < 3.0,
        "role": "Specialist",
        "qualifier": "Deep Mastery",
    },
    {
        "condition": lambda s: s["b_sat"] > 7.0 and s["b_frust"] < 3.0,
        "role": "Teamworker",
        "qualifier": "Anchor",
    },
    {
        "condition": lambda s: s["a_sat"] > 5.0 and s["b_sat"] > 5.0 and s["c_sat"] > 5.0,
        "role": "Coordinator",
        "qualifier": "Balanced",
    },
    {
        "condition": lambda s: s["a_frust"] > 6.0 or s["b_frust"] > 6.0,
        "role": "Monitor-Evaluator",
        "qualifier": "Vigilant",
    },
    {
        "condition": lambda s: s["c_sat"] > 5.5 and s["a_sat"] > 5.5 and s["c_frust"] < 4.0,
        "role": "Implementer",
        "qualifier": "Systematic",
    },
    {
        "condition": lambda s: s["c_sat"] > 6.0 and s["c_frust"] > 5.0,
        "role": "Completer-Finisher",
        "qualifier": "Quality Driven",
    },
]

FALLBACK_ROLE = {"role": "Resource Investigator", "qualifier": "Seeking"}


def infer_belbin_roles(subscales: dict[str, float]) -> list[dict]:
    """Infer Belbin team roles from ABC subscale scores.

    Reference: abc-assessment-spec Section 2.6

    All rules are evaluated (no short-circuit). If none match, the fallback
    Resource Investigator role is returned.

    Args:
        subscales: dict with keys a_sat, a_frust, b_sat, b_frust, c_sat, c_frust.
            Values on 0-10 scale.

    Returns:
        List of dicts, each with keys: role, qualifier.
    """
    matched = []
    for rule in BELBIN_RULES:
        if rule["condition"](subscales):
            matched.append({"role": rule["role"], "qualifier": rule["qualifier"]})

    if not matched:
        return [FALLBACK_ROLE.copy()]

    return matched
