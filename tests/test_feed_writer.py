from datetime import UTC, datetime

import pytest
import yaml

from pipeline.analyzer import AnalysisResult
from pipeline.feed import PublicationStatus
from pipeline.feed_writer import write_feed_item
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Subject, Track


@pytest.fixture
def source():
    return Source(
        slug="cloudflare",
        type=SourceType.HTML_PAGE,
        url="https://example.test/policy",
        display_name="Cloudflare",
        default_tracks=[Track.PLATFORM_ECOSYSTEM],
        tier=SourceTier.PRIMARY,
        role=SourceRole.INFRASTRUCTURE,
    )


@pytest.fixture
def analysis():
    return AnalysisResult(
        change_kind="material",
        importance=0.82,
        title="Signed agents become enforceable",
        summary="Cloudflare documented a signed-agent control.",
        insight="Identity is becoming infrastructure.",
        implication="Sites can distinguish accountable clients.",
        why_it_matters="Crawler policy can become enforceable and auditable.",
        primary_track=Track.PLATFORM_ECOSYSTEM,
        tracks=[Track.PLATFORM_ECOSYSTEM],
        actors=["Cloudflare"],
        trend_signals=["verifiable-agent-identity"],
        confidence="high",
    )


def test_feed_writer_persists_four_editorial_layers_and_evidence(tmp_path, source, analysis):
    observed = datetime(2026, 8, 30, 8, tzinfo=UTC)

    path = write_feed_item(
        feed_dir=tmp_path,
        source=source,
        analysis=analysis,
        status=PublicationStatus.VERIFIED,
        event_date=observed,
        published_at=observed,
        detected_at=observed,
        evidence_ids=["cloudflare--abc123"],
        source_urls=["https://example.test/policy"],
        unified_diff="+signed agents",
        development_slug="signed-agents-become-enforceable",
    )

    text = path.read_text()
    frontmatter = yaml.safe_load(text.split("---", 2)[1])
    assert frontmatter["status"] == "verified"
    assert frontmatter["evidence_ids"] == ["cloudflare--abc123"]
    assert frontmatter["development_slug"] == "signed-agents-become-enforceable"
    assert frontmatter["trend_signals"] == ["verifiable-agent-identity"]
    assert "## Summary\n\nCloudflare documented" in text
    assert "## Insight\n\nIdentity is becoming infrastructure." in text
    assert "## Implication\n\nSites can distinguish accountable clients." in text
    assert "## Why it matters\n\nCrawler policy can become enforceable" in text


def test_backfilled_feed_item_records_processing_metadata(tmp_path, source, analysis):
    published = datetime(2026, 7, 28, 16, 47, tzinfo=UTC)
    processed = datetime(2026, 9, 1, 18, tzinfo=UTC)
    path = write_feed_item(
        feed_dir=tmp_path,
        source=source,
        analysis=analysis,
        status=PublicationStatus.VERIFIED,
        event_date=published,
        published_at=published,
        detected_at=processed,
        evidence_ids=["mcp-spec--abc123"],
        source_urls=["https://example.test/release"],
        unified_diff="",
        backfilled=True,
        processed_at=processed,
        backfill_batch="direct-evidence_2026-06-01_2026-09-01",
    )
    data = yaml.safe_load(path.read_text().split("---", 2)[1])
    assert data["backfilled"] is True
    assert data["processed_at"] == processed
    assert data["backfill_batch"] == "direct-evidence_2026-06-01_2026-09-01"
    assert data["published_at"] == published


def test_backfilled_feed_item_requires_batch_metadata(tmp_path, source, analysis):
    with pytest.raises(ValueError, match="processed_at and backfill_batch"):
        write_feed_item(
            feed_dir=tmp_path,
            source=source,
            analysis=analysis,
            status=PublicationStatus.VERIFIED,
            event_date=datetime(2026, 7, 1, tzinfo=UTC),
            published_at=datetime(2026, 7, 1, tzinfo=UTC),
            detected_at=datetime(2026, 9, 1, tzinfo=UTC),
            evidence_ids=["source--abc"],
            source_urls=["https://example.test/item"],
            unified_diff="",
            backfilled=True,
        )


def _written(tmp_path, source, analysis):
    observed = datetime(2026, 10, 10, 8, tzinfo=UTC)
    path = write_feed_item(
        feed_dir=tmp_path,
        source=source,
        analysis=analysis,
        status=PublicationStatus.VERIFIED,
        event_date=observed,
        published_at=observed,
        detected_at=observed,
        evidence_ids=["cloudflare--abc123"],
        source_urls=["https://example.test/policy"],
        unified_diff="+signed agents",
    )
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def test_frontmatter_carries_subject_players_and_protocols(tmp_path, source, analysis):
    analysis.subject = Subject.AGENT
    analysis.players = ["cloudflare", "openai"]
    analysis.protocols = ["web-bot-auth"]

    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["subject"] == "agent"
    assert frontmatter["players"] == ["cloudflare", "openai"]
    assert frontmatter["protocols"] == ["web-bot-auth"]


def test_frontmatter_omits_empty_entity_lists(tmp_path, source, analysis):
    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["subject"] == "unknown"
    assert "players" not in frontmatter
    assert "protocols" not in frontmatter


def test_frontmatter_never_leaks_the_review_queue_fields(tmp_path, source, analysis):
    analysis.unknown_players = ["Totally Unknown Inc"]
    analysis.unknown_protocols = ["Imaginary Protocol"]

    frontmatter = _written(tmp_path, source, analysis)

    assert "unknown_players" not in frontmatter
    assert "unknown_protocols" not in frontmatter


def test_frontmatter_carries_position_claims(tmp_path, source, analysis):
    from pipeline.analyzer import ResolvedPositionClaim
    from pipeline.positions import PositionStatus

    analysis.position_claims = [
        ResolvedPositionClaim(
            player_slug="cloudflare",
            protocol_slug="web-bot-auth",
            status=PositionStatus.SHIPPED,
        )
    ]

    frontmatter = _written(tmp_path, source, analysis)

    assert frontmatter["position_claims"] == [
        {"player": "cloudflare", "protocol": "web-bot-auth", "status": "shipped"}
    ]


def test_frontmatter_omits_position_claims_when_empty(tmp_path, source, analysis):
    frontmatter = _written(tmp_path, source, analysis)

    assert "position_claims" not in frontmatter
