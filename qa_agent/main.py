import logging
import re
from typing import List

from claude_client import generate_test_cases
from jira_client import get_issue_text, post_comment

logger = logging.getLogger(__name__)

JIRA_ISSUE_RE = re.compile(r"\b([A-Z]+-\d+)\b")


def extract_issue_keys(commit_messages: List[str]) -> List[str]:
    seen = set()
    keys = []
    for message in commit_messages:
        for match in JIRA_ISSUE_RE.finditer(message):
            key = match.group(1)
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def process_issue(issue_key: str) -> None:
    logger.info("Processing %s", issue_key)
    try:
        issue_text = get_issue_text(issue_key)
    except Exception as exc:
        logger.error("Failed to fetch Jira issue %s: %s", issue_key, exc)
        return

    try:
        test_cases = generate_test_cases(issue_text)
    except Exception as exc:
        logger.error("Failed to generate test cases for %s: %s", issue_key, exc)
        return

    comment_body = f"🤖 Auto-generated test cases:\n\n{test_cases}"
    try:
        post_comment(issue_key, comment_body)
        logger.info("Posted test cases to %s", issue_key)
    except Exception as exc:
        logger.error("Failed to post comment to %s: %s", issue_key, exc)


def handle_push_event(commit_messages: List[str]) -> None:
    keys = extract_issue_keys(commit_messages)
    if not keys:
        logger.info("No Jira issue keys found in commits")
        return
    logger.info("Found issue keys: %s", keys)
    for key in keys:
        process_issue(key)
