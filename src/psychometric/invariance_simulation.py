"""Invariance simulation for ABC Assessment.

Generates multi-group synthetic data for measurement invariance testing.
Groups can differ in means (testing scalar invariance) or factor loadings
(testing metric invariance).

Reference: abc-assessment-spec Section 11.1 (simulation parameters)
"""

import numpy as np


def simulate_multigroup_data(
    group_labels: list[str] | None = None,
    n_per_group: int = 300,
    mean_shift: dict[str, float] | None = None,
    loading_shift: dict[str, float] | None = None,
    base_loading: float = 0.7,
    n_factors: int = 6,
    items_per_factor: int = 4,
    seed: int = 42,
) -> dict:
    """Generate multi-group data for invariance testing.

    Reference: abc-assessment-spec Section 11.1

    Each group's data is generated from a 6-factor model. Groups can
    differ in factor means (mean_shift) or factor loadings (loading_shift).
    Identical structure across groups = invariance holds.

    Args:
        group_labels: list of group names (default: ["team_sport", "individual_sport"])
        n_per_group: respondents per group
        mean_shift: dict mapping group name to factor mean shift (default: no shift)
        loading_shift: dict mapping group name to loading adjustment (default: no shift)
        base_loading: default factor loading for all items
        n_factors: number of latent factors
        items_per_factor: items per factor
        seed: random seed

    Returns:
        dict with key "groups": {group_name: np.ndarray of shape (n_per_group, n_items)}
    """
    if group_labels is None:
        group_labels = ["team_sport", "individual_sport"]
    if mean_shift is None:
        mean_shift = {}
    if loading_shift is None:
        loading_shift = {}

    rng = np.random.default_rng(seed)
    n_items = n_factors * items_per_factor
    groups = {}

    for _g_idx, group in enumerate(group_labels):
        # Group-specific parameters
        m_shift = mean_shift.get(group, 0.0)
        l_shift = loading_shift.get(group, 0.0)

        # Generate factor scores with optional mean shift
        factors = rng.standard_normal((n_per_group, n_factors)) + m_shift

        # Generate items from factor model
        data = np.zeros((n_per_group, n_items))
        for f in range(n_factors):
            for i in range(items_per_factor):
                item_idx = f * items_per_factor + i
                loading = base_loading + l_shift
                loading = max(0.1, min(0.95, loading))  # keep in valid range
                error_var = max(0.05, 1.0 - loading**2)
                data[:, item_idx] = loading * factors[:, f] + np.sqrt(
                    error_var
                ) * rng.standard_normal(n_per_group)

        groups[group] = data

    return {"groups": groups}
