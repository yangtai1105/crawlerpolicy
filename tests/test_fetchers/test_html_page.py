import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.sources import Source, SourceType
from pipeline.taxonomy import SourceRole, SourceTier, Track


@pytest.fixture
def html_source():
    return Source(
        slug="gptbot",
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
        default_tracks=[Track.CRAWLER_CONTROLS],
        tier=SourceTier.PRIMARY,
        role=SourceRole.PLATFORM_DOCS,
    )


@respx.mock
async def test_fetches_and_normalizes_main_content(html_source):
    html = """
    <html><head><title>GPTBot</title>
    <script>var x=1;</script>
    </head>
    <body>
      <nav>site nav (should drop)</nav>
      <main>
        <article>
          <h1>GPTBot</h1>
          <p>GPTBot is OpenAI's web crawler.</p>
        </article>
      </main>
      <footer>footer junk</footer>
    </body></html>
    """
    respx.get(html_source.url).mock(return_value=Response(200, text=html))

    result = await fetch_html_page(html_source)

    assert result.mode == ResultMode.DIFFABLE
    assert "GPTBot is OpenAI's web crawler." in result.normalized_content
    assert "script" not in result.normalized_content.lower()
    assert "site nav" not in result.normalized_content
    assert "footer junk" not in result.normalized_content


@respx.mock
async def test_honors_content_selector(html_source):
    html_source_with_sel = html_source.model_copy(
        update={"content_selector": "#doc-body"}
    )
    html = """
    <html><body>
      <div id="doc-body">
        <p>canonical body</p>
      </div>
      <div class="sidebar">sidebar noise</div>
    </body></html>
    """
    respx.get(html_source_with_sel.url).mock(return_value=Response(200, text=html))

    result = await fetch_html_page(html_source_with_sel)

    assert "canonical body" in result.normalized_content
    assert "sidebar noise" not in result.normalized_content


@respx.mock
async def test_raises_on_http_error(html_source):
    respx.get(html_source.url).mock(return_value=Response(503))
    with pytest.raises(Exception, match="503"):
        await fetch_html_page(html_source)


@respx.mock
async def test_follows_one_meta_refresh_document_redirect(html_source):
    respx.get(html_source.url).mock(
        return_value=Response(
            200,
            text=(
                '<meta http-equiv="refresh" content="0; url=/spec/latest">'
                '<a href="/spec/latest">click here</a>'
            ),
        )
    )
    respx.get("https://platform.openai.com/spec/latest").mock(
        return_value=Response(200, text=f"<main>{'Protocol specification. ' * 100}</main>")
    )

    result = await fetch_html_page(html_source)

    assert "Protocol specification" in result.normalized_content


@respx.mock
async def test_follows_one_explicit_moved_to_link(html_source):
    respx.get(html_source.url).mock(
        return_value=Response(
            200,
            text=(
                '<p>Moved to <a href="https://example.test/current">'
                "the current specification</a></p>"
            ),
        )
    )
    respx.get("https://example.test/current").mock(
        return_value=Response(200, text=f"<main>{'Current standard text. ' * 100}</main>")
    )

    result = await fetch_html_page(html_source)

    assert "Current standard text" in result.normalized_content


@respx.mock
async def test_follows_a_bounded_explicit_relocation_chain(html_source):
    respx.get(html_source.url).mock(
        return_value=Response(
            200,
            text='<meta http-equiv="refresh" content="0; url=/spec/index">',
        )
    )
    respx.get("https://platform.openai.com/spec/index").mock(
        return_value=Response(
            200,
            text='<p>Moved to <a href="/spec/v2">the latest version</a></p>',
        )
    )
    respx.get("https://platform.openai.com/spec/v2").mock(
        return_value=Response(200, text=f"<main>{'Final standard text. ' * 100}</main>")
    )

    result = await fetch_html_page(html_source)

    assert "Final standard text" in result.normalized_content
