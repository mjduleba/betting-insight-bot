from __future__ import annotations

import logging

from app.commands.registry import get_handler
from app.commands.types import CommandIdentity
from app.discord.parsing import extract_command_identity
from app.discord.responses import discord_message_response

logger = logging.getLogger(__name__)


def parse_command_identity(payload: dict) -> CommandIdentity:
    '''
    Parse the Discord interaction payload into a normalized command identity.
    '''
    sport, subcommand = extract_command_identity(payload)
    return CommandIdentity(sport=sport, subcommand=subcommand)


async def route_interaction_command(payload: dict) -> dict[str, object]:
    '''
    Route a Discord interaction payload through the shared command registry.
    '''
    identity = parse_command_identity(payload)
    handler = get_handler(identity.sport, identity.subcommand)
    if handler is None:
        logger.warning(
            'Unsupported command received: sport=%s subcommand=%s',
            identity.sport,
            identity.subcommand,
        )
        return _unsupported_command_response(identity)
    return await handler(payload)


def _unsupported_command_response(identity: CommandIdentity) -> dict[str, object]:
    '''
    Build a stable fallback response for unsupported commands.
    '''
    if identity.sport != 'mlb':
        return discord_message_response(
            content='Unsupported command. Only `/mlb game` is available right now.',
            ephemeral=True,
        )
    return discord_message_response(
        content='Unsupported MLB subcommand. Use `/mlb game team`.',
        ephemeral=True,
    )
