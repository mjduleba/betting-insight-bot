from __future__ import annotations

import logging

from app.discord.parsing import get_option_map
from app.discord.responses import discord_message_response
from app.sports.mlb.formatters.game import build_mlb_game_embed
from app.sports.mlb.models import MlbGameRequest
from app.sports.mlb.normalization import normalize_team_name
from app.sports.mlb.services.game import build_game_snapshot

logger = logging.getLogger(__name__)


async def handle_mlb_game_command(payload: dict) -> dict[str, object]:
    '''
    Handle `/mlb game` from the raw Discord interaction payload.
    '''
    # Parse and validate the `/mlb game` request payload
    request = _parse_mlb_game_request(payload)
    if request is None:
        logger.warning('Missing required team input')
        return discord_message_response(
            content='`team` is required. Use `/mlb game team:<team>`.',
            ephemeral=True,
        )

    logger.info('Parsed team request: team=%s', request.team)

    # Build live game snapshot and Discord embed
    snapshot = await build_game_snapshot(team=request.team)
    embed = build_mlb_game_embed(snapshot)
    logger.info('Generated MLB embed for team request: %s', request.team)
    return discord_message_response(embeds=[embed])


def _parse_mlb_game_request(payload: dict) -> MlbGameRequest | None:
    '''
    Parse and validate the `/mlb game` payload into a request model.
    '''
    # Create clean option map for `/mlb game`
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
    if team == 'Unknown Team':
        return None
    return MlbGameRequest(team=team)
