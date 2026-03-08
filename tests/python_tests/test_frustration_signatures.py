"""Tests for frustration signature detection module.

Reference: abc-assessment-spec Section 2.5 (frustration signatures)
Uses strict inequality (>) for all thresholds.

Pattern 1 — High sat + high frust (sat > 5.5, frust > 5.5) -> medium risk
  A: Blocked Drive, B: Conditional Belonging, C: Evaluated Mastery
Pattern 2 — Low sat + high frust (sat < 4.5, frust > 5.5) -> high risk
  A: Controlled Motivation, B: Active Exclusion, C: Competence Threat
"""

from src.python_scoring.frustration_signatures import detect_signatures


def _moderate_subscales() -> dict[str, float]:
    """All scores at 5.0 — no signatures expected."""
    return {
        "a_sat": 5.0,
        "a_frust": 5.0,
        "b_sat": 5.0,
        "b_frust": 5.0,
        "c_sat": 5.0,
        "c_frust": 5.0,
    }


class TestNoSignatures:
    """Cases where no frustration signatures should fire."""

    def test_all_moderate_scores(self):
        """All scores at 5.0 produce no signatures."""
        result = detect_signatures(_moderate_subscales())
        assert result == []

    def test_empty_list_when_no_patterns_match(self):
        """Scores in the middle band (sat between 4.5 and 5.5) with high frust produce nothing."""
        subscales = _moderate_subscales()
        subscales["a_frust"] = 8.0  # high frust, but sat=5.0 is neither > 5.5 nor < 4.5
        result = detect_signatures(subscales)
        assert result == []


class TestSingleSignatures:
    """Cases producing exactly one frustration signature."""

    def test_blocked_drive(self):
        """High sat + high frust in ambition -> Blocked Drive, medium risk."""
        subscales = _moderate_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Blocked Drive"
        assert result[0]["domain"] == "ambition"
        assert result[0]["risk"] == "medium"

    def test_controlled_motivation(self):
        """Low sat + high frust in ambition -> Controlled Motivation, high risk."""
        subscales = _moderate_subscales()
        subscales["a_sat"] = 3.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Controlled Motivation"
        assert result[0]["domain"] == "ambition"
        assert result[0]["risk"] == "high"


class TestDomainLabels:
    """Each domain produces the correct label names."""

    def test_belonging_high_sat(self):
        subscales = _moderate_subscales()
        subscales["b_sat"] = 7.0
        subscales["b_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Conditional Belonging"
        assert result[0]["domain"] == "belonging"

    def test_belonging_low_sat(self):
        subscales = _moderate_subscales()
        subscales["b_sat"] = 3.0
        subscales["b_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Active Exclusion"
        assert result[0]["domain"] == "belonging"

    def test_craft_high_sat(self):
        subscales = _moderate_subscales()
        subscales["c_sat"] = 7.0
        subscales["c_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert result[0]["label"] == "Evaluated Mastery"
        assert result[0]["domain"] == "craft"

    def test_craft_low_sat(self):
        subscales = _moderate_subscales()
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
    """Strict inequality means scores at the threshold do NOT trigger."""

    def test_sat_exactly_5point5_does_not_trigger_blocked(self):
        """sat=5.5 is NOT > 5.5, so no Blocked Drive signature."""
        subscales = _moderate_subscales()
        subscales["a_sat"] = 5.5
        subscales["a_frust"] = 6.0
        result = detect_signatures(subscales)
        assert result == []

    def test_sat_exactly_4point5_does_not_trigger_threat(self):
        """sat=4.5 is NOT < 4.5, so no Controlled Motivation signature."""
        subscales = _moderate_subscales()
        subscales["a_sat"] = 4.5
        subscales["a_frust"] = 6.0
        result = detect_signatures(subscales)
        assert result == []

    def test_frust_exactly_5point5_does_not_trigger(self):
        """frust=5.5 is NOT > 5.5, so no signature fires."""
        subscales = _moderate_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 5.5
        result = detect_signatures(subscales)
        assert result == []


class TestReturnStructure:
    """Verify the return value structure."""

    def test_result_dict_has_correct_keys(self):
        subscales = _moderate_subscales()
        subscales["a_sat"] = 7.0
        subscales["a_frust"] = 7.0
        result = detect_signatures(subscales)
        assert len(result) == 1
        assert set(result[0].keys()) == {"label", "domain", "risk"}
