"""Integration tests for EnhancedABCScorer with optional passion and
regulatory layers.

Reference: improvement-plan-personalization-engine.md Sections 16.1, 16.2
Reference: src/python_scoring/scoring_pipeline.py
"""

from __future__ import annotations

import pytest

from src.python_scoring.overinvestment_trigger import DailySignals
from src.python_scoring.scoring_pipeline import EnhancedABCScorer

REVERSE_POSITIONS = (4, 6)


def _core_responses(
    a_sat=4,
    a_frust=4,
    b_sat=4,
    b_frust=4,
    c_sat=4,
    c_frust=4,
) -> dict[str, int]:
    """Build a 36-item response dict that targets the supplied subscale
    effective scores on the 1-7 scale, accounting for reverse coding at
    positions 4 and 6.
    """
    responses: dict[str, int] = {}
    targets = {
        "AS": a_sat,
        "AF": a_frust,
        "BS": b_sat,
        "BF": b_frust,
        "CS": c_sat,
        "CF": c_frust,
    }
    for prefix, target in targets.items():
        for i in range(1, 7):
            code = f"{prefix}{i}"
            responses[code] = (8 - target) if i in REVERSE_POSITIONS else target
    return responses


def _passion_harmonious() -> dict[str, int]:
    return {"HP1": 7, "HP2": 7, "HP3": 7, "OP1": 1, "OP2": 1, "OP3": 1}


def _passion_obsessive() -> dict[str, int]:
    return {"HP1": 1, "HP2": 1, "HP3": 1, "OP1": 7, "OP2": 7, "OP3": 7}


def _regulatory_identified() -> dict[str, int]:
    return {"AR1": 7, "AR2": 1, "BR1": 7, "BR2": 1, "CR1": 7, "CR2": 1}


def _regulatory_introjected() -> dict[str, int]:
    return {"AR1": 1, "AR2": 7, "BR1": 1, "BR2": 7, "CR1": 1, "CR2": 7}


def _group_conscious_healthy() -> dict[str, int]:
    """High collective satisfaction, high team identification."""
    return {"AG1": 7, "BG1": 7, "CG1": 7, "TI1": 7, "TI2": 7}


def _group_conscious_empathic_risk() -> dict[str, int]:
    """High team identification, low collective satisfaction on all domains."""
    return {"AG1": 1, "BG1": 1, "CG1": 1, "TI1": 7, "TI2": 7}


def _causality_autonomy_dominant() -> dict[str, int]:
    """High on autonomy, low on controlled and impersonal."""
    return {
        "AO1": 7,
        "AO2": 7,
        "AO3": 7,
        "AO4": 7,
        "CO1": 1,
        "CO2": 1,
        "CO3": 1,
        "CO4": 1,
        "IO1": 1,
        "IO2": 1,
        "IO3": 1,
        "IO4": 1,
    }


def _causality_controlled_dominant() -> dict[str, int]:
    return {
        "AO1": 1,
        "AO2": 1,
        "AO3": 1,
        "AO4": 1,
        "CO1": 7,
        "CO2": 7,
        "CO3": 7,
        "CO4": 7,
        "IO1": 1,
        "IO2": 1,
        "IO3": 1,
        "IO4": 1,
    }


def _self_concordance_autonomous() -> dict[str, int]:
    return {"SC1": 1, "SC2": 1, "SC3": 7, "SC4": 7}


def _self_concordance_controlled() -> dict[str, int]:
    return {"SC1": 7, "SC2": 7, "SC3": 1, "SC4": 1}


@pytest.fixture
def scorer():
    return EnhancedABCScorer(demographics={"gender": "male"})


class TestBackwardCompatibility:
    def test_core_only_score_still_works(self, scorer):
        result = scorer.score(_core_responses())
        assert result["passion"] is None
        assert result["regulatory"] is None
        assert result["overinvestment"] is None
        assert result["group_conscious"] is None
        assert result["causality"] is None
        assert result["self_concordance"] is None
        assert result["narratives"]["passion"] is None
        assert result["narratives"]["regulatory"] == {}
        assert result["narratives"]["erosion"] == {}
        assert result["narratives"]["group_conscious"] == {}
        assert result["narratives"]["causality"] is None
        assert result["narratives"]["self_concordance"] is None
        assert result["self_concordance_trajectory"] is None
        assert result["narratives"]["self_concordance_trajectory"] is None


class TestPassionIntegration:
    def test_harmonious_passion_routes_to_harmonious_path(self, scorer):
        # Thriving-only ABC with harmonious passion -> no trigger but
        # passion leaning should be reported.
        thriving = _core_responses(a_sat=7, a_frust=1, b_sat=7, b_frust=1, c_sat=7, c_frust=1)
        result = scorer.score(
            thriving,
            passion_responses=_passion_harmonious(),
        )
        assert result["passion"].leaning == "harmonious"
        assert result["overinvestment"].path == "harmonious"
        assert result["narratives"]["passion"]["summary"]
        assert result["narratives"]["overinvestment"]

    def test_obsessive_passion_with_declining_signals_routes_obsessive(self, scorer):
        thriving = _core_responses(a_sat=7, a_frust=1, b_sat=7, b_frust=1, c_sat=7, c_frust=1)
        signals = DailySignals(recovery_slope=30.0, cognitive_load=80.0)
        result = scorer.score(
            thriving,
            passion_responses=_passion_obsessive(),
            daily_signals=signals,
        )
        assert result["overinvestment"].path == "obsessive"

    def test_no_passion_no_overinvestment_field(self, scorer):
        result = scorer.score(_core_responses())
        assert result["overinvestment"] is None


class TestRegulatoryIntegration:
    def test_regulatory_profile_in_result(self, scorer):
        result = scorer.score(
            _core_responses(),
            regulatory_responses=_regulatory_identified(),
        )
        assert result["regulatory"] is not None
        assert result["regulatory"].domains["ambition"].style == "identified"
        assert result["narratives"]["regulatory"]["ambition"]

    def test_erosion_fires_across_two_measurements(self, scorer):
        # First measurement: identified across all domains
        scorer.score(
            _core_responses(),
            regulatory_responses=_regulatory_identified(),
            weeks_since_last=2,
        )
        # Second measurement: introjected across all domains
        result2 = scorer.score(
            _core_responses(),
            regulatory_responses=_regulatory_introjected(),
            weeks_since_last=2,
        )
        eroded = result2["transition"]["regulation_erosion_events"]
        assert set(eroded) == {"ambition", "belonging", "craft"}
        assert set(result2["narratives"]["erosion"].keys()) == {"ambition", "belonging", "craft"}

    def test_no_erosion_on_stable_regulation(self, scorer):
        scorer.score(
            _core_responses(),
            regulatory_responses=_regulatory_identified(),
        )
        result2 = scorer.score(
            _core_responses(),
            regulatory_responses=_regulatory_identified(),
        )
        assert result2["transition"]["regulation_erosion_events"] == []
        assert result2["narratives"]["erosion"] == {}


class TestGroupConsciousIntegration:
    def test_profile_attached_when_responses_provided(self, scorer):
        result = scorer.score(
            _core_responses(),
            group_conscious_responses=_group_conscious_healthy(),
        )
        assert result["group_conscious"] is not None
        assert result["group_conscious"].collective["ambition"].level == "high"
        assert result["group_conscious"].team_identification.level == "high"

    def test_collective_narratives_for_each_domain(self, scorer):
        result = scorer.score(
            _core_responses(),
            group_conscious_responses=_group_conscious_healthy(),
        )
        gc = result["narratives"]["group_conscious"]
        assert set(gc["collective"].keys()) == {"ambition", "belonging", "craft"}
        assert gc["team_identification"]

    def test_empathic_risk_narrative_when_flagged(self, scorer):
        result = scorer.score(
            _core_responses(),
            group_conscious_responses=_group_conscious_empathic_risk(),
        )
        gc = result["narratives"]["group_conscious"]
        assert "empathic_risk" in gc
        assert set(gc["empathic_risk_domains"]) == {"ambition", "belonging", "craft"}

    def test_no_empathic_risk_key_when_unflagged(self, scorer):
        result = scorer.score(
            _core_responses(),
            group_conscious_responses=_group_conscious_healthy(),
        )
        gc = result["narratives"]["group_conscious"]
        assert "empathic_risk" not in gc


class TestCausalityIntegration:
    def test_profile_attached_when_responses_provided(self, scorer):
        result = scorer.score(
            _core_responses(),
            causality_responses=_causality_autonomy_dominant(),
        )
        assert result["causality"] is not None
        assert result["causality"].dominant == "autonomy"
        assert result["narratives"]["causality"]

    def test_controlled_orientation_renders(self, scorer):
        result = scorer.score(
            _core_responses(),
            causality_responses=_causality_controlled_dominant(),
        )
        assert result["causality"].dominant == "controlled"
        # Narrative should differ from the autonomy version
        auto_result = scorer.score(
            _core_responses(),
            causality_responses=_causality_autonomy_dominant(),
        )
        assert result["narratives"]["causality"] != auto_result["narratives"]["causality"]


class TestSelfConcordanceIntegration:
    def test_profile_attached_when_responses_provided(self, scorer):
        result = scorer.score(
            _core_responses(),
            self_concordance_responses=_self_concordance_autonomous(),
            self_concordance_goal_text="make varsity",
        )
        assert result["self_concordance"] is not None
        assert result["self_concordance"].leaning == "autonomous"
        assert result["self_concordance"].goal_text == "make varsity"
        assert result["narratives"]["self_concordance"]

    def test_controlled_renders_different_text(self, scorer):
        autonomous = scorer.score(
            _core_responses(),
            self_concordance_responses=_self_concordance_autonomous(),
        )
        controlled = scorer.score(
            _core_responses(),
            self_concordance_responses=_self_concordance_controlled(),
        )
        assert (
            autonomous["narratives"]["self_concordance"]
            != controlled["narratives"]["self_concordance"]
        )

    def test_trajectory_suppressed_without_goal_id(self, scorer):
        """Without a goal_id, trajectory tracking does not fire."""
        result = scorer.score(
            _core_responses(),
            self_concordance_responses=_self_concordance_autonomous(),
        )
        assert result["self_concordance_trajectory"] is None
        assert result["narratives"]["self_concordance_trajectory"] is None

    def test_trajectory_insufficient_at_first_two_cycles(self, scorer):
        """With a goal_id but fewer than 3 cycles: insufficient_data, no narrative."""
        for _ in range(2):
            result = scorer.score(
                _core_responses(),
                self_concordance_responses=_self_concordance_autonomous(),
                self_concordance_goal_id="scholarship",
            )
        assert result["self_concordance_trajectory"] is not None
        assert result["self_concordance_trajectory"].label == "insufficient_data"
        assert result["narratives"]["self_concordance_trajectory"] is None

    def test_trajectory_fires_after_three_cycles(self, scorer):
        """After 3 cycles with clear direction: trajectory labeled and narrative rendered."""
        responses_in_order = [
            _self_concordance_controlled(),
            {"SC1": 4, "SC2": 4, "SC3": 4, "SC4": 4},  # midpoint
            _self_concordance_autonomous(),
        ]
        result = None
        for resp in responses_in_order:
            result = scorer.score(
                _core_responses(),
                self_concordance_responses=resp,
                self_concordance_goal_id="scholarship",
            )
        assert result is not None
        traj = result["self_concordance_trajectory"]
        assert traj is not None
        assert traj.label == "becoming_more_autonomous"
        assert traj.n_points_computable == 3
        assert result["narratives"]["self_concordance_trajectory"]

    def test_trajectory_tracks_multiple_goals_independently(self, scorer):
        """Two goals accumulated in parallel; each gets its own trajectory."""
        # Goal A: rising
        for resp in (
            _self_concordance_controlled(),
            {"SC1": 4, "SC2": 4, "SC3": 4, "SC4": 4},
            _self_concordance_autonomous(),
        ):
            scorer.score(
                _core_responses(),
                self_concordance_responses=resp,
                self_concordance_goal_id="goal-A",
            )
        # Goal B: falling
        for resp in (
            _self_concordance_autonomous(),
            {"SC1": 4, "SC2": 4, "SC3": 4, "SC4": 4},
            _self_concordance_controlled(),
        ):
            result = scorer.score(
                _core_responses(),
                self_concordance_responses=resp,
                self_concordance_goal_id="goal-B",
            )
        # The last call's result surfaces goal-B's trajectory
        assert result["self_concordance_trajectory"].label == "becoming_more_controlled"
        # But goal-A's trajectory still lives on the tracker
        goal_a_traj = scorer._goal_trajectory_tracker.get_trajectory("goal-A")
        assert goal_a_traj.label == "becoming_more_autonomous"


class TestFullStackIntegration:
    def test_all_layers_together(self, scorer):
        """Core + every optional layer + signals together."""
        thriving = _core_responses(a_sat=7, a_frust=1, b_sat=7, b_frust=1, c_sat=7, c_frust=1)
        result = scorer.score(
            thriving,
            passion_responses=_passion_harmonious(),
            regulatory_responses=_regulatory_identified(),
            group_conscious_responses=_group_conscious_healthy(),
            causality_responses=_causality_autonomy_dominant(),
            self_concordance_responses=_self_concordance_autonomous(),
            self_concordance_goal_text="qualify for nationals",
            daily_signals=DailySignals(recovery_slope=70.0, cognitive_load=40.0),
        )
        assert result["passion"] is not None
        assert result["regulatory"] is not None
        assert result["overinvestment"] is not None
        assert result["group_conscious"] is not None
        assert result["causality"] is not None
        assert result["self_concordance"] is not None
        assert result["narratives"]["passion"] is not None
        assert len(result["narratives"]["regulatory"]) == 3
        assert result["narratives"]["overinvestment"]
        assert result["narratives"]["group_conscious"]["collective"]
        assert result["narratives"]["causality"]
        assert result["narratives"]["self_concordance"]
