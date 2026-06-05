import hashlib
import hmac
import json
import logging
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

from config import GITHUB_WEBHOOK_SECRET
from main import handle_push_event

logger = logging.getLogger(__name__)

app = FastAPI(title="QA Agent Webhook")


def _verify_signature(payload: bytes, signature: Optional[str]) -> None:
    if not GITHUB_WEBHOOK_SECRET:
        return
    if not signature or not signature.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Missing or invalid signature")
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), payload, digestmod=hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Signature mismatch")


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
):
    payload = await request.body()
    _verify_signature(payload, x_hub_signature_256)

    if x_github_event != "push":
        return {"detail": "ignored"}

    data = json.loads(payload)
    commits: list[dict] = data.get("commits", [])
    repo_full_name: str = data.get("repository", {}).get("full_name", "")
    messages = [c.get("message", "") for c in commits]

    logger.info("Received push with %d commits (repo: %s)", len(commits), repo_full_name)

    background_tasks.add_task(handle_push_event, messages, commits, repo_full_name)

    return {"detail": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
