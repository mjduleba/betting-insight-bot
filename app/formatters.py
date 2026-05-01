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
                    f'Dome: {snapshot.city}'
                ),
                'inline': False,
            },
            {
                'name': 'Weather',
                'value': snapshot.weather,
                'inline': False,
            },
            {
                'name': 'Team Form',
                'value': _format_team_form(snapshot),
                'inline': False,
            },
            {
                'name': 'Probable Pitchers',
                'value': snapshot.probable_pitchers,
                'inline': False,
            },
            {
                'name': 'Recent Starts',
                'value': _format_recent_starts_table(snapshot),
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


def _format_recent_starts_table(snapshot: GameSnapshot) -> str:
    '''
    Render recent pitcher starts as compact table-style text blocks.

    Args:
        snapshot (GameSnapshot): snapshot with structured recent starts data

    Returns:
        str: formatted recent starts block
    '''
    # Parse structured recent starts data from snapshot
    data = snapshot.recent_starts or {}
    away_team = str(data.get('away_team') or snapshot.away_team)
    home_team = str(data.get('home_team') or snapshot.home_team)
    away_starts = data.get('away_starts') or []
    home_starts = data.get('home_starts') or []

    # Build table block for each team
    away_block = _render_pitcher_start_block(away_team, away_starts)
    home_block = _render_pitcher_start_block(home_team, home_starts)
    return f'{away_block}\n\n{home_block}'


def _format_team_form(snapshot: GameSnapshot) -> str:
    '''
    Render team record and last-10 form lines.

    Args:
        snapshot (GameSnapshot): snapshot with structured team form data

    Returns:
        str: formatted team form block
    '''
    # Parse structured team form data from snapshot
    data = snapshot.team_form or {}
    away_team = str(data.get('away_team') or snapshot.away_team)
    home_team = str(data.get('home_team') or snapshot.home_team)
    away_record = str(data.get('away_record') or 'TBD')
    home_record = str(data.get('home_record') or 'TBD')
    away_last10 = str(data.get('away_last10') or 'TBD')
    home_last10 = str(data.get('home_last10') or 'TBD')

    # Build fixed-width table rows for stable Discord alignment
    header = f'{"TEAM".ljust(20)} {"RECORD".ljust(6)} LAST10'
    row_away = f'{away_team[:20].ljust(20)} {away_record.ljust(6)} {away_last10}'
    row_home = f'{home_team[:20].ljust(20)} {home_record.ljust(6)} {home_last10}'
    table = '\n'.join([header, row_away, row_home])

    # Return monospaced table for consistent column rendering
    return f'```text\n{table}\n```'


def _render_pitcher_start_block(team_name: str, starts: list[dict]) -> str:
    '''
    Render a single pitcher's recent starts as a monospaced table.

    Args:
        team_name (str): team label
        starts (list[dict]): list of recent start rows

    Returns:
        str: formatted block
    '''
    # Validate starts before building table block
    if not starts:
        return f'**{team_name}**\nNo recent starts available.'

    # Build table headers
    header = 'DATE       OPP           IP   ER  K'
    divider = '---------- ------------- ---- --- --'
    rows = []
    
    # Build each table row from start data
    for start in starts[:3]:
        date_value = str(start.get('date', 'TBD'))[:10].ljust(10)
        opp_value = str(start.get('opp', 'TBD'))[:13].ljust(13)
        ip_value = str(start.get('ip', '0.0')).rjust(4)
        er_value = str(start.get('er', '0')).rjust(3)
        k_value = str(start.get('k', '0')).rjust(2)
        rows.append(f'{date_value} {opp_value} {ip_value} {er_value} {k_value}')

    # Return monospaced table for Discord embed
    table = '\n'.join([header, divider, *rows])
    return f'**{team_name}**\n```text\n{table}\n```'
