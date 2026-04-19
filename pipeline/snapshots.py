"""Per-source snapshot persistence under `content/snapshots/{slug}/{date}.{ext}`."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def save_snapshot(
    snapshots_root: Path, slug: str, when: datetime, *, content: str, ext: str
) -> Path:
    folder = snapshots_root / slug
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{when.date().isoformat()}.{ext}"
    p.write_text(content)
    return p


_DATE_RX = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.")


def load_latest(snapshots_root: Path, slug: str) -> tuple[str, datetime] | None:
    folder = snapshots_root / slug
    if not folder.exists():
        return None
    candidates: list[tuple[datetime, Path]] = []
    for p in folder.iterdir():
        m = _DATE_RX.match(p.name)
        if not m:
            continue
        y, mo, d = (int(x) for x in m.groups())
        candidates.append((datetime(y, mo, d, tzinfo=timezone.utc), p))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    dt, p = candidates[0]
    return (p.read_text(), dt)
