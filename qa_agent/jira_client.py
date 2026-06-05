import base64
import logging

import httpx

from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

logger = logging.getLogger(__name__)

_COMMENT_MAX_CHARS = 30_000


def _auth_header() -> str:
    token = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    return f"Basic {token}"


def _headers() -> dict:
    return {
        "Authorization": _auth_header(),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def get_issue(issue_key: str) -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"
    response = httpx.get(url, headers=_headers(), timeout=10)
    response.raise_for_status()
    return response.json()


def get_issue_text(issue_key: str) -> str:
    issue = get_issue(issue_key)
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    description_doc = fields.get("description") or {}
    description_text = _extract_adf_text(description_doc)
    ac_text = ""
    for field_value in fields.values():
        if isinstance(field_value, dict) and field_value.get("type") == "doc":
            text = _extract_adf_text(field_value)
            if text and text != description_text:
                ac_text += "\n" + text
    result = f"Summary: {summary}"
    if description_text:
        result += f"\n\nDescription:\n{description_text}"
    if ac_text:
        result += f"\n\nAcceptance Criteria:{ac_text}"
    return result.strip()


def _extract_adf_text(node: dict) -> str:
    if not node or not isinstance(node, dict):
        return ""
    node_type = node.get("type", "")
    if node_type == "text":
        return node.get("text", "")
    parts = []
    for child in node.get("content", []):
        text = _extract_adf_text(child)
        if text:
            parts.append(text)
    separator = "\n" if node_type in ("paragraph", "heading", "listItem", "bulletList", "orderedList") else ""
    return separator.join(parts)


def _split_body(body: str) -> list[str]:
    """Split body into chunks ≤ _COMMENT_MAX_CHARS, breaking on paragraph then line boundaries."""
    if len(body) <= _COMMENT_MAX_CHARS:
        return [body]

    chunks: list[str] = []
    current = ""

    for section in body.split("\n\n"):
        # Section itself exceeds limit — split further on single newlines
        if len(section) > _COMMENT_MAX_CHARS:
            for line in section.split("\n"):
                if len(line) > _COMMENT_MAX_CHARS:
                    line = line[: _COMMENT_MAX_CHARS - 11] + "[truncated]"
                candidate = f"{current}\n{line}" if current else line
                if len(candidate) > _COMMENT_MAX_CHARS:
                    chunks.append(current)
                    current = line
                else:
                    current = candidate
        else:
            candidate = f"{current}\n\n{section}" if current else section
            if len(candidate) > _COMMENT_MAX_CHARS:
                chunks.append(current)
                current = section
            else:
                current = candidate

    if current:
        chunks.append(current)

    return chunks


def _post_single_comment(issue_key: str, body: str) -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": body}],
                }
            ],
        }
    }
    response = httpx.post(url, headers=_headers(), json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def post_comment_adf(issue_key: str, adf_body: dict) -> None:
    """Post a pre-built ADF document as a Jira comment (no splitting — ADF analysis comments are always short)."""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
    payload = {"body": adf_body}
    response = httpx.post(url, headers=_headers(), json=payload, timeout=10)
    response.raise_for_status()


def post_comment(issue_key: str, body: str) -> None:
    chunks = _split_body(body)
    total = len(chunks)

    if total > 1:
        logger.info("Comment for %s split into %d parts (%d chars total)", issue_key, total, len(body))

    for i, chunk in enumerate(chunks, start=1):
        text = chunk if i == 1 else f"(continued {i}/{total})\n\n{chunk}"
        try:
            _post_single_comment(issue_key, text)
            if total > 1:
                logger.info("Posted part %d/%d to %s", i, total, issue_key)
        except Exception as exc:
            if i == 1:
                raise
            # Subsequent chunks: log and continue so earlier chunks aren't lost
            logger.error("Failed to post part %d/%d to %s: %s", i, total, issue_key, exc)
