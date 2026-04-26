"""Tests for Edwards (2001) polynomial regression / response surface analysis.

Reference: Edwards (2001), Ten Difference Score Myths
Reference: Shanock et al. (2010), Polynomial Regression with Response Surface Analysis
Reference: howard-2024-implementation-plan.md V2-B WI-9
"""

import numpy as np
import pytest

from src.psychometric.response_surface import (
    calibrated_concern_probability,
    fit_response_surface,
    test_difference_score_constraints,
)


@pytest.fixture
def rng():
    """Seeded RNG.

    Reference: CLAUDE_RULES.md Rule 7
    """
    return np.random.default_rng(42)


class TestFitResponseSurface:
    def test_response_surface_fits(self, rng):
        """Returns dict with all expected keys."""
        n = 300
        p = rng.standard_normal(n)
        t = rng.standard_normal(n)
        y = p + t + 0.5 * p * t + rng.standard_normal(n) * 0.3

        result = fit_response_surface(p, t, y)

        for key in ("coefficients", "r_squared", "coefficient_se", "surface_features"):
            assert key in result
        for b in ("b0", "b1", "b2", "b3", "b4", "b5"):
            assert b in result["coefficients"]
            assert b in result["coefficient_se"]
        for feat in (
            "peak_personal",
            "peak_team",
            "peak_outcome",
            "line_of_agreement_slope",
            "line_of_disagreement_slope",
            "curvature_along_agreement",
            "curvature_along_disagreement",
        ):
            assert feat in result["surface_features"]

    def test_handles_collinear_p_t(self, rng):
        """P and T correlated at r=0.9: no Heywood, valid coefficients."""
        n = 500
        z = rng.standard_normal(n)
        p = z + 0.1 * rng.standard_normal(n)
        # T highly correlated with P (target r ~ 0.9)
        t = 0.9 * p + np.sqrt(1 - 0.9**2) * rng.standard_normal(n)
        y = 0.5 * p + 0.3 * t + rng.standard_normal(n) * 0.5

        result = fit_response_surface(p, t, y)
        for v in result["coefficients"].values():
            assert np.isfinite(v)
        assert 0.0 <= result["r_squared"] <= 1.0

    def test_surface_peak_at_line_of_agreement(self, rng):
        """Congruence effect: Y = -(P - T)^2 has peak when P = T."""
        n = 800
        p = rng.standard_normal(n)
        t = rng.standard_normal(n)
        # Inverted parabola in (P-T): peak at P == T
        y = -((p - t) ** 2) + rng.standard_normal(n) * 0.05

        result = fit_response_surface(p, t, y)
        peak_p = result["surface_features"]["peak_personal"]
        peak_t = result["surface_features"]["peak_team"]
        assert peak_p is not None and peak_t is not None
        # Peak should sit on the line of agreement (P = T) within tolerance
        assert abs(peak_p - peak_t) < 0.3, f"peak_p={peak_p}, peak_t={peak_t}"


class TestDifferenceScoreConstraints:
    def test_recovers_pure_difference_pattern(self, rng):
        """Y = (P - T) exactly: constraint test does NOT reject."""
        n = 600
        p = rng.standard_normal(n)
        t = rng.standard_normal(n)
        y = p - t + rng.standard_normal(n) * 0.05

        result = test_difference_score_constraints(p, t, y)
        assert result["df_constraint"] == 4
        assert result["reject_difference_hypothesis"] is False
        assert result["p_value"] > 0.05

    def test_rejects_quadratic_pattern(self, rng):
        """Y = P + T^2: constraint test rejects difference-score hypothesis."""
        n = 600
        p = rng.standard_normal(n)
        t = rng.standard_normal(n)
        y = p + t**2 + rng.standard_normal(n) * 0.1

        result = test_difference_score_constraints(p, t, y)
        assert result["reject_difference_hypothesis"] is True
        assert result["p_value"] < 0.05
        assert result["effect_size_r_squared_change"] > 0.0


class TestCalibratedProbability:
    def test_calibrated_probability_in_unit_interval(self, rng):
        """Returns a probability in [0, 1] for any (P, T)."""
        n = 200
        p = rng.standard_normal(n)
        t = rng.standard_normal(n)
        y = -((p - t) ** 2) + rng.standard_normal(n) * 0.5

        surface = fit_response_surface(p, t, y)

        for personal, team in [(0.0, 0.0), (-2.0, 1.0), (1.5, -1.5), (3.0, 3.0)]:
            prob = calibrated_concern_probability(personal, team, surface, criterion_threshold=0.5)
            assert 0.0 <= prob <= 1.0, f"prob={prob} for ({personal},{team})"
