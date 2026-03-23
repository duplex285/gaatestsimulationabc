"""Differential Item Functioning analysis for ABC Assessment.

Detects items that function differently across groups after controlling
for overall trait level. An item with DIF gives systematically different
responses to people from different groups who have the same ability.

Reference: Swaminathan & Rogers (1990), Detecting DIF Using Logistic Regression
Reference: APA/AERA/NCME Standards (2014), Standard 3.8
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def detect_dif(
    responses: np.ndarray,
    group: np.ndarray,
    total_scores: np.ndarray,
    effect_size_threshold: float = 0.10,
) -> list[dict]:
    """Detect DIF using logistic regression for each item.

    Reference: Swaminathan & Rogers (1990)

    For each item, fits two logistic regression models predicting
    the probability of a high response (>= median) from:
        Model 1: total_score only (no group effect)
        Model 2: total_score + group + total_score*group

    DIF is flagged when the group variable adds substantial predictive
    power, measured by the change in pseudo-R-squared (Nagelkerke).
    We approximate this with the change in accuracy as a simpler metric.

    Args:
        responses: response matrix, shape (n_persons, n_items), values in [1, 7]
        group: group membership labels, shape (n_persons,)
        total_scores: total test scores per person, shape (n_persons,)
        effect_size_threshold: delta-R-squared above which DIF is flagged

    Returns:
        List of dicts (one per item), each with:
            item_index: int
            effect_size: float (change in prediction accuracy)
            flagged: bool
    """
    n_persons, n_items = responses.shape
    group_arr = np.array(group)
    unique_groups = np.unique(group_arr)

    # Encode group as numeric
    group_numeric = np.zeros(n_persons)
    for i, g in enumerate(unique_groups):
        group_numeric[group_arr == g] = i

    scaler = StandardScaler()
    total_z = scaler.fit_transform(total_scores.reshape(-1, 1)).ravel()

    results = []

    for item_idx in range(n_items):
        item_responses = responses[:, item_idx]
        # Binarize: above median = 1, below = 0
        median_resp = np.median(item_responses)
        binary_resp = (item_responses >= median_resp).astype(int)

        # Skip if no variance in binary response
        if len(np.unique(binary_resp)) < 2:
            results.append(
                {
                    "item_index": item_idx,
                    "effect_size": 0.0,
                    "flagged": False,
                }
            )
            continue

        # Model 1: total score only
        X1 = total_z.reshape(-1, 1)
        try:
            m1 = LogisticRegression(max_iter=1000, solver="lbfgs")
            m1.fit(X1, binary_resp)
            acc1 = m1.score(X1, binary_resp)
        except Exception:
            acc1 = 0.5

        # Model 2: total score + group + interaction
        interaction = total_z * group_numeric
        X2 = np.column_stack([total_z, group_numeric, interaction])
        try:
            m2 = LogisticRegression(max_iter=1000, solver="lbfgs")
            m2.fit(X2, binary_resp)
            acc2 = m2.score(X2, binary_resp)
        except Exception:
            acc2 = acc1

        effect_size = abs(acc2 - acc1)

        results.append(
            {
                "item_index": item_idx,
                "effect_size": float(effect_size),
                "flagged": effect_size > effect_size_threshold,
            }
        )

    return results
