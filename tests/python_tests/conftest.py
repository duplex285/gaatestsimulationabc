"""Shared fixtures for ABC Assessment test suite.

Reference: abc-assessment-spec Section 1.2 (subscale map)
Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
"""

import pytest

# Item codes per subscale. Items 4 and 6 in each are reverse-scored.
# Reference: abc-assessment-spec Section 1.2
SUBSCALE_ITEMS = {
    "a_sat": ["AS1", "AS2", "AS3", "AS4", "AS5", "AS6"],
    "a_frust": ["AF1", "AF2", "AF3", "AF4", "AF5", "AF6"],
    "b_sat": ["BS1", "BS2", "BS3", "BS4", "BS5", "BS6"],
    "b_frust": ["BF1", "BF2", "BF3", "BF4", "BF5", "BF6"],
    "c_sat": ["CS1", "CS2", "CS3", "CS4", "CS5", "CS6"],
    "c_frust": ["CF1", "CF2", "CF3", "CF4", "CF5", "CF6"],
}

REVERSE_ITEMS = {
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

ALL_ITEMS = [item for items in SUBSCALE_ITEMS.values() for item in items]


@pytest.fixture
def perfect_thriving_responses():
    """All satisfaction items 7, all frustration items 1.

    Expected: sat subscales = 10.0, frust subscales = 0.0, all Thriving.
    Reference: abc-assessment-spec Section 2.1
    """
    responses = {}
    for subscale, items in SUBSCALE_ITEMS.items():
        is_sat = subscale.endswith("_sat")
        for item in items:
            is_reverse = item in REVERSE_ITEMS
            if is_sat:
                # Sat items high: forward=7, reverse=1 (reverse_score(1)=7)
                responses[item] = 1 if is_reverse else 7
            else:
                # Frust items low: forward=1, reverse=7 (reverse_score(7)=1)
                responses[item] = 7 if is_reverse else 1
    return responses


@pytest.fixture
def perfect_distressed_responses():
    """All satisfaction items 1, all frustration items 7.

    Expected: sat subscales = 0.0, frust subscales = 10.0, all Distressed.
    """
    responses = {}
    for subscale, items in SUBSCALE_ITEMS.items():
        is_sat = subscale.endswith("_sat")
        for item in items:
            is_reverse = item in REVERSE_ITEMS
            if is_sat:
                responses[item] = 7 if is_reverse else 1
            else:
                responses[item] = 1 if is_reverse else 7
    return responses


@pytest.fixture
def perfect_vulnerable_responses():
    """All items at maximum (7 for forward, 1 for reverse -> all become 7).

    Expected: sat=10.0, frust=10.0, all Vulnerable.
    """
    responses = {}
    for items in SUBSCALE_ITEMS.values():
        for item in items:
            is_reverse = item in REVERSE_ITEMS
            responses[item] = 1 if is_reverse else 7
    return responses


@pytest.fixture
def perfect_mild_responses():
    """All items at minimum (1 for forward, 7 for reverse -> all become 1).

    Expected: sat=0.0, frust=0.0, all Mild.
    """
    responses = {}
    for items in SUBSCALE_ITEMS.values():
        for item in items:
            is_reverse = item in REVERSE_ITEMS
            responses[item] = 7 if is_reverse else 1
    return responses


@pytest.fixture
def midpoint_responses():
    """All items at 4 (midpoint).

    Expected: all subscales = 5.0 on 0-10 scale.
    Reference: abc-assessment-spec Section 2.1
    """
    return dict.fromkeys(ALL_ITEMS, 4)
