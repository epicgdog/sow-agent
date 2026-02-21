#!/usr/bin/env python3
"""
Push workspace/src changes to a GitHub branch.

Used after a successful agent run when --push is requested.
Requires GITHUB_TOKEN in the environment (with repo write access).

Usage:
  python push_to_github.py <workspace_path> <repo_url> [branch_name]

Branch defaults to sow-agent/run-YYYYMMDD-HHMMSS.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def _url_with_token(repo_url: str, token: str) -> str:
    """Inject token into HTTPS URL for push auth."""
    if not token or not repo_url.startswith("https://"):
        return repo_url
    # https://github.com/owner/repo -> https://<token>@github.com/owner/repo
    match = re.match(r"(https://)(github\.com/.*)", repo_url)
    if match:
        return f"{match.group(1)}{token}@{match.group(2)}"
    return repo_url


def push_workspace_to_github(
    workspace_path: Path,
    repo_url: str,
    branch_name: str | None = None,
    token: str | None = None,
) -> str:
    """
    Commit all changes in workspace/src and push to a new branch.

    Args:
        workspace_path: Workspace root (contains src/)
        repo_url: GitHub repo URL (https://github.com/owner/repo or .git)
        branch_name: Optional branch name; default sow-agent/run-<timestamp>
        token: GitHub token for push; defaults to GITHUB_TOKEN env

    Returns:
        The branch name that was pushed.

    Raises:
        RuntimeError: On git or push failure.
    """
    src_dir = workspace_path / "src"
    if not src_dir.is_dir():
        raise RuntimeError(f"Workspace src not found: {src_dir}")

    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN not set. Set it in the environment or pass token= for auto-push."
        )

    if branch_name is None:
        branch_name = f"sow-agent/run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Normalize repo URL (strip .git for remote add, we'll use auth URL for push)
    push_url = _url_with_token(repo_url.strip().rstrip("/").removesuffix(".git"), token)
    origin_url = push_url
    if not origin_url.startswith("https://") and not origin_url.startswith("git@"):
        origin_url = f"https://github.com/{origin_url}" if "/" in origin_url else repo_url
    if not push_url.startswith("https://") and not push_url.startswith("git@"):
        push_url = f"https://github.com/{push_url}" if "/" in push_url else push_url
    push_url = _url_with_token(push_url, token)

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    def run(cmd: list[str], cwd: Path) -> None:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"Git failed: {r.stderr or r.stdout}")

    run(["git", "init"], src_dir)
    run(["git", "remote", "add", "origin", push_url], src_dir)
    run(["git", "checkout", "-b", branch_name], src_dir)
    run(["git", "add", "-A"], src_dir)
    run(["git", "commit", "-m", "SOW Agent: apply compliance changes"], src_dir)
    run(["git", "push", "-u", "origin", branch_name], src_dir)

    return branch_name


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: push_to_github.py <workspace_path> <repo_url> [branch_name]", file=sys.stderr)
        sys.exit(1)
    workspace_path = Path(sys.argv[1])
    repo_url = sys.argv[2]
    branch_name = sys.argv[3] if len(sys.argv) > 3 else None
    try:
        branch = push_workspace_to_github(workspace_path, repo_url, branch_name)
        print(f"Pushed to branch: {branch}")
    except Exception as e:
        print(f"Push failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
