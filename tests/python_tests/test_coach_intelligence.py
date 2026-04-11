"""Tests for the coach intelligence module."""

from src.python_scoring.coach_intelligence import (
    CoachProfile,
    compute_archetype_distribution,
    compute_cross_sport_patterns,
    compute_frustration_recovery,
    detect_transmission_signal,
)


class TestArchetypeDistribution:
    def test_empty_list(self):
        result = compute_archetype_distribution([])
        assert result["total"] == 0

    def test_single_type(self):
        result = compute_archetype_distribution(["Pioneer", "Pioneer", "Pioneer"])
        assert result["counts"]["Pioneer"] == 3
        assert result["proportions"]["Pioneer"] == 1.0

    def test_mixed_types(self):
        result = compute_archetype_distribution(["Pioneer", "Captain", "Pioneer"])
        assert result["counts"]["Pioneer"] == 2
        assert result["counts"]["Captain"] == 1
        assert abs(result["proportions"]["Pioneer"] - 0.667) < 0.01


class TestFrustrationRecovery:
    def test_no_episodes(self):
        result = compute_frustration_recovery([{"domain": "ambition", "scores": [2.0, 3.0, 2.5]}])
        assert result["ambition"]["episodes_analyzed"] == 0

    def test_recovery_detected(self):
        result = compute_frustration_recovery([{"domain": "ambition", "scores": [2.0, 5.0, 3.0]}])
        assert result["ambition"]["episodes_analyzed"] == 1
        assert result["ambition"]["recovery_rate"] == 1.0
        assert result["ambition"]["median_recovery_time"] == 1

    def test_no_recovery(self):
        result = compute_frustration_recovery([{"domain": "craft", "scores": [5.0, 6.0, 7.0, 8.0]}])
        assert result["craft"]["recovery_rate"] == 0.0


class TestTransmissionSignal:
    def test_no_signal_when_few_affected(self):
        result = detect_transmission_signal(
            [
                {"athlete_id": "a1", "scores": [3.0, 5.0]},
                {"athlete_id": "a2", "scores": [3.0, 3.0]},
                {"athlete_id": "a3", "scores": [3.0, 3.0]},
            ],
            min_affected=3,
        )
        assert result is None

    def test_signal_detected(self):
        result = detect_transmission_signal(
            [
                {"athlete_id": "a1", "scores": [3.0, 5.0]},
                {"athlete_id": "a2", "scores": [3.0, 5.0]},
                {"athlete_id": "a3", "scores": [3.0, 5.0]},
            ],
            min_affected=3,
        )
        assert result is not None
        assert result["affected_count"] == 3
        assert "narrative" in result

    def test_all_athletes_below_threshold(self):
        result = detect_transmission_signal(
            [
                {"athlete_id": "a1", "scores": [3.0, 3.0]},
                {"athlete_id": "a2", "scores": [3.0, 3.0]},
                {"athlete_id": "a3", "scores": [3.0, 3.0]},
            ],
            min_affected=3,
        )
        assert result is None

    def test_short_history_skipped(self):
        result = detect_transmission_signal(
            [
                {"athlete_id": "a1", "scores": [5.0]},
                {"athlete_id": "a2", "scores": [5.0]},
                {"athlete_id": "a3", "scores": [5.0]},
            ],
            min_affected=3,
        )
        assert result is None

    def test_proportion_calculated(self):
        result = detect_transmission_signal(
            [
                {"athlete_id": "a1", "scores": [3.0, 5.0]},
                {"athlete_id": "a2", "scores": [3.0, 5.0]},
                {"athlete_id": "a3", "scores": [3.0, 5.0]},
                {"athlete_id": "a4", "scores": [3.0, 3.0]},
            ],
            min_affected=3,
        )
        assert result is not None
        assert result["proportion_affected"] == 0.75


class TestCrossSportPatterns:
    def test_empty_data(self):
        result = compute_cross_sport_patterns({})
        assert result["sports"] == {}

    def test_single_sport(self):
        result = compute_cross_sport_patterns(
            {
                "basketball": [
                    {"type_name": "Pioneer", "domain_states": {"ambition": "Thriving"}},
                    {"type_name": "Captain", "domain_states": {"ambition": "Thriving"}},
                ]
            }
        )
        assert result["sports"]["basketball"]["athlete_count"] == 2
        assert result["comparisons"]["total_athletes"] == 2

    def test_sport_with_empty_athlete_list(self):
        result = compute_cross_sport_patterns({"basketball": []})
        assert result["sports"]["basketball"]["athlete_count"] == 0

    def test_multiple_sports(self):
        result = compute_cross_sport_patterns(
            {
                "basketball": [
                    {"type_name": "Pioneer", "domain_states": {}},
                ],
                "swimming": [
                    {"type_name": "Artisan", "domain_states": {}},
                ],
            }
        )
        assert len(result["comparisons"]["sports_coached"]) == 2
        assert result["comparisons"]["total_athletes"] == 2


class TestCoachProfile:
    def test_add_athlete(self):
        coach = CoachProfile("c1")
        coach.add_athlete("a1", "Pioneer", {"ambition": "Thriving"})
        assert len(coach.athletes) == 1

    def test_sport_history_tracked(self):
        coach = CoachProfile("c1")
        coach.add_athlete("a1", "Pioneer", {}, sport="basketball")
        coach.add_athlete("a2", "Artisan", {}, sport="swimming")
        assert "basketball" in coach.sport_history
        assert "swimming" in coach.sport_history

    def test_intervention_logging(self):
        coach = CoachProfile("c1")
        coach.log_intervention("a1", "craft", "skill session", 6.0, 4.0)
        summary = coach.get_intervention_summary()
        assert summary["completed"] == 1
        assert summary["mean_improvement"] == 2.0

    def test_incomplete_intervention(self):
        coach = CoachProfile("c1")
        coach.log_intervention("a1", "craft", "ongoing", 6.0)
        summary = coach.get_intervention_summary()
        assert summary["completed"] == 0
        assert summary["mean_improvement"] is None

    def test_summary(self):
        coach = CoachProfile("c1")
        coach.add_athlete("a1", "Pioneer", {"ambition": "Thriving"})
        coach.add_athlete("a2", "Pioneer", {"ambition": "Vulnerable"})
        summary = coach.get_summary()
        assert summary["total_athletes"] == 2
        assert summary["coach_id"] == "c1"


class TestCoachProfileEdgeCases:
    def test_empty_coach_summary(self):
        coach = CoachProfile("c_empty")
        summary = coach.get_summary()
        assert isinstance(summary, dict)
        assert summary["total_athletes"] == 0
        assert summary["archetype_distribution"]["total"] == 0

    def test_single_athlete(self):
        coach = CoachProfile("c_single")
        coach.add_athlete("a1", "Pioneer", {"ambition": "Thriving"}, sport="tennis")
        summary = coach.get_summary()
        assert summary["total_athletes"] == 1

    def test_multiple_incomplete_interventions(self):
        coach = CoachProfile("c_incomplete")
        coach.log_intervention("a1", "ambition", "goal setting", 7.0)
        coach.log_intervention("a2", "belonging", "team activity", 6.5)
        coach.log_intervention("a3", "craft", "drill session", 5.0)
        summary = coach.get_intervention_summary()
        assert summary["total_interventions"] == 3
        assert summary["completed"] == 0
        assert summary["mean_improvement"] is None
