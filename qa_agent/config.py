import os

JIRA_BASE_URL = os.environ["JIRA_BASE_URL"]        # e.g. https://yoursite.atlassian.net
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

ENABLE_COMMIT_ANALYSIS = os.environ.get("ENABLE_COMMIT_ANALYSIS", "false").lower() == "true"
DIFF_MAX_LINES = int(os.environ.get("DIFF_MAX_LINES", "500"))
REDACTION_ENABLED = os.environ.get("REDACTION_ENABLED", "true").lower() == "true"
