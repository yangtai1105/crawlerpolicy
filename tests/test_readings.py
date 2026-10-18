import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from pipeline.readings import (
    DevelopmentNote,
    Reading,
    ReadingResponse,
    build_reading,
    save_reading,
)

NOW = datetime(2026, 10, 17, 8, 0, tzinfo=UTC)


@pytest.fixture
def fake_model():
    model = MagicMock()
    model.generate = AsyncMock(
        return_value=ReadingResponse(
            stance="A2A is moving from message format to delegated authority.",
            adoption_shape="Only platform operators have shipped; defenders are absent.",
            new_entrants="Payment networks arrived this quarter via the authorisation layer.",
            watch_for="Whether defenders propose an observability extension within six months.",
        )
    )
    return model


async def test_build_reading_carries_provenance(fake_model):
    reading = await build_reading(
        fake_model,
        subject_kind="protocol",
        subject_slug="a2a",
        developments=[
            DevelopmentNote(slug="visa-ap2-credentials", title="Visa AP2 Credentials"),
            DevelopmentNote(slug="google-a2a-registry", title="Google A2A Registry"),
        ],
        now=NOW,
    )

    assert reading.subject_kind == "protocol"
    assert reading.subject_slug == "a2a"
    assert reading.built_from == ["visa-ap2-credentials", "google-a2a-registry"]
    assert reading.development_count == 2
    assert reading.generated_at == NOW
    assert reading.merged_at is None
    assert reading.stance.startswith("A2A is moving")


async def test_build_reading_returns_none_with_no_developments(fake_model):
    reading = await build_reading(
        fake_model, subject_kind="protocol", subject_slug="x402", developments=[], now=NOW
    )

    assert reading is None
    fake_model.generate.assert_not_called()


def test_save_reading_names_the_file_by_kind_and_slug(tmp_path):
    reading = Reading(
        subject_kind="front",
        subject_slug="agents-identity",
        stance="s",
        adoption_shape="a",
        new_entrants="n",
        watch_for="w",
        built_from=["one"],
        development_count=1,
        generated_at=NOW,
    )

    path = save_reading(tmp_path, reading)

    assert path.name == "front-agents-identity.json"
    assert json.loads(path.read_text())["subject_slug"] == "agents-identity"
    assert list(tmp_path.glob("*.tmp")) == []


async def test_the_prompt_carries_the_development_text_not_just_slugs(fake_model):
    await build_reading(
        fake_model,
        subject_kind="protocol",
        subject_slug="a2a",
        developments=[
            DevelopmentNote(
                slug="google-a2a-registry",
                title="Google opens the A2A agent registry",
                summary="Registration now requires a verifiable organisation identity.",
            )
        ],
        now=NOW,
    )

    prompt = fake_model.generate.call_args.kwargs["prompt"]
    assert "Google opens the A2A agent registry" in prompt
    assert "verifiable organisation identity" in prompt
