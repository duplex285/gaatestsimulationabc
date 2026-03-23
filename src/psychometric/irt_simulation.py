"""IRT simulation for ABC Assessment.

Generates synthetic Graded Response Model parameters and response data
for pipeline demonstration and parameter recovery testing.

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
Reference: Samejima (1969), Estimation of Latent Ability Using a Response
           Pattern of Graded Scores (Psychometrika Monograph No. 17)
"""

import numpy as np


def grm_probability(
    theta: float,
    discrimination: float,
    difficulty: np.ndarray,
) -> np.ndarray:
    """Compute category probabilities under Samejima's Graded Response Model.

    Reference: Samejima (1969)

    For K categories with K-1 threshold parameters, the cumulative probability
    of responding at or above category k is:

        P*(k | theta) = exp(a * (theta - b_k)) / (1 + exp(a * (theta - b_k)))

    The category probability is:
        P(k | theta) = P*(k | theta) - P*(k+1 | theta)

    with P*(1 | theta) = 1 and P*(K+1 | theta) = 0.

    Args:
        theta: latent trait value for a single person
        discrimination: item discrimination parameter (a > 0)
        difficulty: array of K-1 ordered threshold parameters (b_1 < b_2 < ... < b_{K-1})

    Returns:
        Array of K category probabilities summing to 1.0
    """
    n_categories = len(difficulty) + 1
    cumulative = np.zeros(n_categories + 1)
    cumulative[0] = 1.0  # P*(1) = 1
    for k in range(len(difficulty)):
        z = discrimination * (theta - difficulty[k])
        cumulative[k + 1] = 1.0 / (1.0 + np.exp(-z))
    cumulative[n_categories] = 0.0  # P*(K+1) = 0

    probs = np.diff(-cumulative)  # P(k) = P*(k) - P*(k+1)
    # Clip for numerical stability
    probs = np.maximum(probs, 0.0)
    total = np.sum(probs)
    if total > 0:
        probs /= total
    return probs


def generate_synthetic_grm_parameters(
    n_items: int = 24,
    n_categories: int = 7,
    discrimination_range: tuple[float, float] = (0.8, 2.5),
    seed: int = 42,
) -> dict[str, np.ndarray]:
    """Generate realistic GRM parameters for ABC 6-factor structure.

    Reference: abc-assessment-spec Section 11.1
    Reference: Baker & Kim (2004), Item Response Theory

    Generates discrimination parameters log-normally distributed with
    mean approximately 1.5, matching typical Likert personality items.
    Difficulty thresholds are evenly spaced and ordered within each item,
    spanning the standard normal trait range.

    Args:
        n_items: number of items (default 24 for ABC)
        n_categories: number of Likert categories (default 7)
        discrimination_range: (min, max) for uniform sampling
        seed: random seed for reproducibility

    Returns:
        dict with keys:
            discrimination: shape (n_items,)
            difficulty: shape (n_items, n_categories - 1), ordered within items
    """
    rng = np.random.default_rng(seed)
    n_thresholds = n_categories - 1

    discrimination = rng.uniform(discrimination_range[0], discrimination_range[1], size=n_items)

    difficulty = np.zeros((n_items, n_thresholds))
    for i in range(n_items):
        # Generate sorted thresholds spanning the trait range
        base_points = np.sort(rng.uniform(-2.5, 2.5, size=n_thresholds))
        # Ensure minimum spacing of 0.3 between thresholds
        for j in range(1, n_thresholds):
            if base_points[j] - base_points[j - 1] < 0.3:
                base_points[j] = base_points[j - 1] + 0.3
        difficulty[i] = base_points

    return {
        "discrimination": discrimination,
        "difficulty": difficulty,
    }


def simulate_grm_responses(
    theta: np.ndarray,
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    seed: int = 42,
) -> np.ndarray:
    """Simulate polytomous responses from GRM parameters.

    Reference: Samejima (1969)
    Reference: abc-assessment-spec Section 11.1

    For each person-item combination, computes category probabilities
    under the GRM and samples a response from the categorical distribution.

    Args:
        theta: array of latent trait values, shape (n_persons,)
        discrimination: array of item discrimination, shape (n_items,)
        difficulty: array of item thresholds, shape (n_items, n_categories - 1)
        seed: random seed for reproducibility

    Returns:
        Integer response matrix, shape (n_persons, n_items), values in [1, n_categories]
    """
    rng = np.random.default_rng(seed)
    n_persons = len(theta)
    n_items = len(discrimination)
    n_categories = difficulty.shape[1] + 1

    responses = np.zeros((n_persons, n_items), dtype=int)

    for p in range(n_persons):
        for i in range(n_items):
            probs = grm_probability(theta[p], discrimination[i], difficulty[i])
            # Sample from categorical distribution (1-indexed)
            responses[p, i] = rng.choice(np.arange(1, n_categories + 1), p=probs)

    return responses
