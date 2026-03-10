"""Tests for Belbin team-role inference module.

Reference: abc-assessment-spec Section 2.6

Architecture: ABC subscales select the domain cluster; Big Five percentiles
differentiate roles within each cluster. Scoring is continuous:
role_score = domain_affinity × trait_percentile / 100.

Clusters (Aranzabal et al., 2022):
  Thinking (Craft):    Plant (O), Specialist (C), Monitor-Evaluator (N)
  People (Belonging):  Teamworker (A), Resource Investigator (E), Coordinator (C)
  Action (Ambition):   Shaper (E), Implementer (C), Completer-Finisher (N)
"""

from src.python_scoring.belbin_inference import (
    _rank_domains,
    infer_belbin_roles,
)


def _make_subscales(
    a_sat: float = 5.0,
    a_frust: float = 5.0,
    b_sat: float = 5.0,
    b_frust: float = 5.0,
    c_sat: float = 5.0,
    c_frust: float = 5.0,
) -> dict[str, float]:
    """Build a subscale dict with neutral defaults."""
    return {
        "a_sat": a_sat,
        "a_frust": a_frust,
        "b_sat": b_sat,
        "b_frust": b_frust,
        "c_sat": c_sat,
        "c_frust": c_frust,
    }


def _make_big_five(
    openness: float = 50.0,
    conscientiousness: float = 50.0,
    extraversion: float = 50.0,
    agreeableness: float = 50.0,
    neuroticism: float = 50.0,
) -> dict[str, float]:
    """Build a Big Five dict with neutral defaults."""
    return {
        "openness": openness,
        "conscientiousness": conscientiousness,
        "extraversion": extraversion,
        "agreeableness": agreeableness,
        "neuroticism": neuroticism,
    }


class TestRankDomains:
    """Domain ranking from satisfaction scores."""

    def test_craft_highest(self):
        ranks = _rank_domains(_make_subscales(c_sat=8.0, b_sat=5.0, a_sat=3.0))
        assert ranks["craft"] == 0
        assert ranks["belonging"] == 1
        assert ranks["ambition"] == 2

    def test_ambition_highest(self):
        ranks = _rank_domains(_make_subscales(a_sat=8.0, b_sat=5.0, c_sat=3.0))
        assert ranks["ambition"] == 0

    def test_belonging_highest(self):
        ranks = _rank_domains(_make_subscales(b_sat=8.0, a_sat=5.0, c_sat=3.0))
        assert ranks["belonging"] == 0

    def test_ties_broken_by_domain_order(self):
        """All equal -> ambition > belonging > craft."""
        ranks = _rank_domains(_make_subscales(a_sat=5.0, b_sat=5.0, c_sat=5.0))
        assert ranks["ambition"] == 0
        assert ranks["belonging"] == 1
        assert ranks["craft"] == 2


class TestThinkingCluster:
    """Craft-dominant profiles should produce Thinking cluster roles."""

    def test_plant_from_high_craft_high_openness(self):
        """Craft primary + high Openness -> Plant (Creative)."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(openness=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Plant" in role_names
        plant = next(r for r in roles if r["role"] == "Plant")
        assert plant["qualifier"] == "Creative"

    def test_specialist_from_high_craft_high_conscientiousness(self):
        """Craft primary + high C -> Specialist (Deep Mastery)."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(conscientiousness=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Specialist" in role_names
        specialist = next(r for r in roles if r["role"] == "Specialist")
        assert specialist["qualifier"] == "Deep Mastery"

    def test_monitor_evaluator_from_high_craft_high_neuroticism(self):
        """Craft primary + high N -> Monitor-Evaluator (Vigilant)."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(neuroticism=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Monitor-Evaluator" in role_names
        me = next(r for r in roles if r["role"] == "Monitor-Evaluator")
        assert me["qualifier"] == "Vigilant"


class TestPeopleCluster:
    """Belonging-dominant profiles should produce People cluster roles."""

    def test_teamworker_from_high_belonging_high_agreeableness(self):
        """Belonging primary + high A -> Teamworker (Anchor)."""
        roles = infer_belbin_roles(
            _make_subscales(b_sat=8.0, a_sat=3.0, c_sat=3.0),
            _make_big_five(agreeableness=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Teamworker" in role_names
        tw = next(r for r in roles if r["role"] == "Teamworker")
        assert tw["qualifier"] == "Anchor"

    def test_resource_investigator_from_high_belonging_high_extraversion(self):
        """Belonging primary + high E -> Resource Investigator (Networker)."""
        roles = infer_belbin_roles(
            _make_subscales(b_sat=8.0, a_sat=3.0, c_sat=3.0),
            _make_big_five(extraversion=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Resource Investigator" in role_names
        ri = next(r for r in roles if r["role"] == "Resource Investigator")
        assert ri["qualifier"] == "Networker"

    def test_coordinator_from_high_belonging_high_conscientiousness(self):
        """Belonging primary + high C -> Coordinator (Balanced)."""
        roles = infer_belbin_roles(
            _make_subscales(b_sat=8.0, a_sat=3.0, c_sat=3.0),
            _make_big_five(conscientiousness=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Coordinator" in role_names
        co = next(r for r in roles if r["role"] == "Coordinator")
        assert co["qualifier"] == "Balanced"


class TestActionCluster:
    """Ambition-dominant profiles should produce Action cluster roles."""

    def test_shaper_from_high_ambition_high_extraversion(self):
        """Ambition primary + high E -> Shaper (Inspiring)."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=8.0, b_sat=3.0, c_sat=3.0),
            _make_big_five(extraversion=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Shaper" in role_names
        shaper = next(r for r in roles if r["role"] == "Shaper")
        assert shaper["qualifier"] == "Inspiring"

    def test_implementer_from_high_ambition_high_conscientiousness(self):
        """Ambition primary + high C -> Implementer (Systematic)."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=8.0, b_sat=3.0, c_sat=3.0),
            _make_big_five(conscientiousness=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Implementer" in role_names
        imp = next(r for r in roles if r["role"] == "Implementer")
        assert imp["qualifier"] == "Systematic"

    def test_completer_finisher_from_high_ambition_high_neuroticism(self):
        """Ambition primary + high N -> Completer-Finisher (Quality Driven)."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=8.0, b_sat=3.0, c_sat=3.0),
            _make_big_five(neuroticism=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Completer-Finisher" in role_names
        cf = next(r for r in roles if r["role"] == "Completer-Finisher")
        assert cf["qualifier"] == "Quality Driven"


class TestQualifiers:
    """Qualifier depends on trait percentile relative to NATURAL_THRESHOLD."""

    def test_natural_qualifier_at_threshold(self):
        """Trait at exactly 60.0 -> natural qualifier."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(openness=60.0),
        )
        plant = next(r for r in roles if r["role"] == "Plant")
        assert plant["qualifier"] == "Creative"  # natural

    def test_manageable_qualifier_below_threshold(self):
        """Trait at 59.9 -> manageable qualifier."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(
                openness=59.9,
                conscientiousness=20.0,
                neuroticism=20.0,
                extraversion=20.0,
                agreeableness=20.0,
            ),
        )
        plant = next(r for r in roles if r["role"] == "Plant")
        assert plant["qualifier"] == "Conceptual"  # manageable

    def test_shaper_driving_when_extraversion_below_60(self):
        """Shaper with E < 60 -> Driving (manageable)."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=8.0, b_sat=3.0, c_sat=3.0),
            _make_big_five(extraversion=55.0, conscientiousness=20.0, neuroticism=20.0),
        )
        shaper = next(r for r in roles if r["role"] == "Shaper")
        assert shaper["qualifier"] == "Driving"


class TestMultipleRoles:
    """Multiple roles can fire when scores exceed threshold."""

    def test_primary_cluster_multiple_high_traits(self):
        """Craft primary with both O and C high -> Plant + Specialist."""
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0),
            _make_big_five(openness=70.0, conscientiousness=70.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Plant" in role_names
        assert "Specialist" in role_names

    def test_cross_cluster_when_secondary_domain_strong(self):
        """Close primary/secondary domains can produce cross-cluster roles."""
        # Craft primary (8.0) but ambition strong secondary (7.5)
        # High E should give Shaper from ambition cluster (0.5 * 0.75 = 0.375 > 0.30)
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=7.5, b_sat=3.0),
            _make_big_five(openness=70.0, extraversion=75.0),
        )
        role_names = [r["role"] for r in roles]
        assert "Plant" in role_names  # primary cluster
        assert "Shaper" in role_names  # secondary cluster (ambition)

    def test_all_moderate_still_produces_roles(self):
        """Even with all moderate scores, at least one role fires."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=5.0, b_sat=5.0, c_sat=5.0),
            _make_big_five(),
        )
        assert len(roles) >= 1


class TestGuaranteedRole:
    """Every profile gets at least one role — no fallback needed."""

    def test_all_low_scores_still_returns_role(self):
        """Even extreme low scores produce at least one role."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=1.0, b_sat=1.0, c_sat=1.0),
            _make_big_five(
                openness=1.0,
                conscientiousness=1.0,
                extraversion=1.0,
                agreeableness=1.0,
                neuroticism=1.0,
            ),
        )
        assert len(roles) >= 1
        assert all("role" in r and "qualifier" in r for r in roles)

    def test_all_high_scores_returns_multiple_roles(self):
        """High across the board produces several roles."""
        roles = infer_belbin_roles(
            _make_subscales(a_sat=9.0, b_sat=9.0, c_sat=9.0),
            _make_big_five(
                openness=80.0,
                conscientiousness=80.0,
                extraversion=80.0,
                agreeableness=80.0,
                neuroticism=80.0,
            ),
        )
        assert len(roles) >= 3

    def test_no_resource_investigator_fallback(self):
        """Resource Investigator is earned through belonging + E, not a fallback."""
        roles = infer_belbin_roles(
            _make_subscales(b_sat=8.0, a_sat=3.0, c_sat=3.0),
            _make_big_five(extraversion=75.0),
        )
        ri_roles = [r for r in roles if r["role"] == "Resource Investigator"]
        assert len(ri_roles) == 1
        assert ri_roles[0]["qualifier"] == "Networker"  # natural, not "Seeking"


class TestDomainAffinityScaling:
    """Roles from secondary/tertiary domains score lower."""

    def test_primary_domain_role_scores_higher_than_secondary(self):
        """Same trait percentile, but primary domain role should outscore secondary."""
        subscales = _make_subscales(c_sat=8.0, a_sat=6.0, b_sat=3.0)
        big_five = _make_big_five(conscientiousness=70.0)
        roles = infer_belbin_roles(subscales, big_five)

        specialist = next(r for r in roles if r["role"] == "Specialist")
        implementer = next((r for r in roles if r["role"] == "Implementer"), None)

        # Specialist (craft primary) should score higher than Implementer (ambition secondary)
        assert specialist["score"] > 0.5  # 1.0 * 0.70
        if implementer:
            assert specialist["score"] > implementer["score"]

    def test_tertiary_domain_roles_excluded(self):
        """Tertiary domain roles have affinity 0.0 and never fire.

        Roles are restricted to the top two domain clusters to reduce noise.
        """
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=6.0, b_sat=3.0),
            _make_big_five(agreeableness=99.0),
        )
        role_names = [r["role"] for r in roles]
        # Teamworker is belonging-domain, which is tertiary here
        # Affinity 0.0 × any trait = 0.0 — never fires
        assert "Teamworker" not in role_names


class TestReturnStructure:
    """Validate that return values conform to the expected schema."""

    def test_returns_list_of_dicts_with_role_qualifier_score(self):
        roles = infer_belbin_roles(
            _make_subscales(a_sat=7.0, b_sat=6.0),
            _make_big_five(extraversion=70.0),
        )
        assert isinstance(roles, list)
        for role in roles:
            assert isinstance(role, dict)
            assert "role" in role
            assert "qualifier" in role
            assert "score" in role
            assert isinstance(role["role"], str)
            assert isinstance(role["qualifier"], str)
            assert isinstance(role["score"], float)

    def test_roles_sorted_by_score_descending(self):
        roles = infer_belbin_roles(
            _make_subscales(c_sat=8.0, a_sat=7.0, b_sat=6.0),
            _make_big_five(openness=80.0, conscientiousness=70.0, extraversion=65.0),
        )
        scores = [r["score"] for r in roles]
        assert scores == sorted(scores, reverse=True)


class TestBackwardCompatibility:
    """Function works without explicit big_five argument (computes internally)."""

    def test_subscales_only_still_works(self):
        """Calling with only subscales should compute Big Five internally."""
        roles = infer_belbin_roles(_make_subscales(c_sat=8.0, a_sat=3.0, b_sat=3.0))
        assert len(roles) >= 1
        assert all("role" in r for r in roles)


class TestAllNineRolesCoverable:
    """Each of the 9 roles can be produced with appropriate inputs."""

    def test_all_roles_reachable(self):
        """Verify each role can fire with the right domain + trait combination."""
        all_reached = set()

        # Thinking cluster (craft primary)
        craft_sub = _make_subscales(c_sat=9.0, a_sat=2.0, b_sat=2.0)
        for trait, role_name in [
            ("openness", "Plant"),
            ("conscientiousness", "Specialist"),
            ("neuroticism", "Monitor-Evaluator"),
        ]:
            bf = _make_big_five(**{trait: 90.0})
            roles = infer_belbin_roles(craft_sub, bf)
            names = [r["role"] for r in roles]
            assert role_name in names, f"{role_name} not found with craft + {trait}"
            all_reached.add(role_name)

        # People cluster (belonging primary)
        belong_sub = _make_subscales(b_sat=9.0, a_sat=2.0, c_sat=2.0)
        for trait, role_name in [
            ("agreeableness", "Teamworker"),
            ("extraversion", "Resource Investigator"),
            ("conscientiousness", "Coordinator"),
        ]:
            bf = _make_big_five(**{trait: 90.0})
            roles = infer_belbin_roles(belong_sub, bf)
            names = [r["role"] for r in roles]
            assert role_name in names, f"{role_name} not found with belonging + {trait}"
            all_reached.add(role_name)

        # Action cluster (ambition primary)
        ambition_sub = _make_subscales(a_sat=9.0, b_sat=2.0, c_sat=2.0)
        for trait, role_name in [
            ("extraversion", "Shaper"),
            ("conscientiousness", "Implementer"),
            ("neuroticism", "Completer-Finisher"),
        ]:
            bf = _make_big_five(**{trait: 90.0})
            roles = infer_belbin_roles(ambition_sub, bf)
            names = [r["role"] for r in roles]
            assert role_name in names, f"{role_name} not found with ambition + {trait}"
            all_reached.add(role_name)

        assert len(all_reached) == 9
