"""Integration tests for the EnhancedABCScorer pipeline."""

import pytest

from src.python_scoring.scoring_pipeline import EnhancedABCScorer


def _make_responses(
    a_sat=4,
    a_frust=4,
    b_sat=4,
    b_frust=4,
    c_sat=4,
    c_frust=4,
):
    """Generate a full 36-item response dict with uniform values per subscale."""
    responses = {}
    for i in range(1, 7):
        responses[f"AS{i}"] = a_sat
        responses[f"AF{i}"] = a_frust
        responses[f"BS{i}"] = b_sat
        responses[f"BF{i}"] = b_frust
        responses[f"CS{i}"] = c_sat
        responses[f"CF{i}"] = c_frust
    return responses


@pytest.fixture
def scorer():
    return EnhancedABCScorer(demographics={"gender": "male"})


class TestEnhancedScorerCore:
    def test_returns_all_core_keys(self, scorer):
        result = scorer.score(_make_responses())
        for key in [
            "subscales",
            "domain_states",
            "big_five",
            "type_name",
            "type_domain",
            "profile",
            "frustration_signatures",
            "belbin_roles",
            "context_gaps",
        ]:
            assert key in result, f"Missing core key: {key}"

    def test_returns_enhanced_keys(self, scorer):
        result = scorer.score(_make_responses())
        for key in [
            "bayesian",
            "adjusted_domain_states",
            "narratives",
            "transition",
            "base_rate",
            "trajectory",
        ]:
            assert key in result, f"Missing enhanced key: {key}"

    def test_core_output_unchanged(self):
        """EnhancedABCScorer produces the same core output as ABCScorer."""
        from src.python_scoring.scoring_pipeline import ABCScorer

        responses = _make_responses(a_sat=6, a_frust=2, b_sat=5, b_frust=3, c_sat=4, c_frust=4)
        core = ABCScorer().score(responses)
        enhanced = EnhancedABCScorer().score(responses)

        assert enhanced["type_name"] == core["type_name"]
        assert enhanced["domain_states"] == core["domain_states"]
        assert enhanced["subscales"] == core["subscales"]
        assert enhanced["big_five"] == core["big_five"]


class TestBayesianIntegration:
    def test_bayesian_output_present(self, scorer):
        result = scorer.score(_make_responses())
        assert "subscales" in result["bayesian"]
        assert "domain_states" in result["bayesian"]
        assert "archetype_probabilities" in result["bayesian"]

    def test_archetype_probabilities_sum_to_one(self, scorer):
        result = scorer.score(_make_responses())
        probs = result["bayesian"]["archetype_probabilities"]
        assert abs(sum(probs.values()) - 1.0) < 0.01

    def test_measurement_count_increments(self, scorer):
        scorer.score(_make_responses())
        assert scorer.measurement_count == 1
        scorer.score(_make_responses())
        assert scorer.measurement_count == 2

    def test_domain_state_posteriors_sum_to_one(self, scorer):
        result = scorer.score(_make_responses())
        for domain in ["ambition", "belonging", "craft"]:
            state = result["bayesian"]["domain_states"][domain]
            total = (
                state["posterior_thriving"]
                + state["posterior_vulnerable"]
                + state["posterior_mild"]
                + state["posterior_distressed"]
            )
            assert abs(total - 1.0) < 0.01, f"{domain} posteriors sum to {total}"


class TestNarrativeIntegration:
    def test_archetype_narrative_present(self, scorer):
        result = scorer.score(_make_responses())
        narr = result["narratives"]["archetype"]
        assert "identity_description" in narr
        assert len(narr["identity_description"]) > 50

    def test_domain_narratives_present(self, scorer):
        result = scorer.score(_make_responses())
        for domain in ["ambition", "belonging", "craft"]:
            assert domain in result["narratives"]["domains"]
            narr = result["narratives"]["domains"][domain]
            assert "state_description" in narr

    def test_measurement_disclosure_present(self, scorer):
        result = scorer.score(_make_responses())
        assert len(result["narratives"]["measurement_disclosure"]) > 20

    def test_no_transition_narrative_on_first_measurement(self, scorer):
        result = scorer.score(_make_responses())
        assert result["narratives"]["transition"] is None

    def test_transition_narrative_on_type_change(self):
        scorer = EnhancedABCScorer()
        scorer.score(_make_responses(a_sat=6, b_sat=2, c_sat=2))
        result = scorer.score(
            _make_responses(a_sat=6, b_sat=6, c_sat=2),
            audience="athlete",
        )
        # May be a transition or fluctuation depending on confidence
        if result["transition"]["transition_type"] != "sustained":
            assert result["narratives"]["transition"] is not None

    def test_coach_audience(self):
        scorer = EnhancedABCScorer()
        result = scorer.score(_make_responses(), audience="coach")
        narr = result["narratives"]["archetype"]["identity_description"]
        # Coach narratives should use third person
        assert "you" not in narr.lower().split()[:3] or "this athlete" in narr.lower()


class TestTransitionIntegration:
    def test_first_measurement_no_transition(self, scorer):
        result = scorer.score(_make_responses())
        assert result["transition"]["transition"] is None

    def test_trajectory_summary_present(self, scorer):
        scorer.score(_make_responses())
        result = scorer.score(_make_responses())
        traj = result["trajectory"]
        assert traj["measurement_count"] == 2
        assert traj["current_type"] is not None

    def test_growth_trajectory_tracked(self):
        scorer = EnhancedABCScorer()
        scorer.score(_make_responses(a_sat=2, b_sat=2, c_sat=2))
        scorer.score(_make_responses(a_sat=7, b_sat=2, c_sat=2))
        result = scorer.score(_make_responses(a_sat=7, b_sat=7, c_sat=2))
        trajectory = result["trajectory"]["growth_trajectory"]
        assert len(trajectory) == 3


class TestBaseRateIntegration:
    def test_base_rate_present(self, scorer):
        result = scorer.score(_make_responses())
        assert "distressed_vulnerable_prior" in result["base_rate"]
        assert "source" in result["base_rate"]

    def test_adjusted_domain_states_present(self, scorer):
        result = scorer.score(_make_responses())
        for domain in ["ambition", "belonging", "craft"]:
            assert domain in result["adjusted_domain_states"]
            adj = result["adjusted_domain_states"][domain]
            assert "posteriors" in adj

    def test_different_demographics_different_priors(self):
        scorer_m = EnhancedABCScorer(demographics={"gender": "male"})
        scorer_f = EnhancedABCScorer(demographics={"gender": "female"})
        r_m = scorer_m.score(_make_responses())
        r_f = scorer_f.score(_make_responses())
        assert (
            r_m["base_rate"]["distressed_vulnerable_prior"]
            != r_f["base_rate"]["distressed_vulnerable_prior"]
        )
