"""Diff two normalized text blobs and emit a unified diff."""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass


@dataclass
class DiffResult:
    has_changes: bool
    unified_diff: str


def compute_diff(prev: str, curr: str, context: int = 3) -> DiffResult:
    a_norm = _normalize(prev)
    b_norm = _normalize(curr)
    if a_norm == b_norm:
        return DiffResult(has_changes=False, unified_diff="")
    diff = difflib.unified_diff(
        a_norm.splitlines(),
        b_norm.splitlines(),
        fromfile="prev",
        tofile="curr",
        n=context,
        lineterm="",
    )
    return DiffResult(has_changes=True, unified_diff="\n".join(diff))


_WS = re.compile(r"[ \t]+")
_MULTI_NL = re.compile(r"\n{2,}")


def _normalize(text: str) -> str:
    text = _WS.sub(" ", text)
    text = _MULTI_NL.sub("\n", text)
    return text.strip()
