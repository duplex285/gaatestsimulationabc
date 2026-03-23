"""Item bank for computerized adaptive testing.

Manages item parameters for CAT item selection, providing methods
to query items by factor, domain, and content area, and to compute
item-level information at any theta value.

Reference: Wainer et al. (2000), Computerized Adaptive Testing
Reference: van der Linden & Glas (2010), Elements of Adaptive Testing
"""

from dataclasses import dataclass

import numpy as np

from src.psychometric.irt_simulation import grm_probability


@dataclass
class ItemBankEntry:
    """Single item in the CAT item bank.

    Reference: Wainer et al. (2000)
    """

    item_code: str
    factor: str
    discrimination: float
    difficulty: np.ndarray  # shape (n_categories - 1,)
    content_area: str  # "satisfaction" or "frustration"
    domain: str  # "ambition", "belonging", "craft"


class ItemBank:
    """Manages item parameters for computerized adaptive testing.

    Reference: van der Linden & Glas (2010)
    """

    def __init__(self, items: list[ItemBankEntry]):
        self.items = items
        self._by_code = {item.item_code: item for item in items}

    def get_items_by_factor(self, factor: str) -> list[ItemBankEntry]:
        """Get all items belonging to a specific factor."""
        return [item for item in self.items if item.factor == factor]

    def get_items_by_domain(self, domain: str) -> list[ItemBankEntry]:
        """Get all items belonging to a specific domain."""
        return [item for item in self.items if item.domain == domain]

    def get_item_information_at_theta(self, item: ItemBankEntry, theta: float) -> float:
        """Compute Fisher information for a single item at a given theta.

        Reference: Baker & Kim (2004)

        I(theta) = sum_k [(P'_k)^2 / P_k]

        Computed via numerical differentiation.
        """
        delta = 1e-5
        probs = grm_probability(theta, item.discrimination, item.difficulty)
        probs_plus = grm_probability(theta + delta, item.discrimination, item.difficulty)
        probs_minus = grm_probability(theta - delta, item.discrimination, item.difficulty)

        derivs = (probs_plus - probs_minus) / (2 * delta)

        info = 0.0
        for k in range(len(probs)):
            if probs[k] > 1e-10:
                info += derivs[k] ** 2 / probs[k]

        return float(info)

    def get_unadministered(self, administered: set[str]) -> list[ItemBankEntry]:
        """Get items not yet administered."""
        return [item for item in self.items if item.item_code not in administered]

    def get_content_area_counts(self) -> dict[str, int]:
        """Count items per content area."""
        counts = {}
        for item in self.items:
            counts[item.content_area] = counts.get(item.content_area, 0) + 1
        return counts

    def get_item_by_code(self, code: str) -> ItemBankEntry | None:
        """Look up an item by its code."""
        return self._by_code.get(code)
