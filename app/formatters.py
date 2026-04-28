from __future__ import annotations

import logging

from app.helpers import format_game_time
from app.services import GameSnapshot

logger = logging.getLogger(__name__)


def build_mlb_game_embed(snapshot: GameSnapshot) -> dict:
    '''
    Takes MLB snapshot data and turns it into a Discord embed ready
    to be returned to the user.

    Args:
        snapshot (GameSnapshot): snapshot of data for requested MLB game

    Returns:
        dict: Discord embed to be included in message
    '''
    # Build matchup title for the primary embed header
    matchup = f'{snapshot.away_team} at {snapshot.home_team}'
    logger.info('Formatting MLB game embed for matchup: %s', matchup)

    # Build embed fields in the MVP response order
    return {
        'title': matchup,
        'description': 'Live MLB matchup snapshot (weather, lines, and recaps expanding in next milestones).',
        'color': 0x0B6E4F,
        'fields': [
            {
                'name': 'Game Info',
                'value': (
                    f'Time: {format_game_time(snapshot.scheduled_time)}\n'
                    f'Venue: {snapshot.stadium}\n'
                    f'Location: {snapshot.city}'
                ),
                'inline': False,
            },
            {
                'name': 'Weather',
                'value': snapshot.weather,
                'inline': False,
            },
            {
                'name': 'Probable Pitchers',
                'value': snapshot.probable_pitchers,
                'inline': False,
            },
            {
                'name': 'Recent Starts',
                'value': snapshot.recent_starts,
                'inline': False,
            },
            {
                'name': 'Lines',
                'value': snapshot.lines,
                'inline': False,
            },
        ],
        'footer': {
            'text': 'Powered by MLB Stats API for matchup and probable starter data.',
        },
    }
