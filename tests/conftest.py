import pytest

from pipeline import article_reader


@pytest.fixture(autouse=True)
def _no_linked_article_network(monkeypatch):
    """Keep tests offline: linked-article reads return nothing unless a test opts in."""

    async def _no_articles(urls, *, client=None):
        return [], []

    monkeypatch.setattr(article_reader, "read_linked_articles", _no_articles)
    for name in ("PRIVATE_ARCHIVE_DIR", "PRIVATE_ARCHIVE_REPO", "WAYBACK_SAVE"):
        monkeypatch.delenv(name, raising=False)
