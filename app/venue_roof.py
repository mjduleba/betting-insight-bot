from __future__ import annotations

# Manual venue roof status mapping.
# Canonical values: Open, Retractable, Dome
MLB_VENUE_ROOF_BY_NAME = {
    'American Family Field': 'Retractable',
    'Angel Stadium': 'Open',
    'Busch Stadium': 'Open',
    'Chase Field': 'Retractable',
    'Citi Field': 'Open',
    'Citizens Bank Park': 'Open',
    'Comerica Park': 'Open',
    'Coors Field': 'Open',
    'Dodger Stadium': 'Open',
    'Fenway Park': 'Open',
    'Globe Life Field': 'Retractable',
    'Great American Ball Park': 'Open',
    'Kauffman Stadium': 'Open',
    'loanDepot park': 'Retractable',
    'Daikin Park': 'Retractable',
    'Nationals Park': 'Open',
    'Oracle Park': 'Open',
    'Oriole Park at Camden Yards': 'Open',
    'Petco Park': 'Open',
    'PNC Park': 'Open',
    'Progressive Field': 'Open',
    'Rate Field': 'Open',
    'Rogers Centre': 'Retractable',
    'Sutter Health Park': 'Open',
    'T-Mobile Park': 'Retractable',
    'Target Field': 'Open',
    'Tropicana Field': 'Dome',
    'Truist Park': 'Open',
    'Yankee Stadium': 'Open',
    'Wrigley Field': 'Open',
}

# Alias table for known alternate MLB venue names
VENUE_NAME_ALIASES = {
    'Guaranteed Rate Field': 'Rate Field',
    'Minute Maid Park': 'Daikin Park',
    'Oakland Coliseum': 'Sutter Health Park',
    'Choctaw Stadium': 'Globe Life Field',
    'UNIQLO Field at Dodger Stadium': 'Dodger Stadium',
}


def get_roof_status_for_venue(venue_name: str | None) -> str:
    '''
    Resolve roof status for a venue from manual lookup tables.

    Args:
        venue_name (str | None): venue name from schedule payload

    Returns:
        str: Open, Retractable, Dome, or Unknown
    '''
    # Validate venue name
    if not isinstance(venue_name, str) or not venue_name.strip():
        return 'Unknown'

    # Normalize and map aliases first
    cleaned = venue_name.strip()
    canonical = VENUE_NAME_ALIASES.get(cleaned, cleaned)

    # Return roof status from manual table
    return MLB_VENUE_ROOF_BY_NAME.get(canonical, 'Unknown')
