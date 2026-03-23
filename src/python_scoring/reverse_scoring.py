"""Reverse scoring for ABC Assessment items.

Reference: abc-assessment-spec Section 2.1
Formula: reverse = 8 - response
Items 4 and 6 of each subscale are reverse-scored.
"""

REVERSE_ITEMS = frozenset(
    {
        "AS4",
        "AF4",
        "BS4",
        "BF4",
        "CS4",
        "CF4",
        "AS6",
        "AF6",
        "BS6",
        "BF6",
        "CS6",
        "CF6",
    }
)


def reverse_score(response: int) -> int:
    """Reverse-score a single Likert item.

    Reference: abc-assessment-spec Section 2.1, Section 13.2
    Formula: 8 - response
    """
    if not isinstance(response, int):
        raise TypeError(f"Response must be int, got {type(response).__name__}")
    if response < 1 or response > 7:
        raise ValueError(f"Response must be 1-7, got {response}")
    return 8 - response


def apply_reverse_scoring(responses: dict[str, int]) -> dict[str, int]:
    """Apply reverse scoring to a full response dict (36 core items).

    Reference: abc-assessment-spec Section 1.2, Section 2.1
    Items 4 and 6 of each subscale are reverse-scored:
    AS4, AF4, BS4, BF4, CS4, CF4, AS6, AF6, BS6, BF6, CS6, CF6.
    All other items pass through unchanged.
    """
    scored = {}
    for item, value in responses.items():
        if item in REVERSE_ITEMS:
            scored[item] = reverse_score(value)
        else:
            scored[item] = value
    return scored
