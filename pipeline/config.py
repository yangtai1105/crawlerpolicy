"""Runtime configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class Config:
    repo_root: Path
    gemini_api_key: str
    gemini_analysis_model: str
    publication_cutoff: datetime
    xai_api_key: str = ""
    xai_discovery_model: str = "grok-4.6"
    xai_max_daily_search_calls: int = 6
    xai_monthly_soft_budget_usd: float = 10.0
    alert_emails: list[str] = field(default_factory=list)

    @property
    def snapshots_dir(self) -> Path:
        return self.repo_root / "content" / "snapshots"

    @property
    def events_dir(self) -> Path:
        return self.repo_root / "content" / "events"

    @property
    def feed_dir(self) -> Path:
        return self.repo_root / "content" / "feed"

    @property
    def evidence_dir(self) -> Path:
        return self.repo_root / "content" / "evidence"

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def intelligence_dir(self) -> Path:
        return self.data_dir / "intelligence"

    @property
    def daily_dir(self) -> Path:
        return self.data_dir / "daily"

    @property
    def trends_file(self) -> Path:
        return self.data_dir / "trends.json"

    @property
    def state_dir(self) -> Path:
        return self.repo_root / "state"

    @property
    def sources_yaml(self) -> Path:
        return self.repo_root / "sources.yaml"

    @property
    def raw_dir(self) -> Path:
        return self.repo_root / "content" / "raw"

    @classmethod
    def from_env(cls) -> Config:
        repo_root_raw = os.environ.get("REPO_ROOT")
        if not repo_root_raw:
            repo_root_raw = str(Path(__file__).resolve().parent.parent)
        emails_raw = os.environ.get("ALERT_EMAILS", "")
        emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
        cutoff_raw = os.environ.get("PUBLICATION_CUTOFF", "2026-08-30T00:00:00Z")
        cutoff = datetime.fromisoformat(cutoff_raw.replace("Z", "+00:00"))
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=UTC)
        return cls(
            repo_root=Path(repo_root_raw).resolve(),
            gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
            gemini_analysis_model=os.environ.get(
                "GEMINI_ANALYSIS_MODEL", "gemini-3.7-flash"
            ),
            publication_cutoff=cutoff.astimezone(UTC),
            xai_api_key=os.environ.get("XAI_API_KEY", ""),
            xai_discovery_model=os.environ.get("XAI_DISCOVERY_MODEL", "grok-4.6"),
            xai_max_daily_search_calls=int(
                os.environ.get("XAI_MAX_DAILY_SEARCH_CALLS", "6")
            ),
            xai_monthly_soft_budget_usd=float(
                os.environ.get("XAI_MONTHLY_SOFT_BUDGET_USD", "10")
            ),
            alert_emails=emails,
        )
