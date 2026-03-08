"""Reverse scoring for ABC Assessment items.

Reference: abc-assessment-spec Section 2.1
Formula: reverse = 8 - response
Item 4 of each subscale is reverse-scored.
"""

REVERSE_ITEMS = frozenset({"AS4", "AF4", "BS4", "BF4", "CS4", "CF4"})


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
    """Apply reverse scoring to a full response dict (24 core items).

    Reference: abc-assessment-spec Section 1.2, Section 2.1
    Items AS4, AF4, BS4, BF4, CS4, CF4 are reverse-scored.
    All other items pass through unchanged.
    """
    scored = {}
    for item, value in responses.items():
        if item in REVERSE_ITEMS:
            scored[item] = reverse_score(value)
        else:
            scored[item] = value
    return scored
