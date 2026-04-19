"""Runtime configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Config:
    repo_root: Path
    anthropic_api_key: str
    alert_emails: list[str] = field(default_factory=list)

    @property
    def snapshots_dir(self) -> Path:
        return self.repo_root / "content" / "snapshots"

    @property
    def events_dir(self) -> Path:
        return self.repo_root / "content" / "events"

    @property
    def data_dir(self) -> Path:
        return self.repo_root / "data"

    @property
    def state_dir(self) -> Path:
        return self.repo_root / "state"

    @property
    def sources_yaml(self) -> Path:
        return self.repo_root / "sources.yaml"

    @classmethod
    def from_env(cls) -> "Config":
        repo_root_raw = os.environ.get("REPO_ROOT")
        if not repo_root_raw:
            repo_root_raw = str(Path(__file__).resolve().parent.parent)
        emails_raw = os.environ.get("ALERT_EMAILS", "")
        emails = [e.strip() for e in emails_raw.split(",") if e.strip()]
        return cls(
            repo_root=Path(repo_root_raw).resolve(),
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            alert_emails=emails,
        )
