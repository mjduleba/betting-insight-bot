'''Shared utility functions for normalization and formatting.'''

from __future__ import annotations

from app.shared.time import format_game_time

TEAM_ALIASES = {
    'angels': 'Los Angeles Angels',
    'astros': 'Houston Astros',
    'athletics': 'Athletics',
    "a's": 'Athletics',
    'blue jays': 'Toronto Blue Jays',
    'braves': 'Atlanta Braves',
    'brewers': 'Milwaukee Brewers',
    'cardinals': 'St. Louis Cardinals',
    'cubs': 'Chicago Cubs',
    'diamondbacks': 'Arizona Diamondbacks',
    'dbacks': 'Arizona Diamondbacks',
    'dodgers': 'Los Angeles Dodgers',
    'giants': 'San Francisco Giants',
    'guardians': 'Cleveland Guardians',
    'guards': 'Cleveland Guardians',
    'mariners': 'Seattle Mariners',
    'marlins': 'Miami Marlins',
    'mets': 'New York Mets',
    'nationals': 'Washington Nationals',
    'orioles': 'Baltimore Orioles',
    'padres': 'San Diego Padres',
    'phillies': 'Philadelphia Phillies',
    'pirates': 'Pittsburgh Pirates',
    'rangers': 'Texas Rangers',
    'rays': 'Tampa Bay Rays',
    'red sox': 'Boston Red Sox',
    'reds': 'Cincinnati Reds',
    'rockies': 'Colorado Rockies',
    'royals': 'Kansas City Royals',
    'tigers': 'Detroit Tigers',
    'twins': 'Minnesota Twins',
    'white sox': 'Chicago White Sox',
    'yankees': 'New York Yankees',
}


def normalize_team_name(value: str) -> str:
    '''
    Helper function to normalize team name. Fallback to 'Unknown Team'.

    Args:
        value (str): team name

    Returns:
        str: normalized team name
    '''
    normalized = ' '.join(value.strip().lower().split())
    if not normalized:
        return 'Unknown Team'
    return TEAM_ALIASES.get(normalized, normalized.title())


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
