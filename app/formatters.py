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
        'description': 'Live MLB matchup snapshot (game info, team/pitching stats, and beting markets).',
        'color': 0x0B6E4F,
        'fields': [
            {
                'name': 'Game Info & Weather',
                'value': (
                    f'Time: {format_game_time(snapshot.scheduled_time)}\n'
                    f'Venue: {snapshot.stadium}\n'
                    f'Weather: {snapshot.weather}'
                ),
                'inline': False,
            },
            {
                'name': 'Team Form',
                'value': _format_team_form(snapshot),
                'inline': False,
            },
            {
                'name': 'Starting Pitchers',
                'value': _format_probable_pitchers_block(snapshot),
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
    away_pitcher = str(data.get('away_pitcher') or 'TBD')
    home_pitcher = str(data.get('home_pitcher') or 'TBD')
    if away_pitcher == 'TBD' or home_pitcher == 'TBD':
        parsed_away, parsed_home = _parse_probable_pitcher_names(snapshot.probable_pitchers)
        if away_pitcher == 'TBD':
            away_pitcher = parsed_away
        if home_pitcher == 'TBD':
            home_pitcher = parsed_home
    away_starts = data.get('away_starts') or []
    home_starts = data.get('home_starts') or []

    # Build table block for each team
    away_block = _render_pitcher_start_block(away_pitcher, away_team, away_starts)
    home_block = _render_pitcher_start_block(home_pitcher, home_team, home_starts)
    return f'{away_block}\n{home_block}'


def _format_probable_pitchers_block(snapshot: GameSnapshot) -> str:
    '''
    Render probable pitchers and recent starts in one combined block.

    Args:
        snapshot (GameSnapshot): snapshot with pitcher and recent starts data

    Returns:
        str: formatted probable pitchers block
    '''
    return _format_recent_starts_table(snapshot)


def _parse_probable_pitcher_names(raw_value: str | None) -> tuple[str, str]:
    '''
    Parse probable pitcher names from the summary string.

    Args:
        raw_value (str | None): probable pitchers summary text

    Returns:
        tuple[str, str]: away and home pitcher names
    '''
    if not isinstance(raw_value, str) or ' vs. ' not in raw_value:
        return 'TBD', 'TBD'

    away_part, home_part = raw_value.split(' vs. ', 1)
    away_name = away_part.split(':', 1)[1].strip() if ':' in away_part else 'TBD'
    home_name = home_part.split(':', 1)[1].strip() if ':' in home_part else 'TBD'
    return away_name or 'TBD', home_name or 'TBD'


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


def _render_pitcher_start_block(pitcher_name: str, team_name: str, starts: list[dict]) -> str:
    '''
    Render a single pitcher's recent starts as a monospaced table.

    Args:
        pitcher_name (str): pitcher label
        team_name (str): team label
        starts (list[dict]): list of recent start rows

    Returns:
        str: formatted block
    '''
    # Validate starts before building table block
    if not starts:
        return f'**{pitcher_name} - {team_name}**\nNo recent starts available.'

    # Build table headers
    header = 'DATE       OPP           W/L  IP   H  ER  K'
    divider = '---------- ------------- ---  ---- -- --- --'
    rows = []
    
    # Build each table row from start data
    for start in starts[:3]:
        date_value = str(start.get('date', 'TBD'))[:10].ljust(10)
        opp_value = str(start.get('opp', 'TBD'))[:13].ljust(13)
        wl_value = str(start.get('wl', '-')).rjust(3)
        ip_value = str(start.get('ip', '0.0')).rjust(4)
        h_value = str(start.get('h', '0')).rjust(2)
        er_value = str(start.get('er', '0')).rjust(3)
        k_value = str(start.get('k', '0')).rjust(2)
        rows.append(f'{date_value} {opp_value} {wl_value}  {ip_value} {h_value} {er_value} {k_value}')

    # Return monospaced table for Discord embed
    table = '\n'.join([header, divider, *rows])
    return f'**{pitcher_name} - {team_name}**\n```text\n{table}\n```'
