"""Formatting helpers for Discord embed payloads."""

from __future__ import annotations

from app.helpers import format_game_time
from app.services import MockGameSnapshot


def build_mock_mlb_game_embed(snapshot: MockGameSnapshot) -> dict:
    """Build a Discord embed that mirrors the intended MVP response shape."""

    matchup = f"{snapshot.away_team} at {snapshot.home_team}"
    return {
        "title": matchup,
        "description": "Bootstrap response for Discord wiring and command validation.",
        "color": 0x0B6E4F,
        "fields": [
            {
                "name": "Game Info",
                "value": (
                    f"Time: {format_game_time(snapshot.scheduled_time)}\n"
                    f"Venue: {snapshot.stadium}\n"
                    f"Location: {snapshot.city}"
                ),
                "inline": False,
            },
            {
                "name": "Weather",
                "value": snapshot.weather,
                "inline": False,
            },
            {
                "name": "Probable Pitchers",
                "value": snapshot.probable_pitchers,
                "inline": False,
            },
            {
                "name": "Recent Starts",
                "value": snapshot.recent_starts,
                "inline": False,
            },
            {
                "name": "Lines",
                "value": snapshot.lines,
                "inline": False,
            },
        ],
        "footer": {
            "text": "Mock bootstrap data. Replace with live MLB, weather, and odds feeds next.",
        },
    }
