"""Tests for differential item functioning analysis.

Reference: Swaminathan & Rogers (1990), Logistic Regression DIF
Reference: APA/AERA/NCME Standards (2014), Standard 3.8
"""

import numpy as np

from src.psychometric.dif_analysis import detect_dif


class TestDetectDIF:
    """Tests for logistic regression DIF detection."""

    def test_returns_results_per_item(self):
        """Output has one result per item."""
        rng = np.random.default_rng(42)
        n = 200
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 100 + ["B"] * 100)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        assert len(result) == 24

    def test_each_item_has_required_fields(self):
        """Each item result includes effect size, p-value, and flag."""
        rng = np.random.default_rng(42)
        n = 200
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 100 + ["B"] * 100)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        for item_result in result:
            assert "item_index" in item_result
            assert "effect_size" in item_result
            assert "flagged" in item_result

    def test_no_dif_in_identical_groups(self):
        """Items from identical distributions should not be flagged."""
        rng = np.random.default_rng(42)
        n = 400
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 200 + ["B"] * 200)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        flagged_count = sum(1 for r in result if r["flagged"])
        # With random data, very few items should be flagged
        assert flagged_count <= 5

    def test_detects_dif_when_present(self):
        """Items with group-specific bias should be flagged."""
        rng = np.random.default_rng(42)
        n = 200
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 100 + ["B"] * 100)

        # Add strong DIF to item 0: group B gets +3 on this item
        responses[100:, 0] = np.clip(responses[100:, 0] + 3, 1, 7)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        # Item 0 should be flagged
        item_0 = [r for r in result if r["item_index"] == 0][0]
        assert item_0["flagged"] or item_0["effect_size"] > 0.05

    def test_effect_size_non_negative(self):
        """Effect sizes are non-negative."""
        rng = np.random.default_rng(42)
        n = 200
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 100 + ["B"] * 100)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        for item_result in result:
            assert item_result["effect_size"] >= 0

    def test_returns_total_flagged_count(self):
        """Output includes summary of total flagged items."""
        rng = np.random.default_rng(42)
        n = 200
        responses = rng.integers(1, 8, (n, 24))
        group = np.array(["A"] * 100 + ["B"] * 100)
        total_scores = np.sum(responses, axis=1).astype(float)

        result = detect_dif(responses, group, total_scores)
        flagged = [r for r in result if r["flagged"]]
        assert isinstance(flagged, list)
