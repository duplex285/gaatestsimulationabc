"""Tests for type and state descriptions.

Reference: abc-assessment-spec Section 2.2, Section 2.4
"""

from src.python_scoring.type_derivation import ALL_TYPE_NAMES
from src.python_scoring.type_descriptions import (
    DOMAIN_STATE_DESCRIPTIONS,
    TYPE_DESCRIPTIONS,
    get_state_description,
    get_type_description,
)


class TestTypeDescriptionsCoverage:
    """Every type in the derivation system must have a description."""

    def test_all_types_have_descriptions(self):
        for name in ALL_TYPE_NAMES:
            assert name in TYPE_DESCRIPTIONS, f"Missing description for type: {name}"

    def test_description_count(self):
        """8 motivational types: 8 base patterns with continuous frustration."""
        assert len(TYPE_DESCRIPTIONS) == 8


class TestTypeDescriptionStructure:
    """Every type description must have required fields."""

    def test_required_fields(self):
        required = {
            "tagline",
            "description",
            "strengths",
            "watch_for",
            "growth_edge",
            "pattern",
        }
        for name, desc in TYPE_DESCRIPTIONS.items():
            missing = required - set(desc.keys())
            assert not missing, f"Type '{name}' missing fields: {missing}"

    def test_strengths_are_lists(self):
        for name, desc in TYPE_DESCRIPTIONS.items():
            assert isinstance(desc["strengths"], list), f"Type '{name}' strengths must be a list"
            assert len(desc["strengths"]) >= 2, f"Type '{name}' needs at least 2 strengths"

    def test_pattern_has_all_three_domains(self):
        """Every type pattern must reference all three domains."""
        for name, desc in TYPE_DESCRIPTIONS.items():
            pattern = desc["pattern"]
            assert "ambition" in pattern, f"Type '{name}' pattern missing ambition"
            assert "belonging" in pattern, f"Type '{name}' pattern missing belonging"
            assert "craft" in pattern, f"Type '{name}' pattern missing craft"
            for domain, status in pattern.items():
                assert status in ("strong", "developing"), (
                    f"Type '{name}' pattern {domain}={status} invalid"
                )


class TestGetTypeDescription:
    """Test the lookup function."""

    def test_valid_type(self):
        result = get_type_description("Mentor")
        assert result is not None
        assert result["pattern"]["belonging"] == "strong"

    def test_invalid_type(self):
        assert get_type_description("NonexistentType") is None


class TestStateDescriptions:
    """Every domain state must have a description."""

    def test_all_four_states(self):
        for state in ["Thriving", "Vulnerable", "Mild", "Distressed"]:
            assert state in DOMAIN_STATE_DESCRIPTIONS

    def test_required_fields(self):
        required = {"label", "condition", "summary", "science", "implication", "colour"}
        for state, desc in DOMAIN_STATE_DESCRIPTIONS.items():
            missing = required - set(desc.keys())
            assert not missing, f"State '{state}' missing fields: {missing}"

    def test_get_state_description(self):
        result = get_state_description("Vulnerable")
        assert result is not None
        science = result["science"].lower()
        assert "independent" in science or "frustration" in science

    def test_invalid_state(self):
        assert get_state_description("Happy") is None
