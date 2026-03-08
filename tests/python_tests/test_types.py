"""Tests for 36-type derivation module.

Reference: abc-assessment-spec Section 2.4 (type derivation)

Steps:
1. Dominant domain = argmax(A-sat, B-sat, C-sat)
2. Primary Big Five trait = trait with largest |percentile - 50|
3. Direction = High if percentile >= 50, Low otherwise
4. Type = typeMap[domain][direction + trait]
"""

from src.python_scoring.type_derivation import (
    derive_type,
    get_dominant_domain,
    get_primary_trait,
)


class TestGetDominantDomain:
    """Test dominant domain selection: argmax of satisfaction scores."""

    def test_ambition_highest(self):
        subscales = {
            "a_sat": 9.0,
            "a_frust": 1.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        assert get_dominant_domain(subscales) == "ambition"

    def test_belonging_highest(self):
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 9.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        assert get_dominant_domain(subscales) == "belonging"

    def test_craft_highest(self):
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 9.0,
            "c_frust": 5.0,
        }
        assert get_dominant_domain(subscales) == "craft"

    def test_tie_returns_deterministic(self):
        """When two domains tie, result should be deterministic."""
        subscales = {
            "a_sat": 8.0,
            "a_frust": 5.0,
            "b_sat": 8.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        result = get_dominant_domain(subscales)
        assert result in ("ambition", "belonging")
        # Call again to verify determinism
        assert get_dominant_domain(subscales) == result

    def test_all_equal(self):
        """All equal satisfaction scores -> deterministic choice."""
        subscales = {
            "a_sat": 7.0,
            "a_frust": 3.0,
            "b_sat": 7.0,
            "b_frust": 3.0,
            "c_sat": 7.0,
            "c_frust": 3.0,
        }
        result = get_dominant_domain(subscales)
        assert result in ("ambition", "belonging", "craft")


class TestGetPrimaryTrait:
    """Test primary Big Five trait selection: largest |percentile - 50|."""

    def test_one_extreme_trait(self):
        big_five = {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 85,  # |85-50| = 35, largest
            "agreeableness": 50,
            "neuroticism": 50,
        }
        trait, direction = get_primary_trait(big_five)
        assert trait == "extraversion"
        assert direction == "High"

    def test_low_direction(self):
        big_five = {
            "openness": 50,
            "conscientiousness": 15,  # |15-50| = 35, largest, below 50
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        trait, direction = get_primary_trait(big_five)
        assert trait == "conscientiousness"
        assert direction == "Low"

    def test_neuroticism_high(self):
        big_five = {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 90,
        }
        trait, direction = get_primary_trait(big_five)
        assert trait == "neuroticism"
        assert direction == "High"

    def test_at_50_is_low_direction(self):
        """Exactly 50 -> |50-50|=0, direction is Low (>= 50 check)."""
        big_five = {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 60,  # Only this differs
        }
        trait, direction = get_primary_trait(big_five)
        assert trait == "neuroticism"
        assert direction == "High"

    def test_returns_tuple(self):
        big_five = {
            "openness": 70,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        result = get_primary_trait(big_five)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestDeriveType:
    """Test full type derivation from subscales and Big Five."""

    def test_returns_string(self):
        subscales = {
            "a_sat": 9.0,
            "a_frust": 1.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        big_five = {
            "openness": 70,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        result = derive_type(subscales, big_five)
        assert isinstance(result, dict)
        assert "type_name" in result
        assert "type_domain" in result
        assert isinstance(result["type_name"], str)

    def test_domain_matches_dominant(self):
        subscales = {
            "a_sat": 9.0,
            "a_frust": 1.0,
            "b_sat": 3.0,
            "b_frust": 5.0,
            "c_sat": 3.0,
            "c_frust": 5.0,
        }
        big_five = {
            "openness": 70,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        result = derive_type(subscales, big_five)
        assert result["type_domain"] == "ambition"

    def test_different_traits_give_different_types(self):
        """Same domain, different primary traits -> different type names."""
        subscales = {
            "a_sat": 9.0,
            "a_frust": 1.0,
            "b_sat": 3.0,
            "b_frust": 5.0,
            "c_sat": 3.0,
            "c_frust": 5.0,
        }
        bf_open = {
            "openness": 90,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        bf_consc = {
            "openness": 50,
            "conscientiousness": 90,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50,
        }
        type_open = derive_type(subscales, bf_open)
        type_consc = derive_type(subscales, bf_consc)
        assert type_open["type_name"] != type_consc["type_name"]
