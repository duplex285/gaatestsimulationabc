"""Bayesian scoring for sequential ABC Assessment estimation.

Implements conjugate normal updating for latent trait scores. Each new
measurement refines the posterior, and confidence grows over time.

Mathematical foundation:
    Given a normal prior N(mu_0, sigma_0^2) and an observation x with
    known measurement error sigma_e^2, the posterior is:

        mu_1  = (mu_0 / sigma_0^2  +  x / sigma_e^2)
                / (1 / sigma_0^2  +  1 / sigma_e^2)

        sigma_1^2 = 1 / (1 / sigma_0^2  +  1 / sigma_e^2)

    After n observations the posterior precision equals the sum of the
    prior precision and all observation precisions.

Reference: abc-assessment-spec Section 2.2 (domain thresholds),
           Section 2.4 (type activation threshold)
"""

import math

# ---------------------------------------------------------------------------
# Normal CDF: use scipy if available, otherwise approximate
# ---------------------------------------------------------------------------

try:
    from scipy.stats import norm as _scipy_norm

    def _normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """P(X <= x) for X ~ N(mu, sigma^2), via scipy."""
        return float(_scipy_norm.cdf(x, loc=mu, scale=sigma))

except ImportError:

    def _normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
        """P(X <= x) for X ~ N(mu, sigma^2), Abramowitz & Stegun approx.

        Uses the rational approximation (formula 7.1.26) with maximum
        error < 1.5e-7. Adequate for classification probabilities.
        """
        z = (x - mu) / sigma
        sign = 1
        if z < 0:
            z = -z
            sign = -1
        # Constants from Abramowitz & Stegun
        p = 0.2316419
        b1 = 0.319381530
        b2 = -0.356563782
        b3 = 1.781477937
        b4 = -1.821255978
        b5 = 1.330274429
        t = 1.0 / (1.0 + p * z)
        t2 = t * t
        t3 = t2 * t
        t4 = t3 * t
        t5 = t4 * t
        pdf = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
        upper_tail = pdf * (b1 * t + b2 * t2 + b3 * t3 + b4 * t4 + b5 * t5)
        if sign < 0:
            return upper_tail
        return 1.0 - upper_tail


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUBSCALE_NAMES = ("a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust")

DOMAIN_PAIRS = {
    "ambition": ("a_sat", "a_frust"),
    "belonging": ("b_sat", "b_frust"),
    "craft": ("c_sat", "c_frust"),
}

# Domain state thresholds (abc-assessment-spec Section 2.2)
SAT_THRESHOLD = 6.46
FRUST_THRESHOLD = 4.38

# Type activation threshold (abc-assessment-spec Section 2.4)
TYPE_ACTIVATION_THRESHOLD = 5.5

# 8 archetypes: (A_strong, B_strong, C_strong) -> name
ARCHETYPE_PATTERNS = {
    (True, True, True): "Integrator",
    (True, True, False): "Captain",
    (True, False, True): "Architect",
    (False, True, True): "Mentor",
    (True, False, False): "Pioneer",
    (False, True, False): "Anchor",
    (False, False, True): "Artisan",
    (False, False, False): "Seeker",
}


# ---------------------------------------------------------------------------
# BayesianScorer: single-subscale sequential estimator
# ---------------------------------------------------------------------------


class BayesianScorer:
    """Conjugate normal Bayesian updater for a single subscale.

    Maintains a normal posterior N(posterior_mean, posterior_sd^2) that
    incorporates every observed measurement. The prior starts at a
    population-level estimate and is progressively down-weighted as
    data accumulates.

    All scores are on the 0-10 normalized scale.
    """

    def __init__(self, prior_mean: float = 5.0, prior_sd: float = 2.0):
        """Initialize with a population-level prior.

        Reference: abc-assessment-spec Section 4

        Args:
            prior_mean: Center of the prior distribution (0-10 scale).
                        Can be overridden by base_rate_engine output.
            prior_sd:   Standard deviation of the prior. A wider prior
                        expresses more uncertainty and lets data dominate
                        sooner.
        """
        self.prior_mean = prior_mean
        self.prior_sd = prior_sd
        self.posterior_mean = prior_mean
        self.posterior_sd = prior_sd
        self._history: list[dict] = []

    @property
    def measurements_incorporated(self) -> int:
        """Number of observations incorporated into the posterior.

        Reference: abc-assessment-spec Section 4
        """
        return len(self._history)

    def update(self, new_score: float, measurement_se: float = 0.8) -> dict:
        """Incorporate a new observation via conjugate normal updating.

        Reference: abc-assessment-spec Section 4

        Conjugate update formulae:
            precision_prior = 1 / sigma_prior^2
            precision_data  = 1 / sigma_e^2
            precision_post  = precision_prior + precision_data

            mu_post    = (mu_prior * precision_prior + x * precision_data)
                         / precision_post
            sigma_post = sqrt(1 / precision_post)

        Args:
            new_score:      Observed subscale score (0-10 scale).
            measurement_se: Standard error of the measurement instrument.
                            Default 0.8 reflects moderate reliability for
                            a 6-item Likert subscale.

        Returns:
            Dict with posterior_mean, posterior_sd, credible_interval_90,
            measurements_incorporated, prior_weight, data_weight.
        """
        prior_precision = 1.0 / (self.posterior_sd**2)
        data_precision = 1.0 / (measurement_se**2)
        post_precision = prior_precision + data_precision

        post_mean = (
            self.posterior_mean * prior_precision + new_score * data_precision
        ) / post_precision
        post_sd = math.sqrt(1.0 / post_precision)

        self.posterior_mean = post_mean
        self.posterior_sd = post_sd

        self._history.append(
            {
                "score": new_score,
                "measurement_se": measurement_se,
                "posterior_mean": post_mean,
                "posterior_sd": post_sd,
            }
        )

        prior_weight = prior_precision / post_precision
        data_weight = data_precision / post_precision

        # 90% credible interval: mean +/- 1.645 * sd
        z90 = 1.6449
        ci_low = post_mean - z90 * post_sd
        ci_high = post_mean + z90 * post_sd

        return {
            "posterior_mean": post_mean,
            "posterior_sd": post_sd,
            "credible_interval_90": (ci_low, ci_high),
            "measurements_incorporated": self.measurements_incorporated,
            "prior_weight": prior_weight,
            "data_weight": data_weight,
        }

    def get_personalized_threshold(self, k: float = 1.5, floor: float = 3.0) -> float | None:
        """Compute a personalized lower-bound threshold for this subscale.

        Reference: abc-assessment-spec Section 4

        Formula: max(posterior_mean - k * posterior_sd, floor)

        The threshold is only meaningful after enough measurements have
        accumulated to shrink the posterior sufficiently. Before 6
        measurements the posterior is still heavily influenced by the
        prior, so this method returns None.

        Args:
            k:     Number of posterior SDs below the mean. 1.5 gives a
                   conservative lower bound (~93% of the posterior mass
                   lies above it).
            floor: Absolute minimum threshold on the 0-10 scale.

        Returns:
            Personalized threshold (float) if >= 6 measurements have been
            incorporated, otherwise None.
        """
        if self.measurements_incorporated < 6:
            return None
        return max(self.posterior_mean - k * self.posterior_sd, floor)


# ---------------------------------------------------------------------------
# Domain state classification with uncertainty
# ---------------------------------------------------------------------------


def classify_with_uncertainty(
    sat_scorer: BayesianScorer,
    frust_scorer: BayesianScorer,
    sat_threshold: float = SAT_THRESHOLD,
    frust_threshold: float = FRUST_THRESHOLD,
) -> dict:
    """Classify a domain into one of four states using full posteriors.

    Reference: abc-assessment-spec Section 4

    Instead of a hard threshold on point estimates, this function
    computes the probability of each state from the joint posterior.

    The satisfaction and frustration posteriors are treated as
    independent normals (reasonable given separate subscales). The
    four-state probability mass is:

        P(Thriving)   = P(sat >= t_s) * P(frust <  t_f)
        P(Vulnerable) = P(sat >= t_s) * P(frust >= t_f)
        P(Mild)       = P(sat <  t_s) * P(frust <  t_f)
        P(Distressed) = P(sat <  t_s) * P(frust >= t_f)

    These sum to 1.0 by construction.

    Args:
        sat_scorer:      BayesianScorer for satisfaction subscale.
        frust_scorer:    BayesianScorer for frustration subscale.
        sat_threshold:   Satisfaction split threshold (default 6.46).
        frust_threshold: Frustration split threshold (default 4.38).

    Returns:
        Dict with posterior probabilities for each state, most_likely_state,
        and confidence (the maximum posterior probability).
    """
    p_sat_high = 1.0 - _normal_cdf(
        sat_threshold, sat_scorer.posterior_mean, sat_scorer.posterior_sd
    )
    p_sat_low = 1.0 - p_sat_high

    p_frust_high = 1.0 - _normal_cdf(
        frust_threshold, frust_scorer.posterior_mean, frust_scorer.posterior_sd
    )
    p_frust_low = 1.0 - p_frust_high

    states = {
        "posterior_thriving": p_sat_high * p_frust_low,
        "posterior_vulnerable": p_sat_high * p_frust_high,
        "posterior_mild": p_sat_low * p_frust_low,
        "posterior_distressed": p_sat_low * p_frust_high,
    }

    state_labels = {
        "posterior_thriving": "Thriving",
        "posterior_vulnerable": "Vulnerable",
        "posterior_mild": "Mild",
        "posterior_distressed": "Distressed",
    }

    best_key = max(states, key=states.get)
    states["most_likely_state"] = state_labels[best_key]
    states["confidence"] = states[best_key]

    return states


# ---------------------------------------------------------------------------
# ABCBayesianProfile: full 6-subscale wrapper
# ---------------------------------------------------------------------------


class ABCBayesianProfile:
    """Bayesian profile tracking all six ABC subscales.

    Wraps six BayesianScorer instances (one per subscale) and provides
    methods for domain state classification and archetype probability
    estimation, all with full posterior uncertainty.
    """

    def __init__(self, base_rate_prior: dict = None):
        """Initialize six subscale scorers.

        Reference: abc-assessment-spec Section 4

        Args:
            base_rate_prior: Optional dict from base_rate_engine with keys
                             matching subscale names (a_sat, a_frust, etc.)
                             and values as dicts containing 'mean' and
                             optionally 'sd'. If provided, these override
                             the default N(5.0, 2.0) prior for each
                             subscale.
        """
        self.scorers: dict[str, BayesianScorer] = {}
        for name in SUBSCALE_NAMES:
            if base_rate_prior and name in base_rate_prior:
                prior = base_rate_prior[name]
                mean = prior.get("mean", 5.0) if isinstance(prior, dict) else prior
                sd = prior.get("sd", 2.0) if isinstance(prior, dict) else 2.0
                self.scorers[name] = BayesianScorer(prior_mean=mean, prior_sd=sd)
            else:
                self.scorers[name] = BayesianScorer()

    def update_all(
        self,
        subscales: dict[str, float],
        measurement_ses: dict[str, float] = None,
    ) -> dict:
        """Update all six subscale scorers with a new set of observations.

        Reference: abc-assessment-spec Section 4

        Args:
            subscales:       Dict mapping subscale name to observed score
                             (0-10 scale). Must contain all six subscales.
            measurement_ses: Optional dict mapping subscale name to its
                             measurement SE. Defaults to 0.8 for all.

        Returns:
            Dict with 'subscales' (per-subscale posteriors) and
            'domain_states' (per-domain state probabilities).
        """
        if measurement_ses is None:
            measurement_ses = dict.fromkeys(SUBSCALE_NAMES, 0.8)

        subscale_results = {}
        for name in SUBSCALE_NAMES:
            se = measurement_ses.get(name, 0.8)
            subscale_results[name] = self.scorers[name].update(subscales[name], measurement_se=se)

        domain_states = {}
        for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
            domain_states[domain] = classify_with_uncertainty(
                self.scorers[sat_key], self.scorers[frust_key]
            )

        return {
            "subscales": subscale_results,
            "domain_states": domain_states,
        }

    def get_archetype_probabilities(
        self, activation_threshold: float = TYPE_ACTIVATION_THRESHOLD
    ) -> dict:
        """Compute the probability of each of the 8 archetypes.

        Reference: abc-assessment-spec Section 4

        Each domain's activation probability is P(sat >= threshold)
        computed from that domain's satisfaction posterior. The 8
        archetypes correspond to the 2^3 combinations of
        (A_strong, B_strong, C_strong). Under independence of the
        three satisfaction posteriors:

            P(archetype) = prod over domains of
                P(strong) if strong in pattern else P(developing)

        Args:
            activation_threshold: Satisfaction level at which a domain
                                  counts as "strong" (default 5.5).

        Returns:
            Dict mapping archetype name to probability. All values
            sum to 1.0.
        """
        # P(strong) for each domain
        p_a = 1.0 - _normal_cdf(
            activation_threshold,
            self.scorers["a_sat"].posterior_mean,
            self.scorers["a_sat"].posterior_sd,
        )
        p_b = 1.0 - _normal_cdf(
            activation_threshold,
            self.scorers["b_sat"].posterior_mean,
            self.scorers["b_sat"].posterior_sd,
        )
        p_c = 1.0 - _normal_cdf(
            activation_threshold,
            self.scorers["c_sat"].posterior_mean,
            self.scorers["c_sat"].posterior_sd,
        )

        domain_probs = {"a": p_a, "b": p_b, "c": p_c}

        result = {}
        for (a_strong, b_strong, c_strong), name in ARCHETYPE_PATTERNS.items():
            prob = 1.0
            for key, is_strong in [("a", a_strong), ("b", b_strong), ("c", c_strong)]:
                p_strong = domain_probs[key]
                prob *= p_strong if is_strong else (1.0 - p_strong)
            result[name] = prob

        return result

    def get_summary(self) -> dict:
        """Return a comprehensive summary of the current Bayesian profile.

        Reference: abc-assessment-spec Section 4

        Includes posterior parameters, credible intervals, domain state
        probabilities, archetype probabilities, measurement count, and
        the prior/data weight balance for each subscale.

        Returns:
            Dict with keys: posteriors, domain_states, archetypes,
            measurements_incorporated, weight_balance.
        """
        posteriors = {}
        weight_balance = {}
        z90 = 1.6449

        for name, scorer in self.scorers.items():
            posteriors[name] = {
                "mean": scorer.posterior_mean,
                "sd": scorer.posterior_sd,
                "credible_interval_90": (
                    scorer.posterior_mean - z90 * scorer.posterior_sd,
                    scorer.posterior_mean + z90 * scorer.posterior_sd,
                ),
            }

            # Compute cumulative prior vs data weight.
            # Prior precision = 1/prior_sd^2. Total precision = 1/posterior_sd^2.
            prior_precision = 1.0 / (scorer.prior_sd**2)
            total_precision = 1.0 / (scorer.posterior_sd**2)
            prior_w = prior_precision / total_precision
            weight_balance[name] = {
                "prior_weight": prior_w,
                "data_weight": 1.0 - prior_w,
            }

        domain_states = {}
        for domain, (sat_key, frust_key) in DOMAIN_PAIRS.items():
            domain_states[domain] = classify_with_uncertainty(
                self.scorers[sat_key], self.scorers[frust_key]
            )

        archetypes = self.get_archetype_probabilities()

        # All scorers should have the same count; use the first.
        n = next(iter(self.scorers.values())).measurements_incorporated

        return {
            "posteriors": posteriors,
            "domain_states": domain_states,
            "archetypes": archetypes,
            "measurements_incorporated": n,
            "weight_balance": weight_balance,
        }
