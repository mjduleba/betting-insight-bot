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
from app.logging_config import setup_logging

# Store settings from configuration file
settings = get_settings()

# Configure logger through centralized logging module
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Create app from FastAPI
app = FastAPI(title='Discord MLB Bot')


@app.get('/health')
async def healthcheck() -> dict[str, str]:
    '''
    Simple health check endpoint.

    Returns:
        dict[str, str]: health status
    '''
    return {'status': 'ok'}


@app.post('/interactions')
async def interactions(request: Request) -> JSONResponse:
    '''
    Endpoint that handles incoming Discord slash-command interactions.

    Args:
        request (Request): slash-command request

    Raises:
        HTTPException: invalid requst signature
        HTTPException: invalid interaction payload
        HTTPException: unsupported interaction

    Returns:
        JSONResponse: response to slash-command
    '''
    # Store body of request
    body = await request.body()
    
    # Extract signature and timestamp
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')

    # Verify Discord requst signature, return 401 if False
    if not verify_discord_signature(
        public_key=settings.discord_public_key,
        signature=signature,
        timestamp=timestamp,
        body=body,
    ):
        raise HTTPException(status_code=401, detail='invalid request signature')

    try:
        # Parse payload from request
        payload = json.loads(body.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail='invalid interaction payload') from exc

    # Detect ping and respond accordingly
    if is_ping_interaction(payload):
        return JSONResponse(discord_ping_response())

    # Validate command, return 400 if False
    if payload.get('type') != APPLICATION_COMMAND_TYPE:
        raise HTTPException(status_code=400, detail='unsupported interaction type')

    # Handle slash command and build response
    logger.info('Received command interaction: %s', payload.get('data', {}).get('name'))
    response = await handle_interaction_command(payload)
    return JSONResponse(response)
