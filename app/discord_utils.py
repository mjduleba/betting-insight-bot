from __future__ import annotations

import logging

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

# Initialize interaction types
PING_INTERACTION_TYPE = 1
APPLICATION_COMMAND_TYPE = 2
CHANNEL_MESSAGE_WITH_SOURCE = 4
EPHEMERAL_FLAG = 1 << 6
SUBCOMMAND_OPTION_TYPE = 1

# Create logger
logger = logging.getLogger(__name__)


def verify_discord_signature(
    public_key: str,
    signature: str | None,
    timestamp: str | None,
    body: bytes,
) -> bool:
    '''
    Verify Discord request signature with Ed25519.

    Args:
        public_key (str): Discord application public key
        signature (str | None): Discord request signature header
        timestamp (str | None): Discord request timestamp header
        body (bytes): raw request body

    Returns:
        bool: True if signature is valid, else False
    '''
    # Return False if required headers are missing
    if not signature or not timestamp:
        logger.warning('Missing Discord signature headers')
        return False

    try:
        # Build verify key and validate signature
        verify_key = VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(timestamp.encode('utf-8') + body, bytes.fromhex(signature))
        logger.debug('Discord signature verification passed')
    except (BadSignatureError, ValueError):
        logger.warning('Discord signature verification failed')
        return False
    return True


def is_ping_interaction(payload: dict) -> bool:
    '''
    Detect if an interaction payload is a Discord ping.

    Args:
        payload (dict): Discord interaction payload

    Returns:
        bool: True if interaction type is ping, else False
    '''
    is_ping = payload.get('type') == PING_INTERACTION_TYPE
    if is_ping:
        logger.info('Ping interaction received')
    return is_ping


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
    # Construct Discord response data object
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


def extract_command_identity(payload: dict) -> tuple[str | None, str | None]:
    '''
    Extract top-level command and subcommand names from interaction payload.

    Args:
        payload (dict): Discord interaction payload

    Returns:
        tuple[str | None, str | None]: command and subcommand names
    '''
    # Parse command metadata
    data = payload.get('data') or {}
    command_name = data.get('name')
    subcommand_name = None

    # Find first subcommand from options list
    for option in data.get('options', []):
        if option.get('type') == SUBCOMMAND_OPTION_TYPE:
            subcommand_name = option.get('name')
            break

    logger.info(
        'Extracted command identity: command=%s subcommand=%s',
        command_name,
        subcommand_name,
    )
    return command_name, subcommand_name
