from __future__ import annotations

import logging

PING_INTERACTION_TYPE = 1
APPLICATION_COMMAND_TYPE = 2
SUBCOMMAND_OPTION_TYPE = 1

logger = logging.getLogger(__name__)


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


def extract_command_identity(payload: dict) -> tuple[str | None, str | None]:
    '''
    Extract top-level command and subcommand names from interaction payload.

    Args:
        payload (dict): Discord interaction payload

    Returns:
        tuple[str | None, str | None]: command and subcommand names
    '''
    data = payload.get('data') or {}
    command_name = data.get('name')
    subcommand_name = None

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
