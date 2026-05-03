from __future__ import annotations

import logging

from app.discord.responses import discord_message_response
from app.shared.errors import UpstreamDataError
from app.sports.mlb.formatters.slate import build_mlb_slate_embeds
from app.sports.mlb.models import MlbSlateRequest
from app.sports.mlb.services.slate import build_slate_snapshot

logger = logging.getLogger(__name__)


async def handle_mlb_slate_command(payload: dict) -> dict[str, object]:
    '''
    Handles the `/mlb slate` command by building a snapshot of the current 
    slate and returning one or more embeds.

    Args:
        payload (dict): raw Discord interaction payload

    Returns:
        dict[str, object]: Discord message response with embeds for the current MLB slate
    '''
    # Parse the no-option `/mlb slate` request payload
    request = _parse_mlb_slate_request(payload)
    logger.info('Parsed MLB slate request: %s', request)

    try:
        # Build the current slate snapshot and render one or more embeds
        snapshot = await build_slate_snapshot()
    except UpstreamDataError:
        logger.exception('Unable to build MLB slate snapshot from upstream data')
        return discord_message_response(
            content='Unable to load the MLB slate right now. Please try again shortly.',
            ephemeral=True,
        )

    # Build /mlb slate embed based on snapshot
    embeds = build_mlb_slate_embeds(snapshot)
    logger.info('Generated %s MLB slate embed(s)', len(embeds))
    
    return discord_message_response(embeds=embeds)


def _parse_mlb_slate_request(payload: dict) -> MlbSlateRequest:
    '''
    Parse the `/mlb slate` payload into a request model.

    Args:
        payload (dict): raw Discord interaction payload

    Returns:
        MlbSlateRequest: parsed slate request model
    '''
    # Accept the payload shape for future extensibility, even with no v1 options
    _ = payload
    return MlbSlateRequest()
