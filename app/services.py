"""Service layer for composing MLB game snapshot data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(slots=True)
class MockGameSnapshot:
    """Bootstrap game snapshot returned before real APIs are connected."""

    away_team: str
    home_team: str
    scheduled_time: datetime
    stadium: str
    city: str
    weather: str
    probable_pitchers: str
    recent_starts: str
    lines: str


def build_mock_game_snapshot(away_team: str, home_team: str) -> MockGameSnapshot:
    """Return realistic placeholder data for the Discord plumbing slice."""

    return MockGameSnapshot(
        away_team=away_team,
        home_team=home_team,
        scheduled_time=datetime(2026, 4, 24, 19, 5, tzinfo=ZoneInfo("America/New_York")),
        stadium="Demo Ballpark",
        city="Boston, MA",
        weather="61 F, light breeze to CF, partly cloudy",
        probable_pitchers=f"{away_team}: Placeholder RHP vs. {home_team}: Placeholder LHP",
        recent_starts=(
            f"{away_team}: Last 3 starts - 18.1 IP, 5 ER, 19 K\n"
            f"{home_team}: Last 3 starts - 17.0 IP, 6 ER, 15 K"
        ),
        lines="Moneyline: TBD | Run Line: TBD | Total: TBD",
    )
