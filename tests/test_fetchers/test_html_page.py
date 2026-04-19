import pytest
import respx
from httpx import Response

from pipeline.fetchers.base import ResultMode
from pipeline.fetchers.html_page import fetch_html_page
from pipeline.sources import Pillar, Source, SourceType


@pytest.fixture
def html_source():
    return Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
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
