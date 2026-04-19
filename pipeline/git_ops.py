"""Thin subprocess wrapper around git for commit+push from the pipeline."""
from __future__ import annotations

import subprocess
from pathlib import Path


def stage_and_commit(repo_root: Path, message: str) -> bool:
    """Stage all changes and create a commit. Returns True if a commit was made."""
    subprocess.run(["git", "-C", str(repo_root), "add", "-A"], check=True)
    result = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--quiet"],
    )
    if result.returncode == 0:
        return False
    subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-m", message],
        check=True,
    )
    return True


def push(repo_root: Path, branch: str = "main") -> None:
    subprocess.run(["git", "-C", str(repo_root), "push", "origin", branch], check=True)
