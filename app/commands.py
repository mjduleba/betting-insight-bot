from __future__ import annotations

import logging

from app.discord_utils import discord_message_response, extract_command_identity
from app.sports.mlb.commands.game import handle_mlb_game_command

logger = logging.getLogger(__name__)


async def handle_interaction_command(payload: dict) -> dict:
    '''
    Slash-command router function. 

    Args:
        payload (dict): 

    Returns:
        dict: 
    '''
    # Take command payload and extract command and subcommand
    command_name, subcommand_name = extract_command_identity(payload)
    logger.info(
        'Routing interaction command: command=%s subcommand=%s',
        command_name,
        subcommand_name,
    )

    # Validate sport command is available
    if command_name != 'mlb':
        logger.warning('Unsupported command received: %s', command_name)
        return discord_message_response(
            content='Unsupported command. Only `/mlb game` is available right now.',
            ephemeral=True,
        )

    # Validate sub command for sport is available
    if subcommand_name != 'game':
        logger.warning('Unsupported MLB subcommand received: %s', subcommand_name)
        return discord_message_response(
            content='Unsupported MLB subcommand. Use `/mlb game team`.',
            ephemeral=True,
        )

    return await handle_mlb_game_command(payload)
