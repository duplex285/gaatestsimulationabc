"""Tests for motivational type derivation module.

Reference: abc-assessment-spec Section 2.4

Two-layer type system:
  Layer 1: 125 profile combinations (5 sat levels x 3 domains)
  Layer 2: 8 named archetypes with continuous frustration reporting
"""

from src.python_scoring.type_derivation import (
    ALL_TYPE_NAMES,
    classify_sat_level,
    compute_profile,
    derive_type,
    get_dominant_domain,
)


def _subs(a_sat=5.0, a_frust=3.0, b_sat=5.0, b_frust=3.0, c_sat=5.0, c_frust=3.0):
    return {
        "a_sat": a_sat,
        "a_frust": a_frust,
        "b_sat": b_sat,
        "b_frust": b_frust,
        "c_sat": c_sat,
        "c_frust": c_frust,
    }


class TestClassifySatLevel:
    """5-level satisfaction classification."""

    def test_very_high(self):
        assert classify_sat_level(9.0) == "Very High"

    def test_high(self):
        assert classify_sat_level(7.0) == "High"

    def test_medium(self):
        assert classify_sat_level(5.0) == "Medium"

    def test_low(self):
        assert classify_sat_level(3.0) == "Low"

    def test_very_low(self):
        assert classify_sat_level(1.0) == "Very Low"

    def test_boundary_8(self):
        assert classify_sat_level(8.0) == "Very High"

    def test_boundary_6(self):
        assert classify_sat_level(6.0) == "High"

    def test_boundary_4(self):
        assert classify_sat_level(4.0) == "Medium"

    def test_boundary_2(self):
        assert classify_sat_level(2.0) == "Low"

    def test_boundary_just_below_2(self):
        assert classify_sat_level(1.99) == "Very Low"

    def test_zero(self):
        assert classify_sat_level(0.0) == "Very Low"

    def test_ten(self):
        assert classify_sat_level(10.0) == "Very High"


class TestComputeProfile:
    """125-combination profile generation."""

    def test_returns_levels_codes_and_code_string(self):
        profile = compute_profile(_subs(a_sat=9.0, b_sat=5.0, c_sat=1.0))
        assert profile["levels"]["ambition"] == "Very High"
        assert profile["levels"]["belonging"] == "Medium"
        assert profile["levels"]["craft"] == "Very Low"
        assert profile["codes"]["ambition"] == 5
        assert profile["codes"]["belonging"] == 3
        assert profile["codes"]["craft"] == 1
        assert profile["profile_code"] == "5-3-1"

    def test_all_same_level(self):
        profile = compute_profile(_subs(a_sat=5.0, b_sat=5.0, c_sat=5.0))
        assert profile["profile_code"] == "3-3-3"

    def test_all_very_high(self):
        profile = compute_profile(_subs(a_sat=10.0, b_sat=10.0, c_sat=10.0))
        assert profile["profile_code"] == "5-5-5"


class TestGetDominantDomain:
    def test_ambition_highest(self):
        assert get_dominant_domain(_subs(a_sat=9.0)) == "ambition"

    def test_belonging_highest(self):
        assert get_dominant_domain(_subs(b_sat=9.0)) == "belonging"

    def test_craft_highest(self):
        assert get_dominant_domain(_subs(c_sat=9.0)) == "craft"

    def test_tie_ambition_wins(self):
        result = get_dominant_domain(_subs(a_sat=8.0, b_sat=8.0))
        assert result == "ambition"


class TestBasePatterns:
    """The 8 base patterns from binary satisfaction threshold."""

    def test_integrator_all_strong(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=8.0, c_sat=8.0))
        assert result["type_name"] == "Integrator"

    def test_captain_ab_strong(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=8.0, c_sat=3.0))
        assert result["type_name"] == "Captain"

    def test_architect_ac_strong(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=3.0, c_sat=8.0))
        assert result["type_name"] == "Architect"

    def test_mentor_bc_strong(self):
        result = derive_type(_subs(a_sat=3.0, b_sat=8.0, c_sat=8.0))
        assert result["type_name"] == "Mentor"

    def test_pioneer_a_strong(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=3.0, c_sat=3.0))
        assert result["type_name"] == "Pioneer"

    def test_anchor_b_strong(self):
        result = derive_type(_subs(a_sat=3.0, b_sat=8.0, c_sat=3.0))
        assert result["type_name"] == "Anchor"

    def test_artisan_c_strong(self):
        result = derive_type(_subs(a_sat=3.0, b_sat=3.0, c_sat=8.0))
        assert result["type_name"] == "Artisan"

    def test_seeker_none_strong(self):
        result = derive_type(_subs(a_sat=3.0, b_sat=3.0, c_sat=3.0))
        assert result["type_name"] == "Seeker"


class TestFrustrationLevels:
    """Continuous frustration reporting replaces categorical modifiers."""

    def test_frustration_levels_in_result(self):
        """derive_type returns continuous frustration levels per domain."""
        result = derive_type(
            _subs(a_sat=8.0, b_sat=8.0, c_sat=8.0, a_frust=5.0, b_frust=2.0, c_frust=7.0)
        )
        assert "frustration_levels" in result
        assert result["frustration_levels"]["ambition"] == 5.0
        assert result["frustration_levels"]["belonging"] == 2.0
        assert result["frustration_levels"]["craft"] == 7.0

    def test_frustration_levels_all_low(self):
        """Low frustration across all domains."""
        result = derive_type(_subs(a_frust=1.0, b_frust=2.0, c_frust=1.5))
        assert all(v < 3.0 for v in result["frustration_levels"].values())

    def test_frustration_levels_all_high(self):
        """High frustration across all domains."""
        result = derive_type(_subs(a_frust=8.0, b_frust=7.0, c_frust=9.0))
        assert all(v > 6.0 for v in result["frustration_levels"].values())

    def test_frustration_levels_has_three_domains(self):
        """Frustration levels include all three domains."""
        result = derive_type(_subs())
        assert set(result["frustration_levels"].keys()) == {"ambition", "belonging", "craft"}

    def test_type_name_has_no_modifier_prefix(self):
        """Type name is a bare base pattern, not prefixed with Steady/Striving/Resolute."""
        result = derive_type(
            _subs(a_sat=8.0, b_sat=8.0, c_sat=8.0, a_frust=5.0, b_frust=5.0, c_frust=5.0)
        )
        assert result["type_name"] == "Integrator"
        assert "Steady" not in result["type_name"]
        assert "Striving" not in result["type_name"]
        assert "Resolute" not in result["type_name"]

    def test_frustration_independent_of_base_pattern(self):
        """Frustration levels are the same regardless of base pattern."""
        result_integrator = derive_type(
            _subs(a_sat=8.0, b_sat=8.0, c_sat=8.0, a_frust=5.0, b_frust=2.0, c_frust=7.0)
        )
        result_seeker = derive_type(
            _subs(a_sat=3.0, b_sat=3.0, c_sat=3.0, a_frust=5.0, b_frust=2.0, c_frust=7.0)
        )
        assert result_integrator["frustration_levels"] == result_seeker["frustration_levels"]


class TestAllEightReachable:
    """Every base pattern should be producible."""

    def test_all_8_types_reachable(self):
        produced = set()
        patterns = [
            (8, 8, 8),  # Integrator
            (8, 8, 3),  # Captain
            (8, 3, 8),  # Architect
            (3, 8, 8),  # Mentor
            (8, 3, 3),  # Pioneer
            (3, 8, 3),  # Anchor
            (3, 3, 8),  # Artisan
            (3, 3, 3),  # Seeker
        ]
        for a_s, b_s, c_s in patterns:
            result = derive_type(_subs(a_sat=a_s, b_sat=b_s, c_sat=c_s))
            produced.add(result["type_name"])
        assert produced == ALL_TYPE_NAMES, f"Missing: {ALL_TYPE_NAMES - produced}"


class TestProfileIncludedInResult:
    """derive_type returns the 125-combination profile."""

    def test_profile_in_result(self):
        result = derive_type(_subs(a_sat=9.0, b_sat=5.0, c_sat=1.0))
        assert "profile" in result
        assert result["profile"]["levels"]["ambition"] == "Very High"
        assert result["profile"]["profile_code"] == "5-3-1"


class TestReturnStructure:
    def test_returns_dict_with_required_keys(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=5.0, c_sat=5.0))
        assert isinstance(result, dict)
        assert "type_name" in result
        assert "type_domain" in result
        assert "profile" in result
        assert "frustration_levels" in result

    def test_type_name_is_valid(self):
        result = derive_type(
            _subs(a_sat=8.0, b_sat=8.0, c_sat=3.0, a_frust=2.0, b_frust=2.0, c_frust=2.0)
        )
        assert result["type_name"] in ALL_TYPE_NAMES

    def test_domain_is_valid(self):
        result = derive_type(_subs(a_sat=8.0, b_sat=5.0, c_sat=5.0))
        assert result["type_domain"] in ("ambition", "belonging", "craft")
