from __future__ import annotations

import logging

PING_INTERACTION_TYPE = 1
CHANNEL_MESSAGE_WITH_SOURCE = 4
EPHEMERAL_FLAG = 1 << 6

logger = logging.getLogger(__name__)


def discord_ping_response() -> dict:
    '''
    Build required ping acknowledgement payload.

    Returns:
        dict: Discord ping response payload
    '''
    logger.debug('Building Discord ping response payload')
    return {'type': PING_INTERACTION_TYPE}


def discord_message_response(
    content: str | None = None,
    embeds: list[dict] | None = None,
    ephemeral: bool = False,
) -> dict:
    '''
    Build slash-command response payload for Discord.

    Args:
        content (str | None): plain text response content
        embeds (list[dict] | None): embed objects for rich responses
        ephemeral (bool): whether response should be hidden from channel

    Returns:
        dict: Discord channel message response payload
    '''
    data: dict[str, object] = {}
    if content:
        data['content'] = content
    if embeds:
        data['embeds'] = embeds
    if ephemeral:
        data['flags'] = EPHEMERAL_FLAG

    logger.debug(
        'Building Discord message response: has_content=%s has_embeds=%s ephemeral=%s',
        bool(content),
        bool(embeds),
        ephemeral,
    )
    return {'type': CHANNEL_MESSAGE_WITH_SOURCE, 'data': data}
