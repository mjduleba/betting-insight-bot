"""Slash command routing and command handlers."""

from __future__ import annotations

from app.discord_utils import discord_message_response, extract_command_identity
from app.formatters import build_mock_mlb_game_embed
from app.helpers import get_option_map, normalize_team_name
from app.services import build_mock_game_snapshot


async def handle_interaction_command(payload: dict) -> dict:
    """Route supported Discord slash commands."""

    command_name, subcommand_name = extract_command_identity(payload)

    if command_name != "mlb":
        return discord_message_response(
            content="Unsupported command. Only `/mlb game` is available right now.",
            ephemeral=True,
        )

    if subcommand_name != "game":
        return discord_message_response(
            content="Unsupported MLB subcommand. Use `/mlb game away_team home_team`.",
            ephemeral=True,
        )

    subcommand = next(
        (
            option
            for option in payload.get("data", {}).get("options", [])
            if option.get("name") == "game"
        ),
        None,
    )
    option_map = get_option_map(subcommand.get("options") if subcommand else None)

    away_team = normalize_team_name(str(option_map.get("away_team", "")))
    home_team = normalize_team_name(str(option_map.get("home_team", "")))

    if away_team == "Unknown Team" or home_team == "Unknown Team":
        return discord_message_response(
            content="Both `away_team` and `home_team` are required.",
            ephemeral=True,
        )

    snapshot = build_mock_game_snapshot(away_team=away_team, home_team=home_team)
    embed = build_mock_mlb_game_embed(snapshot)
    return discord_message_response(embeds=[embed])
