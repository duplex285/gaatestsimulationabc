"""Tier-specific reliability reporting for ABC Assessment.

Reports reliability evidence separately for each measurement tier
(6, 18, 36 items) and determines which score interpretations each
tier can support. With 6 items per subscale at the 36-item tier,
Phase 2b showed per-domain classification agreement of only ~67%.
The 6-item and 18-item tiers will be worse.

Reference: APA/AERA/NCME Standards (2014), Standards 2.3, 2.9
Reference: abc-assessment-spec Section 1.2 (measurement tiers)
"""

import numpy as np

from src.psychometric.irt_estimation import item_information
from src.psychometric.irt_subscale_scoring import FACTOR_ITEM_INDICES

# Tier definitions: which items are included at each tier.
# 6-item tier: 1 item per subscale (first item of each)
# 18-item tier: 3 items per subscale (first three of each)
# 36-item tier: all 6 items per subscale
TIER_DEFINITIONS = {
    "6_item": {factor: indices[:1] for factor, indices in FACTOR_ITEM_INDICES.items()},
    "18_item": {factor: indices[:3] for factor, indices in FACTOR_ITEM_INDICES.items()},
    "36_item": {factor: indices[:6] for factor, indices in FACTOR_ITEM_INDICES.items()},
}

# Interpretation types and their minimum reliability requirements
INTERPRETATION_REQUIREMENTS = {
    "directional_subscale_signal": {
        "description": "Which subscales are relatively high or low",
        "min_reliability": 0.40,
        "min_items_per_subscale": 1,
    },
    "subscale_score_reporting": {
        "description": "Reporting individual subscale scores with confidence bands",
        "min_reliability": 0.60,
        "min_items_per_subscale": 2,
    },
    "domain_state_classification": {
        "description": "Classifying into Thriving/Vulnerable/Mild/Distressed",
        "min_reliability": 0.70,
        "min_items_per_subscale": 3,
    },
    "24_type_classification": {
        "description": "Assigning one of 24 named archetypes",
        "min_reliability": 0.75,
        "min_items_per_subscale": 4,
    },
    "frustration_signature_detection": {
        "description": "Detecting risk patterns from frustration scores",
        "min_reliability": 0.65,
        "min_items_per_subscale": 2,
    },
    "reliable_change_detection": {
        "description": "Detecting reliable change between administrations via RCI",
        "min_reliability": 0.70,
        "min_items_per_subscale": 3,
    },
}


def _get_tier_item_indices(tier_name: str) -> list[int]:
    """Get flat list of all item indices for a tier."""
    tier_def = TIER_DEFINITIONS[tier_name]
    indices = []
    for factor_indices in tier_def.values():
        indices.extend(factor_indices)
    return sorted(indices)


def _compute_marginal_reliability(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    item_indices: list[int],
    theta_grid: np.ndarray | None = None,
) -> tuple[float, float]:
    """Compute marginal reliability and mean SEM for a subset of items.

    Marginal reliability is computed as:
        r = 1 - (1 / mean_information)
    averaged over the theta distribution.

    This is analogous to coefficient alpha but derived from IRT,
    making it appropriate for adaptive and variable-length tests.

    Returns:
        (marginal_reliability, mean_sem)
    """
    if theta_grid is None:
        theta_grid = np.linspace(-3, 3, 61)

    sub_disc = discrimination[item_indices]
    sub_diff = difficulty[item_indices]

    info = item_information(theta_grid, sub_disc, sub_diff)
    total_info = np.sum(info, axis=0)  # sum across items at each theta

    # SEM = 1/sqrt(info) at each theta
    sem = np.where(total_info > 0, 1.0 / np.sqrt(total_info), float("inf"))
    mean_sem = float(np.mean(sem[np.isfinite(sem)]))

    # Marginal reliability: average across theta grid
    # r = 1 - mean(SEM^2) / var(theta)
    # For standard normal theta, var = 1
    mean_error_var = float(np.mean(sem[np.isfinite(sem)] ** 2))
    marginal_reliability = max(0.0, min(1.0, 1.0 - mean_error_var))

    return marginal_reliability, mean_sem


def compute_tier_reliability(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
) -> dict:
    """Compute reliability and SEM for each measurement tier.

    Reference: Standard 2.9

    Args:
        discrimination: item discrimination parameters, shape (36,)
        difficulty: item threshold parameters, shape (36, K-1)

    Returns:
        dict mapping tier name to {marginal_reliability, mean_sem, n_items, items_per_subscale}
    """
    result = {}
    for tier_name, tier_factors in TIER_DEFINITIONS.items():
        indices = _get_tier_item_indices(tier_name)
        items_per_sub = len(next(iter(tier_factors.values())))

        rel, sem = _compute_marginal_reliability(discrimination, difficulty, indices)

        result[tier_name] = {
            "marginal_reliability": rel,
            "mean_sem": sem,
            "n_items": len(indices),
            "items_per_subscale": items_per_sub,
        }

    return result


def compute_tier_information_curves(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
    theta_grid: np.ndarray | None = None,
) -> dict:
    """Compute test information functions for each tier.

    Reference: Baker & Kim (2004)

    Args:
        discrimination: item discrimination parameters, shape (36,)
        difficulty: item threshold parameters, shape (36, K-1)
        theta_grid: theta values at which to evaluate (default: -3 to 3)

    Returns:
        dict mapping tier name to {theta, information, peak_theta, peak_information}
    """
    if theta_grid is None:
        theta_grid = np.linspace(-3, 3, 61)

    result = {}
    for tier_name in TIER_DEFINITIONS:
        indices = _get_tier_item_indices(tier_name)
        sub_disc = discrimination[indices]
        sub_diff = difficulty[indices]

        info = item_information(theta_grid, sub_disc, sub_diff)
        total_info = np.sum(info, axis=0)

        peak_idx = np.argmax(total_info)

        result[tier_name] = {
            "theta": theta_grid,
            "information": total_info,
            "peak_theta": float(theta_grid[peak_idx]),
            "peak_information": float(total_info[peak_idx]),
        }

    return result


def determine_supportable_interpretations(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
) -> dict:
    """Determine which interpretations each tier can support.

    Reference: Standards 2.3, 2.9

    For each tier, checks whether the marginal reliability and items
    per subscale meet the minimum requirements for each interpretation type.

    Args:
        discrimination: item discrimination parameters, shape (24,)
        difficulty: item threshold parameters, shape (24, K-1)

    Returns:
        dict mapping tier name to {supported: [...], not_supported: [...], details: {...}}
    """
    tier_rel = compute_tier_reliability(discrimination, difficulty)

    result = {}
    for tier_name, tier_data in tier_rel.items():
        rel = tier_data["marginal_reliability"]
        items_per_sub = tier_data["items_per_subscale"]

        supported = []
        not_supported = []
        details = {}

        for interp_name, requirements in INTERPRETATION_REQUIREMENTS.items():
            meets_reliability = rel >= requirements["min_reliability"]
            meets_items = items_per_sub >= requirements["min_items_per_subscale"]
            is_supported = meets_reliability and meets_items

            if is_supported:
                supported.append(interp_name)
            else:
                not_supported.append(interp_name)

            details[interp_name] = {
                "supported": is_supported,
                "reliability_met": meets_reliability,
                "items_met": meets_items,
                "actual_reliability": rel,
                "required_reliability": requirements["min_reliability"],
                "actual_items": items_per_sub,
                "required_items": requirements["min_items_per_subscale"],
            }

        result[tier_name] = {
            "supported": supported,
            "not_supported": not_supported,
            "details": details,
        }

    return result


def generate_tier_reliability_report(
    discrimination: np.ndarray,
    difficulty: np.ndarray,
) -> dict:
    """Generate complete tier reliability report.

    Aggregates reliability, information curves, and supportable
    interpretations into a single structured report.

    Args:
        discrimination: item discrimination parameters, shape (36,)
        difficulty: item threshold parameters, shape (36, K-1)

    Returns:
        dict with keys: reliability, information_curves, supportable_interpretations
    """
    return {
        "reliability": compute_tier_reliability(discrimination, difficulty),
        "information_curves": compute_tier_information_curves(discrimination, difficulty),
        "supportable_interpretations": determine_supportable_interpretations(
            discrimination, difficulty
        ),
    }
