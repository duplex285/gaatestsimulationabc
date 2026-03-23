"""Tests for CAT engine module.

Reference: Chang & Ying (1999), Maximum Information Item Selection
Reference: PROMIS CAT administration guidelines
"""

import numpy as np
import pytest

from src.psychometric.cat_engine import (
    check_stopping_rule,
    select_next_item,
    simulate_cat_administration,
    update_theta,
)
from src.psychometric.item_bank import ItemBank, ItemBankEntry


@pytest.fixture
def simple_bank():
    """Small item bank for CAT testing."""
    entries = []
    rng = np.random.default_rng(42)
    factors = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    for f_idx, factor in enumerate(factors):
        for i in range(4):
            difficulty = np.sort(rng.uniform(-2.5, 2.5, size=6))
            for j in range(1, 6):
                if difficulty[j] - difficulty[j - 1] < 0.3:
                    difficulty[j] = difficulty[j - 1] + 0.3
            entries.append(
                ItemBankEntry(
                    item_code=f"{factor}_{i}",
                    factor=factor,
                    discrimination=float(rng.uniform(1.0, 2.0)),
                    difficulty=difficulty,
                    content_area="satisfaction" if "sat" in factor else "frustration",
                    domain=["ambition", "belonging", "craft"][f_idx // 2],
                )
            )
    return ItemBank(entries)


class TestSelectNextItem:
    """Tests for maximum information item selection."""

    def test_returns_item(self, simple_bank):
        """Selects an item from the bank."""
        item = select_next_item(simple_bank, administered=set(), current_theta=0.0)
        assert item is not None
        assert item.item_code in [i.item_code for i in simple_bank.items]

    def test_does_not_repeat_items(self, simple_bank):
        """Selected item is not in the administered set."""
        administered = {simple_bank.items[0].item_code}
        item = select_next_item(simple_bank, administered=administered, current_theta=0.0)
        assert item.item_code not in administered

    def test_selects_most_informative(self, simple_bank):
        """Selected item has maximum information at current theta."""
        item = select_next_item(simple_bank, administered=set(), current_theta=0.0)
        selected_info = simple_bank.get_item_information_at_theta(item, 0.0)
        # Should be among the most informative
        all_info = [simple_bank.get_item_information_at_theta(i, 0.0) for i in simple_bank.items]
        assert selected_info >= np.percentile(all_info, 50)

    def test_content_balancing(self, simple_bank):
        """With content constraints, respects balance requirements."""
        # Administer all satisfaction items except one factor
        administered = set()
        for item in simple_bank.items:
            if item.content_area == "satisfaction" and item.factor != "c_sat":
                administered.add(item.item_code)

        content_constraints = {"satisfaction": 10, "frustration": 10}
        item = select_next_item(
            simple_bank,
            administered=administered,
            current_theta=0.0,
            content_constraints=content_constraints,
        )
        assert item is not None


class TestUpdateTheta:
    """Tests for theta re-estimation after each response."""

    def test_returns_theta_and_se(self, simple_bank):
        """Returns updated theta estimate and SE."""
        responses = {"a_sat_0": 5}
        theta, se = update_theta(simple_bank, responses)
        assert isinstance(theta, float)
        assert isinstance(se, float)
        assert se > 0

    def test_high_responses_increase_theta(self, simple_bank):
        """Consistently high responses produce positive theta."""
        responses = {item.item_code: 7 for item in simple_bank.items[:6]}
        theta, _ = update_theta(simple_bank, responses)
        assert theta > 0

    def test_low_responses_decrease_theta(self, simple_bank):
        """Consistently low responses produce negative theta."""
        responses = {item.item_code: 1 for item in simple_bank.items[:6]}
        theta, _ = update_theta(simple_bank, responses)
        assert theta < 0

    def test_more_items_reduces_se(self, simple_bank):
        """More responses produce lower SE."""
        few_responses = {simple_bank.items[0].item_code: 4}
        many_responses = {item.item_code: 4 for item in simple_bank.items[:8]}
        _, se_few = update_theta(simple_bank, few_responses)
        _, se_many = update_theta(simple_bank, many_responses)
        assert se_many < se_few


class TestCheckStoppingRule:
    """Tests for CAT stopping rule."""

    def test_stops_when_se_below_threshold(self):
        """Stops when SE falls below the threshold."""
        assert check_stopping_rule(current_se=0.25, n_administered=6, se_threshold=0.30)

    def test_does_not_stop_below_minimum(self):
        """Does not stop before minimum items even if SE is low."""
        assert not check_stopping_rule(current_se=0.1, n_administered=2, min_items=4)

    def test_stops_at_max_items(self):
        """Stops when max items reached regardless of SE."""
        assert check_stopping_rule(current_se=0.5, n_administered=18, max_items=18)

    def test_continues_when_se_above_threshold(self):
        """Continues when SE is above threshold and below max items."""
        assert not check_stopping_rule(current_se=0.5, n_administered=8, se_threshold=0.30)


class TestSimulateCATAdministration:
    """Tests for full CAT administration simulation."""

    def test_returns_complete_result(self, simple_bank):
        """Output includes all CAT administration data."""
        result = simulate_cat_administration(
            simple_bank, true_theta=0.5, se_threshold=0.35, seed=42
        )
        assert "administered_items" in result
        assert "responses" in result
        assert "theta_history" in result
        assert "se_history" in result
        assert "final_theta" in result
        assert "final_se" in result
        assert "n_items" in result

    def test_respects_max_items(self, simple_bank):
        """Does not exceed max_items."""
        result = simulate_cat_administration(simple_bank, true_theta=0.0, max_items=8, seed=42)
        assert result["n_items"] <= 8

    def test_respects_min_items(self, simple_bank):
        """Administers at least min_items."""
        result = simulate_cat_administration(
            simple_bank, true_theta=0.0, min_items=4, se_threshold=10.0, seed=42
        )
        assert result["n_items"] >= 4

    def test_theta_near_true_theta(self, simple_bank):
        """Final theta estimate is reasonably close to true theta."""
        result = simulate_cat_administration(
            simple_bank, true_theta=1.0, se_threshold=0.35, max_items=20, seed=42
        )
        # With 24 items available, should get within ~1 SD
        assert abs(result["final_theta"] - 1.0) < 2.0

    def test_reproducibility(self, simple_bank):
        """Same seed produces identical administration."""
        r1 = simulate_cat_administration(simple_bank, true_theta=0.0, seed=42)
        r2 = simulate_cat_administration(simple_bank, true_theta=0.0, seed=42)
        assert r1["administered_items"] == r2["administered_items"]
        assert r1["final_theta"] == r2["final_theta"]
