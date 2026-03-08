"""Tests for Belbin team-role inference module.

Reference: abc-assessment-spec Section 2.6

Rule-based inference: all rules evaluated (no short-circuit), multiple roles
can apply. Strict inequality (>) used throughout per spec.
"""

from src.python_scoring.belbin_inference import infer_belbin_roles


def _make_subscales(
    a_sat: float = 5.0,
    a_frust: float = 5.0,
    b_sat: float = 5.0,
    b_frust: float = 5.0,
    c_sat: float = 5.0,
    c_frust: float = 5.0,
) -> dict[str, float]:
    """Build a subscale dict with sensible defaults for concise test setup."""
    return {
        "a_sat": a_sat,
        "a_frust": a_frust,
        "b_sat": b_sat,
        "b_frust": b_frust,
        "c_sat": c_sat,
        "c_frust": c_frust,
    }


class TestShaperRole:
    """Shaper fires when A-sat > 6.5; qualifier depends on B-sat."""

    def test_shaper_inspiring(self):
        """A-sat > 6.5 AND B-sat > 6.0 -> Shaper (Inspiring)."""
        roles = infer_belbin_roles(_make_subscales(a_sat=7.0, b_sat=7.0))
        role_names = [r["role"] for r in roles]
        assert "Shaper" in role_names
        shaper = next(r for r in roles if r["role"] == "Shaper")
        assert shaper["qualifier"] == "Inspiring"

    def test_shaper_driving(self):
        """A-sat > 6.5 AND B-sat <= 6.0 -> Shaper (Driving)."""
        roles = infer_belbin_roles(_make_subscales(a_sat=7.0, b_sat=4.0))
        role_names = [r["role"] for r in roles]
        assert "Shaper" in role_names
        shaper = next(r for r in roles if r["role"] == "Shaper")
        assert shaper["qualifier"] == "Driving"


class TestSpecialistRole:
    """Specialist fires when C-sat > 7.0 AND C-frust < 3.0."""

    def test_specialist_deep_mastery(self):
        roles = infer_belbin_roles(_make_subscales(c_sat=8.0, c_frust=2.0))
        role_names = [r["role"] for r in roles]
        assert "Specialist" in role_names
        specialist = next(r for r in roles if r["role"] == "Specialist")
        assert specialist["qualifier"] == "Deep Mastery"


class TestTeamworkerRole:
    """Teamworker fires when B-sat > 7.0 AND B-frust < 3.0."""

    def test_teamworker_anchor(self):
        roles = infer_belbin_roles(_make_subscales(b_sat=8.0, b_frust=2.0))
        role_names = [r["role"] for r in roles]
        assert "Teamworker" in role_names
        teamworker = next(r for r in roles if r["role"] == "Teamworker")
        assert teamworker["qualifier"] == "Anchor"


class TestCoordinatorRole:
    """Coordinator fires when all three sat > 5.0."""

    def test_coordinator_balanced(self):
        roles = infer_belbin_roles(_make_subscales(a_sat=6.0, b_sat=6.0, c_sat=6.0))
        role_names = [r["role"] for r in roles]
        assert "Coordinator" in role_names
        coordinator = next(r for r in roles if r["role"] == "Coordinator")
        assert coordinator["qualifier"] == "Balanced"


class TestMonitorEvaluatorRole:
    """Monitor-Evaluator fires when A-frust > 6.0 OR B-frust > 6.0."""

    def test_monitor_evaluator_via_a_frust(self):
        roles = infer_belbin_roles(_make_subscales(a_frust=7.0))
        role_names = [r["role"] for r in roles]
        assert "Monitor-Evaluator" in role_names
        me = next(r for r in roles if r["role"] == "Monitor-Evaluator")
        assert me["qualifier"] == "Vigilant"

    def test_monitor_evaluator_via_b_frust(self):
        roles = infer_belbin_roles(_make_subscales(b_frust=7.0))
        role_names = [r["role"] for r in roles]
        assert "Monitor-Evaluator" in role_names


class TestPlantRole:
    """Plant fires when C-sat > 6.5 AND C-frust < 4.0 AND A-sat < 5.0."""

    def test_plant_creative(self):
        roles = infer_belbin_roles(_make_subscales(c_sat=7.0, c_frust=3.0, a_sat=4.0))
        role_names = [r["role"] for r in roles]
        assert "Plant" in role_names
        plant = next(r for r in roles if r["role"] == "Plant")
        assert plant["qualifier"] == "Creative"

    def test_plant_not_triggered_when_a_sat_high(self):
        """High A-sat disqualifies Plant — they become Shaper or Coordinator instead."""
        roles = infer_belbin_roles(_make_subscales(c_sat=7.0, c_frust=3.0, a_sat=7.0))
        role_names = [r["role"] for r in roles]
        assert "Plant" not in role_names

    def test_plant_boundary_c_sat_exactly_6_5(self):
        """c_sat=6.5 exactly should NOT trigger Plant (needs > 6.5)."""
        roles = infer_belbin_roles(_make_subscales(c_sat=6.5, c_frust=3.0, a_sat=4.0))
        role_names = [r["role"] for r in roles]
        assert "Plant" not in role_names


class TestImplementerRole:
    """Implementer fires when C-sat > 5.5 AND A-sat > 5.5 AND C-frust < 4.0."""

    def test_implementer_systematic(self):
        roles = infer_belbin_roles(_make_subscales(c_sat=6.0, a_sat=6.0, c_frust=3.0))
        role_names = [r["role"] for r in roles]
        assert "Implementer" in role_names
        impl = next(r for r in roles if r["role"] == "Implementer")
        assert impl["qualifier"] == "Systematic"

    def test_implementer_not_triggered_high_c_frust(self):
        """High craft frustration blocks Implementer."""
        roles = infer_belbin_roles(_make_subscales(c_sat=6.0, a_sat=6.0, c_frust=5.0))
        role_names = [r["role"] for r in roles]
        assert "Implementer" not in role_names


class TestCompleterFinisherRole:
    """Completer-Finisher fires when C-sat > 6.0 AND C-frust > 5.0."""

    def test_completer_finisher_quality_driven(self):
        roles = infer_belbin_roles(_make_subscales(c_sat=7.0, c_frust=6.0))
        role_names = [r["role"] for r in roles]
        assert "Completer-Finisher" in role_names
        cf = next(r for r in roles if r["role"] == "Completer-Finisher")
        assert cf["qualifier"] == "Quality Driven"

    def test_completer_finisher_boundary_c_frust_exactly_5(self):
        """c_frust=5.0 exactly should NOT trigger (needs > 5.0)."""
        roles = infer_belbin_roles(_make_subscales(c_sat=7.0, c_frust=5.0))
        role_names = [r["role"] for r in roles]
        assert "Completer-Finisher" not in role_names


class TestFallbackRole:
    """When no rule matches, return Resource Investigator (Seeking)."""

    def test_fallback_resource_investigator(self):
        """Moderate scores that trigger no rule."""
        roles = infer_belbin_roles(
            _make_subscales(
                a_sat=4.0,
                a_frust=4.0,
                b_sat=4.0,
                b_frust=4.0,
                c_sat=4.0,
                c_frust=4.0,
            )
        )
        assert len(roles) == 1
        assert roles[0]["role"] == "Resource Investigator"
        assert roles[0]["qualifier"] == "Seeking"

    def test_all_moderate_low_only_fallback(self):
        """All scores at 3.0 -> only Resource Investigator."""
        roles = infer_belbin_roles(
            _make_subscales(
                a_sat=3.0,
                a_frust=3.0,
                b_sat=3.0,
                b_frust=3.0,
                c_sat=3.0,
                c_frust=3.0,
            )
        )
        assert len(roles) == 1
        assert roles[0]["role"] == "Resource Investigator"


class TestMultipleRoles:
    """Multiple rules can fire in a single evaluation."""

    def test_shaper_inspiring_and_coordinator(self):
        """a_sat=7, b_sat=7, c_sat=6 -> Shaper (Inspiring) + Coordinator (Balanced)."""
        roles = infer_belbin_roles(_make_subscales(a_sat=7.0, b_sat=7.0, c_sat=6.0))
        role_names = [r["role"] for r in roles]
        assert "Shaper" in role_names
        assert "Coordinator" in role_names

    def test_specialist_and_coordinator(self):
        """c_sat=8, c_frust=2, a_sat=6, b_sat=6 -> Specialist + Coordinator."""
        roles = infer_belbin_roles(
            _make_subscales(
                a_sat=6.0,
                b_sat=6.0,
                c_sat=8.0,
                c_frust=2.0,
            )
        )
        role_names = [r["role"] for r in roles]
        assert "Specialist" in role_names
        assert "Coordinator" in role_names


class TestBoundaryConditions:
    """Strict inequality (>) means exact boundary values must not trigger."""

    def test_a_sat_exactly_6_5_no_shaper(self):
        """a_sat=6.5 exactly should NOT trigger Shaper (needs > 6.5)."""
        roles = infer_belbin_roles(_make_subscales(a_sat=6.5, b_sat=7.0))
        role_names = [r["role"] for r in roles]
        assert "Shaper" not in role_names

    def test_c_sat_exactly_7_0_no_specialist(self):
        """c_sat=7.0 exactly should NOT trigger Specialist (needs > 7.0)."""
        roles = infer_belbin_roles(_make_subscales(c_sat=7.0, c_frust=2.0))
        role_names = [r["role"] for r in roles]
        assert "Specialist" not in role_names


class TestReturnStructure:
    """Validate that return values conform to the expected schema."""

    def test_returns_list_of_dicts_with_role_and_qualifier(self):
        roles = infer_belbin_roles(_make_subscales(a_sat=7.0, b_sat=7.0))
        assert isinstance(roles, list)
        for role in roles:
            assert isinstance(role, dict)
            assert "role" in role
            assert "qualifier" in role
            assert isinstance(role["role"], str)
            assert isinstance(role["qualifier"], str)
