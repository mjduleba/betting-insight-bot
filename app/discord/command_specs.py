from __future__ import annotations

from app.commands.types import CommandDefinition
from app.sports.mlb.command_specs import MLB_COMMAND_DEFINITIONS


def collect_command_definitions() -> tuple[CommandDefinition, ...]:
    '''
    Collect every command definition supported by the current app.
    '''
    # Extend this tuple as new sport modules are added
    return (*MLB_COMMAND_DEFINITIONS,)


def collect_discord_command_payload() -> list[dict[str, object]]:
    '''
    Build the Discord slash-command registration payload from shared command definitions.
    '''
    # Start from the same definitions used by the runtime registry
    definitions = collect_command_definitions()

    # Group subcommands under Discord's top-level sport command shape
    grouped_commands: dict[str, dict[str, object]] = {}

    for definition in definitions:
        # Reuse the existing sport command entry or create it on first subcommand
        command = grouped_commands.setdefault(
            definition.sport,
            {
                'name': definition.sport,
                'description': definition.sport_description,
                'options': [],
            },
        )

        # Add each subcommand spec beneath its top-level sport command
        command['options'].append(
            {
                'type': 1,
                'name': definition.subcommand,
                'description': definition.subcommand_description,
                'options': list(definition.options),
            }
        )

    # Return the final Discord registration payload
    return list(grouped_commands.values())
