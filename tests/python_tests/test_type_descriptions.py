"""Tests for type and state descriptions.

Reference: abc-assessment-spec Section 2.2, Section 2.4
"""

from src.python_scoring.type_derivation import TYPE_MAP
from src.python_scoring.type_descriptions import (
    DOMAIN_STATE_DESCRIPTIONS,
    TYPE_DESCRIPTIONS,
    get_state_description,
    get_type_description,
)


class TestTypeDescriptionsCoverage:
    """Every type in TYPE_MAP must have a description."""

    def test_all_types_have_descriptions(self):
        """Reference: abc-assessment-spec Section 2.4"""
        all_type_names = set()
        for domain_types in TYPE_MAP.values():
            for type_name in domain_types.values():
                all_type_names.add(type_name)
        for name in all_type_names:
            assert name in TYPE_DESCRIPTIONS, f"Missing description for type: {name}"

    def test_description_count(self):
        """Reference: abc-assessment-spec Section 2.4"""
        assert len(TYPE_DESCRIPTIONS) == 31  # 30 unique + Integrator


class TestTypeDescriptionStructure:
    """Every type description must have required fields."""

    def test_required_fields(self):
        """Reference: abc-assessment-spec Section 2.4"""
        required = {
            "tagline",
            "description",
            "strengths",
            "watch_for",
            "growth_edge",
            "domain",
            "trait",
        }
        for name, desc in TYPE_DESCRIPTIONS.items():
            missing = required - set(desc.keys())
            assert not missing, f"Type '{name}' missing fields: {missing}"

    def test_strengths_are_lists(self):
        """Reference: abc-assessment-spec Section 2.4"""
        for name, desc in TYPE_DESCRIPTIONS.items():
            assert isinstance(desc["strengths"], list), f"Type '{name}' strengths must be a list"
            assert len(desc["strengths"]) >= 2, f"Type '{name}' needs at least 2 strengths"

    def test_domains_are_valid(self):
        """Reference: abc-assessment-spec Section 2.4"""
        valid = {"ambition", "belonging", "craft", "any"}
        for name, desc in TYPE_DESCRIPTIONS.items():
            assert desc["domain"] in valid, f"Type '{name}' has invalid domain: {desc['domain']}"


class TestGetTypeDescription:
    """Test the lookup function."""

    def test_valid_type(self):
        """Reference: abc-assessment-spec Section 2.4"""
        result = get_type_description("Mentor")
        assert result is not None
        assert result["domain"] == "belonging"

    def test_invalid_type(self):
        """Reference: abc-assessment-spec Section 2.4"""
        assert get_type_description("NonexistentType") is None


class TestStateDescriptions:
    """Every domain state must have a description."""

    def test_all_four_states(self):
        """Reference: abc-assessment-spec Section 2.2"""
        for state in ["Thriving", "Vulnerable", "Dormant", "Distressed"]:
            assert state in DOMAIN_STATE_DESCRIPTIONS

    def test_required_fields(self):
        """Reference: abc-assessment-spec Section 2.2"""
        required = {"label", "condition", "summary", "science", "implication", "colour"}
        for state, desc in DOMAIN_STATE_DESCRIPTIONS.items():
            missing = required - set(desc.keys())
            assert not missing, f"State '{state}' missing fields: {missing}"

    def test_get_state_description(self):
        """Reference: abc-assessment-spec Section 2.2"""
        result = get_state_description("Vulnerable")
        assert result is not None
        science = result["science"].lower()
        assert "independent" in science or "frustration" in science

    def test_invalid_state(self):
        """Reference: abc-assessment-spec Section 2.2"""
        assert get_state_description("Happy") is None
