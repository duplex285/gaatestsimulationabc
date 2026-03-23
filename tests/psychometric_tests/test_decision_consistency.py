"""Tests for decision consistency module.

Reference: APA/AERA/NCME Standards (2014), Standards 2.4, 2.14, 2.16
Reference: Jacobson & Truax (1991), Clinical Significance
Reference: Cohen (1960), Kappa Coefficient
"""

import numpy as np
import pytest

from src.psychometric.decision_consistency import (
    compute_classification_kappa,
    compute_conditional_sem_at_thresholds,
    compute_difference_score_reliability,
    simulate_classification_agreement,
)


@pytest.fixture
def high_precision_setup():
    """IRT parameters with high discrimination (precise measurement).

    6 items per subscale, high discrimination = tight SE = stable classifications.
    """
    from src.psychometric.irt_simulation import generate_synthetic_grm_parameters

    params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
    # Boost discrimination for tight measurement
    params["discrimination"] = np.full(36, 2.0)
    return params


@pytest.fixture
def low_precision_setup():
    """IRT parameters with low discrimination (imprecise measurement).

    6 items per subscale, low discrimination = wide SE = unstable classifications.
    """
    from src.psychometric.irt_simulation import generate_synthetic_grm_parameters

    params = generate_synthetic_grm_parameters(n_items=36, n_categories=7, seed=42)
    # Low discrimination for noisy measurement
    params["discrimination"] = np.full(36, 0.6)
    return params


class TestSimulateClassificationAgreement:
    """Tests for classification agreement across simulated replications."""

    def test_returns_required_keys(self, high_precision_setup):
        """Output contains agreement rates for domain states and types."""
        result = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=100,
            n_replications=2,
            seed=42,
        )
        assert "domain_state_agreement" in result
        assert "type_agreement" in result
        assert "per_domain_agreement" in result

    def test_agreement_between_zero_and_one(self, high_precision_setup):
        """Agreement rates are proportions in [0, 1]."""
        result = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=100,
            n_replications=2,
            seed=42,
        )
        assert 0.0 <= result["domain_state_agreement"] <= 1.0
        assert 0.0 <= result["type_agreement"] <= 1.0

    def test_high_precision_yields_higher_per_domain_agreement(self, high_precision_setup):
        """High-discrimination items should produce more stable per-domain classifications.

        Reference: Standard 2.16
        Note: Joint agreement across all 3 domains will be lower (~p^3 for
        independent domains). Per-domain agreement is the primary metric.
        """
        result = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=200,
            n_replications=2,
            seed=42,
        )
        # Per-domain agreement with a=2.0 should exceed chance (25% for 4 states)
        for domain, agreement in result["per_domain_agreement"].items():
            assert agreement > 0.50, (
                f"{domain} per-domain agreement = {agreement:.3f}, expected > 0.50"
            )

    def test_low_precision_yields_lower_agreement(self, low_precision_setup):
        """Low-discrimination items should produce less stable classifications."""
        result = simulate_classification_agreement(
            low_precision_setup["discrimination"],
            low_precision_setup["difficulty"],
            n_persons=200,
            n_replications=2,
            seed=42,
        )
        # With a=0.6, agreement will be lower
        assert result["domain_state_agreement"] < 0.90

    def test_per_domain_has_three_domains(self, high_precision_setup):
        """Per-domain agreement reports for ambition, belonging, craft."""
        result = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=50,
            n_replications=2,
            seed=42,
        )
        assert set(result["per_domain_agreement"].keys()) == {
            "ambition",
            "belonging",
            "craft",
        }

    def test_reproducibility(self, high_precision_setup):
        """Same seed produces identical results.

        Reference: CLAUDE_RULES.md Rule 7
        """
        r1 = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=50,
            n_replications=2,
            seed=42,
        )
        r2 = simulate_classification_agreement(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            n_persons=50,
            n_replications=2,
            seed=42,
        )
        assert r1["domain_state_agreement"] == r2["domain_state_agreement"]


class TestComputeDifferenceScoreReliability:
    """Tests for satisfaction-frustration difference score reliability."""

    def test_returns_per_domain(self):
        """Returns reliability for each of 3 domains.

        Reference: Standard 2.4
        """
        # Simulate subscale scores with known reliability
        rng = np.random.default_rng(42)
        n = 500
        sat_scores = {
            "a_sat": rng.normal(6, 1.5, n),
            "b_sat": rng.normal(6, 1.5, n),
            "c_sat": rng.normal(6, 1.5, n),
        }
        frust_scores = {
            "a_frust": rng.normal(4, 1.5, n),
            "b_frust": rng.normal(4, 1.5, n),
            "c_frust": rng.normal(4, 1.5, n),
        }
        result = compute_difference_score_reliability(
            sat_scores, frust_scores, reliability_sat=0.80, reliability_frust=0.80
        )
        assert set(result.keys()) == {"ambition", "belonging", "craft"}

    def test_reliability_between_zero_and_one(self):
        """Difference score reliability is in [0, 1]."""
        rng = np.random.default_rng(42)
        n = 500
        sat_scores = {"a_sat": rng.normal(6, 1.5, n)}
        frust_scores = {"a_frust": rng.normal(4, 1.5, n)}
        result = compute_difference_score_reliability(
            sat_scores, frust_scores, reliability_sat=0.80, reliability_frust=0.80
        )
        assert 0.0 <= result["ambition"] <= 1.0

    def test_higher_component_reliability_yields_higher_difference_reliability(self):
        """Higher subscale reliability produces higher difference reliability.

        Reference: Standard 2.4, formula: r_diff = (r_x + r_y - 2*r_xy) / (2 - 2*r_xy)
        """
        rng = np.random.default_rng(42)
        n = 500
        sat = {"a_sat": rng.normal(6, 1.5, n)}
        frust = {"a_frust": rng.normal(4, 1.5, n)}

        r_low = compute_difference_score_reliability(
            sat, frust, reliability_sat=0.60, reliability_frust=0.60
        )
        r_high = compute_difference_score_reliability(
            sat, frust, reliability_sat=0.90, reliability_frust=0.90
        )
        assert r_high["ambition"] > r_low["ambition"]

    def test_negative_correlation_improves_reliability(self):
        """Negative sat-frust correlation improves difference reliability.

        This is important: if satisfaction and frustration are negatively
        correlated (as SDT predicts), the difference score is MORE reliable
        than when they are independent.
        """
        rng = np.random.default_rng(42)
        n = 500
        sat = {"a_sat": rng.normal(6, 1.5, n)}

        # Independent frustration
        frust_ind = {"a_frust": rng.normal(4, 1.5, n)}
        r_ind = compute_difference_score_reliability(
            sat, frust_ind, reliability_sat=0.80, reliability_frust=0.80, r_sat_frust=-0.0
        )

        # Negatively correlated frustration
        r_neg = compute_difference_score_reliability(
            sat, frust_ind, reliability_sat=0.80, reliability_frust=0.80, r_sat_frust=-0.40
        )
        assert r_neg["ambition"] > r_ind["ambition"]


class TestComputeConditionalSEMAtThresholds:
    """Tests for conditional standard error at classification thresholds."""

    def test_returns_sem_per_threshold(self, high_precision_setup):
        """Output includes SEM at satisfaction and frustration thresholds.

        Reference: Standard 2.14
        """
        thresholds = {"satisfaction": 6.46, "frustration": 4.38}
        result = compute_conditional_sem_at_thresholds(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            thresholds,
        )
        assert "satisfaction" in result
        assert "frustration" in result

    def test_sem_positive(self, high_precision_setup):
        """SEM values are positive."""
        thresholds = {"satisfaction": 6.46, "frustration": 4.38}
        result = compute_conditional_sem_at_thresholds(
            high_precision_setup["discrimination"],
            high_precision_setup["difficulty"],
            thresholds,
        )
        for name, sem in result.items():
            assert sem > 0, f"SEM at {name} threshold is not positive: {sem}"

    def test_higher_discrimination_lower_sem(self):
        """Higher discrimination produces lower SEM at thresholds."""
        from src.psychometric.irt_simulation import generate_synthetic_grm_parameters

        params = generate_synthetic_grm_parameters(n_items=4, n_categories=7, seed=42)
        thresholds = {"test": 5.0}

        params_low = {**params, "discrimination": np.full(4, 0.6)}
        params_high = {**params, "discrimination": np.full(4, 2.5)}

        sem_low = compute_conditional_sem_at_thresholds(
            params_low["discrimination"], params_low["difficulty"], thresholds
        )
        sem_high = compute_conditional_sem_at_thresholds(
            params_high["discrimination"], params_high["difficulty"], thresholds
        )
        assert sem_high["test"] < sem_low["test"]


class TestComputeClassificationKappa:
    """Tests for Cohen's kappa computation."""

    def test_perfect_agreement(self):
        """Identical classifications yield kappa = 1.0."""
        labels = np.array(["Thriving", "Distressed", "Mild", "Vulnerable"] * 50)
        result = compute_classification_kappa(labels, labels)
        assert abs(result - 1.0) < 1e-10

    def test_kappa_between_minus_one_and_one(self):
        """Kappa is in [-1, 1]."""
        rng = np.random.default_rng(42)
        states = ["Thriving", "Distressed", "Mild", "Vulnerable"]
        a = rng.choice(states, 200)
        b = rng.choice(states, 200)
        result = compute_classification_kappa(a, b)
        assert -1.0 <= result <= 1.0

    def test_random_agreement_near_zero(self):
        """Random classifications yield kappa near 0."""
        rng = np.random.default_rng(42)
        states = ["Thriving", "Distressed", "Mild", "Vulnerable"]
        a = rng.choice(states, 1000)
        b = rng.choice(states, 1000)
        result = compute_classification_kappa(a, b)
        assert abs(result) < 0.15

    def test_moderate_agreement(self):
        """Partially matching classifications yield moderate kappa."""
        rng = np.random.default_rng(42)
        states = ["Thriving", "Distressed", "Mild", "Vulnerable"]
        a = rng.choice(states, 200)
        # 70% agree, 30% random
        b = a.copy()
        flip_idx = rng.choice(200, size=60, replace=False)
        b[flip_idx] = rng.choice(states, 60)
        result = compute_classification_kappa(a, b)
        assert 0.30 < result < 0.90
