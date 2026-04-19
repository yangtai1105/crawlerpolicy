import pytest
from pydantic import ValidationError

from pipeline.sources import Pillar, Source, SourceType, load_sources


def test_html_page_source_minimum_fields():
    s = Source(
        slug="gptbot",
        pillar=Pillar.CRAWLER,
        type=SourceType.HTML_PAGE,
        url="https://platform.openai.com/docs/gptbot",
        display_name="OpenAI GPTBot",
    )
    assert s.slug == "gptbot"
    assert s.pillar == Pillar.CRAWLER


def test_rss_feed_requires_keyword_filter():
    with pytest.raises(ValidationError):
        Source(
            slug="cloudflare-blog",
            pillar=Pillar.ECOSYSTEM,
            type=SourceType.RSS_FEED,
            url="https://blog.cloudflare.com/rss/",
            display_name="Cloudflare Blog",
        )


def test_github_repo_requires_repo_field():
    with pytest.raises(ValidationError):
        Source(
            slug="mcp",
            pillar=Pillar.AGENT,
            type=SourceType.GITHUB_REPO,
            display_name="MCP",
        )


def test_ietf_draft_requires_draft_name():
    with pytest.raises(ValidationError):
        Source(
            slug="wba",
            pillar=Pillar.AGENT,
            type=SourceType.IETF_DRAFT,
            display_name="Web Bot Auth",
        )


def test_load_sources_from_yaml(tmp_path):
    yaml_text = """
- slug: gptbot
  pillar: crawler
  type: html_page
  url: https://platform.openai.com/docs/gptbot
  display_name: OpenAI GPTBot
- slug: cloudflare-blog
  pillar: ecosystem
  type: rss_feed
  url: https://blog.cloudflare.com/rss/
  keyword_filter: ["AI bot", "crawler"]
  display_name: Cloudflare Blog
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    sources = load_sources(p)
    assert len(sources) == 2
    assert sources[0].slug == "gptbot"
    assert sources[1].keyword_filter == ["AI bot", "crawler"]


def test_load_sources_rejects_duplicate_slugs(tmp_path):
    yaml_text = """
- slug: dup
  pillar: crawler
  type: html_page
  url: https://a.example
  display_name: A
- slug: dup
  pillar: crawler
  type: html_page
  url: https://b.example
  display_name: B
"""
    p = tmp_path / "sources.yaml"
    p.write_text(yaml_text)
    with pytest.raises(ValueError, match="duplicate slug"):
        load_sources(p)
