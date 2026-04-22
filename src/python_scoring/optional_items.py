"""Registry for optional (non-core) ABC assessment items.

Reference: abc-assessment-spec Section 16.1, 16.2, 16.3
Reference: docs/passion-items-draft.md
Reference: docs/regulatory-style-items-draft.md
Reference: docs/coach-circumplex-items-draft.md

The core 36-item ABC bank is registered in subscale_computation.py as
SUBSCALE_ITEMS and enforced by REQUIRED_ITEMS in scoring_pipeline.py.
This module registers the three additive layers shipped in 16.1, 16.2,
and 16.3:

- Passion quality (quarterly cadence, athlete-rater): HP1-HP3, OP1-OP3.
- Regulatory style (biweekly cadence, athlete-rater): AR1-AR2, BR1-BR2, CR1-CR2.
- Coach circumplex (quarterly cadence, dual rater): CXA1-CXA5, CXS1-CXS5,
  CXR1-CXR5, CXC1-CXC5, CXH1-CXH4. Administered separately to coach
  and athletes; responses do not mix with the athlete's own ABC form.

All three layers live outside the core REQUIRED_ITEMS so an assessment
that only collects the 36 core items still scores. A delivery system
that includes the optional items can introspect this module to know
which codes belong to which cadence and which scoring module consumes
them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OptionalCadence = Literal["biweekly", "quarterly", "annual"]
Respondent = Literal["athlete", "coach_self_and_athletes"]


@dataclass(frozen=True)
class OptionalItemLayer:
    """Registration metadata for one optional item layer.

    Attributes:
        name: Short identifier used in logs and integration code.
        cadence: How often the layer is administered.
        respondent: Who completes the items. `athlete` means the
            athlete completes them as part of their own assessment flow.
            `coach_self_and_athletes` means the coach completes a self-
            rating and each athlete completes a rating of the coach.
        item_codes: Ordered tuple of item codes for the layer.
        scoring_module: Dotted path to the module that scores the layer.
        reference_doc: Draft-items document with content and rationale.
    """

    name: str
    cadence: OptionalCadence
    respondent: Respondent
    item_codes: tuple[str, ...]
    scoring_module: str
    reference_doc: str


PASSION_LAYER = OptionalItemLayer(
    name="passion_quality",
    cadence="quarterly",
    respondent="athlete",
    item_codes=("HP1", "HP2", "HP3", "OP1", "OP2", "OP3"),
    scoring_module="src.python_scoring.passion_quality",
    reference_doc="docs/passion-items-draft.md",
)

REGULATORY_LAYER = OptionalItemLayer(
    name="regulatory_style",
    cadence="biweekly",
    respondent="athlete",
    item_codes=("AR1", "AR2", "BR1", "BR2", "CR1", "CR2"),
    scoring_module="src.python_scoring.regulatory_style",
    reference_doc="docs/regulatory-style-items-draft.md",
)

COACH_CIRCUMPLEX_LAYER = OptionalItemLayer(
    name="coach_circumplex",
    cadence="quarterly",
    respondent="coach_self_and_athletes",
    item_codes=(
        "CXA1",
        "CXA2",
        "CXA3",
        "CXA4",
        "CXA5",
        "CXS1",
        "CXS2",
        "CXS3",
        "CXS4",
        "CXS5",
        "CXR1",
        "CXR2",
        "CXR3",
        "CXR4",
        "CXR5",
        "CXC1",
        "CXC2",
        "CXC3",
        "CXC4",
        "CXC5",
        "CXH1",
        "CXH2",
        "CXH3",
        "CXH4",
    ),
    scoring_module="src.python_scoring.coach_circumplex",
    reference_doc="docs/coach-circumplex-items-draft.md",
)

GROUP_CONSCIOUS_LAYER = OptionalItemLayer(
    name="group_conscious",
    cadence="biweekly",
    respondent="athlete",
    item_codes=("AG1", "BG1", "CG1", "TI1", "TI2"),
    scoring_module="src.python_scoring.group_conscious",
    reference_doc="docs/group-conscious-items-draft.md",
)

CAUSALITY_ORIENTATIONS_LAYER = OptionalItemLayer(
    name="causality_orientations",
    cadence="annual",
    respondent="athlete",
    item_codes=(
        "AO1",
        "AO2",
        "AO3",
        "AO4",
        "CO1",
        "CO2",
        "CO3",
        "CO4",
        "IO1",
        "IO2",
        "IO3",
        "IO4",
    ),
    scoring_module="src.python_scoring.causality_orientations",
    reference_doc="docs/causality-orientations-items-draft.md",
)

SELF_CONCORDANCE_LAYER = OptionalItemLayer(
    name="self_concordance",
    cadence="biweekly",
    respondent="athlete",
    item_codes=("SC1", "SC2", "SC3", "SC4"),
    scoring_module="src.python_scoring.self_concordance",
    reference_doc="docs/self-concordance-items-draft.md",
)

OPTIONAL_LAYERS: tuple[OptionalItemLayer, ...] = (
    PASSION_LAYER,
    REGULATORY_LAYER,
    COACH_CIRCUMPLEX_LAYER,
    GROUP_CONSCIOUS_LAYER,
    CAUSALITY_ORIENTATIONS_LAYER,
    SELF_CONCORDANCE_LAYER,
)


def _check_layer_uniqueness() -> None:
    """Fail fast at import time if any item code appears in more than one layer.

    This is a safety net beyond the equivalent test assertion so that a
    future layer added in a branch cannot silently collide with existing
    codes until the test suite is run.
    """
    seen: dict[str, str] = {}
    for layer in OPTIONAL_LAYERS:
        for code in layer.item_codes:
            if code in seen:
                raise ValueError(
                    f"duplicate item code {code!r} in layers {seen[code]!r} and {layer.name!r}"
                )
            seen[code] = layer.name


_check_layer_uniqueness()

ALL_OPTIONAL_CODES: frozenset[str] = frozenset(
    code for layer in OPTIONAL_LAYERS for code in layer.item_codes
)


def get_layer(name: str) -> OptionalItemLayer:
    """Return the layer registration by name.

    Raises KeyError if no layer matches.

    Reference: abc-assessment-spec Section 16.8
    """
    for layer in OPTIONAL_LAYERS:
        if layer.name == name:
            return layer
    raise KeyError(f"unknown optional item layer: {name!r}")


def is_optional_item(code: str) -> bool:
    """Return True if code belongs to any registered optional layer.

    Reference: abc-assessment-spec Section 16.8
    """
    return code in ALL_OPTIONAL_CODES


def layer_for_item(code: str) -> OptionalItemLayer | None:
    """Return the layer that owns the given item code, or None.

    Reference: abc-assessment-spec Section 16.8
    """
    for layer in OPTIONAL_LAYERS:
        if code in layer.item_codes:
            return layer
    return None
