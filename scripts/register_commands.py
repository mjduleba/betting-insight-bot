"""Script for registering Discord slash commands."""

from __future__ import annotations

import asyncio
import sys

import httpx

from app.config import get_settings

COMMAND_PAYLOAD = [
    {
        "name": "mlb",
        "description": "MLB matchup tools",
        "options": [
            {
                "type": 1,
                "name": "game",
                "description": "Get a pregame MLB matchup snapshot",
                "options": [
                    {
                        "type": 3,
                        "name": "away_team",
                        "description": "Away team name",
                        "required": True,
                    },
                    {
                        "type": 3,
                        "name": "home_team",
                        "description": "Home team name",
                        "required": True,
                    },
                ],
            }
        ],
    }
]


async def register_guild_commands() -> None:
    """Register the bot's guild-scoped slash commands."""

    settings = get_settings()
    url = (
        "https://discord.com/api/v10/applications/"
        f"{settings.discord_application_id}/guilds/{settings.discord_guild_id}/commands"
    )
    headers = {
        "Authorization": f"Bot {settings.discord_bot_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.put(url, headers=headers, json=COMMAND_PAYLOAD)

    if response.is_success:
        print(
            f"Registered {len(response.json())} guild command(s) "
            f"for guild {settings.discord_guild_id}."
        )
        return

    print("Discord command registration failed.", file=sys.stderr)
    print(f"Status: {response.status_code}", file=sys.stderr)
    print(response.text, file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    try:
        asyncio.run(register_guild_commands())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
