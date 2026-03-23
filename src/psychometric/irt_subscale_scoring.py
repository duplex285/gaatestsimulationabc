"""IRT subscale scoring bridge for ABC Assessment.

Maps IRT theta estimates to the 0-10 subscale scores used by the
existing scoring pipeline, enabling downstream compatibility with
domain classification, type derivation, and other modules.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
Reference: abc-assessment-spec Section 1.2 (subscale map, 36 items)
"""

import numpy as np

from src.psychometric.irt_estimation import score_theta_eap

# Item indices within the 36-item response matrix, grouped by factor.
# Order: AS1-AS6, AF1-AF6, BS1-BS6, BF1-BF6, CS1-CS6, CF1-CF6
# Reference: abc-assessment-spec Section 1.2
FACTOR_ITEM_INDICES = {
    "a_sat": [0, 1, 2, 3, 4, 5],
    "a_frust": [6, 7, 8, 9, 10, 11],
    "b_sat": [12, 13, 14, 15, 16, 17],
    "b_frust": [18, 19, 20, 21, 22, 23],
    "c_sat": [24, 25, 26, 27, 28, 29],
    "c_frust": [30, 31, 32, 33, 34, 35],
}


def theta_to_subscale_score(
    theta: float,
    center: float = 5.0,
    scale: float = 2.5,
    clamp_min: float = 0.0,
    clamp_max: float = 10.0,
) -> float:
    """Convert a theta estimate to the 0-10 subscale score.

    Reference: abc-assessment-spec Section 2.1

    Maps theta (mean=0, SD=1 in standard normal metric) to [0, 10] via:
        score = center + theta * scale

    Clamped to [clamp_min, clamp_max] to prevent out-of-range values.

    Args:
        theta: latent trait estimate (standard normal metric)
        center: score corresponding to theta=0 (default 5.0)
        scale: points per unit theta (default 2.5, so +/-2 SD spans 0-10)
        clamp_min: minimum allowed score
        clamp_max: maximum allowed score

    Returns:
        Score on the target scale, clamped to [clamp_min, clamp_max]
    """
    score = center + theta * scale
    return float(max(clamp_min, min(clamp_max, score)))


def score_subscales_irt(
    responses: np.ndarray,
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    prior_mean: float = 0.0,
    prior_sd: float = 1.0,
) -> dict:
    """Score all 6 ABC subscales using IRT (EAP) estimation.

    Reference: abc-assessment-spec Section 2.1
    Reference: Bock & Mislevy (1982)

    For each factor, extracts the relevant 6-item subset from the full
    response matrix, estimates theta via EAP using that factor's item
    parameters, then converts to the 0-10 scale.

    Args:
        responses: integer response matrix, shape (n_persons, 36), values in [1, 7]
        discrimination: item discrimination parameters, shape (36,)
        difficulty: item threshold parameters, shape (36, 6)
        prior_mean: mean of the normal prior on theta
        prior_sd: SD of the normal prior on theta

    Returns:
        dict with keys:
            scores: {factor_name: array of 0-10 scores} for each of 6 factors
            standard_errors: {factor_name: array of SEs} for each factor
            theta: {factor_name: array of raw theta estimates} for each factor
    """
    scores = {}
    standard_errors = {}
    theta_estimates = {}

    for factor, indices in FACTOR_ITEM_INDICES.items():
        # Extract factor-specific responses and parameters
        factor_responses = responses[:, indices]
        factor_discrimination = discrimination[indices]
        factor_difficulty = difficulty[indices]

        # EAP estimation for this factor
        theta_hat, se_hat = score_theta_eap(
            factor_responses,
            factor_discrimination,
            factor_difficulty,
            prior_mean=prior_mean,
            prior_sd=prior_sd,
        )

        # Convert theta to 0-10 scale
        factor_scores = np.array([theta_to_subscale_score(t) for t in theta_hat])

        scores[factor] = factor_scores
        standard_errors[factor] = se_hat
        theta_estimates[factor] = theta_hat

    return {
        "scores": scores,
        "standard_errors": standard_errors,
        "theta": theta_estimates,
    }
