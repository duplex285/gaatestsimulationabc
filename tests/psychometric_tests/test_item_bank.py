"""Tests for item bank module.

Reference: Wainer et al. (2000), Computerized Adaptive Testing
Reference: van der Linden & Glas (2010), Elements of Adaptive Testing
"""

import numpy as np
import pytest

from src.psychometric.item_bank import ItemBank, ItemBankEntry


@pytest.fixture
def sample_bank():
    """Create a sample item bank with 24 items across 6 factors."""
    entries = []
    factors = ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]
    domains = ["ambition", "ambition", "belonging", "belonging", "craft", "craft"]
    content_areas = ["satisfaction", "frustration"] * 3

    rng = np.random.default_rng(42)
    for f_idx, factor in enumerate(factors):
        for i in range(4):
            item_code = f"{factor.upper().replace('_', '')}{i + 1}"
            entries.append(
                ItemBankEntry(
                    item_code=item_code,
                    factor=factor,
                    discrimination=float(rng.uniform(0.8, 2.5)),
                    difficulty=rng.uniform(-2.5, 2.5, size=6),
                    content_area=content_areas[f_idx],
                    domain=domains[f_idx],
                )
            )
    return ItemBank(entries)


class TestItemBankEntry:
    """Tests for the ItemBankEntry dataclass."""

    def test_create_entry(self):
        """Can create an entry with all required fields."""
        entry = ItemBankEntry(
            item_code="AS1",
            factor="a_sat",
            discrimination=1.5,
            difficulty=np.array([-2, -1, 0, 1, 2, 3], dtype=float),
            content_area="satisfaction",
            domain="ambition",
        )
        assert entry.item_code == "AS1"
        assert entry.discrimination == 1.5

    def test_difficulty_shape(self):
        """Difficulty has 6 thresholds for 7-point Likert."""
        entry = ItemBankEntry(
            item_code="AS1",
            factor="a_sat",
            discrimination=1.5,
            difficulty=np.zeros(6),
            content_area="satisfaction",
            domain="ambition",
        )
        assert len(entry.difficulty) == 6


class TestItemBank:
    """Tests for the ItemBank class."""

    def test_total_items(self, sample_bank):
        """Bank contains all 24 items."""
        assert len(sample_bank.items) == 24

    def test_get_items_by_factor(self, sample_bank):
        """Can retrieve items for a specific factor."""
        a_sat_items = sample_bank.get_items_by_factor("a_sat")
        assert len(a_sat_items) == 4
        assert all(item.factor == "a_sat" for item in a_sat_items)

    def test_get_items_by_domain(self, sample_bank):
        """Can retrieve items for a specific domain."""
        ambition_items = sample_bank.get_items_by_domain("ambition")
        assert len(ambition_items) == 8  # 4 sat + 4 frust

    def test_get_item_information_at_theta(self, sample_bank):
        """Can compute information for a single item at a theta value."""
        item = sample_bank.items[0]
        info = sample_bank.get_item_information_at_theta(item, 0.0)
        assert info > 0

    def test_information_varies_with_theta(self, sample_bank):
        """Information at different theta values differs."""
        item = sample_bank.items[0]
        info_low = sample_bank.get_item_information_at_theta(item, -2.0)
        info_mid = sample_bank.get_item_information_at_theta(item, 0.0)
        info_high = sample_bank.get_item_information_at_theta(item, 2.0)
        # At least two should differ
        assert not (info_low == info_mid == info_high)

    def test_get_unadministered(self, sample_bank):
        """Can filter to items not yet administered."""
        administered = {"ASAT1", "ASAT2"}
        remaining = sample_bank.get_unadministered(administered)
        assert len(remaining) == 22
        assert all(item.item_code not in administered for item in remaining)

    def test_content_balance_counts(self, sample_bank):
        """Can count items per content area."""
        counts = sample_bank.get_content_area_counts()
        assert "satisfaction" in counts
        assert "frustration" in counts
        assert counts["satisfaction"] == 12
        assert counts["frustration"] == 12
