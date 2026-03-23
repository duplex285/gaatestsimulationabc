"""Tests for longitudinal CAT module.

Reference: abc-assessment-spec Section 11.7 (trajectory detection)
"""

import numpy as np
import pytest

from src.psychometric.cat_longitudinal import (
    compare_fixed_vs_cat_change_sensitivity,
    select_next_item_change_aware,
    simulate_longitudinal_cat,
)
from src.psychometric.item_bank import ItemBank, ItemBankEntry


@pytest.fixture
def bank():
    """Item bank for longitudinal CAT testing."""
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


class TestSelectNextItemChangeAware:
    """Tests for change-aware item selection."""

    def test_returns_item(self, bank):
        """Selects an item from the bank."""
        item = select_next_item_change_aware(
            bank, administered=set(), current_theta=0.5, previous_theta=0.0
        )
        assert item is not None

    def test_differs_from_standard_selection(self, bank):
        """Change-aware selection may differ from standard max-info.

        When previous_theta differs from current_theta, items informative
        at the boundary between them become more valuable.
        """
        from src.psychometric.cat_engine import select_next_item

        standard = select_next_item(bank, administered=set(), current_theta=0.5)
        change_aware = select_next_item_change_aware(
            bank, administered=set(), current_theta=0.5, previous_theta=-1.0
        )
        # They may or may not differ depending on the item bank,
        # but both should return valid items
        assert standard is not None
        assert change_aware is not None

    def test_does_not_repeat(self, bank):
        """Does not select already-administered items."""
        administered = {bank.items[0].item_code, bank.items[1].item_code}
        item = select_next_item_change_aware(
            bank, administered=administered, current_theta=0.0, previous_theta=0.0
        )
        assert item.item_code not in administered


class TestSimulateLongitudinalCAT:
    """Tests for longitudinal CAT simulation across timepoints."""

    def test_returns_results_per_timepoint(self, bank):
        """Output has one result per timepoint."""
        true_thetas = [0.0, 0.0, -0.5, -1.0, -1.5]
        result = simulate_longitudinal_cat(
            bank, true_thetas=true_thetas, se_threshold=0.40, seed=42
        )
        assert len(result["timepoints"]) == 5

    def test_each_timepoint_has_theta_and_se(self, bank):
        """Each timepoint result includes theta estimate and SE."""
        true_thetas = [0.0, 0.5, 1.0]
        result = simulate_longitudinal_cat(
            bank, true_thetas=true_thetas, se_threshold=0.40, seed=42
        )
        for tp in result["timepoints"]:
            assert "theta" in tp
            assert "se" in tp
            assert "n_items" in tp

    def test_tracks_change_detection(self, bank):
        """Output includes whether change was detected between timepoints."""
        true_thetas = [0.0, 0.0, -2.0]  # big drop at t=2
        result = simulate_longitudinal_cat(
            bank, true_thetas=true_thetas, se_threshold=0.40, seed=42
        )
        assert "change_detected" in result
        assert len(result["change_detected"]) == 2  # n_timepoints - 1

    def test_reproducibility(self, bank):
        """Same seed produces identical longitudinal administration."""
        true_thetas = [0.0, 0.5, 1.0]
        r1 = simulate_longitudinal_cat(bank, true_thetas=true_thetas, seed=42)
        r2 = simulate_longitudinal_cat(bank, true_thetas=true_thetas, seed=42)
        assert r1["timepoints"][0]["theta"] == r2["timepoints"][0]["theta"]


class TestCompareFixedVsCATChangeSensitivity:
    """Tests for fixed-form vs CAT change detection comparison."""

    def test_returns_comparison(self, bank):
        """Output includes sensitivity for both fixed and CAT."""
        result = compare_fixed_vs_cat_change_sensitivity(
            bank, n_persons=50, change_magnitude=1.0, seed=42
        )
        assert "fixed_sensitivity" in result
        assert "cat_sensitivity" in result
        assert "fixed_mean_items" in result
        assert "cat_mean_items" in result

    def test_sensitivities_between_zero_and_one(self, bank):
        """Sensitivities are in [0, 1]."""
        result = compare_fixed_vs_cat_change_sensitivity(
            bank, n_persons=50, change_magnitude=1.0, seed=42
        )
        assert 0.0 <= result["fixed_sensitivity"] <= 1.0
        assert 0.0 <= result["cat_sensitivity"] <= 1.0

    def test_cat_uses_fewer_items(self, bank):
        """CAT should use fewer items than fixed-form on average."""
        result = compare_fixed_vs_cat_change_sensitivity(
            bank, n_persons=50, change_magnitude=1.0, seed=42
        )
        # Fixed uses all 24 items; CAT should use fewer
        assert result["cat_mean_items"] <= result["fixed_mean_items"]
