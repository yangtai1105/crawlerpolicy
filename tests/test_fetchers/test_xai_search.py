import json
from datetime import UTC, datetime

import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.xai_search import fetch_xai_search
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


def _source() -> Source:
    return Source(
        slug="x-access-discovery",
        type=SourceType.XAI_SEARCH,
        query="Find consequential crawler policy changes.",
        x_handles=["Cloudflare", "GoogleSearchC"],
        lookback_hours=36,
        shadow=True,
        display_name="X — Access & Discovery",
        default_tracks=[Track.CRAWLER_CONTROLS, Track.SEARCH_DISCOVERY],
        tier=SourceTier.COMMENTARY,
        role=SourceRole.REPORTING,
    )


def _response(candidates: list[dict], *, calls: int = 1) -> dict:
    return {
        "id": "response-1",
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": json.dumps({"candidates": candidates}),
                    }
                ],
            }
        ],
        "citations": ["https://x.com/Cloudflare/status/2031535503443374365"],
        "usage": {"input_tokens": 500, "output_tokens": 100},
        "server_side_tool_usage": {"SERVER_SIDE_TOOL_X_SEARCH": calls},
    }


def _candidate(*, post_id: str, published_at: str) -> dict:
    return {
        "post_id": post_id,
        "post_url": f"https://x.com/Cloudflare/status/{post_id}",
        "author_handle": "Cloudflare",
        "published_at": published_at,
        "title": "Cloudflare changes crawler controls",
        "synopsis": "Cloudflare announced a concrete crawler-control change.",
        "linked_urls": ["https://blog.cloudflare.com/example"],
    }


@respx.mock
async def test_xai_search_returns_deduplicated_per_post_candidates():
    route = respx.post("https://api.x.ai/v1/responses").mock(
        return_value=Response(
            200,
            json=_response(
                [
                    _candidate(
                        post_id="2031535503443374365",
                        published_at="2026-09-03T04:00:00Z",
                    ),
                    _candidate(
                        post_id="2031535503443374365",
                        published_at="2026-09-03T04:00:00Z",
                    ),
                ]
            ),
        )
    )

    result = await fetch_xai_search(
        _source(),
        api_key="xai-test",
        model="grok-4.6",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert route.called
    assert result.mode is ResultMode.PER_ITEM
    assert [item.guid for item in result.items] == ["2031535503443374365"]
    assert result.items[0].metadata == {
        "author_handle": "Cloudflare",
        "post_url": "https://x.com/Cloudflare/status/2031535503443374365",
        "linked_urls": ["https://blog.cloudflare.com/example"],
        "provider_citations": [
            "https://x.com/Cloudflare/status/2031535503443374365"
        ],
    }
    assert result.metadata["x_search_calls"] == 1
    assert result.metadata["estimated_tool_cost_usd"] == 0.005

    payload = json.loads(route.calls.last.request.content)
    assert payload["model"] == "grok-4.6"
    assert payload["max_turns"] == 2
    assert payload["tools"] == [
        {
            "type": "x_search",
            "from_date": "2026-09-01",
            "to_date": "2026-09-03",
            "allowed_x_handles": ["Cloudflare", "GoogleSearchC"],
        }
    ]


@respx.mock
async def test_xai_search_rejects_posts_outside_precise_hour_window():
    respx.post("https://api.x.ai/v1/responses").mock(
        return_value=Response(
            200,
            json=_response(
                [
                    _candidate(
                        post_id="old",
                        published_at="2026-09-01T19:59:59Z",
                    ),
                    _candidate(
                        post_id="future",
                        published_at="2026-09-03T08:00:01Z",
                    ),
                ]
            ),
        )
    )

    result = await fetch_xai_search(
        _source(),
        api_key="xai-test",
        model="grok-4.6",
        now=datetime(2026, 9, 3, 8, tzinfo=UTC),
    )

    assert result.items == []


@respx.mock
async def test_xai_search_rejects_non_json_model_output():
    invalid = _response([])
    invalid["output"][0]["content"][0]["text"] = "No results today."
    respx.post("https://api.x.ai/v1/responses").mock(
        return_value=Response(200, json=invalid)
    )

    try:
        await fetch_xai_search(
            _source(),
            api_key="xai-test",
            model="grok-4.6",
            now=datetime(2026, 9, 3, 8, tzinfo=UTC),
        )
    except ValueError as error:
        assert "valid candidate JSON" in str(error)
    else:
        raise AssertionError("non-JSON xAI output must fail validation")
