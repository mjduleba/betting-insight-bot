from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
class MlbGameRequest:
    '''
    Parsed command input for `/mlb game`.
    '''
    team: str
