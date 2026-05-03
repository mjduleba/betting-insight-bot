from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def format_game_time(dt: datetime | None) -> str:
    '''
    Universally format a game start time for Discord display.

    Args:
        dt (datetime | None): game start time

    Returns:
        str: start time formatted as string
    '''
    if dt is None:
        return 'TBD'

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))

    eastern = dt.astimezone(ZoneInfo('America/New_York'))
    return eastern.strftime('%a, %b %d at %-I:%M %p ET')
