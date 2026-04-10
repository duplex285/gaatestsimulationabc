"""Tests for BaseRateEngine: demographic priors and Bayesian classification adjustment.

Covers config loading, stratum selection priority, posterior arithmetic,
and confidence calibration.
"""

from pathlib import Path

import pytest
import yaml

from src.python_scoring.base_rate_engine import BaseRateEngine

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """BaseRateEngine loaded from the project's default config."""
    return BaseRateEngine()


@pytest.fixture
def config():
    """Raw YAML config for reference values."""
    project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / "config" / "base_rates.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


class TestConfigLoading:
    def test_loads_default_config(self, engine):
        """Engine loads without error using the default config path."""
        assert engine is not None

    def test_loads_explicit_config(self):
        """Engine loads when given an explicit path."""
        project_root = Path(__file__).resolve().parent.parent.parent
        path = str(project_root / "config" / "base_rates.yaml")
        engine = BaseRateEngine(config_path=path)
        assert engine is not None

    def test_missing_config_raises(self, tmp_path):
        """Engine raises FileNotFoundError for a missing config file."""
        with pytest.raises(FileNotFoundError):
            BaseRateEngine(config_path=str(tmp_path / "nonexistent.yaml"))


# ---------------------------------------------------------------------------
# get_prior: demographic combinations
# ---------------------------------------------------------------------------


class TestGetPrior:
    def test_overall_fallback(self, engine, config):
        """Empty demographics returns the overall base rate."""
        result = engine.get_prior({})
        expected = config["near_constant_exhaustion"]["overall"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_gender_male(self, engine, config):
        """Gender=male selects the by_gender.male rate."""
        result = engine.get_prior({"gender": "male"})
        expected = config["near_constant_exhaustion"]["by_gender"]["male"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_gender_female(self, engine, config):
        """Gender=female selects the by_gender.female rate."""
        result = engine.get_prior({"gender": "female"})
        expected = config["near_constant_exhaustion"]["by_gender"]["female"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_sexual_orientation_lgbtq(self, engine, config):
        """Sexual orientation=lgbtq_plus selects the correct rate."""
        result = engine.get_prior({"sexual_orientation": "lgbtq_plus"})
        expected = config["near_constant_exhaustion"]["by_sexual_orientation"]["lgbtq_plus"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_race_ethnicity(self, engine, config):
        """Race/ethnicity=latinx selects the correct rate."""
        result = engine.get_prior({"race_ethnicity": "latinx"})
        expected = config["near_constant_exhaustion"]["by_race_ethnicity"]["latinx"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_financial_stress_high(self, engine, config):
        """Financial stress=high selects the correct rate."""
        result = engine.get_prior({"financial_stress": "high"})
        expected = config["near_constant_exhaustion"]["by_financial_stress"]["high"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_division(self, engine, config):
        """Division=d1 selects the correct rate."""
        result = engine.get_prior({"division": "d1"})
        expected = config["near_constant_exhaustion"]["by_division"]["d1"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_priority_financial_over_gender(self, engine, config):
        """Financial stress takes priority over gender (higher in stratum order)."""
        result = engine.get_prior({"financial_stress": "high", "gender": "male"})
        expected = config["near_constant_exhaustion"]["by_financial_stress"]["high"]
        assert result["distressed_vulnerable_prior"] == expected
        assert "by_financial_stress.high" in result["source"]

    def test_priority_sexual_orientation_over_gender(self, engine, config):
        """Sexual orientation takes priority over gender."""
        result = engine.get_prior({"sexual_orientation": "lgbtq_plus", "gender": "female"})
        expected = config["near_constant_exhaustion"]["by_sexual_orientation"]["lgbtq_plus"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_priority_gender_over_division(self, engine, config):
        """Gender takes priority over division."""
        result = engine.get_prior({"gender": "female", "division": "d1"})
        expected = config["near_constant_exhaustion"]["by_gender"]["female"]
        assert result["distressed_vulnerable_prior"] == expected


# ---------------------------------------------------------------------------
# get_prior: empty and partial demographics
# ---------------------------------------------------------------------------


class TestGetPriorEdgeCases:
    def test_empty_demographics(self, engine, config):
        """Empty dict falls back to overall rate."""
        result = engine.get_prior({})
        expected = config["near_constant_exhaustion"]["overall"]
        assert result["distressed_vulnerable_prior"] == expected
        assert "overall" in result["source"]

    def test_unknown_demographic_key(self, engine, config):
        """Unrecognized keys are ignored; falls back to overall."""
        result = engine.get_prior({"favorite_color": "blue"})
        expected = config["near_constant_exhaustion"]["overall"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_unknown_demographic_value(self, engine, config):
        """Known key with unrecognized value falls back to overall."""
        result = engine.get_prior({"gender": "unknown_value"})
        expected = config["near_constant_exhaustion"]["overall"]
        assert result["distressed_vulnerable_prior"] == expected

    def test_partial_demographics_uses_available(self, engine, config):
        """Only the matching stratum is used when some keys are absent."""
        result = engine.get_prior({"division": "d2"})
        expected = config["near_constant_exhaustion"]["by_division"]["d2"]
        assert result["distressed_vulnerable_prior"] == expected


# ---------------------------------------------------------------------------
# get_prior: source description
# ---------------------------------------------------------------------------


class TestGetPriorSource:
    def test_source_format_with_match(self, engine):
        """Source string follows 'yaml_key.value' format."""
        result = engine.get_prior({"gender": "male"})
        assert result["source"] == "by_gender.male"

    def test_source_format_overall(self, engine):
        """Source string for overall fallback contains 'overall'."""
        result = engine.get_prior({})
        assert "overall" in result["source"]


# ---------------------------------------------------------------------------
# get_prior: any_exhaustion_prior computation
# ---------------------------------------------------------------------------


class TestAnyExhaustionPrior:
    def test_any_exhaustion_is_multiplied(self, engine, config):
        """any_exhaustion_prior = min(rate * multiplier, cap)."""
        result = engine.get_prior({"gender": "male"})
        rate = config["near_constant_exhaustion"]["by_gender"]["male"]
        multiplier = config["domain_state_mapping"]["any_recent_exhaustion"]["multiplier"]
        cap = config["domain_state_mapping"]["any_recent_exhaustion"]["cap"]
        expected = round(min(rate * multiplier, cap), 4)
        assert result["any_exhaustion_prior"] == expected

    def test_any_exhaustion_capped(self, engine, config):
        """any_exhaustion_prior never exceeds the cap."""
        result = engine.get_prior({"financial_stress": "high"})
        cap = config["domain_state_mapping"]["any_recent_exhaustion"]["cap"]
        assert result["any_exhaustion_prior"] <= cap


# ---------------------------------------------------------------------------
# adjust_classification: different raw states
# ---------------------------------------------------------------------------


class TestAdjustClassification:
    def test_distressed_returns_four_states(self, engine):
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 3.0, "frustration": 8.0}, prior=0.25
        )
        assert set(result["posteriors"].keys()) == {"Thriving", "Vulnerable", "Mild", "Distressed"}

    def test_thriving_returns_four_states(self, engine):
        result = engine.adjust_classification(
            "Thriving", {"satisfaction": 8.0, "frustration": 2.0}, prior=0.25
        )
        assert set(result["posteriors"].keys()) == {"Thriving", "Vulnerable", "Mild", "Distressed"}

    def test_vulnerable_is_positive(self, engine):
        """Vulnerable is treated as a positive test result."""
        result = engine.adjust_classification(
            "Vulnerable", {"satisfaction": 7.0, "frustration": 6.0}, prior=0.25
        )
        # With prior=0.25 and positive test, posterior for D/V group should be elevated
        p_dv = result["posteriors"]["Distressed"] + result["posteriors"]["Vulnerable"]
        assert p_dv > 0.25  # higher than the prior

    def test_mild_is_negative(self, engine):
        """Mild is treated as a negative test result."""
        result = engine.adjust_classification(
            "Mild", {"satisfaction": 4.0, "frustration": 3.0}, prior=0.25
        )
        p_dv = result["posteriors"]["Distressed"] + result["posteriors"]["Vulnerable"]
        assert p_dv < 0.25  # lower than the prior

    def test_invalid_state_raises(self, engine):
        with pytest.raises(ValueError, match="raw_state must be one of"):
            engine.adjust_classification(
                "Invalid", {"satisfaction": 5.0, "frustration": 5.0}, prior=0.25
            )

    def test_raw_state_preserved(self, engine):
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 3.0, "frustration": 8.0}, prior=0.25
        )
        assert result["raw_state"] == "Distressed"

    def test_adjusted_state_is_valid(self, engine):
        result = engine.adjust_classification(
            "Thriving", {"satisfaction": 8.0, "frustration": 2.0}, prior=0.25
        )
        assert result["adjusted_state"] in {"Thriving", "Vulnerable", "Mild", "Distressed"}

    def test_base_rate_used_stored(self, engine):
        result = engine.adjust_classification(
            "Thriving", {"satisfaction": 8.0, "frustration": 2.0}, prior=0.30
        )
        assert result["base_rate_used"] == 0.30


# ---------------------------------------------------------------------------
# adjust_classification: posteriors sum to 1.0
# ---------------------------------------------------------------------------


class TestPosteriorsSumToOne:
    @pytest.mark.parametrize("raw_state", ["Thriving", "Vulnerable", "Mild", "Distressed"])
    def test_posteriors_sum_to_one(self, engine, raw_state):
        result = engine.adjust_classification(
            raw_state, {"satisfaction": 5.0, "frustration": 5.0}, prior=0.25
        )
        total = sum(result["posteriors"].values())
        assert abs(total - 1.0) < 1e-4, f"Posteriors sum to {total}, not 1.0"

    def test_posteriors_sum_to_one_extreme_prior(self, engine):
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 1.0, "frustration": 9.0}, prior=0.90
        )
        total = sum(result["posteriors"].values())
        assert abs(total - 1.0) < 1e-4


# ---------------------------------------------------------------------------
# adjust_classification: confidence levels
# ---------------------------------------------------------------------------


class TestConfidenceLevels:
    def test_confidence_is_valid_level(self, engine):
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 3.0, "frustration": 8.0}, prior=0.25
        )
        assert result["confidence"] in {"low", "moderate", "high"}

    def test_high_confidence_with_strong_signal(self, engine):
        """Very high prior + positive test + extreme scores should yield high confidence."""
        result = engine.adjust_classification(
            "Distressed",
            {"satisfaction": 0.5, "frustration": 9.5},
            prior=0.80,
            sensitivity=0.95,
            specificity=0.95,
        )
        assert result["confidence"] == "high"

    def test_low_confidence_with_ambiguous_signal(self, engine):
        """Near-50/50 prior with weak test accuracy spreads mass evenly."""
        result = engine.adjust_classification(
            "Mild",
            {"satisfaction": 5.0, "frustration": 5.0},
            prior=0.50,
            sensitivity=0.55,
            specificity=0.55,
        )
        # With near-chance accuracy and 50/50 prior, posteriors are spread
        assert result["confidence"] in {"low", "moderate"}


# ---------------------------------------------------------------------------
# High vs low base rate produces different posteriors
# ---------------------------------------------------------------------------


class TestBaseRateEffect:
    def test_high_base_rate_raises_positive_posterior(self, engine):
        """Higher base rate raises posterior for D/V group given the same raw state."""
        low = engine.adjust_classification(
            "Distressed", {"satisfaction": 3.0, "frustration": 7.0}, prior=0.10
        )
        high = engine.adjust_classification(
            "Distressed", {"satisfaction": 3.0, "frustration": 7.0}, prior=0.60
        )
        p_dv_low = low["posteriors"]["Distressed"] + low["posteriors"]["Vulnerable"]
        p_dv_high = high["posteriors"]["Distressed"] + high["posteriors"]["Vulnerable"]
        assert p_dv_high > p_dv_low

    def test_low_base_rate_pulls_toward_negative(self, engine):
        """Very low base rate can flip a Distressed raw state to a lower adjusted state."""
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 5.0, "frustration": 5.0}, prior=0.02
        )
        # With a 2% base rate, even a positive test result has low PPV
        p_dv = result["posteriors"]["Distressed"] + result["posteriors"]["Vulnerable"]
        assert p_dv < 0.50


# ---------------------------------------------------------------------------
# Edge cases: very high/low base rates
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_prior_near_zero(self, engine):
        """Prior near zero produces valid posteriors that sum to 1."""
        result = engine.adjust_classification(
            "Distressed", {"satisfaction": 5.0, "frustration": 5.0}, prior=0.001
        )
        total = sum(result["posteriors"].values())
        assert abs(total - 1.0) < 1e-4
        # Nearly all mass should be in the negative group
        p_mt = result["posteriors"]["Mild"] + result["posteriors"]["Thriving"]
        assert p_mt > 0.90

    def test_prior_near_one(self, engine):
        """Prior near one produces valid posteriors that sum to 1."""
        result = engine.adjust_classification(
            "Thriving", {"satisfaction": 8.0, "frustration": 2.0}, prior=0.999
        )
        total = sum(result["posteriors"].values())
        assert abs(total - 1.0) < 1e-4
        # Despite negative test, near-certain prior keeps D/V mass high
        p_dv = result["posteriors"]["Distressed"] + result["posteriors"]["Vulnerable"]
        assert p_dv > 0.50

    def test_perfect_sensitivity_specificity(self, engine):
        """Perfect test accuracy with moderate prior."""
        result = engine.adjust_classification(
            "Distressed",
            {"satisfaction": 3.0, "frustration": 7.0},
            prior=0.30,
            sensitivity=1.0,
            specificity=1.0,
        )
        # Perfect test: P(truly D/V | ABC says D/V) = 1.0
        p_dv = result["posteriors"]["Distressed"] + result["posteriors"]["Vulnerable"]
        assert abs(p_dv - 1.0) < 1e-4

    def test_all_four_posteriors_nonnegative(self, engine):
        """No posterior probability should be negative."""
        result = engine.adjust_classification(
            "Vulnerable", {"satisfaction": 9.0, "frustration": 1.0}, prior=0.50
        )
        for state, prob in result["posteriors"].items():
            assert prob >= 0.0, f"{state} posterior is negative: {prob}"
