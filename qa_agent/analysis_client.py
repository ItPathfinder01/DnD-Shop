import json
import logging

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-sonnet-4-6"

_SYSTEM_PROMPT = """You are a QA engineer performing a code review against task requirements.

Given a Jira task description and a git commit diff, analyse whether the implementation matches the requirements.

Respond ONLY with valid JSON in this exact structure:
{
  "verdict": "<MATCH|PARTIAL|MISMATCH|UNCLEAR>",
  "summary": "<1-3 sentence explanation of the verdict>",
  "warnings": ["<specific gap or concern>"]
}

Verdict definitions:
- MATCH: implementation clearly and fully addresses all requirements
- PARTIAL: implementation addresses some requirements but gaps exist
- MISMATCH: implementation contradicts or ignores the requirements
- UNCLEAR: insufficient context to make a determination (diff too small, requirements too vague)

Rules:
- warnings may be an empty array when verdict is MATCH
- Always write in English regardless of input language
- Be specific about which requirements are addressed or missing
- Do not include markdown formatting in the JSON values"""


def analyze_diff_vs_requirements(
    issue_key: str,
    issue_text: str,
    diff: str,
    truncated: bool,
) -> dict:
    """Returns {"verdict": str, "summary": str, "warnings": list[str]}."""
    truncation_note = (
        "\n\n⚠️ Diff was truncated to fit limits — analysis covers partial diff only."
        if truncated
        else ""
    )

    user_content = (
        f"Task: {issue_key}\n\n"
        f"Requirements:\n{issue_text}\n\n"
        f"Commit diff:{truncation_note}\n{diff}"
    )

    response = _client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.splitlines()[1:])
        raw = raw.rstrip("`").strip()

    result = json.loads(raw)

    verdict = result.get("verdict", "UNCLEAR")
    if verdict not in {"MATCH", "PARTIAL", "MISMATCH", "UNCLEAR"}:
        logger.warning("Unexpected verdict '%s' for %s, defaulting to UNCLEAR", verdict, issue_key)
        result["verdict"] = "UNCLEAR"

    return result
