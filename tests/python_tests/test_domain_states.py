"""Tests for domain state classification module.

Reference: abc-assessment-spec Section 2.2 (domain state classification)
Split thresholds on the 0-10 normalized scale:
  Satisfaction threshold: 6.46
  Frustration threshold:  4.38

| Satisfaction | Frustration | State      |
|-------------|-------------|------------|
| >= 6.46     | < 4.38      | Thriving   |
| >= 6.46     | >= 4.38     | Vulnerable |
| < 6.46      | < 4.38      | Mild    |
| < 6.46      | >= 4.38     | Distressed |
"""

from src.python_scoring.domain_classification import (
    classify_all_domains,
    classify_domain_state,
)


class TestClassifyDomainState:
    """Test single domain classification."""

    def test_thriving(self):
        assert classify_domain_state(sat=8.0, frust=2.0) == "Thriving"

    def test_vulnerable(self):
        assert classify_domain_state(sat=8.0, frust=8.0) == "Vulnerable"

    def test_dormant(self):
        assert classify_domain_state(sat=2.0, frust=2.0) == "Mild"

    def test_distressed(self):
        assert classify_domain_state(sat=2.0, frust=8.0) == "Distressed"

    # Boundary tests at split thresholds (sat=6.46, frust=4.38)
    def test_boundary_sat_above_frust_below(self):
        """sat >= 6.46, frust < 4.38 -> Thriving."""
        assert classify_domain_state(sat=6.46, frust=4.37) == "Thriving"

    def test_boundary_both_at_threshold(self):
        """Both at threshold -> Vulnerable."""
        assert classify_domain_state(sat=6.46, frust=4.38) == "Vulnerable"

    def test_boundary_sat_below_frust_at(self):
        """sat < 6.46, frust >= 4.38 -> Distressed."""
        assert classify_domain_state(sat=6.45, frust=4.38) == "Distressed"

    def test_boundary_both_below(self):
        """sat < 6.46, frust < 4.38 -> Mild."""
        assert classify_domain_state(sat=6.45, frust=4.37) == "Mild"

    # Extreme values
    def test_perfect_thriving_scores(self):
        assert classify_domain_state(sat=10.0, frust=0.0) == "Thriving"

    def test_perfect_distressed_scores(self):
        assert classify_domain_state(sat=0.0, frust=10.0) == "Distressed"

    def test_all_zero(self):
        assert classify_domain_state(sat=0.0, frust=0.0) == "Mild"

    def test_all_max(self):
        assert classify_domain_state(sat=10.0, frust=10.0) == "Vulnerable"


class TestClassifyAllDomains:
    """Test classifying all three domains from subscale scores."""

    def test_all_thriving(self):
        subscales = {
            "a_sat": 10.0,
            "a_frust": 0.0,
            "b_sat": 10.0,
            "b_frust": 0.0,
            "c_sat": 10.0,
            "c_frust": 0.0,
        }
        states = classify_all_domains(subscales)
        assert states["ambition"] == "Thriving"
        assert states["belonging"] == "Thriving"
        assert states["craft"] == "Thriving"

    def test_all_distressed(self):
        subscales = {
            "a_sat": 0.0,
            "a_frust": 10.0,
            "b_sat": 0.0,
            "b_frust": 10.0,
            "c_sat": 0.0,
            "c_frust": 10.0,
        }
        states = classify_all_domains(subscales)
        assert states["ambition"] == "Distressed"
        assert states["belonging"] == "Distressed"
        assert states["craft"] == "Distressed"

    def test_all_vulnerable(self):
        subscales = {
            "a_sat": 10.0,
            "a_frust": 10.0,
            "b_sat": 10.0,
            "b_frust": 10.0,
            "c_sat": 10.0,
            "c_frust": 10.0,
        }
        states = classify_all_domains(subscales)
        assert states["ambition"] == "Vulnerable"
        assert states["belonging"] == "Vulnerable"
        assert states["craft"] == "Vulnerable"

    def test_all_dormant(self):
        subscales = {
            "a_sat": 0.0,
            "a_frust": 0.0,
            "b_sat": 0.0,
            "b_frust": 0.0,
            "c_sat": 0.0,
            "c_frust": 0.0,
        }
        states = classify_all_domains(subscales)
        assert states["ambition"] == "Mild"
        assert states["belonging"] == "Mild"
        assert states["craft"] == "Mild"

    def test_mixed_states(self):
        subscales = {
            "a_sat": 8.0,
            "a_frust": 2.0,  # Thriving
            "b_sat": 3.0,
            "b_frust": 8.0,  # Distressed
            "c_sat": 8.0,
            "c_frust": 8.0,  # Vulnerable
        }
        states = classify_all_domains(subscales)
        assert states["ambition"] == "Thriving"
        assert states["belonging"] == "Distressed"
        assert states["craft"] == "Vulnerable"

    def test_returns_three_domains(self):
        subscales = {
            "a_sat": 5.0,
            "a_frust": 5.0,
            "b_sat": 5.0,
            "b_frust": 5.0,
            "c_sat": 5.0,
            "c_frust": 5.0,
        }
        states = classify_all_domains(subscales)
        assert set(states.keys()) == {"ambition", "belonging", "craft"}
