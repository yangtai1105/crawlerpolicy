from pathlib import Path

from pipeline.sources import SourceType, load_sources
from pipeline.taxonomy import FRONT_TRACKS, SourceRole, SourceTier, Track


def test_all_tracks_have_configured_coverage():
    sources = load_sources(Path("sources.yaml"))
    covered = {track for source in sources for track in source.default_tracks}

    assert covered == set(Track)


def test_every_front_has_required_authoritative_coverage():
    sources = load_sources(Path("sources.yaml"))

    for front, tracks in FRONT_TRACKS.items():
        assert any(
            source.required_for_coverage
            and source.tier in {SourceTier.PRIMARY, SourceTier.MEASUREMENT}
            and set(source.default_tracks).intersection(tracks)
            for source in sources
        ), front


def test_initial_canonical_coverage_batch_is_configured():
    sources = {source.slug: source for source in load_sources(Path("sources.yaml"))}
    expected_urls = {
        "google-search-central-blog": "https://developers.google.com/search/blog",
        "ietf-webbotauth-wg": "https://datatracker.ietf.org/group/webbotauth/",
        "c2pa-specifications": "https://spec.c2pa.org/",
        "w3c-tdmrep": "https://w3c.github.io/tdm-reservation-protocol/spec/",
        "rsl-standard": "https://rslstandard.org/rsl",
        "iab-comp": "https://iabtechlab.com/standards/comp-content-monetization-protocols-initiative/",
        "us-copyright-office-ai": "https://www.copyright.gov/ai/",
        "cloudflare-radar-ai-insights": "https://radar.cloudflare.com/ai-insights",
    }

    assert {slug: sources[slug].url for slug in expected_urls} == expected_urls
    assert sources["cloudflare-radar-ai-insights"].type is SourceType.CF_BROWSER_RUN
    assert sources["cloudflare-radar-ai-insights"].tier is SourceTier.MEASUREMENT
    assert sources["cloudflare-radar-ai-insights"].role is SourceRole.MEASUREMENT
    assert {
        slug for slug in expected_urls if sources[slug].required_for_coverage
    } == {
        "google-search-central-blog",
        "ietf-webbotauth-wg",
        "w3c-tdmrep",
        "us-copyright-office-ai",
        "cloudflare-radar-ai-insights",
    }


def test_publication_sources_do_not_enable_gemini_search():
    enabled = [source for source in load_sources(Path("sources.yaml")) if source.enabled]

    assert all(source.type is not SourceType.GEMINI_SEARCH for source in enabled)
