import anthropic

from config import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a QA engineer. Given a Jira task description, generate structured manual test cases.

Format each test case exactly as follows:

**Test Case N: <Title>**
- **Preconditions:** <what must be true before the test>
- **Steps:**
  1. <step>
  2. <step>
  ...
- **Expected Result:** <what should happen>

Generate between 3 and 7 test cases covering the happy path and the most important edge cases.
Always write test cases in English."""


def generate_test_cases(issue_text: str) -> str:
    with _client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Generate test cases for the following Jira task:\n\n{issue_text}",
            }
        ],
    ) as stream:
        return stream.get_final_message().content[0].text
