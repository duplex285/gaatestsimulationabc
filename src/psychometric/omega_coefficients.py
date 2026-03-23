"""Omega coefficient computation for bifactor models.

Computes omega hierarchical, omega subscale, and explained common variance
from bifactor model loadings to determine whether subscale scores are
independently interpretable or dominated by a general factor.

Reference: McDonald (1999), Test Theory: A Unified Treatment
Reference: Reise, Bonifay, & Haviland (2013), Scoring and Modeling
           Issues in Bifactor Analysis, Psychological Assessment
Reference: Reise (2012), The Rediscovery of Bifactor Measurement Models,
           Multivariate Behavioral Research
"""

import numpy as np


def compute_omega_hierarchical(
    general_loadings: np.ndarray,
    specific_loadings: np.ndarray,
) -> float:
    """Compute omega hierarchical from bifactor loadings.

    Reference: McDonald (1999); Reise, Bonifay, & Haviland (2013)

    Omega-h = (sum of general loadings)^2 /
              [(sum of general loadings)^2 + sum of uniquenesses]

    where uniqueness for each item = 1 - general_loading^2 - specific_loading^2.

    Interpretation:
        omega_h > 0.80: essentially unidimensional, subscales add little
        omega_h > 0.50: general factor substantial, subscale interpretation cautious
        omega_h < 0.50: subscales are meaningfully distinct from general factor

    Args:
        general_loadings: loading of each item on the general factor, shape (n_items,)
        specific_loadings: loading of each item on its specific factor, shape (n_items,)

    Returns:
        Omega hierarchical value in [0, 1]
    """
    sum_general = np.sum(general_loadings)
    uniquenesses = 1.0 - general_loadings**2 - specific_loadings**2
    uniquenesses = np.maximum(uniquenesses, 0.0)  # clip negative uniquenesses

    numerator = sum_general**2
    denominator = numerator + np.sum(uniquenesses)

    if denominator <= 0:
        return 0.0

    return float(np.clip(numerator / denominator, 0.0, 1.0))


def compute_omega_subscale(
    general_loadings_subscale: np.ndarray,
    specific_loadings_subscale: np.ndarray,
) -> float:
    """Compute omega subscale for a single subscale from bifactor loadings.

    Reference: Reise, Bonifay, & Haviland (2013)

    Omega-s = (sum of specific loadings)^2 /
              [(sum of general loadings)^2 + (sum of specific loadings)^2 + sum of uniquenesses]

    Measures the proportion of reliable subscale variance attributable to the
    specific factor after removing the general factor.

    Interpretation:
        omega_s > 0.50: subscale has substantial unique reliable variance
        omega_s < 0.30: subscale adds little beyond general factor

    Args:
        general_loadings_subscale: general factor loadings for items in this subscale
        specific_loadings_subscale: specific factor loadings for items in this subscale

    Returns:
        Omega subscale value in [0, 1]
    """
    sum_specific = np.sum(specific_loadings_subscale)
    sum_general = np.sum(general_loadings_subscale)
    uniquenesses = 1.0 - general_loadings_subscale**2 - specific_loadings_subscale**2
    uniquenesses = np.maximum(uniquenesses, 0.0)

    numerator = sum_specific**2
    denominator = sum_general**2 + sum_specific**2 + np.sum(uniquenesses)

    if denominator <= 0:
        return 0.0

    return float(np.clip(numerator / denominator, 0.0, 1.0))


def compute_ecv(
    general_loadings: np.ndarray,
    specific_loadings: np.ndarray,
) -> float:
    """Compute Explained Common Variance from bifactor loadings.

    Reference: Reise, Bonifay, & Haviland (2013)

    ECV = sum(general_loadings^2) / [sum(general_loadings^2) + sum(specific_loadings^2)]

    Measures the proportion of common variance attributable to the general factor.

    Interpretation:
        ECV > 0.85: general factor accounts for most common variance
        ECV > 0.60: general factor is substantial
        ECV < 0.50: specific factors carry more common variance than general

    Args:
        general_loadings: loading of each item on the general factor, shape (n_items,)
        specific_loadings: loading of each item on its specific factor, shape (n_items,)

    Returns:
        ECV value in [0, 1]
    """
    gen_var = np.sum(general_loadings**2)
    spec_var = np.sum(specific_loadings**2)
    total = gen_var + spec_var

    if total <= 0:
        return 0.0

    return float(gen_var / total)
