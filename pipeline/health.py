"""Truthful stage-aware health calculation for pipeline runs."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from pipeline.sources import Source


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"


class StageStatus(StrEnum):
    PENDING = "pending"
    OK = "ok"
    FAILED = "failed"


class SourceRunStatus(BaseModel):
    fetch: StageStatus = StageStatus.PENDING
    evidence: StageStatus = StageStatus.PENDING
    analysis: StageStatus = StageStatus.PENDING
    publish: StageStatus = StageStatus.PENDING
    error: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    events_written: list[str] = Field(default_factory=list)
    feed_items_written: list[str] = Field(default_factory=list)

    @property
    def completed(self) -> bool:
        return all(
            stage is StageStatus.OK
            for stage in (self.fetch, self.evidence, self.analysis, self.publish)
        )


class Coverage(BaseModel):
    configured: int
    completed: int
    fetched: int
    analyzed: int
    published: int
    failed: int
    required_failed: int


class StageCounts(BaseModel):
    ok: int = 0
    failed: int = 0
    pending: int = 0


class RunHealth(BaseModel):
    status: HealthStatus
    last_attempted_at: datetime
    last_fully_successful_at: datetime | None
    coverage: Coverage
    stages: dict[str, StageCounts]
    per_source: dict[str, SourceRunStatus]


def build_run_health(
    *,
    sources: list[Source],
    per_source: dict[str, SourceRunStatus],
    now: datetime,
    last_full_success: datetime | None,
) -> RunHealth:
    statuses = {
        source.slug: per_source.get(
            source.slug,
            SourceRunStatus(error="source did not run"),
        )
        for source in sources
    }
    completed = sum(status.completed for status in statuses.values())
    failed = len(sources) - completed
    required_failed = sum(
        source.required_for_coverage and not statuses[source.slug].completed
        for source in sources
    )
    configured = len(sources)
    completion_ratio = completed / configured if configured else 0.0

    if required_failed or completion_ratio < 0.70:
        status = HealthStatus.CRITICAL
    elif failed or completion_ratio < 0.95:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.HEALTHY

    stage_counts: dict[str, StageCounts] = {}
    for stage_name in ("fetch", "evidence", "analysis", "publish"):
        values = [getattr(source_status, stage_name) for source_status in statuses.values()]
        stage_counts[stage_name] = StageCounts(
            ok=values.count(StageStatus.OK),
            failed=values.count(StageStatus.FAILED),
            pending=values.count(StageStatus.PENDING),
        )

    return RunHealth(
        status=status,
        last_attempted_at=now,
        last_fully_successful_at=(
            now if status is HealthStatus.HEALTHY else last_full_success
        ),
        coverage=Coverage(
            configured=configured,
            completed=completed,
            fetched=stage_counts["fetch"].ok,
            analyzed=stage_counts["analysis"].ok,
            published=stage_counts["publish"].ok,
            failed=failed,
            required_failed=required_failed,
        ),
        stages=stage_counts,
        per_source=statuses,
    )


def exit_code_for_health(health: RunHealth | HealthStatus) -> int:
    status = health.status if isinstance(health, RunHealth) else health
    return 2 if status is HealthStatus.CRITICAL else 0
