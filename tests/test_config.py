from pathlib import Path

from pipeline.config import Config


def test_config_paths_resolve_relative_to_repo_root(tmp_path, monkeypatch):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    cfg = Config.from_env()
    assert cfg.repo_root == tmp_path
    assert cfg.snapshots_dir == tmp_path / "content" / "snapshots"
    assert cfg.events_dir == tmp_path / "content" / "events"
    assert cfg.data_dir == tmp_path / "data"
    assert cfg.state_dir == tmp_path / "state"
    assert cfg.sources_yaml == tmp_path / "sources.yaml"


def test_config_reads_required_env(monkeypatch, tmp_path):
    monkeypatch.setenv("REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("ALERT_EMAILS", "a@x.com,b@x.com")
    cfg = Config.from_env()
    assert cfg.anthropic_api_key == "sk-ant-test"
    assert cfg.alert_emails == ["a@x.com", "b@x.com"]
