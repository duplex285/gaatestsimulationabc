"""Shared fixtures for psychometric test suite.

Reference: abc-assessment-spec Section 1.2 (subscale map)
Reference: abc-assessment-spec Section 11.1 (simulation parameters)
"""

import numpy as np
import pytest

# Factor structure: 6 factors, 4 items each
FACTORS = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
ITEMS_PER_FACTOR = 4
N_ITEMS = len(FACTORS) * ITEMS_PER_FACTOR
N_CATEGORIES = 7  # 7-point Likert


@pytest.fixture
def seed():
    """Fixed seed for reproducibility.

    Reference: CLAUDE_RULES.md Rule 7 (reproducibility non-negotiable)
    """
    return 42


@pytest.fixture
def known_discrimination():
    """Known discrimination parameters for parameter recovery tests.

    24 items, realistic range for personality Likert items (0.8-2.5).
    Reference: Baker & Kim (2004), Item Response Theory
    """
    rng = np.random.default_rng(42)
    return rng.uniform(0.8, 2.5, size=N_ITEMS)


@pytest.fixture
def known_difficulty():
    """Known difficulty (threshold) parameters for parameter recovery tests.

    24 items x 6 thresholds (7 categories - 1).
    Thresholds are ordered within each item and span the trait range.
    Reference: Samejima (1969), Estimation of Latent Ability
    """
    rng = np.random.default_rng(42)
    difficulty = np.zeros((N_ITEMS, N_CATEGORIES - 1))
    for i in range(N_ITEMS):
        base_points = np.sort(rng.uniform(-2.5, 2.5, size=N_CATEGORIES - 1))
        # Ensure minimum spacing of 0.3 between thresholds
        for j in range(1, len(base_points)):
            if base_points[j] - base_points[j - 1] < 0.3:
                base_points[j] = base_points[j - 1] + 0.3
        difficulty[i] = base_points
    return difficulty


@pytest.fixture
def known_theta():
    """Known true theta values for scoring recovery tests.

    500 respondents, standard normal distribution.
    """
    rng = np.random.default_rng(42)
    return rng.standard_normal(500)


@pytest.fixture
def small_theta():
    """Small set of known theta values for unit tests.

    10 respondents spanning the trait range.
    """
    return np.linspace(-2.5, 2.5, 10)
