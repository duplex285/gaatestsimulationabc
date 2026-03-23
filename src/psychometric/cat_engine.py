"""CAT engine for ABC Assessment.

Implements standard computerized adaptive testing: maximum information
item selection, EAP theta updating after each response, and stopping
rules based on SE threshold or maximum items.

Reference: Chang & Ying (1999), Maximum Information Item Selection
Reference: Bock & Mislevy (1982), Adaptive EAP Estimation
Reference: PROMIS CAT administration guidelines
"""

import numpy as np

from src.psychometric.irt_simulation import grm_probability
from src.psychometric.item_bank import ItemBank, ItemBankEntry


def select_next_item(
    item_bank: ItemBank,
    administered: set[str],
    current_theta: float,
    content_constraints: dict[str, int] | None = None,
) -> ItemBankEntry | None:
    """Select the next item via maximum Fisher information.

    Reference: Chang & Ying (1999)

    Selects the unadministered item with the highest information at
    the current theta estimate, optionally respecting content balance.

    Args:
        item_bank: the item bank to select from
        administered: set of already-administered item codes
        current_theta: current theta estimate
        content_constraints: optional max items per content area

    Returns:
        The selected ItemBankEntry, or None if no items remain
    """
    available = item_bank.get_unadministered(administered)
    if not available:
        return None

    # Apply content constraints if specified
    if content_constraints:
        administered_counts = {}
        for code in administered:
            item = item_bank.get_item_by_code(code)
            if item:
                area = item.content_area
                administered_counts[area] = administered_counts.get(area, 0) + 1

        filtered = []
        for item in available:
            area_count = administered_counts.get(item.content_area, 0)
            max_allowed = content_constraints.get(item.content_area, float("inf"))
            if area_count < max_allowed:
                filtered.append(item)

        if filtered:
            available = filtered

    # Select by maximum information
    best_item = None
    best_info = -1.0
    for item in available:
        info = item_bank.get_item_information_at_theta(item, current_theta)
        if info > best_info:
            best_info = info
            best_item = item

    return best_item


def update_theta(
    item_bank: ItemBank,
    responses: dict[str, int],
    prior_mean: float = 0.0,
    prior_sd: float = 1.0,
    quadrature_points: int = 41,
) -> tuple[float, float]:
    """Re-estimate theta after each response using EAP.

    Reference: Bock & Mislevy (1982)

    Args:
        item_bank: the item bank containing item parameters
        responses: dict mapping item_code to response value (1-7)
        prior_mean: prior mean for theta
        prior_sd: prior SD for theta
        quadrature_points: number of integration points

    Returns:
        (theta_estimate, standard_error)
    """
    from scipy.stats import norm

    theta_grid = np.linspace(
        prior_mean - 4 * prior_sd, prior_mean + 4 * prior_sd, quadrature_points
    )
    prior_weights = norm.pdf(theta_grid, loc=prior_mean, scale=prior_sd)
    prior_weights /= np.sum(prior_weights)

    log_likelihood = np.zeros(quadrature_points)
    for q in range(quadrature_points):
        ll = 0.0
        for item_code, response in responses.items():
            item = item_bank.get_item_by_code(item_code)
            if item is None:
                continue
            probs = grm_probability(theta_grid[q], item.discrimination, item.difficulty)
            category_idx = response - 1
            if 0 <= category_idx < len(probs):
                ll += np.log(max(probs[category_idx], 1e-15))
        log_likelihood[q] = ll

    log_posterior = log_likelihood + np.log(np.maximum(prior_weights, 1e-15))
    log_posterior -= np.max(log_posterior)
    posterior = np.exp(log_posterior)
    posterior /= np.sum(posterior)

    theta_hat = float(np.sum(posterior * theta_grid))
    variance = float(np.sum(posterior * (theta_grid - theta_hat) ** 2))
    se = float(np.sqrt(max(variance, 1e-10)))

    return theta_hat, se


def check_stopping_rule(
    current_se: float,
    n_administered: int,
    se_threshold: float = 0.30,
    max_items: int = 18,
    min_items: int = 4,
) -> bool:
    """Check whether CAT should terminate.

    Reference: PROMIS CAT administration guidelines

    Stops when SE < threshold OR max items reached.
    Never stops before min_items.

    Args:
        current_se: current standard error of theta estimate
        n_administered: number of items administered so far
        se_threshold: SE below which to stop
        max_items: maximum items to administer
        min_items: minimum items before stopping allowed

    Returns:
        True if CAT should stop
    """
    if n_administered < min_items:
        return False
    if n_administered >= max_items:
        return True
    return current_se < se_threshold


def simulate_cat_administration(
    item_bank: ItemBank,
    true_theta: float,
    se_threshold: float = 0.30,
    max_items: int = 18,
    min_items: int = 4,
    seed: int = 42,
) -> dict:
    """Simulate a complete CAT administration for one respondent.

    Reference: PROMIS CAT administration guidelines

    Args:
        item_bank: the item bank
        true_theta: the respondent's true latent trait value
        se_threshold: SE stopping threshold
        max_items: maximum items
        min_items: minimum items
        seed: random seed for response simulation

    Returns:
        dict with: administered_items, responses, theta_history,
                   se_history, final_theta, final_se, n_items
    """
    rng = np.random.default_rng(seed)

    administered = set()
    administered_items = []
    responses = {}
    theta_history = []
    se_history = []

    current_theta = 0.0  # start at prior mean
    current_se = 1.0  # start with prior SE

    while not check_stopping_rule(
        current_se, len(administered), se_threshold, max_items, min_items
    ):
        # Select next item
        item = select_next_item(item_bank, administered, current_theta)
        if item is None:
            break

        # Simulate response from true theta
        probs = grm_probability(true_theta, item.discrimination, item.difficulty)
        response = int(rng.choice(np.arange(1, len(probs) + 1), p=probs))

        # Record
        administered.add(item.item_code)
        administered_items.append(item.item_code)
        responses[item.item_code] = response

        # Update theta
        current_theta, current_se = update_theta(item_bank, responses)
        theta_history.append(current_theta)
        se_history.append(current_se)

    return {
        "administered_items": administered_items,
        "responses": responses,
        "theta_history": theta_history,
        "se_history": se_history,
        "final_theta": current_theta,
        "final_se": current_se,
        "n_items": len(administered),
    }
