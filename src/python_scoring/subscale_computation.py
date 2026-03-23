"""Subscale computation for ABC Assessment.

Reference: abc-assessment-spec Section 2.1, Section 13.2
Subscale mean = mean of 6 items (after reverse coding), on 1-7 scale.
Normalized = ((mean - 1) / 6) * 10, yielding 0-10 scale.
"""

SUBSCALE_ITEMS = {
    "a_sat": ["AS1", "AS2", "AS3", "AS4", "AS5", "AS6"],
    "a_frust": ["AF1", "AF2", "AF3", "AF4", "AF5", "AF6"],
    "b_sat": ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6"],
    "b_frust": ["BF1", "BF2", "BF3", "BF4", "BF5", "BF6"],
    "c_sat": ["CS1", "CS2", "CS3", "CS4", "CS5", "CS6"],
    "c_frust": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6"],
}


def compute_subscale_mean(items: list[int | float]) -> float:
    """Compute mean of a 6-item subscale on the 1-7 scale.

    Reference: abc-assessment-spec Section 13.2
    Formula: (1/6) * sum(items)
    """
    if len(items) != 6:
        raise ValueError(f"Subscale requires exactly 6 items, got {len(items)}")
    for val in items:
        if val < 1 or val > 7:
            raise ValueError(f"Item value must be 1-7, got {val}")
    return sum(items) / 6.0


def normalize_to_10(mean_score: float) -> float:
    """Normalize a 1-7 subscale mean to 0-10 scale.

    Reference: abc-assessment-spec Section 2.1
    Formula: ((mean - 1) / 6) * 10
    """
    return ((mean_score - 1.0) / 6.0) * 10.0


def compute_all_subscales(scored_responses: dict[str, int]) -> dict[str, float]:
    """Compute all 6 normalized subscale scores from reverse-scored responses.

    Reference: abc-assessment-spec Section 2.1
    Returns dict with keys: a_sat, a_frust, b_sat, b_frust, c_sat, c_frust.
    Values are on 0-10 scale.
    """
    result = {}
    for subscale, items in SUBSCALE_ITEMS.items():
        values = [scored_responses[item] for item in items]
        raw_mean = compute_subscale_mean(values)
        result[subscale] = normalize_to_10(raw_mean)
    return result
