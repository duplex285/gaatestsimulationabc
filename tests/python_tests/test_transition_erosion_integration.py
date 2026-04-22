"""Tests for TransitionTracker + regulation-erosion integration.

Reference: improvement-plan-personalization-engine.md Section 16.1
Reference: src/python_scoring/transition_engine.py
"""

from __future__ import annotations

from src.python_scoring.regulatory_style import score_regulatory_style
from src.python_scoring.transition_engine import TransitionTracker


def _identified():
    return score_regulatory_style({"AR1": 7, "AR2": 1, "BR1": 7, "BR2": 1, "CR1": 7, "CR2": 1})


def _introjected():
    return score_regulatory_style({"AR1": 1, "AR2": 7, "BR1": 1, "BR2": 7, "CR1": 1, "CR2": 7})


def _ambition_only_erodes():
    """Ambition goes to introjected; belonging and craft stay identified."""
    return score_regulatory_style({"AR1": 1, "AR2": 7, "BR1": 7, "BR2": 1, "CR1": 7, "CR2": 1})


class TestBackwardCompatibility:
    def test_existing_record_signature_still_works(self):
        tracker = TransitionTracker()
        result = tracker.record("Integrator")
        assert result["type_name"] == "Integrator"
        assert result["transition"] is None
        assert result["regulation_erosion_events"] == []

    def test_no_profile_means_no_erosion(self):
        tracker = TransitionTracker()
        tracker.record("Integrator")
        entry = tracker.record("Pioneer")
        assert entry["regulation_erosion_events"] == []


class TestErosionDetectedAcrossHistory:
    def test_two_profile_drop_fires(self):
        tracker = TransitionTracker()
        tracker.record("Integrator", regulatory_profile=_identified())
        entry = tracker.record("Integrator", regulatory_profile=_introjected())
        assert "ambition" in entry["regulation_erosion_events"]
        assert "belonging" in entry["regulation_erosion_events"]
        assert "craft" in entry["regulation_erosion_events"]

    def test_stable_profiles_no_erosion(self):
        tracker = TransitionTracker()
        tracker.record("Integrator", regulatory_profile=_identified())
        entry = tracker.record("Integrator", regulatory_profile=_identified())
        assert entry["regulation_erosion_events"] == []

    def test_single_domain_erodes(self):
        tracker = TransitionTracker()
        tracker.record("Integrator", regulatory_profile=_identified())
        entry = tracker.record("Integrator", regulatory_profile=_ambition_only_erodes())
        assert entry["regulation_erosion_events"] == ["ambition"]

    def test_missing_profile_in_middle_still_detects(self):
        """History: identified -> (no profile) -> introjected. Erosion
        runs on computable subset, so it still fires."""
        tracker = TransitionTracker()
        tracker.record("Integrator", regulatory_profile=_identified())
        tracker.record("Integrator", regulatory_profile=None)
        entry = tracker.record("Integrator", regulatory_profile=_introjected())
        assert "ambition" in entry["regulation_erosion_events"]


class TestSummaryIncludesErosion:
    def test_latest_erosion_in_summary(self):
        tracker = TransitionTracker()
        tracker.record("Integrator", regulatory_profile=_identified())
        tracker.record("Integrator", regulatory_profile=_introjected())
        summary = tracker.get_summary()
        assert set(summary["latest_regulation_erosion_domains"]) == {
            "ambition",
            "belonging",
            "craft",
        }

    def test_empty_tracker_summary_has_no_erosion_key_issue(self):
        tracker = TransitionTracker()
        summary = tracker.get_summary()
        # Empty tracker still produces a summary dict without crashing
        assert summary["measurement_count"] == 0
        assert "latest_regulation_erosion_domains" not in summary or (
            summary.get("latest_regulation_erosion_domains") == []
        )


class TestAlignedHistory:
    def test_regulatory_profiles_list_aligns_with_history(self):
        tracker = TransitionTracker()
        tracker.record("Integrator")
        tracker.record("Integrator", regulatory_profile=_identified())
        tracker.record("Integrator")
        assert len(tracker.regulatory_profiles) == len(tracker.history) == 3
        assert tracker.regulatory_profiles[0] is None
        assert tracker.regulatory_profiles[1] is not None
        assert tracker.regulatory_profiles[2] is None
