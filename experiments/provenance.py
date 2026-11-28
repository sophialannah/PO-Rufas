"""Report Git provenance without requiring .git in an exported source copy."""

from pathlib import Path
import subprocess


def git_context():
    root = Path(__file__).resolve().parents[1]
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
        if revision.returncode:
            return dict(commit=None, dirty=None, source="exported_source_without_git")
        status = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
        return dict(commit=revision.stdout.strip(), dirty=bool(status.stdout.strip()), source="git_worktree")
    except FileNotFoundError:
        return dict(commit=None, dirty=None, source="git_unavailable")
