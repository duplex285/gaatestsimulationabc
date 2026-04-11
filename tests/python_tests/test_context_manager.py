"""Tests for the cross-domain context manager.

Reference: abc-assessment-spec Section 7
"""

import pytest

from src.python_scoring.context_manager import DomainContextManager


class TestContextSwitching:
    """Verify that the context manager loads and switches contexts correctly."""

    def test_default_context_is_sport(self):
        ctx = DomainContextManager()
        assert ctx.context_name == "sport"

    def test_switch_to_professional(self):
        ctx = DomainContextManager(context="professional")
        assert ctx.context_name == "professional"

    def test_switch_to_military(self):
        ctx = DomainContextManager(context="military")
        assert ctx.context_name == "military"

    def test_switch_to_healthcare(self):
        ctx = DomainContextManager(context="healthcare")
        assert ctx.context_name == "healthcare"

    def test_switch_to_transition(self):
        ctx = DomainContextManager(context="transition")
        assert ctx.context_name == "transition"

    def test_invalid_context_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown context"):
            DomainContextManager(context="nonexistent")


class TestGetLabels:
    """Verify label retrieval across contexts."""

    def test_get_labels_returns_three_domains(self):
        ctx = DomainContextManager()
        labels = ctx.get_labels()
        assert set(labels.keys()) == {"ambition", "belonging", "craft"}

    def test_get_labels_sport_uses_ambition_belonging_craft(self):
        ctx = DomainContextManager(context="sport")
        labels = ctx.get_labels()
        assert labels["ambition"] == "Ambition"
        assert labels["belonging"] == "Belonging"
        assert labels["craft"] == "Craft"

    def test_get_labels_professional_uses_drive_connection_mastery(self):
        ctx = DomainContextManager(context="professional")
        labels = ctx.get_labels()
        assert labels["ambition"] == "Drive"
        assert labels["belonging"] == "Connection"
        assert labels["craft"] == "Mastery"


class TestDescriptionsAndPrompts:
    """Verify descriptions and prompts are populated."""

    def test_get_descriptions_returns_non_empty_strings(self):
        ctx = DomainContextManager()
        descriptions = ctx.get_descriptions()
        for domain, desc in descriptions.items():
            assert isinstance(desc, str), f"{domain} description is not a string"
            assert len(desc) > 0, f"{domain} description is empty"

    def test_get_prompts_returns_satisfaction_and_frustration(self):
        ctx = DomainContextManager()
        prompts = ctx.get_prompts()
        for domain, prompt_pair in prompts.items():
            assert "satisfaction_prompt" in prompt_pair, f"{domain} missing satisfaction_prompt"
            assert "frustration_prompt" in prompt_pair, f"{domain} missing frustration_prompt"


class TestAvailableContexts:
    """Verify the full list of available contexts."""

    def test_available_contexts_returns_all_five(self):
        ctx = DomainContextManager()
        available = ctx.available_contexts()
        assert available == ["healthcare", "military", "professional", "sport", "transition"]
