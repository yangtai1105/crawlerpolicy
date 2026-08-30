from datetime import UTC, datetime

from pipeline.health import (
    HealthStatus,
    SourceRunStatus,
    build_run_health,
    exit_code_for_health,
)
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track

NOW = datetime(2026, 8, 29, 8, tzinfo=UTC)


def _source(slug: str, *, required: bool) -> Source:
    return Source(
        slug=slug,
        type=SourceType.HTML_PAGE,
        url=f"https://{slug}.example",
        display_name=slug,
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
        required_for_coverage=required,
    )


def _ok() -> SourceRunStatus:
    return SourceRunStatus(fetch="ok", evidence="ok", analysis="ok", publish="ok")


def test_required_source_failure_is_critical():
    required = _source("required", required=True)
    optional = _source("optional", required=False)

    health = build_run_health(
        sources=[required, optional],
        per_source={
            required.slug: SourceRunStatus(fetch="failed", error="network down"),
            optional.slug: _ok(),
        },
        now=NOW,
        last_full_success=None,
    )

    assert health.status is HealthStatus.CRITICAL
    assert health.coverage.required_failed == 1
    assert health.last_fully_successful_at is None
    assert exit_code_for_health(health) == 2


def test_optional_failure_with_sufficient_coverage_is_degraded():
    sources = [_source(f"source-{index}", required=False) for index in range(4)]
    per_source = {source.slug: _ok() for source in sources}
    per_source[sources[-1].slug] = SourceRunStatus(
        fetch="failed", error="optional source unavailable"
    )
    previous_success = datetime(2026, 8, 28, 8, tzinfo=UTC)

    health = build_run_health(
        sources=sources,
        per_source=per_source,
        now=NOW,
        last_full_success=previous_success,
    )

    assert health.status is HealthStatus.DEGRADED
    assert health.coverage.completed == 3
    assert health.coverage.failed == 1
    assert health.last_fully_successful_at == previous_success
    assert exit_code_for_health(health) == 0


def test_healthy_run_updates_last_full_success_and_stage_totals():
    source = _source("required", required=True)

    health = build_run_health(
        sources=[source],
        per_source={source.slug: _ok()},
        now=NOW,
        last_full_success=None,
    )

    assert health.status is HealthStatus.HEALTHY
    assert health.last_fully_successful_at == NOW
    assert health.stages["analysis"].ok == 1
    assert exit_code_for_health(health) == 0
