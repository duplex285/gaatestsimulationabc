"""Latent Profile Analysis (LPA) for ABC Assessment.

Wraps `sklearn.mixture.GaussianMixture` with the five-criterion model
selection convention from the SDT person-centered literature.

Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
Reference: Wang, Morin, Ryan, Liu (2016); Vansteenkiste et al. (2009)
Reference: Morin & Marsh (2015)
Reference: Lo, Mendell, Rubin (2001), aLMR test
Reference: howard-2024-implementation-plan.md V2-B WI-16

Five-criterion convention (replaces the simple BIC delta > 10 rule):
  1. ABIC elbow inspection
  2. BIC + CAIC + ABIC weighted majority
  3. aLMR or BLRT non-significance (NOT yet implemented; see note below)
  4. Substantive interpretability (caller's responsibility)
  5. Entropy >= 0.70 for posterior assignment

Implementation note on aLMR / BLRT.
sklearn does not expose either test directly. The Lo-Mendell-Rubin (2001)
analytical aLMR and the bootstrap LRT (Nylund-Asparouhov-Muthen 2007) are
non-trivial to ship correctly and were judged out of scope for the time
budget. We rely on BIC + CAIC + ABIC + entropy + the parsimony tiebreak.
This is documented as a limitation; a future revision can layer aLMR/BLRT
on top of `_compute_information_criteria`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, cohen_kappa_score
from sklearn.mixture import GaussianMixture


def _n_params(gmm: GaussianMixture, n_features: int) -> int:
    """Return the number of free parameters in a fitted GaussianMixture.

    Reference: sklearn.mixture documentation; matches the formulation used
    inside GaussianMixture._n_parameters.
    """
    k = gmm.n_components
    if gmm.covariance_type == "full":
        cov_params = k * n_features * (n_features + 1) / 2
    elif gmm.covariance_type == "diag":
        cov_params = k * n_features
    elif gmm.covariance_type == "tied":
        cov_params = n_features * (n_features + 1) / 2
    elif gmm.covariance_type == "spherical":
        cov_params = k
    else:
        raise ValueError(f"Unknown covariance_type {gmm.covariance_type}")
    mean_params = k * n_features
    weight_params = k - 1  # constrained to sum to 1
    return int(cov_params + mean_params + weight_params)


def _compute_information_criteria(gmm: GaussianMixture, scores: np.ndarray) -> dict[str, float]:
    """Return AIC, BIC, sample-size adjusted BIC (ABIC), and CAIC.

    Reference: Sclove (1987) ABIC; Bozdogan (1987) CAIC.

    Formulas:
      log_likelihood = sum of per-sample log-likelihoods
      AIC  = -2 * LL + 2 * n_params
      BIC  = -2 * LL + log(n) * n_params
      ABIC = -2 * LL + log((n + 2) / 24) * n_params       # Sclove 1987
      CAIC = -2 * LL + (log(n) + 1) * n_params            # Bozdogan 1987
    """
    n, p = scores.shape
    n_pars = _n_params(gmm, p)
    log_likelihood = float(gmm.score(scores) * n)  # score returns mean LL
    aic = -2.0 * log_likelihood + 2.0 * n_pars
    bic = -2.0 * log_likelihood + np.log(n) * n_pars
    abic = -2.0 * log_likelihood + np.log((n + 2.0) / 24.0) * n_pars
    caic = -2.0 * log_likelihood + (np.log(n) + 1.0) * n_pars
    return {
        "log_likelihood": log_likelihood,
        "aic": float(aic),
        "bic": float(bic),
        "abic": float(abic),
        "caic": float(caic),
        "n_params": n_pars,
    }


def _compute_normalized_entropy(posteriors: np.ndarray) -> float:
    """Normalized entropy (Celeux & Soromenho 1996).

    entropy = 1 - sum(P log P) / (n * log(k))

    Returns 1.0 for k = 1 (degenerate case: perfect assignment).
    """
    n, k = posteriors.shape
    if k <= 1:
        return 1.0
    p = np.clip(posteriors, 1e-12, 1.0)
    plogp = -np.sum(p * np.log(p))
    return float(1.0 - plogp / (n * np.log(k)))


def _select_k_five_criterion(
    results: dict[int, dict],
    entropy_threshold: float,
) -> tuple[int, str, dict]:
    """Apply the five-criterion model selection convention.

    Reference: howard-2024-implementation-plan.md V2-B WI-16

    Strategy:
      a. BIC + CAIC + ABIC weighted majority vote (each criterion picks its min).
      b. ABIC elbow: find k where ABIC reduction drops below 10% of the
         maximum reduction (parsimony heuristic).
      c. Filter candidates to those with entropy >= entropy_threshold (skip
         the filter for k = 1, which has trivial entropy).
      d. Among surviving candidates, prefer the smaller k when scores are
         within 2 BIC units (parsimony tiebreak).
    """
    ks = sorted(k for k in results if k >= 1)
    if not ks:
        raise ValueError("No fitted LPA solutions to select from.")

    # Per-criterion winner
    bic_winner = min(ks, key=lambda k: results[k]["bic"])
    caic_winner = min(ks, key=lambda k: results[k]["caic"])
    abic_winner = min(ks, key=lambda k: results[k]["abic"])

    votes: dict[int, int] = {}
    for w in (bic_winner, caic_winner, abic_winner):
        votes[w] = votes.get(w, 0) + 1
    weighted_winner = max(votes, key=lambda k: votes[k])

    # ABIC elbow: largest k for which adding another class reduces ABIC
    # by less than 10% of the max single-step reduction observed
    abic_vals = [results[k]["abic"] for k in ks]
    elbow = ks[0]
    if len(ks) >= 2:
        deltas = np.diff(abic_vals)  # negative when ABIC drops with bigger k
        improvements = -deltas  # positive when ABIC improves
        if improvements.size > 0 and improvements.max() > 0:
            threshold = 0.10 * improvements.max()
            elbow = ks[0]
            for i, imp in enumerate(improvements):
                if imp >= threshold:
                    elbow = ks[i + 1]
                else:
                    break

    # Entropy filter
    eligible = [k for k in ks if (k == 1) or (results[k]["entropy"] >= entropy_threshold)]
    if not eligible:
        eligible = ks  # fall back to all ks if none meet entropy

    # Parsimony tiebreak: among the weighted_winner / elbow candidates,
    # prefer the smaller k if BIC is within 2 of weighted_winner's BIC.
    candidates = [k for k in (weighted_winner, elbow, abic_winner) if k in eligible]
    if not candidates:
        candidates = eligible

    best_bic = min(results[k]["bic"] for k in candidates)
    parsimonious = min(
        (k for k in candidates if results[k]["bic"] - best_bic <= 2.0),
        default=min(candidates),
    )

    rationale = (
        f"BIC winner k={bic_winner}; CAIC winner k={caic_winner}; "
        f"ABIC winner k={abic_winner}; weighted-vote k={weighted_winner}; "
        f"ABIC elbow k={elbow}; entropy-eligible {eligible}; "
        f"selected k={parsimonious} after parsimony tiebreak (within 2 BIC)."
    )
    summary = {
        "bic_winner": bic_winner,
        "caic_winner": caic_winner,
        "abic_winner": abic_winner,
        "weighted_vote_winner": weighted_winner,
        "abic_elbow": elbow,
        "entropy_eligible": eligible,
    }
    return parsimonious, rationale, summary


def fit_lpa(
    scores: np.ndarray,
    k_range: tuple[int, int] = (1, 6),
    covariance_type: str = "diag",
    random_state: int = 42,
    entropy_threshold: float = 0.70,
    n_init: int = 10,
) -> dict:
    """Latent profile analysis with five-criterion model selection.

    Reference: Howard, Morin, Gagne (2020); Fernet et al. (2020)
    Reference: Wang, Morin, Ryan, Liu (2016); Vansteenkiste et al. (2009)
    Reference: howard-2024-implementation-plan.md V2-B WI-16

    Args:
        scores: (n, p) factor scores or subscale means.
        k_range: inclusive (k_min, k_max) range to fit.
        covariance_type: "diag" (default) or "full".
        random_state: seed for reproducibility (Rule 7).
        entropy_threshold: minimum normalized entropy for class assignment.
        n_init: number of EM restarts per k.

    Returns:
        dict with keys:
          results_per_k: dict[k] -> dict(n_classes, log_likelihood, aic, bic,
                                         abic, caic, entropy, posteriors,
                                         means, proportions)
          selected_k: int
          selection_rationale: str
          criteria_summary: dict with bic_winner, abic_elbow, etc.
    """
    if scores.ndim != 2:
        raise ValueError("scores must be 2-D (n, p).")
    if covariance_type not in ("diag", "full"):
        raise ValueError("covariance_type must be 'diag' or 'full'.")

    k_min, k_max = k_range
    n, p = scores.shape
    results: dict[int, dict] = {}

    for k in range(k_min, k_max + 1):
        gmm = GaussianMixture(
            n_components=k,
            covariance_type=covariance_type,
            random_state=random_state,
            n_init=n_init,
            reg_covar=1e-4,
        )
        gmm.fit(scores)
        posteriors = gmm.predict_proba(scores)
        info = _compute_information_criteria(gmm, scores)
        entropy = _compute_normalized_entropy(posteriors)
        results[k] = {
            "n_classes": k,
            "log_likelihood": info["log_likelihood"],
            "aic": info["aic"],
            "bic": info["bic"],
            "abic": info["abic"],
            "caic": info["caic"],
            "entropy": entropy,
            "posteriors": posteriors,
            "means": gmm.means_.copy(),
            "proportions": gmm.weights_.copy(),
            "n_params": info["n_params"],
        }

    selected_k, rationale, summary = _select_k_five_criterion(
        results, entropy_threshold=entropy_threshold
    )

    return {
        "results_per_k": results,
        "selected_k": selected_k,
        "selection_rationale": rationale,
        "criteria_summary": summary,
        "n_observations": n,
        "n_indicators": p,
    }


def compare_to_archetypes(
    lpa_result: dict,
    archetype_labels: np.ndarray,
) -> dict:
    """Cross-tab LPA classes against the 8 a-priori archetypes.

    Reference: howard-2024-implementation-plan.md V2-B WI-16
    Reference: Vansteenkiste et al. (2009); Morin & Marsh (2015)
    Reference: Hubert & Arabie (1985), Adjusted Rand Index
    Reference: Cohen (1960), kappa coefficient

    Args:
        lpa_result: output of fit_lpa.
        archetype_labels: (n,) integer labels for the 8 a-priori archetypes.

    Returns:
        dict with adjusted_rand_index, cohens_kappa, contingency_table,
        interpretation.
    """
    selected_k = lpa_result["selected_k"]
    posteriors = lpa_result["results_per_k"][selected_k]["posteriors"]
    lpa_assignments = np.argmax(posteriors, axis=1)
    archetype_labels = np.asarray(archetype_labels).astype(int)

    if lpa_assignments.shape[0] != archetype_labels.shape[0]:
        raise ValueError("LPA assignments and archetype labels must have the same length.")

    ari = float(adjusted_rand_score(archetype_labels, lpa_assignments))
    kappa = float(cohen_kappa_score(archetype_labels, lpa_assignments))

    n_lpa = int(lpa_assignments.max()) + 1
    n_arc = int(archetype_labels.max()) + 1
    contingency = np.zeros((n_lpa, n_arc), dtype=int)
    for lpa_c, arc_c in zip(lpa_assignments, archetype_labels, strict=False):
        contingency[lpa_c, arc_c] += 1

    if kappa >= 0.6:
        interp = "strong agreement (kappa >= 0.60)"
    elif kappa >= 0.4:
        interp = "moderate agreement (0.40 <= kappa < 0.60)"
    elif kappa >= 0.2:
        interp = "weak agreement (0.20 <= kappa < 0.40)"
    else:
        interp = "negligible agreement (kappa < 0.20)"

    return {
        "adjusted_rand_index": ari,
        "cohens_kappa": kappa,
        "contingency_table": contingency,
        "interpretation": interp,
    }


def profile_centroids(
    lpa_result: dict,
    indicator_names: list[str],
) -> pd.DataFrame:
    """Return per-class mean profile across indicators.

    Reference: howard-2024-implementation-plan.md V2-B WI-16

    Used for plotting and substantive interpretation. Rows are class
    indices (0..k-1), columns are indicator names.
    """
    selected_k = lpa_result["selected_k"]
    means = lpa_result["results_per_k"][selected_k]["means"]
    if means.shape[1] != len(indicator_names):
        raise ValueError(
            f"means has {means.shape[1]} columns but {len(indicator_names)} names provided."
        )
    df = pd.DataFrame(means, columns=indicator_names)
    df.index.name = "class"
    return df
