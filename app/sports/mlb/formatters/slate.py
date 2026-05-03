from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.sports.mlb.models import MlbSlateGameRow

EASTERN_TZ = ZoneInfo('America/New_York')


def format_mlb_slate_row(row: MlbSlateGameRow) -> str:
    '''
    Render one MLB slate row according to its game status.

    Args:
        row (MlbSlateGameRow): normalized slate row

    Returns:
        str: display string for one slate game
    '''
    # Route row rendering through the unified status type
    if row.status_type == 'upcoming':
        return _format_upcoming_row(row)
    if row.status_type == 'live':
        return _format_live_row(row)
    if row.status_type == 'final':
        return _format_final_row(row)
    return _format_other_row(row)


def _format_upcoming_row(row: MlbSlateGameRow) -> str:
    '''
    Render one upcoming MLB slate row.

    Args:
        row (MlbSlateGameRow): normalized upcoming slate row

    Returns:
        str: display string for one upcoming game
    '''
    # Build the left-side scheduled time fragment in ET
    time_fragment = _format_short_game_time(row.scheduled_time)

    # Build matchup fragment with team records when available
    matchup_fragment = (
        f'{_format_team_with_record(row.away_team, row.away_team_record)} '
        f'at {_format_team_with_record(row.home_team, row.home_team_record)}'
    )

    # Append probable pitchers only when at least one pitcher is present
    pitcher_fragment = _format_pitcher_matchup(row)
    if pitcher_fragment:
        return f'{time_fragment} | {matchup_fragment} | {pitcher_fragment}'
    return f'{time_fragment} | {matchup_fragment}'


def _format_live_row(row: MlbSlateGameRow) -> str:
    '''
    Render one live MLB slate row.

    Args:
        row (MlbSlateGameRow): normalized live slate row

    Returns:
        str: display string for one live game
    '''
    # Prefer inning/state label for live rows, with status fallback
    status_fragment = row.inning_state_label or row.short_status_label
    score_fragment = _format_score_fragment(row)
    matchup_fragment = f'{row.away_team} at {row.home_team}'
    return f'{status_fragment} | {score_fragment} | {matchup_fragment}'


def _format_final_row(row: MlbSlateGameRow) -> str:
    '''
    Render one final MLB slate row.

    Args:
        row (MlbSlateGameRow): normalized final slate row

    Returns:
        str: display string for one final game
    '''
    # Prefer canonical Final label, but preserve any richer short label
    status_fragment = row.short_status_label or 'Final'
    score_fragment = _format_score_fragment(row)
    matchup_fragment = f'{row.away_team} at {row.home_team}'
    return f'{status_fragment} | {score_fragment} | {matchup_fragment}'


def _format_other_row(row: MlbSlateGameRow) -> str:
    '''
    Render one delayed, postponed, or otherwise nonstandard MLB slate row.

    Args:
        row (MlbSlateGameRow): normalized nonstandard slate row

    Returns:
        str: display string for one nonstandard game
    '''
    # Prefer status, then matchup, then scheduled time for nonstandard rows
    status_fragment = row.short_status_label
    matchup_fragment = f'{row.away_team} at {row.home_team}'
    time_fragment = _format_short_game_time(row.scheduled_time)
    return f'{status_fragment} | {matchup_fragment} | {time_fragment}'


def _format_team_with_record(team_name: str, record: str | None) -> str:
    '''
    Render a team label with optional record text.

    Args:
        team_name (str): team display name
        record (str | None): wins-losses record when available

    Returns:
        str: formatted team label
    '''
    # Omit record parentheses entirely when record data is unavailable
    if record:
        return f'{team_name} ({record})'
    return team_name


def _format_pitcher_matchup(row: MlbSlateGameRow) -> str | None:
    '''
    Render the probable pitcher matchup fragment for an upcoming row.

    Args:
        row (MlbSlateGameRow): normalized slate row

    Returns:
        str | None: formatted pitcher matchup or None when absent
    '''
    # Format each probable pitcher independently so missing data omits cleanly
    away_pitcher = _format_pitcher_with_record(
        row.away_probable_pitcher_name,
        row.away_probable_pitcher_record,
    )
    home_pitcher = _format_pitcher_with_record(
        row.home_probable_pitcher_name,
        row.home_probable_pitcher_record,
    )

    # Return pitchers based on presence
    if away_pitcher and home_pitcher:
        return f'{away_pitcher} vs {home_pitcher}'
    if away_pitcher:
        return away_pitcher
    if home_pitcher:
        return home_pitcher
    return None


def _format_pitcher_with_record(name: str | None, record: str | None) -> str | None:
    '''
    Render one probable pitcher with optional record text.

    Args:
        name (str | None): pitcher display name
        record (str | None): pitcher season record when available

    Returns:
        str | None: formatted pitcher label or None when absent
    '''
    # Omit the pitcher fragment entirely when the pitcher is unknown
    if not name:
        return None
    if record:
        return f'{name} ({record})'
    return name


def _format_score_fragment(row: MlbSlateGameRow) -> str:
    '''
    Render the away-home score fragment for live or final rows.

    Args:
        row (MlbSlateGameRow): normalized slate row

    Returns:
        str: formatted score text
    '''
    # Fallback to placeholders if score data is unexpectedly missing
    away_score = str(row.away_score) if row.away_score is not None else '-'
    home_score = str(row.home_score) if row.home_score is not None else '-'
    return f'{row.away_team} {away_score} - {row.home_team} {home_score}'


def _format_short_game_time(game_time: datetime | None) -> str:
    '''
    Render one scheduled first-pitch time in short Eastern Time format.

    Args:
        game_time (datetime | None): scheduled first-pitch datetime

    Returns:
        str: short scheduled time string
    '''
    # Omit missing time data with a stable fallback string
    if game_time is None:
        return 'TBD'

    # Default naive datetimes to UTC before converting to ET
    if game_time.tzinfo is None:
        game_time = game_time.replace(tzinfo=ZoneInfo('UTC'))

    eastern = game_time.astimezone(EASTERN_TZ)
    return eastern.strftime('%-I:%M ET')
