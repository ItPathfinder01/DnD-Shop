import logging
import re
import time
from typing import List

from claude_client import generate_test_cases
from jira_client import get_issue_text, post_comment

logger = logging.getLogger(__name__)

JIRA_ISSUE_RE = re.compile(r"\b([A-Z]+-\d+)\b")

# Dedup: issue_key -> timestamp of last analysis comment posted
_analysis_posted_at: dict[str, float] = {}
_DEDUP_WINDOW_SEC = 300  # 5 minutes


def extract_issue_keys(commit_messages: List[str]) -> List[str]:
    seen: set[str] = set()
    keys: List[str] = []
    for message in commit_messages:
        for match in JIRA_ISSUE_RE.finditer(message):
            key = match.group(1)
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def _map_keys_to_shas(commits: List[dict]) -> dict[str, List[str]]:
    """Return {issue_key: [sha, ...]} combining all commits in the push."""
    mapping: dict[str, List[str]] = {}
    for commit in commits:
        sha = commit.get("id", "")
        for match in JIRA_ISSUE_RE.finditer(commit.get("message", "")):
            key = match.group(1)
            mapping.setdefault(key, []).append(sha)
    return mapping


def _process_test_cases(issue_key: str, issue_text: str) -> None:
    try:
        test_cases = generate_test_cases(issue_text)
    except Exception as exc:
        logger.error("Failed to generate test cases for %s: %s", issue_key, exc)
        return

    try:
        post_comment(issue_key, f"🤖 Auto-generated test cases:\n\n{test_cases}")
        logger.info("Posted test cases to %s", issue_key)
    except Exception as exc:
        logger.error("Failed to post test cases comment to %s: %s", issue_key, exc)


def _analyze_issue(
    issue_key: str,
    issue_text: str,
    shas: List[str],
    repo_full_name: str,
) -> None:
    from config import REDACTION_ENABLED
    from github_client import fetch_commit_diff, combine_diffs
    from redactor import redact
    from analysis_client import analyze_diff_vs_requirements

    # 5-minute dedup guard
    last_posted = _analysis_posted_at.get(issue_key, 0)
    if time.time() - last_posted < _DEDUP_WINDOW_SEC:
        logger.info("Skipping analysis for %s — already posted within last 5 min", issue_key)
        return

    raw_diffs: List[tuple[str, bool]] = []
    for sha in shas:
        try:
            raw_diffs.append(fetch_commit_diff(repo_full_name, sha))
        except Exception as exc:
            logger.error("Failed to fetch diff %s/%s: %s", issue_key, sha[:8], exc)

    if not raw_diffs:
        logger.warning("No diffs retrieved for %s — skipping analysis", issue_key)
        return

    diff, truncated = combine_diffs(raw_diffs)

    if REDACTION_ENABLED:
        diff, redaction_count = redact(diff)
        if redaction_count:
            logger.info("Redacted %d sensitive items from diff for %s", redaction_count, issue_key)

    result = analyze_diff_vs_requirements(issue_key, issue_text, diff, truncated)
    comment = _format_analysis_comment(issue_key, result, truncated)
    post_comment(issue_key, comment)
    _analysis_posted_at[issue_key] = time.time()
    logger.info("Posted analysis to %s (verdict: %s)", issue_key, result.get("verdict"))


def _format_analysis_comment(issue_key: str, result: dict, truncated: bool) -> str:
    verdict = result.get("verdict", "UNCLEAR")
    summary = result.get("summary", "")
    warnings: List[str] = result.get("warnings", [])

    lines = [
        f"🔍 Commit Analysis — {issue_key}",
        "",
        f"Verdict: {verdict}",
        "",
        f"Summary: {summary}",
    ]

    if truncated:
        lines += ["", "⚠️ Diff truncated, partial analysis only"]

    if warnings:
        lines += ["", "Warnings:"]
        for w in warnings:
            lines.append(f"⚠️ {w}")

    lines += [
        "",
        "Note: This is an advisory analysis. Multiple tasks may be deployed",
        "together and not all requirements may be addressed in a single commit.",
    ]
    return "\n".join(lines)


def handle_push_event(
    commit_messages: List[str],
    commits: List[dict] | None = None,
    repo_full_name: str = "",
) -> None:
    from config import ENABLE_COMMIT_ANALYSIS

    keys = extract_issue_keys(commit_messages)
    if not keys:
        logger.info("No Jira issue keys found in commits")
        return
    logger.info("Found issue keys: %s", keys)

    key_to_shas = _map_keys_to_shas(commits or [])

    for key in keys:
        try:
            issue_text = get_issue_text(key)
        except Exception as exc:
            logger.error("Failed to fetch Jira issue %s: %s", key, exc)
            continue

        # Test cases always run first — must not be blocked by analysis
        _process_test_cases(key, issue_text)

        if ENABLE_COMMIT_ANALYSIS and repo_full_name:
            try:
                _analyze_issue(key, issue_text, key_to_shas.get(key, []), repo_full_name)
            except Exception as exc:
                logger.error("Commit analysis failed for %s (non-blocking): %s", key, exc)
