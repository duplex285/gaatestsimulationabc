"""Tests for context gap analysis module.

Reference: abc-assessment-spec Section 2.7 (context gap analysis)

Formula: gap = team_score - personal_score (per subscale)
Threshold: -1.5 (strict less-than; exactly -1.5 does NOT flag)
Only satisfaction subscales (a_sat, b_sat, c_sat) trigger flags.
"""

from src.python_scoring.context_gap import compute_context_gaps


def _make_scores(a_sat=5.0, a_frust=5.0, b_sat=5.0, b_frust=5.0, c_sat=5.0, c_frust=5.0):
    """Build a subscale score dict with convenient defaults."""
    return {
        "a_sat": a_sat,
        "a_frust": a_frust,
        "b_sat": b_sat,
        "b_frust": b_frust,
        "c_sat": c_sat,
        "c_frust": c_frust,
    }


class TestNoneTeam:
    """When team scores are absent, no gaps or flags are produced."""

    def test_none_team_returns_empty_gaps(self):
        result = compute_context_gaps(personal=_make_scores(), team=None)
        assert result["gaps"] == {}

    def test_none_team_returns_empty_flagged(self):
        result = compute_context_gaps(personal=_make_scores())
        assert result["flagged"] == []


class TestIdenticalScores:
    """Identical personal and team scores produce zero gaps and no flags."""

    def test_identical_scores_all_gaps_zero(self):
        scores = _make_scores()
        result = compute_context_gaps(personal=scores, team=scores.copy())
        for gap in result["gaps"].values():
            assert gap == 0.0

    def test_identical_scores_no_flags(self):
        scores = _make_scores()
        result = compute_context_gaps(personal=scores, team=scores.copy())
        assert result["flagged"] == []


class TestSatisfactionFlags:
    """Satisfaction subscales with gap < -1.5 are flagged."""

    def test_team_2_points_lower_on_a_sat(self):
        personal = _make_scores(a_sat=7.0)
        team = _make_scores(a_sat=5.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert result["gaps"]["a_sat"] == -2.0
        assert result["flagged"] == ["a_sat"]

    def test_multiple_flagged_sat_subscales(self):
        personal = _make_scores(a_sat=8.0, b_sat=8.0, c_sat=8.0)
        team = _make_scores(a_sat=5.0, b_sat=5.0, c_sat=5.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert sorted(result["flagged"]) == ["a_sat", "b_sat", "c_sat"]


class TestFrustrationNeverFlagged:
    """Frustration gaps are computed but never trigger flags."""

    def test_large_negative_frustration_gap_not_flagged(self):
        personal = _make_scores(a_frust=8.0, b_frust=8.0, c_frust=8.0)
        team = _make_scores(a_frust=2.0, b_frust=2.0, c_frust=2.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert result["gaps"]["a_frust"] == -6.0
        assert result["flagged"] == []


class TestBoundaryConditions:
    """Boundary tests around the -1.5 threshold."""

    def test_gap_exactly_negative_1point5_not_flagged(self):
        """gap == -1.5 does NOT flag (strict less-than)."""
        personal = _make_scores(a_sat=6.5)
        team = _make_scores(a_sat=5.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert result["gaps"]["a_sat"] == -1.5
        assert result["flagged"] == []

    def test_gap_negative_1point51_flagged(self):
        """gap == -1.51 flags."""
        personal = _make_scores(b_sat=6.51)
        team = _make_scores(b_sat=5.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert result["gaps"]["b_sat"] < -1.5
        assert "b_sat" in result["flagged"]


class TestPositiveGaps:
    """Positive gaps (team higher than personal) never flag."""

    def test_positive_gap_no_flags(self):
        personal = _make_scores(a_sat=3.0, b_sat=3.0, c_sat=3.0)
        team = _make_scores(a_sat=8.0, b_sat=8.0, c_sat=8.0)
        result = compute_context_gaps(personal=personal, team=team)
        assert result["flagged"] == []
        assert result["gaps"]["a_sat"] == 5.0


class TestReturnStructure:
    """The return dict has the correct keys and all six subscales."""

    def test_return_has_gaps_and_flagged_keys(self):
        result = compute_context_gaps(personal=_make_scores(), team=_make_scores())
        assert set(result.keys()) == {"gaps", "flagged"}

    def test_all_six_subscale_gaps_computed(self):
        result = compute_context_gaps(personal=_make_scores(), team=_make_scores())
        expected_keys = {"a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust"}
        assert set(result["gaps"].keys()) == expected_keys
