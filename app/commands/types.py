from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

# Shared response and handler types used by command modules
DiscordResponse = dict[str, object]
CommandHandler = Callable[[dict], Awaitable[DiscordResponse]]


@dataclass(frozen=True, slots=True)
class CommandIdentity:
    '''
    Normalized command identity extracted from a Discord interaction payload.
    '''
    sport: str | None
    subcommand: str | None


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    '''
    Shared command definition used for runtime routing and Discord registration.
    '''
    # Top-level sport command, such as `mlb`
    sport: str

    # User-facing description for the top-level sport command
    sport_description: str

    # Subcommand name beneath the sport command, such as `game`
    subcommand: str

    # User-facing description for the subcommand
    subcommand_description: str

    # Runtime handler invoked when this command is routed
    handler: CommandHandler

    # Discord option payload for the subcommand
    options: tuple[dict[str, object], ...] = ()
