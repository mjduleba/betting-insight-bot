from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.sports.mlb.models import MlbSlateGameRow, MlbSlateSnapshot

EASTERN_TZ = ZoneInfo('America/New_York')
EMBED_DESCRIPTION_LIMIT = 4096
EMBED_COLOR = 0x0B6E4F


def build_mlb_slate_embeds(snapshot: MlbSlateSnapshot) -> list[dict]:
    '''
    Build one or more Discord embeds for an MLB slate snapshot.

    Args:
        snapshot (MlbSlateSnapshot): normalized slate snapshot

    Returns:
        list[dict]: ordered embed payloads for the daily slate
    '''
    # Build the stable title prefix from the ET board date
    title = f'MLB Slate - {snapshot.board_date.strftime("%a, %b %d")}'

    # Return a single empty-state embed when no games are scheduled
    if not snapshot.games:
        return [
            {
                'title': title,
                'description': 'No MLB games scheduled today.',
                'color': EMBED_COLOR,
            }
        ]

    # Render every game row in slate order before packing embed descriptions
    row_lines = [format_mlb_slate_row(row) for row in snapshot.games]
    count_line = _format_game_count(snapshot.total_game_count)
    description_chunks = _split_slate_descriptions(count_line, row_lines)

    # Build one embed per packed description chunk
    embeds: list[dict] = []
    for index, description in enumerate(description_chunks):
        embed_title = title if index == 0 else f'{title} (cont.)'
        embeds.append(
            {
                'title': embed_title,
                'description': description,
                'color': EMBED_COLOR,
            }
        )
    return embeds


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


def _format_game_count(total_games: int) -> str:
    '''
    Render the summary game-count line for the slate description.

    Args:
        total_games (int): total number of slate games

    Returns:
        str: formatted count summary line
    '''
    # Match singular or plural game wording automatically
    noun = 'game' if total_games == 1 else 'games'
    return f'{total_games} {noun}'


def _split_slate_descriptions(count_line: str, row_lines: list[str]) -> list[str]:
    '''
    Split formatted slate rows into embed-safe description chunks.

    Args:
        count_line (str): summary line for the first embed
        row_lines (list[str]): ordered formatted game rows

    Returns:
        list[str]: packed description chunks split at row boundaries
    '''
    # Seed the first embed with the game-count summary line
    chunks: list[str] = []
    current_lines = [count_line]

    # Append each row to the current chunk unless it would exceed the limit
    for row_line in row_lines:
        candidate_lines = [*current_lines, row_line]
        candidate_description = '\n'.join(candidate_lines)
        if len(candidate_description) <= EMBED_DESCRIPTION_LIMIT:
            current_lines = candidate_lines
            continue

        chunks.append('\n'.join(current_lines))
        current_lines = [row_line]

    # Flush the final chunk after all rows are packed
    if current_lines:
        chunks.append('\n'.join(current_lines))
    return chunks
