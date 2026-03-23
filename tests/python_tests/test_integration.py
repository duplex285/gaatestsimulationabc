"""Integration tests for the complete scoring pipeline.

Tests end-to-end flow: raw responses -> scored profile.
Also tests edge cases and realistic scenarios.

Reference: abc-assessment-spec Section 2.1 (full pipeline)
Reference: abc-assessment-spec Section 11.4 (scoring pipeline verification)
"""

import pytest

from src.python_scoring.scoring_pipeline import ABCScorer
from tests.python_tests.conftest import ALL_ITEMS


@pytest.fixture
def scorer():
    return ABCScorer()


def make_responses(sat_val, frust_val):
    """Helper: create responses with uniform sat and frust values.

    Forward items get the value directly.
    Reverse items get (8 - value) so after reverse scoring they equal the value.
    """
    responses = {}
    sat_subscales = ["a_sat", "b_sat", "c_sat"]
    frust_subscales = ["a_frust", "b_frust", "c_frust"]
    prefixes = {
        "a_sat": "AS",
        "a_frust": "AF",
        "b_sat": "BS",
        "b_frust": "BF",
        "c_sat": "CS",
        "c_frust": "CF",
    }
    reverse_items = {
        "AS4",
        "AF4",
        "BS4",
        "BF4",
        "CS4",
        "CF4",
        "AS6",
        "AF6",
        "BS6",
        "BF6",
        "CS6",
        "CF6",
    }

    for subscale in sat_subscales:
        prefix = prefixes[subscale]
        for i in range(1, 7):
            item = f"{prefix}{i}"
            if item in reverse_items:
                responses[item] = 8 - sat_val
            else:
                responses[item] = sat_val

    for subscale in frust_subscales:
        prefix = prefixes[subscale]
        for i in range(1, 7):
            item = f"{prefix}{i}"
            if item in reverse_items:
                responses[item] = 8 - frust_val
            else:
                responses[item] = frust_val

    return responses


class TestEndToEndPipeline:
    """Test complete pipeline from raw responses to scored profile."""

    def test_pipeline_returns_complete_result(self, scorer):
        responses = make_responses(sat_val=5, frust_val=3)
        result = scorer.score(responses)
        assert "subscales" in result
        assert "domain_states" in result
        assert "big_five" in result
        assert "type_name" in result
        assert "type_domain" in result

    def test_pipeline_36_items_required(self, scorer):
        """Pipeline should handle exactly 36 core items."""
        responses = make_responses(sat_val=5, frust_val=3)
        assert len(responses) == 36
        result = scorer.score(responses)
        assert len(result["subscales"]) == 6

    def test_high_sat_low_frust_all_thriving(self, scorer):
        responses = make_responses(sat_val=6, frust_val=2)
        result = scorer.score(responses)
        for domain in ["ambition", "belonging", "craft"]:
            assert result["domain_states"][domain] == "Thriving"

    def test_low_sat_high_frust_all_distressed(self, scorer):
        responses = make_responses(sat_val=2, frust_val=6)
        result = scorer.score(responses)
        for domain in ["ambition", "belonging", "craft"]:
            assert result["domain_states"][domain] == "Distressed"


class TestRealisticProfiles:
    """Test with realistic, asymmetric profiles."""

    def test_ambition_thriving_belonging_distressed(self, scorer):
        """Mixed profile: high ambition, low belonging."""
        responses = {}
        # A-sat high
        for i, item in enumerate(["AS1", "AS2", "AS3", "AS4", "AS5", "AS6"]):
            responses[item] = [7, 6, 7, 2, 7, 2][i]  # AS4,AS6 reverse: 8-2=6
        # A-frust low
        for i, item in enumerate(["AF1", "AF2", "AF3", "AF4", "AF5", "AF6"]):
            responses[item] = [1, 2, 1, 6, 1, 6][i]  # AF4,AF6 reverse: 8-6=2
        # B-sat low
        for i, item in enumerate(["BS1", "BS2", "BS3", "BS4", "BS5", "BS6"]):
            responses[item] = [2, 1, 2, 6, 2, 6][i]  # BS4,BS6 reverse: 8-6=2
        # B-frust high
        for i, item in enumerate(["BF1", "BF2", "BF3", "BF4", "BF5", "BF6"]):
            responses[item] = [6, 7, 6, 2, 6, 2][i]  # BF4,BF6 reverse: 8-2=6
        # C-sat mid
        for i, item in enumerate(["CS1", "CS2", "CS3", "CS4", "CS5", "CS6"]):
            responses[item] = [4, 4, 4, 4, 4, 4][i]  # CS4,CS6 reverse: 8-4=4
        # C-frust mid
        for i, item in enumerate(["CF1", "CF2", "CF3", "CF4", "CF5", "CF6"]):
            responses[item] = [4, 4, 4, 4, 4, 4][i]  # CF4,CF6 reverse: 8-4=4

        result = scorer.score(responses)

        # A-sat should be high (mean ~6.5 -> ~9.17)
        assert result["subscales"]["a_sat"] > 7.0
        # B-frust should be high
        assert result["subscales"]["b_frust"] > 7.0
        # Ambition should be Thriving
        assert result["domain_states"]["ambition"] == "Thriving"
        # Belonging should be Distressed
        assert result["domain_states"]["belonging"] == "Distressed"
        # Dominant domain should be Ambition (highest sat)
        assert result["type_domain"] == "ambition"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_same_value(self, scorer):
        """All items at same value should not crash."""
        for val in range(1, 8):
            responses = dict.fromkeys(ALL_ITEMS, val)
            result = scorer.score(responses)
            # Should not raise and should have valid structure
            assert "subscales" in result
            assert "domain_states" in result

    def test_scores_always_in_range(self, scorer):
        """All subscale scores must be in [0, 10] for any valid input."""
        import random

        random.seed(123)
        for _ in range(50):
            responses = {}
            for item in ALL_ITEMS:
                responses[item] = random.randint(1, 7)
            result = scorer.score(responses)
            for subscale, score in result["subscales"].items():
                assert 0.0 <= score <= 10.0, f"{subscale}={score} out of range"

    def test_big_five_always_in_range(self, scorer):
        """All Big Five percentiles must be in [1, 99] for any valid input."""
        import random

        random.seed(456)
        for _ in range(50):
            responses = {}
            for item in ALL_ITEMS:
                responses[item] = random.randint(1, 7)
            result = scorer.score(responses)
            for trait, val in result["big_five"].items():
                assert 1 <= val <= 99, f"{trait}={val} out of [1, 99]"

    def test_domain_states_always_valid(self, scorer):
        """Domain states must be one of the four valid values."""
        import random

        random.seed(789)
        valid_states = {"Thriving", "Vulnerable", "Mild", "Distressed"}
        for _ in range(50):
            responses = {}
            for item in ALL_ITEMS:
                responses[item] = random.randint(1, 7)
            result = scorer.score(responses)
            for domain, state in result["domain_states"].items():
                assert state in valid_states, f"{domain}={state} invalid"

    def test_invalid_response_raises(self, scorer):
        """Responses outside 1-7 should raise an error."""
        responses = dict.fromkeys(ALL_ITEMS, 4)
        responses["AS1"] = 0  # Invalid
        with pytest.raises((ValueError, AssertionError)):
            scorer.score(responses)

    def test_missing_item_raises(self, scorer):
        """Missing items should raise an error."""
        responses = dict.fromkeys(ALL_ITEMS, 4)
        del responses["AS4"]  # Remove one item to test missing
        with pytest.raises((ValueError, KeyError, AssertionError)):
            scorer.score(responses)
