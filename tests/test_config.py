
from datetime import UTC, datetime

from pipeline.config import Config


def test_config_paths_resolve_relative_to_repo_root(tmp_path, monkeypatch):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    cfg = Config.from_env()
    assert cfg.repo_root == tmp_path
    assert cfg.snapshots_dir == tmp_path / "content" / "snapshots"
    assert cfg.events_dir == tmp_path / "content" / "events"
    assert cfg.evidence_dir == tmp_path / "content" / "evidence"
    assert cfg.intelligence_dir == tmp_path / "data" / "intelligence"
    assert cfg.trends_file == tmp_path / "data" / "trends.json"
    assert cfg.data_dir == tmp_path / "data"
    assert cfg.state_dir == tmp_path / "state"
    assert cfg.sources_yaml == tmp_path / "sources.yaml"


def test_config_reads_required_env(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test")
    monkeypatch.setenv("GEMINI_ANALYSIS_MODEL", "gemini-3.7-flash-preview")
    monkeypatch.setenv("PUBLICATION_CUTOFF", "2026-09-01T00:00:00Z")
    monkeypatch.setenv("ALERT_EMAILS", "a@x.com,b@x.com")
    cfg = Config.from_env()
    assert cfg.gemini_api_key == "gemini-test"
    assert cfg.gemini_analysis_model == "gemini-3.7-flash-preview"
    assert cfg.publication_cutoff == datetime(2026, 9, 1, tzinfo=UTC)
    assert cfg.alert_emails == ["a@x.com", "b@x.com"]


def test_config_uses_publication_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.delenv("GEMINI_ANALYSIS_MODEL", raising=False)
    monkeypatch.delenv("PUBLICATION_CUTOFF", raising=False)

    cfg = Config.from_env()

    assert cfg.gemini_analysis_model == "gemini-3.7-flash"
    assert cfg.publication_cutoff == datetime(2026, 8, 30, tzinfo=UTC)
    assert cfg.feed_dir == tmp_path / "content" / "feed"


def test_config_reads_xai_discovery_limits(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("XAI_API_KEY", "xai-test")
    monkeypatch.setenv("XAI_DISCOVERY_MODEL", "grok-4.6")
    monkeypatch.setenv("XAI_MAX_DAILY_SEARCH_CALLS", "4")
    monkeypatch.setenv("XAI_MONTHLY_SOFT_BUDGET_USD", "7.5")

    cfg = Config.from_env()

    assert cfg.xai_api_key == "xai-test"
    assert cfg.xai_discovery_model == "grok-4.6"
    assert cfg.xai_max_daily_search_calls == 4
    assert cfg.xai_monthly_soft_budget_usd == 7.5


def test_config_uses_xai_discovery_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_DISCOVERY_MODEL", raising=False)
    monkeypatch.delenv("XAI_MAX_DAILY_SEARCH_CALLS", raising=False)
    monkeypatch.delenv("XAI_MONTHLY_SOFT_BUDGET_USD", raising=False)

    cfg = Config.from_env()

    assert cfg.xai_api_key == ""
    assert cfg.xai_discovery_model == "grok-4.6"
    assert cfg.xai_max_daily_search_calls == 6
    assert cfg.xai_monthly_soft_budget_usd == 10.0
