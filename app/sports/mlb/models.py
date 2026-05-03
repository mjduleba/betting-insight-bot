from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal


@dataclass(frozen=True, slots=True)
class MlbGameRequest:
    '''
    Parsed command input for `/mlb game`.
    '''
    team: str

@dataclass(frozen=True, slots=True)
class MlbSlateRequest:
    '''
    Parsed command input for `/mlb slate`.
    '''


@dataclass(slots=True)
class GameSnapshot:
    '''
    Structured snapshot used to build the MLB Discord embed.
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

@dataclass(frozen=True, slots=True)
class MlbSlateGameRow:
    '''
    Unified row model for one game on the daily MLB slate.
    '''
    status_type: Literal['upcoming', 'live', 'final', 'other']
    away_team: str
    home_team: str
    away_team_record: str | None
    home_team_record: str | None
    scheduled_time: datetime | None
    short_status_label: str
    away_score: int | None
    home_score: int | None
    inning_state_label: str | None
    away_probable_pitcher_name: str | None
    home_probable_pitcher_name: str | None
    away_probable_pitcher_record: str | None
    home_probable_pitcher_record: str | None


@dataclass(frozen=True, slots=True)
class MlbSlateSnapshot:
    '''
    Ordered MLB slate snapshot for a single Eastern Time board date.
    '''
    board_date: date
    total_game_count: int
    games: list[MlbSlateGameRow]
