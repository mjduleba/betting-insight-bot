"""Shared utility functions for normalization and formatting."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

TEAM_ALIASES = {
    "angels": "Los Angeles Angels",
    "astros": "Houston Astros",
    "athletics": "Athletics",
    "a's": "Athletics",
    "blue jays": "Toronto Blue Jays",
    "braves": "Atlanta Braves",
    "brewers": "Milwaukee Brewers",
    "cardinals": "St. Louis Cardinals",
    "cubs": "Chicago Cubs",
    "diamondbacks": "Arizona Diamondbacks",
    "dbacks": "Arizona Diamondbacks",
    "dodgers": "Los Angeles Dodgers",
    "giants": "San Francisco Giants",
    "guardians": "Cleveland Guardians",
    "guards": "Cleveland Guardians",
    "mariners": "Seattle Mariners",
    "marlins": "Miami Marlins",
    "mets": "New York Mets",
    "nationals": "Washington Nationals",
    "orioles": "Baltimore Orioles",
    "padres": "San Diego Padres",
    "phillies": "Philadelphia Phillies",
    "pirates": "Pittsburgh Pirates",
    "rangers": "Texas Rangers",
    "rays": "Tampa Bay Rays",
    "red sox": "Boston Red Sox",
    "reds": "Cincinnati Reds",
    "rockies": "Colorado Rockies",
    "royals": "Kansas City Royals",
    "tigers": "Detroit Tigers",
    "twins": "Minnesota Twins",
    "white sox": "Chicago White Sox",
    "yankees": "New York Yankees",
}


def normalize_team_name(value: str) -> str:
    """Normalize user team input into a readable MLB team name."""

    normalized = " ".join(value.strip().lower().split())
    if not normalized:
        return "Unknown Team"
    return TEAM_ALIASES.get(normalized, normalized.title())


def get_option_map(options: list[dict] | None) -> dict[str, object]:
    """Map Discord option payloads by option name."""

    if not options:
        return {}
    return {option["name"]: option.get("value") for option in options if "name" in option}


def format_game_time(dt: datetime | None) -> str:
    """Format a datetime for Discord embed display."""

    if dt is None:
        return "TBD"

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    eastern = dt.astimezone(ZoneInfo("America/New_York"))
    return eastern.strftime("%a, %b %d at %-I:%M %p ET")
