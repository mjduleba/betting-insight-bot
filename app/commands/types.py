from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

DiscordResponse = dict[str, object]
CommandHandler = Callable[[dict], Awaitable[DiscordResponse]]


@dataclass(frozen=True, slots=True)
class CommandIdentity:
    sport: str | None
    subcommand: str | None
