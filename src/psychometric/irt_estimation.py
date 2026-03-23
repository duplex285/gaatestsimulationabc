"""IRT estimation for ABC Assessment.

Provides theta scoring via Expected A Posteriori (EAP) estimation
and item information function computation under the Graded Response Model.

Reference: Bock & Mislevy (1982), Adaptive EAP Estimation of Ability
           in a Microcomputer Environment
Reference: Baker & Kim (2004), Item Response Theory: Parameter Estimation
           Techniques (2nd ed.)
Reference: Samejima (1969), Estimation of Latent Ability Using a Response
           Pattern of Graded Scores
"""

import numpy as np
from scipy.stats import norm

from src.psychometric.irt_simulation import grm_probability


def score_theta_eap(
    responses: np.ndarray,
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    prior_mean: float = 0.0,
    prior_sd: float = 1.0,
    quadrature_points: int = 61,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute Expected A Posteriori theta estimates with standard errors.

    Reference: Bock & Mislevy (1982)

    Uses Gaussian quadrature to integrate over the posterior distribution
    of theta given the observed response pattern. The prior is normal
    with specified mean and SD.

    For each person, the posterior is:
        p(theta | responses) proportional to L(responses | theta) * prior(theta)

    where L is the product of GRM category probabilities across items.

    The EAP estimate is E[theta | responses] and the SE is SD[theta | responses].

    Args:
        responses: integer response matrix, shape (n_persons, n_items), values in [1, K]
        discrimination: item discrimination parameters, shape (n_items,)
        difficulty: item threshold parameters, shape (n_items, K-1)
        prior_mean: mean of the normal prior on theta
        prior_sd: SD of the normal prior on theta
        quadrature_points: number of integration points (more = more precise, slower)

    Returns:
        (theta_estimates, standard_errors), each shape (n_persons,)
    """
    n_persons, n_items = responses.shape

    # Set up quadrature grid
    theta_grid = np.linspace(
        prior_mean - 4 * prior_sd, prior_mean + 4 * prior_sd, quadrature_points
    )
    # Prior weights (normal density at each quadrature point)
    prior_weights = norm.pdf(theta_grid, loc=prior_mean, scale=prior_sd)
    prior_weights /= np.sum(prior_weights)  # normalize to sum to 1

    theta_hat = np.zeros(n_persons)
    se_hat = np.zeros(n_persons)

    for p in range(n_persons):
        # Compute log-likelihood at each quadrature point
        log_likelihood = np.zeros(quadrature_points)
        for q in range(quadrature_points):
            ll = 0.0
            for i in range(n_items):
                probs = grm_probability(theta_grid[q], discrimination[i], difficulty[i])
                category_idx = responses[p, i] - 1  # convert to 0-indexed
                prob = probs[category_idx]
                ll += np.log(max(prob, 1e-15))
            log_likelihood[q] = ll

        # Posterior = likelihood * prior (in log space for stability)
        log_posterior = log_likelihood + np.log(np.maximum(prior_weights, 1e-15))
        # Shift for numerical stability
        log_posterior -= np.max(log_posterior)
        posterior = np.exp(log_posterior)
        posterior /= np.sum(posterior)

        # EAP estimate: E[theta | responses]
        theta_hat[p] = np.sum(posterior * theta_grid)

        # SE: SD[theta | responses]
        variance = np.sum(posterior * (theta_grid - theta_hat[p]) ** 2)
        se_hat[p] = np.sqrt(max(variance, 1e-10))

    return theta_hat, se_hat


def item_information(
    theta: np.ndarray,
    discrimination: np.ndarray,
    difficulty: np.ndarray,
) -> np.ndarray:
    """Compute item information functions across a theta range.

    Reference: Baker & Kim (2004), Item Response Theory
    Reference: Samejima (1969)

    For the GRM, item information at theta is:
        I(theta) = sum_k [ (P'_k(theta))^2 / P_k(theta) ]

    where P_k is the probability of category k and P'_k is its derivative.
    We compute this numerically via finite differences.

    Args:
        theta: array of theta values at which to compute information
        discrimination: item discrimination parameters, shape (n_items,)
        difficulty: item threshold parameters, shape (n_items, K-1)

    Returns:
        Information matrix, shape (n_items, len(theta))
    """
    n_items = len(discrimination)
    n_theta = len(theta)
    info = np.zeros((n_items, n_theta))

    delta = 1e-5  # for numerical derivative

    for i in range(n_items):
        for t in range(n_theta):
            probs = grm_probability(theta[t], discrimination[i], difficulty[i])
            probs_plus = grm_probability(theta[t] + delta, discrimination[i], difficulty[i])
            probs_minus = grm_probability(theta[t] - delta, discrimination[i], difficulty[i])

            # Central difference derivative
            derivs = (probs_plus - probs_minus) / (2 * delta)

            # Information = sum of (derivative^2 / probability) for each category
            for k in range(len(probs)):
                if probs[k] > 1e-10:
                    info[i, t] += derivs[k] ** 2 / probs[k]

    return info
