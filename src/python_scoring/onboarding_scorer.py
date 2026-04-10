"""
6-Item Onboarding Scorer for ABC Assessment.

The 6-item tier (1 item per subscale) has 0.714 reliability and
50% interpretation confidence. This is too weak to assign archetype
labels. The onboarding scorer suppresses labels and shows:

1. Domain-level directional signals ("Ambition appears strongest")
2. Probability distributions over archetypes
3. Invitation to take the full assessment

This follows Phase 5b (tier reliability) findings and the Bayesian
principle that a weak likelihood should produce a wide posterior.

Reference:
    improvement-plan-personalization-engine.md, Section 9
    gold-standard-upgrade-plan.md, Phase 5b
"""

from __future__ import annotations

from src.python_scoring.bayesian_scorer import ABCBayesianProfile
from src.python_scoring.subscale_computation import normalize_to_10

# 6-item tier: 1 item per subscale
ONBOARDING_ITEMS = {
    "a_sat": ["AS1"],
    "a_frust": ["AF1"],
    "b_sat": ["BS1"],
    "b_frust": ["BF1"],
    "c_sat": ["CS1"],
    "c_frust": ["CF1"],
}

# Wider measurement error for single-item subscales
ONBOARDING_SE = 1.5  # vs 0.8 for full 6-item subscales

DOMAIN_LABELS = {
    "ambition": "Ambition",
    "belonging": "Belonging",
    "craft": "Craft",
}


def score_onboarding(
    responses: dict[str, int],
    demographics: dict | None = None,  # noqa: ARG001 (reserved for future base rate integration)
) -> dict:
    """
    Score a 6-item onboarding assessment.

    Reference: abc-assessment-spec Section 9

    Unlike the full pipeline, this does NOT return:
    - A hard archetype label
    - Domain state classifications
    - Frustration signatures
    - Belbin roles

    Instead it returns:
    - Domain-level directional signals
    - Probability distribution over archetypes
    - A narrative invitation to take the full assessment

    Args:
        responses: Dict mapping item codes (AS1, AF1, BS1, BF1, CS1, CF1)
            to 1-7 Likert scale responses.
        demographics: Optional demographic info for base rate priors.

    Returns:
        Dict with directional signals, archetype probabilities, and
        invitation narrative.
    """
    _validate_onboarding_responses(responses)

    # Compute single-item subscale scores
    # Cannot use compute_subscale_mean (requires 6 items).
    # Single item IS the mean on the 1-7 scale.
    subscales = {}
    for subscale_key, items in ONBOARDING_ITEMS.items():
        raw_value = float(responses[items[0]])
        subscales[subscale_key] = normalize_to_10(raw_value)

    # Create Bayesian profile with wide priors (reflecting uncertainty)
    profile = ABCBayesianProfile()
    ses = dict.fromkeys(subscales, ONBOARDING_SE)
    bayesian = profile.update_all(subscales, ses)

    # Archetype probabilities
    archetype_probs = profile.get_archetype_probabilities()

    # Sort by probability
    sorted_probs = sorted(archetype_probs.items(), key=lambda x: x[1], reverse=True)

    # Directional signals
    sat_scores = {
        "ambition": subscales["a_sat"],
        "belonging": subscales["b_sat"],
        "craft": subscales["c_sat"],
    }
    strongest = max(sat_scores, key=sat_scores.get)
    developing = [d for d in sat_scores if d != strongest]

    # Build directional narrative
    strongest_label = DOMAIN_LABELS[strongest]
    developing_labels = " and ".join(DOMAIN_LABELS[d] for d in developing)

    directional_narrative = (
        f"Your responses suggest {strongest_label} is your strongest "
        f"area right now. {developing_labels} are still developing."
    )

    # Top 2 archetype candidates
    top1_name, top1_prob = sorted_probs[0]
    top2_name, top2_prob = sorted_probs[1]

    archetype_narrative = (
        f"Based on your initial responses, you are most likely "
        f"a {top1_name} ({top1_prob:.0%}) or "
        f"a {top2_name} ({top2_prob:.0%}). "
        f"Take the full assessment for a clearer picture."
    )

    invitation = (
        "This is a starting point, not a label. "
        "Six questions give a directional signal. "
        "The full 36-item assessment takes about 8 minutes and "
        "provides a complete profile with confidence bands."
    )

    return {
        "tier": "onboarding",
        "items_answered": 6,
        "subscales": subscales,
        "directional": {
            "strongest_domain": strongest,
            "developing_domains": developing,
            "narrative": directional_narrative,
        },
        "archetype_probabilities": dict(sorted_probs),
        "top_candidates": [
            {"name": top1_name, "probability": top1_prob},
            {"name": top2_name, "probability": top2_prob},
        ],
        "narratives": {
            "directional": directional_narrative,
            "archetype_candidates": archetype_narrative,
            "invitation": invitation,
        },
        "bayesian": bayesian,
        # Explicitly absent: type_name, domain_states, frustration_signatures,
        # belbin_roles. These require higher measurement confidence.
        "suppressed": [
            "type_name",
            "domain_states",
            "frustration_signatures",
            "belbin_roles",
        ],
    }


def _validate_onboarding_responses(responses: dict[str, int]) -> None:
    """Validate the 6 required onboarding items.

    Reference: abc-assessment-spec Section 9
    """
    required = {"AS1", "AF1", "BS1", "BF1", "CS1", "CF1"}
    missing = required - set(responses.keys())
    if missing:
        raise ValueError(f"Missing onboarding items: {sorted(missing)}")

    for item in required:
        value = responses[item]
        if not isinstance(value, int):
            raise ValueError(f"Response for {item} must be int, got {type(value).__name__}")
        if value < 1 or value > 7:
            raise ValueError(f"Response for {item} must be 1-7, got {value}")
