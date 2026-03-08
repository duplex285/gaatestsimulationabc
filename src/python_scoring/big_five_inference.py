"""Big Five personality inference from ABC subscale scores.

Reference: abc-assessment-spec Section 2.3, Section 13.2

Steps:
1. Centre each subscale: (score - 5) / 5
2. Dot product with weight row
3. Convert to percentile: 50 + z * 30, clamped to [1, 99]
"""

# Weight matrix from spec Section 2.3
# Rows: O, C, E, A, N. Columns: a_sat, a_frust, b_sat, b_frust, c_sat, c_frust.
WEIGHT_MATRIX = {
    "openness": [0.25, -0.10, 0.15, -0.05, 0.35, -0.15],
    "conscientiousness": [0.40, -0.25, 0.10, -0.10, 0.55, -0.30],
    "extraversion": [0.30, -0.15, 0.45, -0.20, 0.15, -0.10],
    "agreeableness": [0.05, -0.15, 0.50, -0.40, 0.10, -0.05],
    "neuroticism": [-0.20, 0.48, -0.25, 0.45, -0.15, 0.42],
}

SUBSCALE_ORDER = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]


def centre_subscales(subscales: dict[str, float]) -> dict[str, float]:
    """Centre each subscale score: (score - 5) / 5.

    Reference: abc-assessment-spec Section 2.3
    Input scores are on 0-10 scale. Output is roughly -1.0 to +1.0.
    """
    return {key: (val - 5.0) / 5.0 for key, val in subscales.items()}


def compute_big_five(subscales: dict[str, float]) -> dict[str, float]:
    """Compute Big Five percentiles from subscale scores.

    Reference: abc-assessment-spec Section 2.3, Section 13.2
    """
    centred = centre_subscales(subscales)
    centred_vec = [centred[key] for key in SUBSCALE_ORDER]

    result = {}
    for trait, weights in WEIGHT_MATRIX.items():
        z = sum(w * s for w, s in zip(weights, centred_vec, strict=True))
        percentile = 50.0 + z * 30.0
        percentile = max(1.0, min(99.0, percentile))
        result[trait] = round(percentile, 1)
    return result
