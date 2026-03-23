"""Decision consistency analysis for ABC Assessment.

Quantifies how reliably the instrument classifies athletes into domain states,
types, and frustration signature categories across repeated administrations.

Reference: APA/AERA/NCME Standards (2014), Standards 2.4, 2.14, 2.16
Reference: Cohen (1960), A Coefficient of Agreement for Nominal Scales
Reference: Jacobson & Truax (1991), Clinical Significance
"""

import numpy as np

from src.psychometric.irt_estimation import item_information, score_theta_eap
from src.psychometric.irt_simulation import simulate_grm_responses
from src.psychometric.irt_subscale_scoring import (
    FACTOR_ITEM_INDICES,
    theta_to_subscale_score,
)

# Domain state thresholds (from domain_classification.py)
SAT_THRESHOLD = 6.46
FRUST_THRESHOLD = 4.38

# Domain pairs mapping (from domain_classification.py)
DOMAIN_PAIRS = {
    "ambition": ("a_sat", "a_frust"),
    "belonging": ("b_sat", "b_frust"),
    "craft": ("c_sat", "c_frust"),
}

# Type derivation threshold (from type_derivation.py)
TYPE_ACTIVATION_THRESHOLD = 5.5
FRUST_MODIFIER_THRESHOLD = 5.0


def _classify_domain_state(sat: float, frust: float) -> str:
    """Classify a single domain state from sat/frust scores.

    Reference: abc-assessment-spec Section 2.2
    """
    high_sat = sat >= SAT_THRESHOLD
    high_frust = frust >= FRUST_THRESHOLD
    if high_sat and not high_frust:
        return "Thriving"
    if high_sat and high_frust:
        return "Vulnerable"
    if not high_sat and not high_frust:
        return "Mild"
    return "Distressed"


def _derive_type_name(subscales: dict[str, float]) -> str:
    """Derive the 24-type name from subscale scores.

    Simplified version of type_derivation.py for consistency analysis.
    Reference: abc-assessment-spec Section 2.3
    """
    # Base pattern from satisfaction activation
    a_strong = subscales.get("a_sat", 0) >= TYPE_ACTIVATION_THRESHOLD
    b_strong = subscales.get("b_sat", 0) >= TYPE_ACTIVATION_THRESHOLD
    c_strong = subscales.get("c_sat", 0) >= TYPE_ACTIVATION_THRESHOLD

    patterns = {
        (True, True, True): "Integrator",
        (True, True, False): "Captain",
        (True, False, True): "Architect",
        (False, True, True): "Mentor",
        (True, False, False): "Pioneer",
        (False, True, False): "Anchor",
        (False, False, True): "Artisan",
        (False, False, False): "Seeker",
    }
    base = patterns[(a_strong, b_strong, c_strong)]

    # Frustration modifier
    frust_count = sum(
        1
        for key in ["a_frust", "b_frust", "c_frust"]
        if subscales.get(key, 0) >= FRUST_MODIFIER_THRESHOLD
    )
    if frust_count == 0:
        modifier = "Steady"
    elif frust_count == 1:
        modifier = "Striving"
    else:
        modifier = "Resolute"

    return f"{modifier} {base}"


def _score_subscales_from_responses(
    responses: np.ndarray,
    discrimination: np.ndarray,
    difficulty: np.ndarray,
) -> list[dict[str, float]]:
    """Score all persons into 6 subscales using IRT.

    Returns list of dicts, one per person.
    """
    n_persons = responses.shape[0]
    all_subscales = []

    for factor, indices in FACTOR_ITEM_INDICES.items():
        factor_responses = responses[:, indices]
        factor_disc = discrimination[indices]
        factor_diff = difficulty[indices]
        theta_hat, _ = score_theta_eap(factor_responses, factor_disc, factor_diff)

        for p in range(n_persons):
            if p >= len(all_subscales):
                all_subscales.append({})
            all_subscales[p][factor] = theta_to_subscale_score(theta_hat[p])

    return all_subscales


def simulate_classification_agreement(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    n_persons: int = 200,
    n_replications: int = 2,
    seed: int = 42,
) -> dict:
    """Simulate classification agreement across independent administrations.

    Reference: Standard 2.16

    Generates true theta values for n_persons, then simulates n_replications
    independent response sets from the same true theta. Scores each replication
    and classifies into domain states and types. Reports agreement rates.

    Args:
        discrimination: item discrimination parameters, shape (n_items,)
        difficulty: item threshold parameters, shape (n_items, K-1)
        n_persons: number of simulated persons
        n_replications: number of independent administrations (default 2)
        seed: random seed for reproducibility

    Returns:
        dict with keys:
            domain_state_agreement: proportion classified same across all replications
            type_agreement: proportion with same type name across replications
            per_domain_agreement: {domain: agreement_rate} for each domain
            n_persons: sample size
    """
    rng = np.random.default_rng(seed)
    n_items = len(discrimination)

    # Generate true theta (one per subscale factor, 6 factors)
    # Use per-factor theta for realistic simulation
    true_theta_per_factor = rng.standard_normal((n_persons, 6))

    # Generate full true theta vector (expand to item level)
    # Each person gets a theta for each of 6 factors
    # Simulate responses from factor-level theta
    replication_classifications = []

    for rep in range(n_replications):
        rep_seed = seed + rep * 1000

        # Build full response matrix: for each factor, simulate 4 items
        responses = np.zeros((n_persons, n_items), dtype=int)
        list(FACTOR_ITEM_INDICES.keys())

        for f_idx, (_factor, indices) in enumerate(FACTOR_ITEM_INDICES.items()):
            factor_disc = discrimination[indices]
            factor_diff = difficulty[indices]
            factor_theta = true_theta_per_factor[:, f_idx]

            factor_responses = simulate_grm_responses(
                factor_theta, factor_disc, factor_diff, seed=rep_seed + f_idx
            )
            responses[:, indices] = factor_responses

        # Score and classify
        subscales_list = _score_subscales_from_responses(responses, discrimination, difficulty)

        classifications = []
        for p in range(n_persons):
            subscales = subscales_list[p]
            domain_states = {}
            for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
                domain_states[domain] = _classify_domain_state(
                    subscales[sat_key], subscales[frust_key]
                )
            type_name = _derive_type_name(subscales)
            classifications.append(
                {
                    "domain_states": domain_states,
                    "type_name": type_name,
                }
            )

        replication_classifications.append(classifications)

    # Compute agreement between replication 0 and replication 1
    rep_a = replication_classifications[0]
    rep_b = replication_classifications[1]

    # Domain state agreement: all 3 domains must match
    domain_match = 0
    per_domain_match = dict.fromkeys(DOMAIN_PAIRS, 0)
    type_match = 0

    for p in range(n_persons):
        all_domains_match = True
        for domain in DOMAIN_PAIRS:
            if rep_a[p]["domain_states"][domain] == rep_b[p]["domain_states"][domain]:
                per_domain_match[domain] += 1
            else:
                all_domains_match = False
        if all_domains_match:
            domain_match += 1
        if rep_a[p]["type_name"] == rep_b[p]["type_name"]:
            type_match += 1

    return {
        "domain_state_agreement": domain_match / n_persons,
        "type_agreement": type_match / n_persons,
        "per_domain_agreement": {d: count / n_persons for d, count in per_domain_match.items()},
        "n_persons": n_persons,
    }


def compute_difference_score_reliability(
    sat_scores: dict[str, np.ndarray],
    frust_scores: dict[str, np.ndarray],  # noqa: ARG001
    reliability_sat: float = 0.80,
    reliability_frust: float = 0.80,
    r_sat_frust: float = 0.0,
) -> dict[str, float]:
    """Compute reliability of satisfaction-frustration difference scores.

    Reference: Standard 2.4
    Reference: Nunnally & Bernstein (1994), Psychometric Theory

    Formula: r_diff = (r_x + r_y - 2*r_xy) / (2 - 2*r_xy)

    where r_x and r_y are subscale reliabilities and r_xy is their correlation.
    When r_xy is negative (as SDT predicts for sat-frust), the difference
    score is MORE reliable than when they are independent.

    Args:
        sat_scores: dict mapping sat subscale name to score array
        frust_scores: dict mapping frust subscale name to score array
        reliability_sat: reliability coefficient for satisfaction subscales
        reliability_frust: reliability coefficient for frustration subscales
        r_sat_frust: correlation between satisfaction and frustration (default 0)

    Returns:
        dict mapping domain name to difference score reliability
    """
    domain_map = {
        "a_sat": "ambition",
        "b_sat": "belonging",
        "c_sat": "craft",
    }

    result = {}
    for sat_key, domain in domain_map.items():
        if sat_key in sat_scores:
            r_x = reliability_sat
            r_y = reliability_frust
            r_xy = r_sat_frust

            denominator = 2.0 - 2.0 * r_xy
            if abs(denominator) < 1e-10:
                result[domain] = 0.0
            else:
                r_diff = (r_x + r_y - 2.0 * r_xy) / denominator
                result[domain] = float(max(0.0, min(1.0, r_diff)))

    return result


def compute_conditional_sem_at_thresholds(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    thresholds: dict[str, float],
) -> dict[str, float]:
    """Compute conditional SEM at specific score thresholds.

    Reference: Standard 2.14

    Converts each threshold from the 0-10 scale back to theta, computes
    the test information at that theta, and returns 1/sqrt(information) as
    the conditional SEM.

    Args:
        discrimination: item discrimination parameters, shape (n_items,)
        difficulty: item threshold parameters, shape (n_items, K-1)
        thresholds: dict mapping threshold name to score on 0-10 scale

    Returns:
        dict mapping threshold name to conditional SEM (in theta units)
    """
    result = {}

    for name, score_value in thresholds.items():
        # Convert 0-10 score back to theta: theta = (score - 5.0) / 2.5
        theta_at_threshold = (score_value - 5.0) / 2.5
        theta_array = np.array([theta_at_threshold])

        # Compute total test information at this theta
        info = item_information(theta_array, discrimination, difficulty)
        total_info = np.sum(info[:, 0])

        # SEM = 1 / sqrt(information)
        sem = 1.0 / np.sqrt(total_info) if total_info > 0 else float("inf")

        result[name] = float(sem)

    return result


def compute_classification_kappa(
    labels_a: np.ndarray,
    labels_b: np.ndarray,
) -> float:
    """Compute Cohen's kappa for classification agreement.

    Reference: Cohen (1960), A Coefficient of Agreement for Nominal Scales

    Kappa = (p_o - p_e) / (1 - p_e)

    where p_o is observed agreement and p_e is expected agreement by chance.

    Args:
        labels_a: classification labels from administration A, shape (n,)
        labels_b: classification labels from administration B, shape (n,)

    Returns:
        Cohen's kappa value in [-1, 1]
    """
    n = len(labels_a)
    if n == 0:
        return 0.0

    # Get all unique labels
    all_labels = list(set(np.concatenate([labels_a, labels_b])))

    # Observed agreement
    p_o = np.sum(labels_a == labels_b) / n

    # Expected agreement by chance
    p_e = 0.0
    for label in all_labels:
        p_a = np.sum(labels_a == label) / n
        p_b = np.sum(labels_b == label) / n
        p_e += p_a * p_b

    if abs(1.0 - p_e) < 1e-10:
        return 1.0 if p_o == 1.0 else 0.0

    kappa = (p_o - p_e) / (1.0 - p_e)
    return float(kappa)
