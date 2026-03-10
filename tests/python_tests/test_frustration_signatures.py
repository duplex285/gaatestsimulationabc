"""Tests for frustration signature detection module.

Reference: abc-assessment-spec Section 2.5 (frustration signatures)
Uses split thresholds aligned with domain classification:
  Satisfaction threshold: 6.46
  Frustration threshold:  4.38

Pattern 1 — High sat + high frust (sat >= 6.46, frust >= 4.38) -> medium risk
  A: Blocked Drive, B: Conditional Belonging, C: Evaluated Mastery
Pattern 2 — Low sat + high frust (sat < 6.46, frust >= 4.38) -> high risk
  A: Controlled Motivation, B: Active Exclusion, C: Competence Threat

No gap zone: every participant with frust >= 4.38 receives a signature.
"""

from src.python_scoring.frustration_signatures import detect_signatures


def _low_frust_subscales() -> dict[str, float]:
    """All scores with low frustration — no signatures expected."""
    return {
        "a_sat": 5.0,
        "a_frust": 3.0,
        "b_sat": 5.0,
        "b_frust": 3.0,
        "c_sat": 5.0,
        "c_frust": 3.0,
    }


class TestNoSignatures:
    """Cases where no frustration signatures should fire."""

    def test_all_low_frust(self):
        """Frustration below 4.38 produces no signatures."""
        result = detect_signatures(_low_frust_subscales())
        assert result == []

    def test_frust_just_below_threshold(self):
        """frust=4.37 is < 4.38, so no signature fires."""
        subscales = _low_frust_subscales()
        subscales["a_frust"] = 4.37
        result = detect_signatures(subscales)
        assert result == []


class TestSingleSignatures:
    """Cases producing exactly one frustration signature."""

    def test_blocked_drive(self):
        """High sat + high frust in ambition -> Blocked Drive, medium risk."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Blocked Drive"
        assert result[0]["domain"] == "ambition"
        assert result[0]["risk"] == "medium"

    def test_controlled_motivation(self):
        """Low sat + high frust in ambition -> Controlled Motivation, high risk."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 3.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Controlled Motivation"
        assert result[0]["domain"] == "ambition"
        assert result[0]["risk"] == "high"

    def test_no_gap_zone_mid_sat_high_frust(self):
        """sat=5.0, frust=5.0: sat < 6.46 and frust >= 4.38 -> high risk signature fires."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 5.0
        subscales["a_frust"] = 5.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Controlled Motivation"
        assert result[0]["risk"] == "high"


class TestDomainLabels:
    """Each domain produces the correct label names."""

    def test_belonging_high_sat(self):
        subscales = _low_frust_subscales()
        subscales["b_sat"] = 7.0
        subscales["b_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Conditional Belonging"
        assert result[0]["domain"] == "belonging"

    def test_belonging_low_sat(self):
        subscales = _low_frust_subscales()
        subscales["b_sat"] = 3.0
        subscales["b_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Active Exclusion"
        assert result[0]["domain"] == "belonging"

    def test_craft_high_sat(self):
        subscales = _low_frust_subscales()
        subscales["c_sat"] = 7.0
        subscales["c_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Evaluated Mastery"
        assert result[0]["domain"] == "craft"

    def test_craft_low_sat(self):
        subscales = _low_frust_subscales()
        subscales["c_sat"] = 3.0
        subscales["c_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Competence Threat"
        assert result[0]["domain"] == "craft"


class TestMultipleSignatures:
    """A person can have signatures across multiple domains."""

    def test_signatures_across_all_domains(self):
        subscales = {
            "a_sat": 7.0,
            "a_frust": 7.0,  # Blocked Drive
            "b_sat": 3.0,
            "b_frust": 7.0,  # Active Exclusion
            "c_sat": 7.0,
            "c_frust": 7.0,  # Evaluated Mastery
        }
        result = detect_signatures(subscales)
        assert len(result) == 3
        labels = {sig["label"] for sig in result}
        assert labels == {"Blocked Drive", "Active Exclusion", "Evaluated Mastery"}


class TestBoundaryConditions:
    """Boundary tests at split thresholds."""

    def test_frust_exactly_at_threshold_fires(self):
        """frust=4.38 is >= 4.38, so signature fires."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 4.38
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Blocked Drive"

    def test_sat_exactly_at_threshold_is_medium(self):
        """sat=6.46 is >= 6.46, so medium risk (Blocked Drive, not Controlled Motivation)."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 6.46
        subscales["a_frust"] = 5.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Blocked Drive"
        assert result[0]["risk"] == "medium"

    def test_sat_just_below_threshold_is_high(self):
        """sat=6.45 is < 6.46, so high risk (Controlled Motivation)."""
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 6.45
        subscales["a_frust"] = 5.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Controlled Motivation"
        assert result[0]["risk"] == "high"


class TestReturnStructure:
    """Verify the return value structure."""

    def test_result_dict_has_correct_keys(self):
        subscales = _low_frust_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert set(result[0].keys()) == {"label", "domain", "risk"}
