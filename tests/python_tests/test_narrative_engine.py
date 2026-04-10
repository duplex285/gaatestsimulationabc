"""Tests for the narrative engine."""

import pytest

from src.python_scoring.narrative_engine import NarrativeEngine

ARCHETYPES = [
    "Integrator",
    "Captain",
    "Architect",
    "Mentor",
    "Pioneer",
    "Anchor",
    "Artisan",
    "Seeker",
]
AUDIENCES = ["athlete", "coach"]
DOMAINS = ["ambition", "belonging", "craft"]
STATES = ["Thriving", "Vulnerable", "Mild", "Distressed"]


@pytest.fixture
def engine():
    return NarrativeEngine()


class TestArchetypeNarratives:
    def test_all_archetypes_have_athlete_narratives(self, engine):
        for archetype in ARCHETYPES:
            result = engine.generate_archetype_narrative(archetype, "athlete")
            assert "identity_description" in result, f"Missing for {archetype}"
            assert len(result["identity_description"]) > 50

    def test_all_archetypes_have_coach_narratives(self, engine):
        for archetype in ARCHETYPES:
            result = engine.generate_archetype_narrative(archetype, "coach")
            assert "identity_description" in result, f"Missing for {archetype}"
            assert len(result["identity_description"]) > 50

    def test_athlete_uses_second_person(self, engine):
        result = engine.generate_archetype_narrative("Pioneer", "athlete")
        text = result["identity_description"].lower()
        assert "you" in text

    def test_coach_uses_third_person(self, engine):
        result = engine.generate_archetype_narrative("Pioneer", "coach")
        text = result["identity_description"].lower()
        assert "this athlete" in text or "they" in text or "athlete" in text

    def test_has_strengths(self, engine):
        for archetype in ARCHETYPES:
            result = engine.generate_archetype_narrative(archetype, "athlete")
            assert "strengths" in result
            assert len(result["strengths"]) >= 2

    def test_has_growth_edge(self, engine):
        for archetype in ARCHETYPES:
            result = engine.generate_archetype_narrative(archetype, "athlete")
            assert "growth_edge" in result
            assert len(result["growth_edge"]) > 20

    def test_no_em_dashes(self, engine):
        """CLAUDE.md hard rule: never use em-dashes."""
        for archetype in ARCHETYPES:
            for audience in AUDIENCES:
                result = engine.generate_archetype_narrative(archetype, audience)
                for key, value in result.items():
                    if isinstance(value, str):
                        assert "\u2014" not in value, (
                            f"Em-dash found in {archetype}/{audience}/{key}"
                        )
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                assert "\u2014" not in item


class TestDomainStateNarratives:
    def test_all_combinations_produce_output(self, engine):
        for domain in DOMAINS:
            for state in STATES:
                result = engine.generate_domain_state_narrative(domain, state, 5.0, "athlete")
                assert "state_description" in result
                assert len(result["state_description"]) > 20

    def test_athlete_gets_reflection_prompt(self, engine):
        result = engine.generate_domain_state_narrative("ambition", "Thriving", 8.0, "athlete")
        assert "reflection_prompt" in result or "conversation_starter" in result

    def test_coach_gets_conversation_starter(self, engine):
        result = engine.generate_domain_state_narrative("ambition", "Thriving", 8.0, "coach")
        assert "conversation_starter" in result or "reflection_prompt" in result

    def test_confidence_language_high(self, engine):
        result = engine.generate_domain_state_narrative(
            "ambition", "Thriving", 8.0, "athlete", posterior_confidence=0.9
        )
        text = result["state_description"].lower()
        assert "likely" in text or "strong" in text or "clear" in text

    def test_no_em_dashes_in_states(self, engine):
        for domain in DOMAINS:
            for state in STATES:
                result = engine.generate_domain_state_narrative(domain, state, 5.0, "athlete")
                for _key, value in result.items():
                    if isinstance(value, str):
                        assert "\u2014" not in value


class TestSignatureNarratives:
    SIGNATURES = [
        {"label": "Blocked Drive", "domain": "ambition", "risk": "medium"},
        {"label": "Conditional Belonging", "domain": "belonging", "risk": "medium"},
        {"label": "Evaluated Mastery", "domain": "craft", "risk": "medium"},
        {"label": "Controlled Motivation", "domain": "ambition", "risk": "high"},
        {"label": "Active Exclusion", "domain": "belonging", "risk": "high"},
        {"label": "Competence Threat", "domain": "craft", "risk": "high"},
    ]

    def test_all_signatures_produce_output(self, engine):
        for sig in self.SIGNATURES:
            result = engine.generate_signature_narrative(sig, "athlete")
            assert "description" in result
            assert "action_prompt" in result
            assert len(result["description"]) > 30

    def test_effort_cost_framing(self, engine):
        """Frustration should be framed as effort cost, not 'broken'."""
        for sig in self.SIGNATURES:
            result = engine.generate_signature_narrative(sig, "athlete")
            text = result["description"].lower()
            assert "broken" not in text
            # "failing" is allowed in negated form ("you are not failing")
            if "failing" in text:
                assert "not failing" in text, f"'failing' used without negation in {sig['label']}"


class TestTransitionNarratives:
    TRANSITION_TYPES = ["growth", "exploration", "regression", "fluctuation", "sustained"]

    def test_all_transition_types_produce_output(self, engine):
        for tt in self.TRANSITION_TYPES:
            result = engine.generate_transition_narrative("Pioneer", "Captain", tt, "athlete")
            assert isinstance(result, str)
            assert len(result) > 20

    def test_growth_is_positive(self, engine):
        result = engine.generate_transition_narrative("Pioneer", "Captain", "growth", "athlete")
        # Should not contain negative framing
        assert "worse" not in result.lower()
        assert "decline" not in result.lower()


class TestMeasurementDisclosure:
    def test_early_measurement(self, engine):
        result = engine.generate_measurement_disclosure(1, "athlete")
        assert isinstance(result, str)
        assert len(result) > 20

    def test_established_measurement(self, engine):
        result = engine.generate_measurement_disclosure(8, "athlete")
        assert isinstance(result, str)
        assert len(result) > 20

    def test_coach_disclosure(self, engine):
        result = engine.generate_measurement_disclosure(3, "coach")
        assert isinstance(result, str)
