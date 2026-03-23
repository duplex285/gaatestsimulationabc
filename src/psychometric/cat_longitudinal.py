"""Longitudinal CAT for ABC Assessment.

Adapts computerized adaptive testing for repeated measurement, where
the goal is not just precise estimation at each timepoint but also
sensitive detection of change between timepoints.

Standard CAT selects items that maximize information at the current
theta estimate. Longitudinal CAT selects items that maximize information
at the boundary between the previous theta and the current theta estimate,
increasing sensitivity to change.

Reference: abc-assessment-spec Section 11.7 (trajectory detection)
Reference: Phase 2b finding: conditional SEM ~0.20 theta units at thresholds
"""

import numpy as np

from src.psychometric.cat_engine import (
    check_stopping_rule,
    simulate_cat_administration,
    update_theta,
)
from src.psychometric.item_bank import ItemBank, ItemBankEntry


def select_next_item_change_aware(
    item_bank: ItemBank,
    administered: set[str],
    current_theta: float,
    previous_theta: float,
) -> ItemBankEntry | None:
    """Select next item maximizing information at the change boundary.

    Instead of maximizing information at current_theta (standard CAT),
    maximizes information at the midpoint between previous_theta and
    current_theta. This makes the test more sensitive to detecting
    whether the person has actually changed.

    Args:
        item_bank: the item bank
        administered: set of already-administered item codes
        current_theta: current theta estimate
        previous_theta: theta estimate from previous administration

    Returns:
        The selected ItemBankEntry, or None if no items remain
    """
    available = item_bank.get_unadministered(administered)
    if not available:
        return None

    # Target theta: midpoint between previous and current
    # This is where change detection is most informative
    target_theta = (previous_theta + current_theta) / 2.0

    best_item = None
    best_info = -1.0
    for item in available:
        info = item_bank.get_item_information_at_theta(item, target_theta)
        if info > best_info:
            best_info = info
            best_item = item

    return best_item


def simulate_longitudinal_cat(
    item_bank: ItemBank,
    true_thetas: list[float],
    se_threshold: float = 0.35,
    max_items: int = 18,
    min_items: int = 4,
    seed: int = 42,
) -> dict:
    """Run CAT across multiple timepoints for the same person.

    At each timepoint after the first, uses change-aware item selection
    targeting the boundary between the previous and current theta.

    Args:
        item_bank: the item bank
        true_thetas: true theta at each timepoint
        se_threshold: SE stopping threshold per administration
        max_items: max items per administration
        min_items: min items per administration
        seed: random seed

    Returns:
        dict with:
            timepoints: list of per-timepoint results (theta, se, n_items)
            change_detected: list of bools (n_timepoints - 1)
    """
    n_timepoints = len(true_thetas)
    timepoints = []
    change_detected = []

    previous_theta = None

    for t in range(n_timepoints):
        true_theta = true_thetas[t]
        t_seed = seed + t * 100

        if t == 0 or previous_theta is None:
            # First timepoint: standard CAT
            result = simulate_cat_administration(
                item_bank,
                true_theta=true_theta,
                se_threshold=se_threshold,
                max_items=max_items,
                min_items=min_items,
                seed=t_seed,
            )
        else:
            # Subsequent timepoints: change-aware CAT
            result = _run_change_aware_cat(
                item_bank,
                true_theta=true_theta,
                previous_theta=previous_theta,
                se_threshold=se_threshold,
                max_items=max_items,
                min_items=min_items,
                seed=t_seed,
            )

        tp_result = {
            "theta": result["final_theta"],
            "se": result["final_se"],
            "n_items": result["n_items"],
        }
        timepoints.append(tp_result)

        # Detect change from previous timepoint
        if previous_theta is not None:
            prev_se = timepoints[t - 1]["se"]
            curr_se = result["final_se"]
            se_diff = np.sqrt(prev_se**2 + curr_se**2)
            change = abs(result["final_theta"] - previous_theta)
            detected = change > 1.96 * se_diff if se_diff > 0 else False
            change_detected.append(bool(detected))

        previous_theta = result["final_theta"]

    return {
        "timepoints": timepoints,
        "change_detected": change_detected,
    }


def _run_change_aware_cat(
    item_bank: ItemBank,
    true_theta: float,
    previous_theta: float,
    se_threshold: float,
    max_items: int,
    min_items: int,
    seed: int,
) -> dict:
    """Run a single CAT administration with change-aware item selection."""
    from src.psychometric.irt_simulation import grm_probability

    rng = np.random.default_rng(seed)

    administered = set()
    administered_items = []
    responses = {}
    theta_history = []
    se_history = []

    current_theta = previous_theta  # start from previous estimate
    current_se = 1.0

    while not check_stopping_rule(
        current_se, len(administered), se_threshold, max_items, min_items
    ):
        # Change-aware item selection
        item = select_next_item_change_aware(item_bank, administered, current_theta, previous_theta)
        if item is None:
            break

        # Simulate response
        probs = grm_probability(true_theta, item.discrimination, item.difficulty)
        response = int(rng.choice(np.arange(1, len(probs) + 1), p=probs))

        administered.add(item.item_code)
        administered_items.append(item.item_code)
        responses[item.item_code] = response

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


def compare_fixed_vs_cat_change_sensitivity(
    item_bank: ItemBank,
    n_persons: int = 100,
    change_magnitude: float = 1.0,
    se_threshold: float = 0.35,
    max_items: int = 18,
    seed: int = 42,
) -> dict:
    """Compare fixed-form vs CAT for detecting a known change.

    Simulates n_persons who each have theta=0 at T1 and theta=change_magnitude
    at T2. Compares how often the change is detected (RCI > 1.96) using:
    - Fixed form: all 36 items at both timepoints
    - CAT: adaptive administration at both timepoints

    Args:
        item_bank: the item bank
        n_persons: number of simulated persons
        change_magnitude: true theta change between T1 and T2
        se_threshold: CAT stopping threshold
        max_items: max items for CAT
        seed: random seed

    Returns:
        dict with fixed_sensitivity, cat_sensitivity, fixed_mean_items, cat_mean_items
    """
    fixed_detected = 0
    cat_detected = 0
    cat_total_items = 0
    fixed_total_items = 0

    for p in range(n_persons):
        p_seed = seed + p

        # Fixed form: use all items at both timepoints
        fixed_t1 = simulate_cat_administration(
            item_bank,
            true_theta=0.0,
            se_threshold=0.01,
            max_items=36,
            min_items=36,
            seed=p_seed,
        )
        fixed_t2 = simulate_cat_administration(
            item_bank,
            true_theta=change_magnitude,
            se_threshold=0.01,
            max_items=36,
            min_items=36,
            seed=p_seed + 50000,
        )

        se_diff_fixed = np.sqrt(fixed_t1["final_se"] ** 2 + fixed_t2["final_se"] ** 2)
        if se_diff_fixed > 0:
            rci_fixed = abs(fixed_t2["final_theta"] - fixed_t1["final_theta"]) / se_diff_fixed
            if rci_fixed > 1.96:
                fixed_detected += 1
        fixed_total_items += fixed_t1["n_items"] + fixed_t2["n_items"]

        # CAT: adaptive at both timepoints
        cat_result = simulate_longitudinal_cat(
            item_bank,
            true_thetas=[0.0, change_magnitude],
            se_threshold=se_threshold,
            max_items=max_items,
            seed=p_seed,
        )
        if cat_result["change_detected"] and cat_result["change_detected"][0]:
            cat_detected += 1
        cat_total_items += sum(tp["n_items"] for tp in cat_result["timepoints"])

    return {
        "fixed_sensitivity": fixed_detected / n_persons if n_persons > 0 else 0.0,
        "cat_sensitivity": cat_detected / n_persons if n_persons > 0 else 0.0,
        "fixed_mean_items": fixed_total_items / n_persons if n_persons > 0 else 0,
        "cat_mean_items": cat_total_items / n_persons if n_persons > 0 else 0,
    }
