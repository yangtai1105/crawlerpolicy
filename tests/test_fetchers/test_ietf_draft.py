import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.ietf_draft import fetch_ietf_draft
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def ietf_source():
    return Source(
        slug="wba",
        pillar=Pillar.AGENT,
        type=SourceType.IETF_DRAFT,
        draft_name="draft-cloudflare-httpbis-web-bot-auth",
        display_name="Web Bot Auth",
    )


@respx.mock
async def test_fetches_latest_revision_text(ietf_source):
    meta_url = (
        "https://datatracker.ietf.org/api/v1/doc/document/"
        "draft-cloudflare-httpbis-web-bot-auth/?format=json"
    )
    respx.get(meta_url).mock(
        return_value=Response(
            200,
            json={"rev": "02", "name": "draft-cloudflare-httpbis-web-bot-auth"},
        )
    )
    txt_url = "https://www.ietf.org/archive/id/draft-cloudflare-httpbis-web-bot-auth-02.txt"
    respx.get(txt_url).mock(return_value=Response(200, text="Full text of draft-02 body."))

    result = await fetch_ietf_draft(ietf_source)

    assert result.mode == ResultMode.DIFFABLE
    assert "Full text of draft-02 body." in result.normalized_content
    assert result.raw_ext == "txt"
