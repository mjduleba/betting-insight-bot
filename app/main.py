"""FastAPI entrypoint for Discord interactions."""

from __future__ import annotations

import json
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.commands import handle_interaction_command
from app.config import get_settings
from app.discord_utils import (
    APPLICATION_COMMAND_TYPE,
    discord_ping_response,
    is_ping_interaction,
    verify_discord_signature,
)

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Discord MLB Bot")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Simple health endpoint for local verification."""

    return {"status": "ok"}


@app.post("/interactions")
async def interactions(request: Request) -> JSONResponse:
    """Handle Discord interaction webhook requests."""

    body = await request.body()
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    if not verify_discord_signature(
        public_key=settings.discord_public_key,
        signature=signature,
        timestamp=timestamp,
        body=body,
    ):
        raise HTTPException(status_code=401, detail="invalid request signature")

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid interaction payload") from exc

    if is_ping_interaction(payload):
        return JSONResponse(discord_ping_response())

    if payload.get("type") != APPLICATION_COMMAND_TYPE:
        raise HTTPException(status_code=400, detail="unsupported interaction type")

    logger.info("Received command interaction: %s", payload.get("data", {}).get("name"))
    response = await handle_interaction_command(payload)
    return JSONResponse(response)
