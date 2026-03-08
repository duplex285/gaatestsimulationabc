"""Complete ABC Assessment scoring pipeline.

Reference: abc-assessment-spec Section 2.1 (full pipeline)

Pipeline:
  Raw responses (1-7)
    -> Reverse-score items (8 - r)
    -> Subscale means (1.0 - 7.0)
    -> Normalize to 0-10
    -> Domain state classification
    -> Big Five inference
    -> 36-type derivation
"""

from src.python_scoring.big_five_inference import compute_big_five
from src.python_scoring.domain_classification import classify_all_domains
from src.python_scoring.reverse_scoring import apply_reverse_scoring
from src.python_scoring.subscale_computation import compute_all_subscales
from src.python_scoring.type_derivation import derive_type

REQUIRED_ITEMS = frozenset(
    [
        "AS1",
        "AS2",
        "AS3",
        "AS4",
        "AF1",
        "AF2",
        "AF3",
        "AF4",
        "BS1",
        "BS2",
        "BS3",
        "BS4",
        "BF1",
        "BF2",
        "BF3",
        "BF4",
        "CS1",
        "CS2",
        "CS3",
        "CS4",
        "CF1",
        "CF2",
        "CF3",
        "CF4",
    ]
)


class ABCScorer:
    """Orchestrates the full ABC scoring pipeline.

    Reference: abc-assessment-spec Section 2.1
    """

    def score(self, responses: dict[str, int]) -> dict:
        """Score a complete set of 24 item responses.

        Reference: abc-assessment-spec Section 2.1

        Args:
            responses: Dict mapping item codes (AS1, AF1, etc.) to
                responses on 1-7 Likert scale.

        Returns:
            Dict with subscales, domain_states, big_five, type_name, type_domain.
        """
        self._validate_responses(responses)

        # Step 1: Reverse score items
        # Reference: abc-assessment-spec Section 2.1
        scored = apply_reverse_scoring(responses)

        # Step 2-3: Compute subscale means and normalize to 0-10
        # Reference: abc-assessment-spec Section 2.1, Section 13.2
        subscales = compute_all_subscales(scored)

        # Step 4: Domain state classification
        # Reference: abc-assessment-spec Section 2.2
        domain_states = classify_all_domains(subscales)

        # Step 5: Big Five inference
        # Reference: abc-assessment-spec Section 2.3
        big_five = compute_big_five(subscales)

        # Step 6: 36-type derivation
        # Reference: abc-assessment-spec Section 2.4
        type_result = derive_type(subscales, big_five)

        return {
            "subscales": subscales,
            "domain_states": domain_states,
            "big_five": big_five,
            "type_name": type_result["type_name"],
            "type_domain": type_result["type_domain"],
        }

    def _validate_responses(self, responses: dict[str, int]) -> None:
        """Validate that all 24 required items are present and in range.

        Reference: abc-assessment-spec Section 1.1
        """
        missing = REQUIRED_ITEMS - set(responses.keys())
        if missing:
            raise ValueError(f"Missing required items: {sorted(missing)}")

        for item, value in responses.items():
            if item not in REQUIRED_ITEMS:
                continue
            if not isinstance(value, int):
                raise ValueError(f"Response for {item} must be int, got {type(value).__name__}")
            if value < 1 or value > 7:
                raise ValueError(f"Response for {item} must be 1-7, got {value}")
