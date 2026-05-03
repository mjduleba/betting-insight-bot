from __future__ import annotations

from app.commands.types import CommandDefinition
from app.sports.mlb.commands.game import handle_mlb_game_command


# Shared command definition for `/mlb game`
MLB_GAME_COMMAND = CommandDefinition(
    sport='mlb',
    sport_description='MLB matchup tools',
    subcommand='game',
    subcommand_description='Get a pregame MLB matchup snapshot',
    handler=handle_mlb_game_command,
    options=(
        {
            'type': 3,
            'name': 'team',
            'description': 'Team name',
            'required': True,
        },
    ),
)

# Export tuple for shared collectors to consume
MLB_COMMAND_DEFINITIONS = (MLB_GAME_COMMAND,)
