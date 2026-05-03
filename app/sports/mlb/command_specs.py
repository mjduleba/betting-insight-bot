from __future__ import annotations

from app.commands.types import CommandDefinition
from app.sports.mlb.commands.game import handle_mlb_game_command
from app.sports.mlb.commands.slate import handle_mlb_slate_command


# Command definition for `/mlb game`
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

# Command definition for `/mlb slate`
MLB_SLATE_COMMAND = CommandDefinition(
    sport='mlb',
    sport_description='MLB matchup tools',
    subcommand='slate',
    subcommand_description='Get the daily MLB slate',
    handler=handle_mlb_slate_command,
    options=(),
)

# Export tuple for shared collectors to consume
MLB_COMMAND_DEFINITIONS = (MLB_GAME_COMMAND, MLB_SLATE_COMMAND)
