import base64
import httpx

from config import JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN


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


def post_comment(issue_key: str, body: str) -> dict:
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
