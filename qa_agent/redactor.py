import logging
import re

logger = logging.getLogger(__name__)

# PEM private keys (multiline)
_PEM_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.DOTALL,
)

# Env var assignments: PASSWORD=secret, SECRET_KEY="value", TOKEN=abc123
_ENV_VAR_RE = re.compile(
    r"(?i)((?:password|passwd|secret|token|api[_\-]?key|auth[_\-]?key)\s*=\s*['\"]?)([^\s'\"]{6,})"
)

# Simple token patterns
_TOKEN_PATTERNS: list[re.Pattern] = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),          # Anthropic / OpenAI
    re.compile(r"AKIA[0-9A-Z]{16}"),              # AWS access key
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),           # GitHub personal token
    re.compile(r"xox[baprs]-[0-9a-zA-Z\-]{10,}", re.IGNORECASE),  # Slack
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),        # Google API key
    re.compile(r"eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"),  # JWT
    re.compile(r"ATATT[a-zA-Z0-9]{80,}"),         # Atlassian API token
]

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"(?<!\d)\+?[1-9]\d{7,14}(?!\d)")


def redact(text: str) -> tuple[str, int]:
    """Redact sensitive data from text. Returns (redacted_text, redaction_count)."""
    count = 0

    text, n = _PEM_RE.subn("[REDACTED]", text)
    count += n

    def _redact_env_value(m: re.Match) -> str:
        nonlocal count
        count += 1
        return m.group(1) + "[REDACTED]"

    text = _ENV_VAR_RE.sub(_redact_env_value, text)

    for pattern in _TOKEN_PATTERNS:
        text, n = pattern.subn("[REDACTED]", text)
        count += n

    text, n = _EMAIL_RE.subn("[REDACTED]", text)
    count += n

    text, n = _PHONE_RE.subn("[REDACTED]", text)
    count += n

    return text, count
