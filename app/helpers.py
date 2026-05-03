'''Shared utility functions for normalization and formatting.'''

from __future__ import annotations

from app.shared.time import format_game_time
from app.sports.mlb.normalization import normalize_team_name

def get_option_map(options: list[dict] | None) -> dict[str, object]:
    '''
    Helper function to flatten the the parameters of the slash-command.

    Args:
        options (list[dict] | None): Discor options

    Returns:
        dict[str, object]: flattened dictionary keyed by option name
    '''
    if not options:
        return {}
    return {option['name']: option.get('value') for option in options if 'name' in option}
