"""Tests for the 6-item onboarding scorer."""

import pytest

from src.python_scoring.onboarding_scorer import score_onboarding


@pytest.fixture
def basic_responses():
    return {"AS1": 6, "AF1": 2, "BS1": 4, "BF1": 3, "CS1": 3, "CF1": 2}


class TestOnboardingScorer:
    def test_returns_tier_label(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert result["tier"] == "onboarding"
        assert result["items_answered"] == 6

    def test_no_hard_type_label(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "type_name" not in result
        assert "type_name" in result["suppressed"]

    def test_no_domain_states(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "domain_states" not in result
        assert "domain_states" in result["suppressed"]

    def test_no_frustration_signatures(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "frustration_signatures" not in result

    def test_no_belbin_roles(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "belbin_roles" not in result

    def test_has_directional_signals(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "directional" in result
        assert "strongest_domain" in result["directional"]
        assert result["directional"]["strongest_domain"] == "ambition"

    def test_has_archetype_probabilities(self, basic_responses):
        result = score_onboarding(basic_responses)
        probs = result["archetype_probabilities"]
        assert len(probs) == 8
        assert abs(sum(probs.values()) - 1.0) < 0.01

    def test_top_candidates(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert len(result["top_candidates"]) == 2
        assert (
            result["top_candidates"][0]["probability"] >= result["top_candidates"][1]["probability"]
        )

    def test_has_narratives(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "directional" in result["narratives"]
        assert "archetype_candidates" in result["narratives"]
        assert "invitation" in result["narratives"]

    def test_invitation_mentions_full_assessment(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "full" in result["narratives"]["invitation"].lower()
        assert "36" in result["narratives"]["invitation"]

    def test_directional_narrative_names_strongest(self, basic_responses):
        result = score_onboarding(basic_responses)
        assert "Ambition" in result["narratives"]["directional"]

    def test_missing_item_raises(self):
        with pytest.raises(ValueError, match="Missing"):
            score_onboarding({"AS1": 5, "AF1": 3, "BS1": 4, "BF1": 3, "CS1": 3})

    def test_out_of_range_raises(self, basic_responses):
        basic_responses["AS1"] = 8
        with pytest.raises(ValueError, match="1-7"):
            score_onboarding(basic_responses)

    def test_subscales_present(self, basic_responses):
        result = score_onboarding(basic_responses)
        for key in ["a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"]:
            assert key in result["subscales"]

    def test_wider_uncertainty_than_full(self, basic_responses):
        """Onboarding should show wider credible intervals than full assessment."""
        result = score_onboarding(basic_responses)
        # Check that bayesian posteriors exist and have reasonable spread
        for subscale_key in ["a_sat", "a_frust"]:
            posterior = result["bayesian"]["subscales"][subscale_key]
            ci = posterior["credible_interval_90"]
            width = ci[1] - ci[0]
            # With single item (SE=1.5), CI should be wider than ~2.5
            assert width > 2.0, f"CI too narrow for single item: {width}"
