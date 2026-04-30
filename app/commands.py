from __future__ import annotations

import logging

from app.discord_utils import discord_message_response, extract_command_identity
from app.formatters import build_mlb_game_embed
from app.helpers import get_option_map, normalize_team_name
from app.services import build_game_snapshot

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

    # Create clean option map for /mode
    subcommand = next(
        (
            option
            for option in payload.get('data', {}).get('options', [])
            if option.get('name') == 'game'
        ),
        None,
    )
    option_map = get_option_map(subcommand.get('options') if subcommand else None)

    # Normalize requested team name
    team = normalize_team_name(str(option_map.get('team', '')))
    logger.info('Parsed team request: team=%s', team)

    # Validate team input
    if team == 'Unknown Team':
        logger.warning('Missing required team input')
        return discord_message_response(
            content='`team` is required. Use `/mlb game team:<team>`.',
            ephemeral=True,
        )

    # Build live game snapshot and Discord embed
    snapshot = await build_game_snapshot(team=team)
    embed = build_mlb_game_embed(snapshot)
    logger.info('Generated MLB embed for team request: %s', team)
    return discord_message_response(embeds=[embed])
