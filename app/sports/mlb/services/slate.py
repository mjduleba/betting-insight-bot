from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import httpx

from app.shared.errors import UpstreamDataError
from app.sports.mlb.clients.stats_api import (
    fetch_pitcher_record,
    fetch_schedule_games,
    fetch_team_record,
)
from app.sports.mlb.models import MlbSlateGameRow, MlbSlateSnapshot

# Set up a logger for this module
logger = logging.getLogger(__name__)

# Set timezone to Eastern Time for consistent slate date handling
EASTERN_TZ = ZoneInfo('America/New_York')


async def build_slate_snapshot() -> MlbSlateSnapshot:
    '''
    Build snapshot for MLB slate by fetching current day's schedule and
    normalizing into unified slate game rows.

    Raises:
        UpstreamDataError: MLB slate data load failure

    Returns:
        MlbSlateSnapshot: Normalized snapshot of MLB slate for current board date
    '''
    # Store current date in EST for consistent slate building
    board_date = datetime.now(tz=EASTERN_TZ).date()
    logger.info('Building MLB slate snapshot for board_date=%s', board_date.isoformat())

    try:
        # Fetch scheduled games for board date
        games = await fetch_schedule_games(start_date=board_date, end_date=board_date)
        
        # Normalize each game into a slate row concurrently, then sort by scheduled time
        rows = await asyncio.gather(*[_build_slate_row(game) for game in games])
        rows.sort(key=_slate_sort_key)
        
        return MlbSlateSnapshot(
            board_date=board_date,
            total_game_count=len(rows),
            games=rows,
        )
    except (httpx.HTTPError, ValueError) as exc:
        logger.exception('MLB API request failed while building slate snapshot')
        raise UpstreamDataError('Failed to load MLB slate data.') from exc


async def _build_slate_row(game: dict) -> MlbSlateGameRow:
    '''
    Build normalized slate row for a single MLB game.

    Args:
        game (dict): Raw game data from MLB schedule API

    Returns:
        MlbSlateGameRow: Normalized slate row with extracted data
    '''
    # Retrieve team data and game status from game payload
    teams = game.get('teams') or {}
    away_data = teams.get('away') or {}
    home_data = teams.get('home') or {}
    away_team_info = away_data.get('team') or {}
    home_team_info = home_data.get('team') or {}
    status = game.get('status') or {}

    # Classify game status (upcoming, live, final, other)
    status_type = _classify_status_type(status)
    
    # Extact game date time and short status label for display
    scheduled_time = _parse_game_datetime(game.get('gameDate'))
    short_status_label = _extract_short_status_label(status, status_type)
    
    # Extract score and inning for live/final games
    away_score = _extract_score(away_data)
    home_score = _extract_score(home_data)
    inning_state_label = _extract_inning_state_label(game, status_type)

    # Create initial slate row with available data, placeholders used for upcoming values
    row = MlbSlateGameRow(
        status_type=status_type,
        away_team=away_team_info.get('name') or 'TBD',
        home_team=home_team_info.get('name') or 'TBD',
        away_team_record=None,
        home_team_record=None,
        scheduled_time=scheduled_time,
        short_status_label=short_status_label,
        away_score=away_score,
        home_score=home_score,
        inning_state_label=inning_state_label,
        away_probable_pitcher_name=_extract_probable_pitcher_name(away_data),
        home_probable_pitcher_name=_extract_probable_pitcher_name(home_data),
        away_probable_pitcher_record=None,
        home_probable_pitcher_record=None,
    )

    # Return early for in-progress/finalized games
    if status_type != 'upcoming':
        return row

    # Upcoming games retrieve team records and pitcher records
    away_team_record, home_team_record, away_pitcher_record, home_pitcher_record = await asyncio.gather(
        _fetch_display_team_record(away_team_info.get('id')),
        _fetch_display_team_record(home_team_info.get('id')),
        fetch_pitcher_record(_extract_probable_pitcher_id(away_data)),
        fetch_pitcher_record(_extract_probable_pitcher_id(home_data)),
    )

    # Append retrieved records to slate row and return
    return MlbSlateGameRow(
        status_type=row.status_type,
        away_team=row.away_team,
        home_team=row.home_team,
        away_team_record=away_team_record,
        home_team_record=home_team_record,
        scheduled_time=row.scheduled_time,
        short_status_label=row.short_status_label,
        away_score=row.away_score,
        home_score=row.home_score,
        inning_state_label=row.inning_state_label,
        away_probable_pitcher_name=row.away_probable_pitcher_name,
        home_probable_pitcher_name=row.home_probable_pitcher_name,
        away_probable_pitcher_record=away_pitcher_record,
        home_probable_pitcher_record=home_pitcher_record,
    )


async def _fetch_display_team_record(team_id: int | None) -> str | None:
    '''
    Extractor for team record.

    Args:
        team_id (int | None): team ID for record lookup

    Returns:
        str | None: formatted team record
    '''
    # Fetch team record for display and validate
    record = await fetch_team_record(team_id)
    if not record or record == 'TBD':
        return None
    return record


def _classify_status_type(status: dict) -> str:
    '''
    Classifier for MLB games into broad status types for display logic.

    Args:
        status (dict): Raw status data from MLB schedule API for a game

    Returns:
        str: Game status (upcoming, live, final, other) for display classification
    '''
    # Extract and normalize abstract and detailed game states
    abstract_state = str(status.get('abstractGameState') or '').strip().lower()
    detailed_state = str(status.get('detailedState') or '').strip().lower()

    # Classify game status into broad categories for display logic
    if abstract_state in {'preview', 'pregame'}:
        return 'upcoming'
    if detailed_state in {'scheduled', 'pre-game', 'warmup'}:
        return 'upcoming'
    if abstract_state == 'live':
        return 'live'
    if abstract_state == 'final':
        return 'final'
    return 'other'


def _extract_short_status_label(status: dict, status_type: str) -> str:
    '''
    Extractor for short status label for MLB games, prioritizing detailed 
    state when available.

    Args:
        status (dict): Raw status data from MLB schedule API for a game
        status_type (str): Broad status type for game (upcoming, live, final, other)

    Returns:
        str: Short status label for display
    '''
    # Extract and normalize abstract and detailed game states for short status label
    detailed_state = str(status.get('detailedState') or '').strip()
    abstract_state = str(status.get('abstractGameState') or '').strip()

    # Prioritize short status label based on game status type and available data, with fallbacks
    if status_type == 'final':
        return 'Final'
    if detailed_state:
        return detailed_state
    if abstract_state:
        return abstract_state
    return 'Status TBD'


def _extract_inning_state_label(game: dict, status_type: str) -> str | None:
    '''
    Inning state label extractor for live MLB games, returns None for non-live games.

    Args:
        game (dict): Raw game data from MLB schedule API
        status_type (str): Status type of the game (upcoming, live, final, other)

    Returns:
        str | None: Formatted inning state label for live games.
    '''
    # Check if game is live, return None otherwise
    if status_type != 'live':
        return None

    # Extract inning half and ordinal from linescore
    linescore = game.get('linescore') or {}
    inning_half = str(linescore.get('inningHalf') or '').strip()
    inning_ordinal = str(linescore.get('currentInningOrdinal') or '').strip()

    # Format inning state based on available data, return None if missing
    if inning_half and inning_ordinal:
        return f'{inning_half} {inning_ordinal}'
    if inning_ordinal:
        return inning_ordinal
    return None


def _extract_score(team_data: dict) -> int | None:
    '''
    Extractor for team score from schedule team data.

    Args:
        team_data (dict): Raw team data from MLB schedule API for a game

    Returns:
        int | None: Team score if available and valid, otherwise None
    '''
    # Extract score from team data and validate
    score = team_data.get('score')
    if isinstance(score, int):
        return score
    return None


def _extract_probable_pitcher_name(team_data: dict) -> str | None:
    '''
    Extractor for probable pitcher name from schedule team data.

    Args:
        team_data (dict): Raw team data from MLB schedule API for a game

    Returns:
        str | None: Probable pitcher full name if available and valid, otherwise None
    '''
    # Extractor for probable pitcher name from schedule team data.
    probable_pitcher = team_data.get('probablePitcher') or {}
    name = probable_pitcher.get('fullName')
    
    # Validate and return normalized name, otherwise return None
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def _extract_probable_pitcher_id(team_data: dict) -> int | None:
    '''
    Extractor for probable pitcher ID from schedule team data.

    Args:
        team_data (dict): Raw team data from MLB schedule API for a game

    Returns:
        int | None: Probable pitcher ID if available and valid, otherwise None
    '''
    # Extractor for probable pitcher ID from schedule team data
    probable_pitcher = team_data.get('probablePitcher') or {}
    pitcher_id = probable_pitcher.get('id')
    
    # Validate and return pitcher ID if it's an integer, otherwise return None
    if isinstance(pitcher_id, int):
        return pitcher_id
    return None


def _parse_game_datetime(raw_game_date: str | None) -> datetime | None:
    '''
    Parse MLB gameDate into a timezone-aware datetime.

    Args:
        raw_game_date (str | None): raw MLB schedule gameDate string

    Returns:
        datetime | None: parsed timezone-aware scheduled datetime
    '''
    # Validate raw gameDate value
    if not raw_game_date:
        return None

    # Normalize trailing Z into an ISO-compatible UTC offset
    normalized = raw_game_date.replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        logger.warning('Unable to parse slate gameDate value: %s', raw_game_date)
        return None

    # Default naive parsed values to UTC
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _slate_sort_key(row: MlbSlateGameRow) -> tuple[int, datetime]:
    '''
    Build a stable slate sort key using scheduled first pitch.

    Args:
        row (MlbSlateGameRow): normalized slate row

    Returns:
        tuple[int, datetime]: sort key with missing times pushed last
    '''
    # Push rows with unknown times to the end of the slate
    if row.scheduled_time is None:
        return (1, datetime.max.replace(tzinfo=UTC))

    # Normalize scheduled times into UTC for stable ordering
    return (0, row.scheduled_time.astimezone(UTC))
