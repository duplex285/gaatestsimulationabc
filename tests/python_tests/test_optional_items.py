"""Tests for the optional-items registry.

Reference: src/python_scoring/optional_items.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.causality_orientations import ALL_ITEMS as CAUSALITY_ITEMS
from src.python_scoring.coach_circumplex import ALL_ITEMS as CIRCUMPLEX_ITEMS
from src.python_scoring.group_conscious import ALL_ITEMS as GROUP_CONSCIOUS_ITEMS
from src.python_scoring.optional_items import (
    ALL_OPTIONAL_CODES,
    CAUSALITY_ORIENTATIONS_LAYER,
    COACH_CIRCUMPLEX_LAYER,
    GROUP_CONSCIOUS_LAYER,
    OPTIONAL_LAYERS,
    PASSION_LAYER,
    REGULATORY_LAYER,
    SELF_CONCORDANCE_LAYER,
    get_layer,
    is_optional_item,
    layer_for_item,
)
from src.python_scoring.passion_quality import ALL_ITEMS as PASSION_ITEMS
from src.python_scoring.regulatory_style import ALL_ITEMS as REGULATORY_ITEMS
from src.python_scoring.self_concordance import ALL_ITEMS as SELF_CONCORDANCE_ITEMS


class TestRegistration:
    def test_passion_layer_matches_scoring_module(self):
        assert set(PASSION_LAYER.item_codes) == set(PASSION_ITEMS)
        assert PASSION_LAYER.cadence == "quarterly"

    def test_regulatory_layer_matches_scoring_module(self):
        assert set(REGULATORY_LAYER.item_codes) == set(REGULATORY_ITEMS)
        assert REGULATORY_LAYER.cadence == "biweekly"

    def test_circumplex_layer_matches_scoring_module(self):
        assert set(COACH_CIRCUMPLEX_LAYER.item_codes) == set(CIRCUMPLEX_ITEMS)
        assert COACH_CIRCUMPLEX_LAYER.cadence == "quarterly"
        assert COACH_CIRCUMPLEX_LAYER.respondent == "coach_self_and_athletes"

    def test_group_conscious_layer_matches_scoring_module(self):
        assert set(GROUP_CONSCIOUS_LAYER.item_codes) == set(GROUP_CONSCIOUS_ITEMS)
        assert GROUP_CONSCIOUS_LAYER.cadence == "biweekly"
        assert GROUP_CONSCIOUS_LAYER.respondent == "athlete"

    def test_causality_orientations_layer_matches_scoring_module(self):
        assert set(CAUSALITY_ORIENTATIONS_LAYER.item_codes) == set(CAUSALITY_ITEMS)
        assert CAUSALITY_ORIENTATIONS_LAYER.cadence == "annual"
        assert CAUSALITY_ORIENTATIONS_LAYER.respondent == "athlete"

    def test_self_concordance_layer_matches_scoring_module(self):
        assert set(SELF_CONCORDANCE_LAYER.item_codes) == set(SELF_CONCORDANCE_ITEMS)
        assert SELF_CONCORDANCE_LAYER.cadence == "biweekly"
        assert SELF_CONCORDANCE_LAYER.respondent == "athlete"

    def test_all_optional_codes_is_union(self):
        expected = (
            set(PASSION_LAYER.item_codes)
            | set(REGULATORY_LAYER.item_codes)
            | set(COACH_CIRCUMPLEX_LAYER.item_codes)
            | set(GROUP_CONSCIOUS_LAYER.item_codes)
            | set(CAUSALITY_ORIENTATIONS_LAYER.item_codes)
            | set(SELF_CONCORDANCE_LAYER.item_codes)
        )
        assert expected == ALL_OPTIONAL_CODES

    def test_no_overlap_between_layers(self):
        all_sets = [
            set(PASSION_LAYER.item_codes),
            set(REGULATORY_LAYER.item_codes),
            set(COACH_CIRCUMPLEX_LAYER.item_codes),
            set(GROUP_CONSCIOUS_LAYER.item_codes),
            set(CAUSALITY_ORIENTATIONS_LAYER.item_codes),
            set(SELF_CONCORDANCE_LAYER.item_codes),
        ]
        for i, s1 in enumerate(all_sets):
            for s2 in all_sets[i + 1 :]:
                assert s1.isdisjoint(s2)


class TestLookup:
    def test_is_optional_item_true_for_passion(self):
        assert is_optional_item("HP1") is True

    def test_is_optional_item_true_for_regulatory(self):
        assert is_optional_item("AR1") is True

    def test_is_optional_item_false_for_core(self):
        assert is_optional_item("AS1") is False

    def test_is_optional_item_false_for_unknown(self):
        assert is_optional_item("XYZ") is False

    def test_layer_for_item_passion(self):
        assert layer_for_item("OP2") is PASSION_LAYER

    def test_layer_for_item_regulatory(self):
        assert layer_for_item("BR1") is REGULATORY_LAYER

    def test_layer_for_item_circumplex(self):
        assert layer_for_item("CXA1") is COACH_CIRCUMPLEX_LAYER

    def test_layer_for_item_group_conscious(self):
        assert layer_for_item("AG1") is GROUP_CONSCIOUS_LAYER
        assert layer_for_item("TI1") is GROUP_CONSCIOUS_LAYER

    def test_layer_for_item_causality(self):
        assert layer_for_item("AO1") is CAUSALITY_ORIENTATIONS_LAYER
        assert layer_for_item("CO1") is CAUSALITY_ORIENTATIONS_LAYER
        assert layer_for_item("IO1") is CAUSALITY_ORIENTATIONS_LAYER

    def test_layer_for_item_self_concordance(self):
        for code in ("SC1", "SC2", "SC3", "SC4"):
            assert layer_for_item(code) is SELF_CONCORDANCE_LAYER

    def test_layer_for_item_unknown_returns_none(self):
        assert layer_for_item("XYZ") is None


class TestGetLayer:
    def test_get_passion(self):
        assert get_layer("passion_quality") is PASSION_LAYER

    def test_get_regulatory(self):
        assert get_layer("regulatory_style") is REGULATORY_LAYER

    def test_get_circumplex(self):
        assert get_layer("coach_circumplex") is COACH_CIRCUMPLEX_LAYER

    def test_get_group_conscious(self):
        assert get_layer("group_conscious") is GROUP_CONSCIOUS_LAYER

    def test_get_causality_orientations(self):
        assert get_layer("causality_orientations") is CAUSALITY_ORIENTATIONS_LAYER

    def test_get_self_concordance(self):
        assert get_layer("self_concordance") is SELF_CONCORDANCE_LAYER

    def test_unknown_layer_raises(self):
        with pytest.raises(KeyError):
            get_layer("bogus")


class TestImmutability:
    def test_layers_tuple_is_immutable(self):
        assert isinstance(OPTIONAL_LAYERS, tuple)

    def test_all_optional_codes_is_frozenset(self):
        assert isinstance(ALL_OPTIONAL_CODES, frozenset)


class TestUniquenessGuard:
    """The import-time guard must catch a duplicate item code."""

    def test_duplicate_item_code_raises(self):
        # Inject a duplicate by monkeypatching the tuple that the guard reads.
        import src.python_scoring.optional_items as module
        from src.python_scoring.optional_items import (
            OptionalItemLayer,
            _check_layer_uniqueness,
        )

        original = module.OPTIONAL_LAYERS
        duplicate_layer = OptionalItemLayer(
            name="duplicate_for_test",
            cadence="biweekly",
            respondent="athlete",
            item_codes=("HP1",),  # collides with passion
            scoring_module="nonexistent",
            reference_doc="nonexistent",
        )
        module.OPTIONAL_LAYERS = original + (duplicate_layer,)
        try:
            with pytest.raises(ValueError, match="duplicate item code"):
                _check_layer_uniqueness()
        finally:
            module.OPTIONAL_LAYERS = original
