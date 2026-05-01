'''Service layer for composing MLB game snapshot data.'''

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import httpx

from app.api_clients import (
    fetch_pitcher_recent_starts,
    fetch_schedule_games,
    fetch_team_standing_snapshot,
)

logger = logging.getLogger(__name__)
EASTERN_TZ = ZoneInfo('America/New_York')


@dataclass(slots=True)
class GameSnapshot:
    '''
    Game snapshot DataClass.
    '''
    away_team: str
    home_team: str
    scheduled_time: datetime | None
    stadium: str
    weather: str
    team_form: dict[str, str]
    probable_pitchers: str
    recent_starts: dict[str, Any]
    lines: str


async def build_game_snapshot(team: str) -> GameSnapshot:
    '''
    Build a live MLB game snapshot with fallback values.

    Args:
        team (str): normalized team name

    Returns:
        GameSnapshot: snapshot used to build Discord embed
    '''
    # Build a short forward window to find today's or next game
    start_date = date.today()
    end_date = start_date + timedelta(days=1)
    logger.info(
        'Building game snapshot for team=%s window=%s..%s',
        team,
        start_date.isoformat(),
        end_date.isoformat(),
    )

    try:
        # Fetch schedule and select requested matchup from the window
        games = await fetch_schedule_games(start_date=start_date, end_date=end_date)
        selected_game = _select_requested_team_game(games, team=team)
        if selected_game is None:
            logger.warning('No scheduled game found for team: %s', team)
            return _build_fallback_snapshot(team=team)

        # Build live snapshot once the target game is found
        snapshot = await _build_snapshot_from_game(
            selected_game=selected_game,
        )
        logger.info('Built live game snapshot for team: %s', team)
        return snapshot
    except (httpx.HTTPError, ValueError) as exc:
        logger.exception('MLB API request failed, returning fallback snapshot')
        return _build_fallback_snapshot(team=team)


def _select_requested_team_game(games: list[dict], team: str) -> dict | None:
    '''
    Pick the earliest game matching the requested team.

    Args:
        games (list[dict]): flattened game payload list
        team (str): normalized team name

    Returns:
        dict | None: selected game payload
    '''
    # Collect games where the requested team is home or away
    matching_games = []
    for game in games:
        teams = game.get('teams') or {}
        away = (teams.get('away') or {}).get('team') or {}
        home = (teams.get('home') or {}).get('team') or {}
        if away.get('name') == team or home.get('name') == team:
            matching_games.append(game)

    if not matching_games:
        logger.debug('No matching games in schedule payload for %s', team)
        return None

    # Sort by gameDate for deterministic selection.
    matching_games.sort(key=lambda game: game.get('gameDate') or '')

    # Choose todays first game, if possible
    today_et = datetime.now(tz=EASTERN_TZ).date()
    todays_games = [
        game
        for game in matching_games
        if _extract_game_date_et(game) == today_et
    ]
    if todays_games:
        logger.debug(
            'Matched %s game(s); selected today-first game in ET',
            len(matching_games),
        )
        return todays_games[0]

    # Choose next available game, if no game today
    now_utc = datetime.now(tz=UTC)
    upcoming_games = []
    for game in matching_games:
        scheduled = _parse_game_datetime(game.get('gameDate'))
        if scheduled and scheduled >= now_utc:
            upcoming_games.append((scheduled, game))

    if upcoming_games:
        upcoming_games.sort(key=lambda item: item[0])
        logger.debug(
            'Matched %s game(s); selected next upcoming game',
            len(matching_games),
        )
        return upcoming_games[0][1]

    # Fallback to earliest scheduled game in query window
    logger.debug(
        'Matched %s game(s); no upcoming game found, selecting earliest in window',
        len(matching_games),
    )
    return matching_games[0]


async def _build_snapshot_from_game(
    selected_game: dict,
) -> GameSnapshot:
    '''
    Build snapshot from selected MLB schedule game payload.

    Args:
        selected_game (dict): selected game payload
    Returns:
        GameSnapshot: live snapshot populated from MLB schedule data
    '''
    teams = selected_game.get('teams') or {}
    away_data = teams.get('away') or {}
    home_data = teams.get('home') or {}
    away_team_info = away_data.get('team') or {}
    home_team_info = home_data.get('team') or {}
    away_team = away_team_info.get('name') or 'TBD'
    home_team = home_team_info.get('name') or 'TBD'
    venue = selected_game.get('venue') or {}

    # Parse key game attributes from schedule payload
    game_date_raw = selected_game.get('gameDate')
    game_date = _parse_game_datetime(game_date_raw)
    stadium = venue.get('name', 'TBD')

    # Retrieve team identifiers for record and form lookups
    away_team_id = away_team_info.get('id')
    home_team_id = home_team_info.get('id')

    # Retrieve team record and last-10 data with one standings call per team
    away_standing = await fetch_team_standing_snapshot(away_team_id)
    home_standing = await fetch_team_standing_snapshot(home_team_id)
    away_record = away_standing.get('record', 'TBD')
    home_record = home_standing.get('record', 'TBD')
    away_last10 = away_standing.get('last10', 'TBD')
    home_last10 = home_standing.get('last10', 'TBD')

    away_pitcher = ((away_data.get('probablePitcher') or {}).get('fullName')) or 'TBD'
    home_pitcher = ((home_data.get('probablePitcher') or {}).get('fullName')) or 'TBD'
    away_pitcher_id = ((away_data.get('probablePitcher') or {}).get('id'))
    home_pitcher_id = ((home_data.get('probablePitcher') or {}).get('id'))
    probable_pitchers = f'{away_team}: {away_pitcher} vs. {home_team}: {home_pitcher}'

    # Retrieve per-start data for each probable pitcher
    away_recent_starts = await fetch_pitcher_recent_starts(away_pitcher_id)
    home_recent_starts = await fetch_pitcher_recent_starts(home_pitcher_id)
    weather = _format_game_weather(selected_game.get('weather') or {})

    return GameSnapshot(
        away_team=away_team,
        home_team=home_team,
        scheduled_time=game_date,
        stadium=stadium,
        weather=weather,
        team_form={
            'away_team': away_team,
            'home_team': home_team,
            'away_record': away_record,
            'home_record': home_record,
            'away_last10': away_last10,
            'home_last10': home_last10,
        },
        probable_pitchers=probable_pitchers,
        # Store structured recent start rows for table formatting in embed
        recent_starts={
            'away_team': away_team,
            'home_team': home_team,
            'away_starts': away_recent_starts,
            'home_starts': home_recent_starts,
        },
        lines='Moneyline: TBD | Run Line: TBD | Total: TBD',
    )


def _build_fallback_snapshot(team: str) -> GameSnapshot:
    '''
    Build fallback snapshot when live API data is unavailable.

    Args:
        team (str): normalized team name

    Returns:
        GameSnapshot: fallback snapshot with placeholders
    '''
    logger.info('Building fallback game snapshot for team: %s', team)
    return GameSnapshot(
        away_team=team,
        home_team='TBD',
        scheduled_time=None,
        stadium='TBD',
        weather='TBD (weather unavailable)',
        team_form={
            'away_team': team,
            'home_team': 'Opponent',
            'away_record': 'TBD',
            'home_record': 'TBD',
            'away_last10': 'TBD',
            'home_last10': 'TBD',
        },
        probable_pitchers='No game found in the current 1-day lookup window.',
        # Keep empty table rows in fallback payload for consistent formatter input
        recent_starts={
            'away_team': team,
            'home_team': 'Opponent',
            'away_starts': [],
            'home_starts': [],
        },
        lines='Moneyline: TBD | Run Line: TBD | Total: TBD',
    )


def _parse_game_datetime(raw_game_date: str | None) -> datetime | None:
    '''
    Parse MLB gameDate string into timezone-aware datetime.

    Args:
        raw_game_date (str | None): raw game date string from MLB API

    Returns:
        datetime | None: parsed datetime value
    '''
    if not raw_game_date:
        logger.debug('Missing gameDate in schedule payload')
        return None

    # MLB gameDate is UTC ISO format with trailing Z
    normalized = raw_game_date.replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        logger.warning('Unable to parse gameDate value: %s', raw_game_date)
        return None
    if parsed.tzinfo is None:
        logger.debug('Parsed gameDate missing tzinfo; defaulting to UTC')
        return parsed.replace(tzinfo=UTC)
    return parsed


def _format_game_weather(weather_data: dict[str, Any]) -> str:
    '''
    Format weather hydration into a compact display line.

    Args:
        weather_data (dict[str, Any]): game weather object from schedule hydration

    Returns:
        str: formatted weather summary
    '''
    if not isinstance(weather_data, dict):
        return 'TBD (weather unavailable)'

    condition = weather_data.get('condition')
    temp = weather_data.get('temp')
    wind = weather_data.get('wind')

    parts: list[str] = []
    if isinstance(condition, str) and condition.strip():
        parts.append(condition.strip())
    if isinstance(temp, str) and temp.strip():
        parts.append(f'{temp.strip()}°F')
    elif isinstance(temp, int):
        parts.append(f'{temp}°F')
    if isinstance(wind, str) and wind.strip():
        parts.append(wind.strip())

    if not parts:
        return 'TBD (weather unavailable)'

    return ', '.join(parts)

def _extract_game_date_et(game: dict) -> date | None:
    '''
    Convert gameDate into an Eastern Time calendar date.

    Args:
        game (dict): MLB game payload

    Returns:
        date | None: ET date when parse succeeds
    '''
    scheduled = _parse_game_datetime(game.get('gameDate'))
    if scheduled is None:
        return None
    return scheduled.astimezone(EASTERN_TZ).date()
