from __future__ import annotations

import logging
from datetime import date
from typing import Any

import httpx

from app.config import get_settings

# Create global logger
logger = logging.getLogger(__name__)

# MLB API Base URL
MLB_STATS_API_BASE_URL = get_settings().mlb_stats_api_base_url

async def fetch_schedule_games(start_date: date, end_date: date) -> list[dict]:
    '''
    Fetch MLB schedule games in a date range.

    Args:
        start_date (date): first date in schedule window
        end_date (date): last date in schedule window

    Returns:
        list[dict]: flattened list of game payloads
    '''
    # Store URL for schedule call
    url = f'{MLB_STATS_API_BASE_URL}/schedule'
    params = {
        'sportId': 1,
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
    }

    logger.info(
        'Fetching MLB schedule: start_date=%s end_date=%s',
        params['startDate'],
        params['endDate'],
    )

    # Send async GET request for /schedule endpoint
    payload = await _fetch_json(url, params=params)

    # Parse games from response
    games: list[dict] = []
    for schedule_date in payload.get('dates', []):
        games.extend(schedule_date.get('games', []))

    logger.info('Fetched %s MLB games from schedule endpoint', len(games))
    return games


async def fetch_venue_city(venue_id: int | None) -> str | None:
    '''
    Fetch venue city by venue id.

    Args:
        venue_id (int | None): MLB venue identifier

    Returns:
        str | None: city name when available
    '''
    # Validate venue identifier
    if venue_id is None:
        return None

    # Store URL for venues request
    url = f'{MLB_STATS_API_BASE_URL}/venues/{venue_id}'
    logger.debug('Fetching venue details: venue_id=%s', venue_id)

    # Send async GET request for /venues endpoint
    payload = await _fetch_json(url)

    # Validate response
    venues = payload.get('venues', [])
    if not venues:
        return None

    # Parse venues response and return
    location = venues[0].get('location') or {}
    return location.get('city')


async def fetch_team_record(team_id: int | None) -> str | None:
    '''
    Fetch team wins-losses record by team id.

    Args:
        team_id (int | None): MLB team identifier

    Returns:
        str | None: formatted record like "12-8"
    '''
    # Validate team ID
    if team_id is None:
        return None

    # Create URL to fetch team record based on ID
    url = f'{MLB_STATS_API_BASE_URL}/teams/{team_id}'
    
    # Create parameters for API request body
    params = {'season': date.today().year}
    logger.debug('Fetching team record: team_id=%s', team_id)

    # Send request for team record data
    payload = await _fetch_json(url, params=params)
    
    # Validate response
    teams = payload.get('teams') or []
    if not teams:
        return None

    # Extract record, wins, and losses
    record = (teams[0].get('record') or {})
    wins = record.get('wins')
    losses = record.get('losses')
    
    # Validate wins and losses data types
    if isinstance(wins, int) and isinstance(losses, int):
        return f'{wins}-{losses}'
    return None


async def fetch_team_last10(team_id: int | None) -> str | None:
    '''
    Fetch team last-10 record from standings records endpoint.

    Args:
        team_id (int | None): MLB team identifier

    Returns:
        str | None: formatted last-10 record like "7-3"
    '''
    # Validate team ID
    if team_id is None:
        return None

    # Create URL for team standings
    url = f'{MLB_STATS_API_BASE_URL}/standings'
    
    # Create parameters for API request body
    params = {'leagueId': '103,104', 'season': date.today().year, 'standingsTypes': 'regularSeason'}
    logger.debug('Fetching team last-10 record: team_id=%s', team_id)

    # Send request and store payload
    payload = await _fetch_json(url, params=params)
    
    # Store recors from response
    records = payload.get('records') or []
    
    # Parse wins and loss from records response
    for group in records:
        for team_record in group.get('teamRecords') or []:
            team = team_record.get('team') or {}
            if team.get('id') != team_id:
                continue

            records_split = team_record.get('records') or {}
            split_records = records_split.get('splitRecords') or []
            for split in split_records:
                if split.get('type') != 'lastTen':
                    continue

                wins = split.get('wins')
                losses = split.get('losses')
                if isinstance(wins, int) and isinstance(losses, int):
                    return f'{wins}-{losses}'
    return None


async def fetch_pitcher_recent_form(pitcher_id: int | None, starts: int = 3) -> str | None:
    '''
    Fetch recent starting pitcher form summary from game log stats.

    Args:
        pitcher_id (int | None): MLB player identifier
        starts (int): number of recent starts to summarize

    Returns:
        str | None: formatted summary string
    '''
    # Validate pitcher ID
    if pitcher_id is None:
        return None

    # Create URL for pitcher stats request
    url = f'{MLB_STATS_API_BASE_URL}/people/{pitcher_id}/stats'
    
    # Store parameters for API request body
    params = {'stats': 'gameLog', 'group': 'pitching'}
    logger.debug('Fetching pitcher recent form: pitcher_id=%s starts=%s', pitcher_id, starts)

    # Send request and store payload
    payload = await _fetch_json(url, params=params)
    
    # Extract recent starts, default to 3
    starts_list = _extract_recent_starts(payload=payload, max_starts=starts)
    
    # Validate recent starts
    if not starts_list:
        return None

    return _format_pitcher_recent_form(starts_list)


async def fetch_pitcher_recent_starts(
    pitcher_id: int | None,
    starts: int = 3,
) -> list[dict[str, str]]:
    '''
    Fetch a pitcher's recent starts as row data for table formatting.

    Args:
        pitcher_id (int | None): MLB player identifier
        starts (int): number of recent starts

    Returns:
        list[dict[str, str]]: recent start rows
    '''
    # Validate pitcher ID
    if pitcher_id is None:
        return []

    # Create URL for pitcher stats request
    url = f'{MLB_STATS_API_BASE_URL}/people/{pitcher_id}/stats'
    
    # Store parameters for API request body
    params = {'stats': 'gameLog', 'group': 'pitching'}
    logger.debug('Fetching pitcher recent starts: pitcher_id=%s starts=%s', pitcher_id, starts)

    # Send request and store payload
    payload = await _fetch_json(url, params=params)
    
    # Extract and format recent starts into display rows
    starts_list = _extract_recent_starts(payload=payload, max_starts=starts)
    return _format_recent_start_rows(starts_list)


def _extract_recent_starts(payload: dict[str, Any], max_starts: int) -> list[dict[str, Any]]:
    '''
    Extract recent starts from gameLog splits.

    Args:
        payload (dict[str, Any]): /people/{id}/stats response
        max_starts (int): max starts to return

    Returns:
        list[dict[str, Any]]: filtered start splits, newest first
    '''
    # Retrieve stats list and validate
    stats = payload.get('stats') or []
    if not stats:
        return []

    # Retreive splits from stats section
    splits = stats[0].get('splits') or []
    if not splits:
        return []

    # Retreive starts from split and sort by date
    only_starts = [split for split in splits if (split.get('stat') or {}).get('gamesStarted') == 1]
    only_starts.sort(key=lambda split: split.get('date') or '', reverse=True)
    return only_starts[:max_starts]


def _format_pitcher_recent_form(starts: list[dict[str, Any]]) -> str | None:
    '''
    Format compact recent starts pitching summary.

    Args:
        starts (list[dict[str, Any]]): recent start split entries

    Returns:
        str | None: summary like "Last 3 GS: 17.1 IP, 5 ER, 19 K"
    '''
    # Validate starts
    if not starts:
        return None

    # Create totals for major statistical categories
    total_outs = 0
    total_er = 0
    total_so = 0
    counted = 0

    # Loop through starts
    for start in starts:
        # Store each stat category
        stat = start.get('stat') or {}
        outs = stat.get('outs')
        er = stat.get('earnedRuns')
        so = stat.get('strikeOuts')
        
        # Validate outs category
        if not isinstance(outs, int):
            continue
        
        # Add to totals
        total_outs += outs
        total_er += er if isinstance(er, int) else 0
        total_so += so if isinstance(so, int) else 0
        counted += 1

    # Validate at least one start
    if counted == 0:
        return None

    # 
    innings = f'{total_outs // 3}.{total_outs % 3}'
    return f'Last {counted} GS: {innings} IP, {total_er} ER, {total_so} K'


def _format_recent_start_rows(starts: list[dict[str, Any]]) -> list[dict[str, str]]:
    '''
    Convert raw start splits into simple row dictionaries.

    Args:
        starts (list[dict[str, Any]]): recent start split entries

    Returns:
        list[dict[str, str]]: rows ready for display
    '''
    # Create output row collection
    rows: list[dict[str, str]] = []
    
    # Loop through starts and build display rows
    for start in starts:
        # Store each stat category
        stat = start.get('stat') or {}
        outs = stat.get('outs')
        er = stat.get('earnedRuns')
        so = stat.get('strikeOuts')
        
        # Validate outs category
        if not isinstance(outs, int):
            continue

        # Store opponent and append formatted start row
        opponent = (start.get('opponent') or {}).get('name') or 'TBD'
        rows.append(
            {
                'date': str(start.get('date') or 'TBD'),
                'opp': str(opponent),
                'ip': f'{outs // 3}.{outs % 3}',
                'er': str(er if isinstance(er, int) else 0),
                'k': str(so if isinstance(so, int) else 0),
            }
        )
    
    # Return parsed rows
    return rows


async def _fetch_json(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    '''
    Send an async GET request and return decoded JSON.

    Args:
        url (str): endpoint URL
        params (dict[str, Any] | None): query params

    Returns:
        dict[str, Any]: JSON payload
    '''
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
