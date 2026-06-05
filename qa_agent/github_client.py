import logging
import re

import httpx

from config import GITHUB_TOKEN, DIFF_MAX_LINES

logger = logging.getLogger(__name__)

_SKIP_FILENAMES = re.compile(
    r"(package-lock\.json|yarn\.lock|poetry\.lock|Pipfile\.lock|composer\.lock|"
    r"\.min\.js|\.min\.css|\.map|\.snap)$"
)
_BINARY_EXTENSIONS = re.compile(
    r"\.(png|jpg|jpeg|gif|ico|pdf|zip|tar|gz|whl|exe|bin|so|dylib|ttf|woff|woff2|eot)$",
    re.IGNORECASE,
)


def _is_skippable(filename: str) -> bool:
    return bool(_SKIP_FILENAMES.search(filename)) or bool(_BINARY_EXTENSIONS.search(filename))


def _filter_diff(raw_diff: str) -> str:
    result = []
    skip_current = False
    for line in raw_diff.splitlines(keepends=True):
        if line.startswith("diff --git "):
            parts = line.split(" ")
            filename = parts[-1].strip().lstrip("b/")
            skip_current = _is_skippable(filename)
        if not skip_current:
            result.append(line)
    return "".join(result)


def fetch_commit_diff(repo_full_name: str, sha: str) -> tuple[str, bool]:
    """Fetch filtered diff for a single commit. Returns (diff_text, was_truncated)."""
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{repo_full_name}/commits/{sha}"
    resp = httpx.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    filtered = _filter_diff(resp.text)
    lines = filtered.splitlines()
    if len(lines) > DIFF_MAX_LINES:
        logger.info("Diff for %s truncated: %d → %d lines", sha[:8], len(lines), DIFF_MAX_LINES)
        return "\n".join(lines[:DIFF_MAX_LINES]), True
    return filtered, False


def combine_diffs(diffs: list[tuple[str, bool]]) -> tuple[str, bool]:
    """Merge multiple diffs, re-apply line cap, propagate truncation flag."""
    combined = "\n".join(d for d, _ in diffs)
    any_truncated = any(t for _, t in diffs)
    lines = combined.splitlines()
    if len(lines) > DIFF_MAX_LINES:
        return "\n".join(lines[:DIFF_MAX_LINES]), True
    return combined, any_truncated
