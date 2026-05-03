from __future__ import annotations

from app.commands.types import CommandHandler
from app.sports.mlb.commands.game import handle_mlb_game_command

CommandKey = tuple[str, str]

_REGISTRY: dict[CommandKey, CommandHandler] = {}


def register_handler(sport: str, subcommand: str, handler: CommandHandler) -> None:
    '''
    Register a command handler for a sport and subcommand pair.
    '''
    key = (sport, subcommand)
    if key in _REGISTRY:
        raise ValueError(
            f'Handler already registered for sport={sport!r} subcommand={subcommand!r}',
        )
    _REGISTRY[key] = handler


def get_handler(sport: str | None, subcommand: str | None) -> CommandHandler | None:
    '''
    Look up a command handler from the registry.
    '''
    if sport is None or subcommand is None:
        return None
    return _REGISTRY.get((sport, subcommand))


def clear_registry() -> None:
    '''
    Clear all registered handlers.

    Useful for tests when registry state must be reset.
    '''
    _REGISTRY.clear()


def registered_commands() -> dict[CommandKey, CommandHandler]:
    '''
    Return a shallow copy of the current registry.
    '''
    return dict(_REGISTRY)


def _register_builtin_handlers() -> None:
    '''
    Register the built-in command handlers supported by the current app.
    '''
    register_handler('mlb', 'game', handle_mlb_game_command)


_register_builtin_handlers()
