"""Readability enforcement for user-facing narrative templates.

Reference: improvement-plan-personalization-engine.md Section 17.2

Flesch-Kincaid grade-level thresholds:
    athlete-facing <= 8
    coach-facing   <= 10

Templates with placeholders are rendered once per domain before
measurement so that substituted wording counts. The rule applies to all
new user-facing narratives (passion, regulatory, erosion, overinvestment).
It does not yet cover the older archetype and domain-state narratives;
those are covered by a planned follow-up pass and are out of scope here.
"""

from __future__ import annotations

import textstat

from src.python_scoring.narrative_engine import (
    _EROSION_NARRATIVES,
    _OVERINVESTMENT_NARRATIVES,
    _PASSION_NARRATIVES,
    _REGULATORY_NARRATIVES,
    NarrativeEngine,
)

ATHLETE_MAX_GRADE = 8.0
COACH_MAX_GRADE = 10.0


def _grade(text: str) -> float:
    return float(textstat.flesch_kincaid_grade(text))


def _target_for(audience: str) -> float:
    return ATHLETE_MAX_GRADE if audience == "athlete" else COACH_MAX_GRADE


class TestPassionTemplatesReadable:
    def test_all_passion_templates_under_target(self):
        failures: list[str] = []
        for leaning, audiences in _PASSION_NARRATIVES.items():
            for audience, content in audiences.items():
                target = _target_for(audience)
                for key, text in content.items():
                    grade = _grade(text)
                    if grade > target:
                        failures.append(
                            f"passion/{leaning}/{audience}/{key} "
                            f"grade={grade:.1f} target<={target}: {text!r}"
                        )
        assert not failures, "\n".join(failures)


class TestOverinvestmentTemplatesReadable:
    def test_all_overinvestment_templates_under_target(self):
        failures: list[str] = []
        for path, audiences in _OVERINVESTMENT_NARRATIVES.items():
            for audience, text in audiences.items():
                target = _target_for(audience)
                grade = _grade(text)
                if grade > target:
                    failures.append(
                        f"overinvestment/{path}/{audience} grade={grade:.1f} "
                        f"target<={target}: {text!r}"
                    )
        assert not failures, "\n".join(failures)


class TestRegulatoryTemplatesReadable:
    """Raw templates before domain substitution."""

    def test_all_regulatory_raw_templates_under_target(self):
        failures: list[str] = []
        for style, audiences in _REGULATORY_NARRATIVES.items():
            for audience, text in audiences.items():
                target = _target_for(audience)
                grade = _grade(text)
                if grade > target:
                    failures.append(
                        f"regulatory/{style}/{audience} grade={grade:.1f} "
                        f"target<={target}: {text!r}"
                    )
        assert not failures, "\n".join(failures)


class TestRegulatoryRenderedReadable:
    """Rendered output after domain substitution, per domain."""

    def test_all_rendered_regulatory_under_target(self):
        engine = NarrativeEngine()
        failures: list[str] = []
        for style in engine.VALID_REGULATORY_STYLES:
            for domain in engine.VALID_DOMAINS:
                for audience in ("athlete", "coach"):
                    text = engine.generate_regulatory_narrative(domain, style, audience)
                    target = _target_for(audience)
                    grade = _grade(text)
                    if grade > target:
                        failures.append(
                            f"rendered/{domain}/{style}/{audience} "
                            f"grade={grade:.1f} target<={target}: {text!r}"
                        )
        assert not failures, "\n".join(failures)


class TestErosionTemplatesReadable:
    def test_raw_erosion_templates_under_target(self):
        failures: list[str] = []
        for audience, text in _EROSION_NARRATIVES.items():
            target = _target_for(audience)
            grade = _grade(text)
            if grade > target:
                failures.append(f"erosion/{audience} grade={grade:.1f} target<={target}: {text!r}")
        assert not failures, "\n".join(failures)

    def test_rendered_erosion_under_target(self):
        engine = NarrativeEngine()
        failures: list[str] = []
        for domain in engine.VALID_DOMAINS:
            for audience in ("athlete", "coach"):
                text = engine.generate_erosion_narrative(domain, audience)
                target = _target_for(audience)
                grade = _grade(text)
                if grade > target:
                    failures.append(
                        f"erosion/{domain}/{audience} grade={grade:.1f} target<={target}: {text!r}"
                    )
        assert not failures, "\n".join(failures)


class TestReadabilityHelperSanity:
    """Guardrails so a silent textstat change would surface here."""

    def test_simple_sentence_is_under_target(self):
        grade = _grade("The sky is blue today.")
        assert grade < 5.0

    def test_complex_sentence_is_over_target(self):
        text = (
            "The intersectional methodology underlying the bifactor-"
            "structural equation modeling necessitates a rigorous "
            "consideration of multicollinearity and psychometric invariance."
        )
        grade = _grade(text)
        assert grade > 12.0
