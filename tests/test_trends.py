from datetime import UTC, datetime

from pipeline.taxonomy import SourceTier
from pipeline.trends import (
    EventEvidence,
    Trend,
    TrendStatus,
    load_trends,
    propose_delta,
    save_trends,
)


def _event(*, tier: SourceTier) -> EventEvidence:
    return EventEvidence(
        event_id="event-1",
        source_tier=tier,
        evidence_ids=["evidence-1"],
        event_date=datetime(2026, 8, 28, tzinfo=UTC),
    )


def test_commentary_alone_cannot_change_trend_status():
    trend = Trend(
        key="agent-traffic",
        title="Agent traffic",
        status=TrendStatus.EMERGING,
    )

    delta = propose_delta(
        trend,
        [_event(tier=SourceTier.COMMENTARY)],
        proposed=TrendStatus.ACCELERATING,
    )

    assert delta.accepted is False
    assert delta.current_status is TrendStatus.EMERGING
    assert delta.reason == "status changes require primary or measurement evidence"


def test_primary_evidence_can_change_trend_status():
    trend = Trend(
        key="agent-traffic",
        title="Agent traffic",
        status=TrendStatus.EMERGING,
    )

    delta = propose_delta(
        trend,
        [_event(tier=SourceTier.MEASUREMENT)],
        proposed=TrendStatus.ACCELERATING,
    )

    assert delta.accepted is True
    assert delta.previous_status is TrendStatus.EMERGING
    assert delta.current_status is TrendStatus.ACCELERATING
    assert delta.evidence_event_ids == ["event-1"]


def test_trend_registry_round_trips_atomically(tmp_path):
    path = tmp_path / "trends.json"
    trends = [
        Trend(
            key="agent-traffic",
            title="Agent traffic",
            status=TrendStatus.EMERGING,
            thesis="Verified agent traffic is becoming measurable.",
        )
    ]

    save_trends(path, trends)

    assert load_trends(path) == trends
    assert list(tmp_path.glob("*.tmp")) == []
