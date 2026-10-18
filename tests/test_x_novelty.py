from datetime import UTC, datetime, timedelta

from pipeline.evidence import EvidenceRecord, EvidenceStage, save_evidence
from pipeline.x_novelty import (
    NoveltyVerdict,
    SeenItem,
    load_seen,
    normalize_url,
    screen_x_candidate,
)

NOW = datetime(2026, 10, 18, 12, tzinfo=UTC)


def _record(evidence_id="x-discovery--a", *, hours_old=3, links=None, title="Meta drops train"):
    return EvidenceRecord(
        evidence_id=evidence_id,
        source="x-discovery",
        source_url=f"https://x.com/someone/status/{evidence_id}",
        supporting_urls=links if links is not None else ["https://example.com/story"],
        published_at=NOW - timedelta(hours=hours_old),
        detected_at=NOW,
        content_path=f"content/evidence/x-discovery/{evidence_id}.json",
        content_hash="sha256:x",
        external_id=evidence_id,
        stage=EvidenceStage.FETCHED,
        title=title,
        content="Meta removed 'train' from its terms.",
        discovery_metadata={"author_handle": "someone"},
    )


def _seen(ref="feed:meta-terms", urls=()):
    return SeenItem(
        ref=ref,
        title="Meta revises terms",
        origin="press-gazette",
        when=NOW - timedelta(days=1),
        urls=frozenset(normalize_url(url) for url in urls),
    )


class FakeModel:
    def __init__(self, verdict):
        self.verdict = verdict
        self.calls = 0

    async def generate(self, *, response_model, system_instruction, prompt):
        self.calls += 1
        return self.verdict


def test_normalize_url_ignores_scheme_www_and_trailing_slash():
    assert normalize_url("https://www.Example.com/a/") == normalize_url("http://example.com/a")


async def test_old_post_is_stale_without_a_model_call():
    model = FakeModel(NoveltyVerdict(is_new=True, reason="x"))
    decision = await screen_x_candidate(
        _record(hours_old=60), seen=[_seen()], model=model, now=NOW
    )
    assert decision.outcome == "stale"
    assert model.calls == 0


async def test_shared_link_with_feed_item_is_covered_without_a_model_call():
    model = FakeModel(NoveltyVerdict(is_new=True, reason="x"))
    decision = await screen_x_candidate(
        _record(),
        seen=[_seen(urls=["https://www.example.com/story/"])],
        model=model,
        now=NOW,
    )
    assert decision.outcome == "covered"
    assert decision.matched == "feed:meta-terms"
    assert model.calls == 0


async def test_model_judges_same_development_in_other_words_as_duplicate():
    model = FakeModel(
        NoveltyVerdict(is_new=False, matched_ref="x:x-discovery--b", reason="same Meta change")
    )
    decision = await screen_x_candidate(
        _record(), seen=[_seen(ref="x:x-discovery--b")], model=model, now=NOW
    )
    assert decision.outcome == "duplicate"
    assert not decision.surfaces
    assert decision.as_metadata()["matched"] == "x:x-discovery--b"


async def test_unseen_development_surfaces():
    model = FakeModel(NoveltyVerdict(is_new=True, reason="nothing similar"))
    decision = await screen_x_candidate(_record(), seen=[_seen()], model=model, now=NOW)
    assert decision.surfaces


def test_load_seen_reads_recent_feed_and_x_evidence_but_not_self(tmp_path):
    feed = tmp_path / "feed"
    feed.mkdir()
    (feed / "recent.md").write_text(
        "---\nslug: recent\ntitle: Recent\nsource: cloudflare-blog\n"
        "detected_at: 2026-10-17T10:00:00+00:00\nevidence_ids: [cf--1]\n"
        "source_urls: ['https://blog.cloudflare.com/x']\n---\nbody\n"
    )
    (feed / "old.md").write_text(
        "---\nslug: old\ntitle: Old\nsource: cloudflare-blog\n"
        "detected_at: 2026-09-01T10:00:00+00:00\n---\nbody\n"
    )
    evidence = tmp_path / "evidence"
    earlier = _record("x-discovery--b")
    earlier.stage = EvidenceStage.ANALYZED
    save_evidence(evidence, earlier)
    save_evidence(evidence, _record("x-discovery--a"))

    seen = load_seen(
        feed_dir=feed,
        evidence_dir=evidence,
        x_source="x-discovery",
        exclude_evidence_id="x-discovery--a",
        now=NOW,
    )

    assert {item.ref for item in seen} == {"feed:recent", "x:x-discovery--b"}
