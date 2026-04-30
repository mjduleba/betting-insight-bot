'''Service layer for composing MLB game snapshot data.'''

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import httpx

from app.api_clients import fetch_schedule_games, fetch_venue_city

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GameSnapshot:
    '''
    Game snapshot DataClass.
    '''
    away_team: str
    home_team: str
    scheduled_time: datetime | None
    stadium: str
    city: str
    weather: str
    probable_pitchers: str
    recent_starts: str
    lines: str


async def build_game_snapshot(team: str) -> GameSnapshot:
    '''
    Build a live MLB game snapshot with fallback values.

    Args:
        team (str): normalized team name

    Returns:
        GameSnapshot: snapshot used to build Discord embed
    '''
    # Build a short forward window to find the next scheduled matchup
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

    # If multiple games match in range, pick the earliest one
    matching_games.sort(key=lambda game: game.get('gameDate') or '')
    logger.debug('Matched %s game(s); selecting earliest gameDate', len(matching_games))
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
    away_team = ((away_data.get('team') or {}).get('name')) or 'TBD'
    home_team = ((home_data.get('team') or {}).get('name')) or 'TBD'
    venue = selected_game.get('venue') or {}

    # Parse key game attributes from schedule payload
    game_date_raw = selected_game.get('gameDate')
    game_date = _parse_game_datetime(game_date_raw)
    stadium = venue.get('name', 'TBD')

    venue_id = venue.get('id')
    city = 'TBD'
    if isinstance(venue_id, int):
        # Enrich city from venue endpoint when available
        city = await fetch_venue_city(venue_id) or 'TBD'

    away_pitcher = ((away_data.get('probablePitcher') or {}).get('fullName')) or 'TBD'
    home_pitcher = ((home_data.get('probablePitcher') or {}).get('fullName')) or 'TBD'
    probable_pitchers = f'{away_team}: {away_pitcher} vs. {home_team}: {home_pitcher}'

    return GameSnapshot(
        away_team=away_team,
        home_team=home_team,
        scheduled_time=game_date,
        stadium=stadium,
        city=city,
        weather='TBD (weather integration pending)',
        probable_pitchers=probable_pitchers,
        recent_starts=(
            f'{away_team}: Recent starts integration pending\n'
            f'{home_team}: Recent starts integration pending'
        ),
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
        city='TBD',
        weather='TBD (weather integration pending)',
        probable_pitchers=f'{team}: TBD vs. TBD: TBD',
        recent_starts=(
            f'{team}: Recent starts integration pending\n'
            'TBD: Recent starts integration pending'
        ),
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
