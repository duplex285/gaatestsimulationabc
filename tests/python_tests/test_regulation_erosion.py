"""Tests for the regulation-erosion detector.

Reference: improvement-plan-personalization-engine.md Section 16.1
Reference: src/python_scoring/regulation_erosion.py

Covers:
- Single profile returns no events
- Two-profile drop fires
- Two-profile rise does not fire
- Three-profile drop-then-recover does not fire
- Three-profile sustained drop fires
- Only affected domains are flagged
- not_computed in the series is skipped without breaking detection
"""

from __future__ import annotations

from src.python_scoring.regulation_erosion import detect_regulation_erosion
from src.python_scoring.regulatory_style import score_regulatory_style


def _profile(
    ar_auto: int,
    ar_ctrl: int,
    br_auto: int = 7,
    br_ctrl: int = 1,
    cr_auto: int = 7,
    cr_ctrl: int = 1,
):
    """Score a profile with controllable Ambition style; other domains
    default to identified (auto=7, ctrl=1) so they do not erode."""
    return score_regulatory_style(
        {
            "AR1": ar_auto,
            "AR2": ar_ctrl,
            "BR1": br_auto,
            "BR2": br_ctrl,
            "CR1": cr_auto,
            "CR2": cr_ctrl,
        }
    )


class TestBaselineBehavior:
    def test_single_profile_returns_empty(self):
        events = detect_regulation_erosion([_profile(7, 1)])
        assert events == []

    def test_empty_list_returns_empty(self):
        assert detect_regulation_erosion([]) == []


class TestTwoProfileSeries:
    def test_drop_identified_to_introjected_fires(self):
        series = [_profile(7, 1), _profile(1, 7)]  # identified -> introjected
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].domain == "ambition"
        assert events[0].style_series[-1] == "introjected"
        assert events[0].style_series[0] == "identified"

    def test_rise_does_not_fire(self):
        series = [_profile(1, 7), _profile(7, 1)]  # introjected -> identified
        events = detect_regulation_erosion(series)
        assert events == []

    def test_flat_does_not_fire(self):
        series = [_profile(7, 1), _profile(7, 1)]
        assert detect_regulation_erosion(series) == []

    def test_drop_by_one_rank_fires(self):
        """identified (3) -> conflicted (2) is a one-step drop, still fires."""
        series = [_profile(7, 1), _profile(7, 7)]
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].style_series == ["identified", "conflicted"]


class TestThreeProfileSeries:
    def test_sustained_drop_fires(self):
        series = [_profile(7, 1), _profile(7, 7), _profile(1, 7)]
        # identified -> conflicted -> introjected
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].domain == "ambition"

    def test_drop_then_recover_does_not_fire(self):
        """Single-cycle drop with recovery: latest rank equals starting."""
        series = [_profile(7, 1), _profile(7, 7), _profile(7, 1)]
        # identified -> conflicted -> identified
        assert detect_regulation_erosion(series) == []

    def test_drop_then_partial_recovery_does_not_fire(self):
        """Latest rank higher than two measurements ago -> no fire."""
        series = [_profile(1, 7), _profile(7, 7), _profile(7, 1)]
        # introjected -> conflicted -> identified (upward trajectory)
        assert detect_regulation_erosion(series) == []

    def test_sustained_low_after_drop_fires(self):
        """identified -> introjected -> introjected: drop held, fires.

        This is the case the original latest-vs-prior rule missed. The
        monotonic-non-increase-plus-net-drop rule catches it: ranks
        [3, 1, 1] satisfy 1 <= 1 <= 3 and 1 < 3.
        """
        series = [_profile(7, 1), _profile(1, 7), _profile(1, 7)]
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].domain == "ambition"
        assert events[0].rank_series[-3:] == [3, 1, 1]

    def test_plateau_after_step_down_fires(self):
        """identified -> conflicted -> conflicted: drop held, fires."""
        series = [_profile(7, 1), _profile(7, 7), _profile(7, 7)]
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].rank_series[-3:] == [3, 2, 2]

    def test_step_down_after_plateau_fires(self):
        """identified -> identified -> conflicted: monotonic with net drop."""
        series = [_profile(7, 1), _profile(7, 1), _profile(7, 7)]
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].rank_series[-3:] == [3, 3, 2]


class TestMultiDomainIsolation:
    def test_only_affected_domain_flagged(self):
        """Ambition drops; belonging and craft stay identified."""
        series = [
            _profile(ar_auto=7, ar_ctrl=1),
            _profile(ar_auto=1, ar_ctrl=7),
        ]
        events = detect_regulation_erosion(series)
        assert len(events) == 1
        assert events[0].domain == "ambition"

    def test_multiple_domains_can_fire(self):
        """Ambition and belonging both erode; craft stays healthy."""
        series = [
            score_regulatory_style(
                {
                    "AR1": 7,
                    "AR2": 1,
                    "BR1": 7,
                    "BR2": 1,
                    "CR1": 7,
                    "CR2": 1,
                }
            ),
            score_regulatory_style(
                {
                    "AR1": 1,
                    "AR2": 7,
                    "BR1": 1,
                    "BR2": 7,
                    "CR1": 7,
                    "CR2": 1,
                }
            ),
        ]
        events = detect_regulation_erosion(series)
        flagged = {e.domain for e in events}
        assert flagged == {"ambition", "belonging"}


class TestNotComputedHandling:
    def test_skips_not_computed_measurements(self):
        """A measurement with not_computed style does not break detection."""
        # Ambition: identified, [not_computed], introjected.
        # Computable series is identified -> introjected: fires.
        p1 = score_regulatory_style(
            {
                "AR1": 7,
                "AR2": 1,
                "BR1": 7,
                "BR2": 1,
                "CR1": 7,
                "CR2": 1,
            }
        )
        p2 = score_regulatory_style(
            {
                "BR1": 7,
                "BR2": 1,
                "CR1": 7,
                "CR2": 1,  # AR items missing
            }
        )
        p3 = score_regulatory_style(
            {
                "AR1": 1,
                "AR2": 7,
                "BR1": 7,
                "BR2": 1,
                "CR1": 7,
                "CR2": 1,
            }
        )
        events = detect_regulation_erosion([p1, p2, p3])
        amb = [e for e in events if e.domain == "ambition"]
        assert len(amb) == 1

    def test_all_not_computed_returns_empty(self):
        p1 = score_regulatory_style({})
        p2 = score_regulatory_style({})
        assert detect_regulation_erosion([p1, p2]) == []
