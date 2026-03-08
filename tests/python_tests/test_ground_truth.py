"""Ground truth tests: known-answer datasets that must pass with 100% accuracy.

These are the non-negotiable validation tests. If any of these fail,
the scoring pipeline is broken.

Reference: abc-assessment-spec Section 2.1 (scoring pipeline)
Reference: abc-assessment-spec Section 2.2 (domain states)
Reference: CLAUDE_RULES.md Rule 5 (ground truth tests mandatory)
"""

import pytest

from src.python_scoring.scoring_pipeline import ABCScorer


@pytest.fixture
def scorer():
    return ABCScorer()


class TestPerfectThriving:
    """All sat items at max (7), all frust items at min (1).

    After reverse scoring, sat items -> 7, frust items -> 1.
    Sat subscale mean = 7.0, normalized = 10.0.
    Frust subscale mean = 1.0, normalized = 0.0.
    All domains: Thriving.
    """

    def test_satisfaction_scores(self, scorer, perfect_thriving_responses):
        result = scorer.score(perfect_thriving_responses)
        assert result["subscales"]["a_sat"] == pytest.approx(10.0)
        assert result["subscales"]["b_sat"] == pytest.approx(10.0)
        assert result["subscales"]["c_sat"] == pytest.approx(10.0)

    def test_frustration_scores(self, scorer, perfect_thriving_responses):
        result = scorer.score(perfect_thriving_responses)
        assert result["subscales"]["a_frust"] == pytest.approx(0.0)
        assert result["subscales"]["b_frust"] == pytest.approx(0.0)
        assert result["subscales"]["c_frust"] == pytest.approx(0.0)

    def test_domain_states(self, scorer, perfect_thriving_responses):
        result = scorer.score(perfect_thriving_responses)
        assert result["domain_states"]["ambition"] == "Thriving"
        assert result["domain_states"]["belonging"] == "Thriving"
        assert result["domain_states"]["craft"] == "Thriving"


class TestPerfectDistressed:
    """All sat items at min (1), all frust items at max (7).

    Sat subscale mean = 1.0, normalized = 0.0.
    Frust subscale mean = 7.0, normalized = 10.0.
    All domains: Distressed.
    """

    def test_satisfaction_scores(self, scorer, perfect_distressed_responses):
        result = scorer.score(perfect_distressed_responses)
        assert result["subscales"]["a_sat"] == pytest.approx(0.0)
        assert result["subscales"]["b_sat"] == pytest.approx(0.0)
        assert result["subscales"]["c_sat"] == pytest.approx(0.0)

    def test_frustration_scores(self, scorer, perfect_distressed_responses):
        result = scorer.score(perfect_distressed_responses)
        assert result["subscales"]["a_frust"] == pytest.approx(10.0)
        assert result["subscales"]["b_frust"] == pytest.approx(10.0)
        assert result["subscales"]["c_frust"] == pytest.approx(10.0)

    def test_domain_states(self, scorer, perfect_distressed_responses):
        result = scorer.score(perfect_distressed_responses)
        assert result["domain_states"]["ambition"] == "Distressed"
        assert result["domain_states"]["belonging"] == "Distressed"
        assert result["domain_states"]["craft"] == "Distressed"


class TestPerfectVulnerable:
    """All items produce max score (7 after reverse scoring).

    Both sat and frust = 7.0 raw, normalized = 10.0.
    All domains: Vulnerable.
    """

    def test_satisfaction_scores(self, scorer, perfect_vulnerable_responses):
        result = scorer.score(perfect_vulnerable_responses)
        assert result["subscales"]["a_sat"] == pytest.approx(10.0)
        assert result["subscales"]["b_sat"] == pytest.approx(10.0)
        assert result["subscales"]["c_sat"] == pytest.approx(10.0)

    def test_frustration_scores(self, scorer, perfect_vulnerable_responses):
        result = scorer.score(perfect_vulnerable_responses)
        assert result["subscales"]["a_frust"] == pytest.approx(10.0)
        assert result["subscales"]["b_frust"] == pytest.approx(10.0)
        assert result["subscales"]["c_frust"] == pytest.approx(10.0)

    def test_domain_states(self, scorer, perfect_vulnerable_responses):
        result = scorer.score(perfect_vulnerable_responses)
        assert result["domain_states"]["ambition"] == "Vulnerable"
        assert result["domain_states"]["belonging"] == "Vulnerable"
        assert result["domain_states"]["craft"] == "Vulnerable"


class TestPerfectDormant:
    """All items produce min score (1 after reverse scoring).

    Both sat and frust = 1.0 raw, normalized = 0.0.
    All domains: Dormant.
    """

    def test_satisfaction_scores(self, scorer, perfect_dormant_responses):
        result = scorer.score(perfect_dormant_responses)
        assert result["subscales"]["a_sat"] == pytest.approx(0.0)
        assert result["subscales"]["b_sat"] == pytest.approx(0.0)
        assert result["subscales"]["c_sat"] == pytest.approx(0.0)

    def test_frustration_scores(self, scorer, perfect_dormant_responses):
        result = scorer.score(perfect_dormant_responses)
        assert result["subscales"]["a_frust"] == pytest.approx(0.0)
        assert result["subscales"]["b_frust"] == pytest.approx(0.0)
        assert result["subscales"]["c_frust"] == pytest.approx(0.0)

    def test_domain_states(self, scorer, perfect_dormant_responses):
        result = scorer.score(perfect_dormant_responses)
        assert result["domain_states"]["ambition"] == "Dormant"
        assert result["domain_states"]["belonging"] == "Dormant"
        assert result["domain_states"]["craft"] == "Dormant"


class TestKnownMidpoint:
    """All items at 4 (midpoint of 1-7 scale).

    Subscale mean = 4.0, normalized = ((4-1)/6)*10 = 5.0.
    All domains: Dormant (5.0 < 5.5 threshold).
    """

    def test_all_subscales_at_midpoint(self, scorer, midpoint_responses):
        result = scorer.score(midpoint_responses)
        for subscale in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            assert result["subscales"][subscale] == pytest.approx(5.0), f"{subscale} should be 5.0"

    def test_domain_states_all_dormant(self, scorer, midpoint_responses):
        """5.0 < 5.5 threshold, so all Dormant."""
        result = scorer.score(midpoint_responses)
        for domain in ["ambition", "belonging", "craft"]:
            assert result["domain_states"][domain] == "Dormant"

    def test_big_five_all_at_50(self, scorer, midpoint_responses):
        """Midpoint subscales -> centred to 0 -> all Big Five at 50th percentile."""
        result = scorer.score(midpoint_responses)
        for trait in [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]:
            assert result["big_five"][trait] == pytest.approx(50.0), f"{trait} should be 50"


class TestScorerOutputStructure:
    """Test that ABCScorer.score() returns the expected structure."""

    def test_has_subscales(self, scorer, midpoint_responses):
        result = scorer.score(midpoint_responses)
        assert "subscales" in result

    def test_has_domain_states(self, scorer, midpoint_responses):
        result = scorer.score(midpoint_responses)
        assert "domain_states" in result

    def test_has_big_five(self, scorer, midpoint_responses):
        result = scorer.score(midpoint_responses)
        assert "big_five" in result

    def test_has_type(self, scorer, midpoint_responses):
        result = scorer.score(midpoint_responses)
        assert "type_name" in result
        assert "type_domain" in result
