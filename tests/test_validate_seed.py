import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.entities import load_registry  # noqa: E402
from pipeline.positions import PositionStatus  # noqa: E402
from scripts.validate_seed import SeedRow, seed_to_registry, validate_seed  # noqa: E402

REGISTRY = load_registry()


def _row(**overrides) -> dict:
    base = dict(
        player="Cloudflare",
        protocol="Web Bot Auth",
        status="shipped",
        since="2026-07-11",
        source_url="https://blog.cloudflare.com/web-bot-auth",
        note="",
    )
    base.update(overrides)
    return base


def test_a_complete_row_validates():
    assert validate_seed([SeedRow(**_row())], REGISTRY) == []


def test_a_row_without_a_source_url_is_refused():
    errors = validate_seed([SeedRow(**_row(source_url=""))], REGISTRY)

    assert any("source_url" in e for e in errors)


def test_a_row_without_a_since_date_is_refused():
    errors = validate_seed([SeedRow(**_row(since=""))], REGISTRY)

    assert any("since" in e for e in errors)


def test_a_player_outside_the_registry_is_refused():
    errors = validate_seed([SeedRow(**_row(player="Totally Unknown Inc"))], REGISTRY)

    assert any("Totally Unknown Inc" in e for e in errors)


def test_a_protocol_outside_the_registry_is_refused():
    errors = validate_seed([SeedRow(**_row(protocol="Imaginary Protocol"))], REGISTRY)

    assert any("Imaginary Protocol" in e for e in errors)


def test_an_unknown_status_is_refused():
    errors = validate_seed([SeedRow(**_row(status="enthusiastic"))], REGISTRY)

    assert any("enthusiastic" in e for e in errors)


def test_status_none_is_refused_because_absence_is_not_recorded():
    errors = validate_seed([SeedRow(**_row(status="none"))], REGISTRY)

    assert any("none" in e for e in errors)


def test_a_bot_name_resolves_to_its_operator():
    rows = [SeedRow(**_row(player="ClaudeBot", protocol="MCP"))]

    assert validate_seed(rows, REGISTRY) == []
    registry = seed_to_registry(rows, REGISTRY)
    assert registry.get("anthropic", "mcp").status is PositionStatus.SHIPPED


def test_the_shipped_seed_file_is_valid():
    import yaml

    raw = yaml.safe_load(Path("data/positions.seed.yaml").read_text()) or {}
    rows = [SeedRow(**row) for row in (raw.get("rows") or [])]

    assert validate_seed(rows, REGISTRY) == []


def test_a_duplicate_cell_is_refused():
    rows = [SeedRow(**_row()), SeedRow(**_row(since="2026-08-01"))]

    errors = validate_seed(rows, REGISTRY)

    assert any("duplicate" in e for e in errors)


def test_a_source_url_that_is_not_a_url_is_refused():
    errors = validate_seed([SeedRow(**_row(source_url="not-a-url"))], REGISTRY)

    assert any("not a URL" in e for e in errors)


def test_a_malformed_since_date_is_refused():
    errors = validate_seed([SeedRow(**_row(since="July 11"))], REGISTRY)

    assert any("not an ISO date" in e for e in errors)
