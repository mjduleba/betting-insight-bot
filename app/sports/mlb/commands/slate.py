from __future__ import annotations

from app.discord.responses import discord_message_response


async def handle_mlb_slate_command(payload: dict) -> dict[str, object]:
    '''
    Temporary `/mlb slate` handler until the slate service and formatter land.
    '''
    _ = payload
    return discord_message_response(
        content='`/mlb slate` is not implemented yet.',
        ephemeral=True,
    )
