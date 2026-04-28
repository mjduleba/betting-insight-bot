from __future__ import annotations

import logging
from datetime import date
import os

import httpx

# Store MLB Stats Base API URL
MLB_STATS_API_BASE_URL = os.getenv('MLB_STATS_API_BASE_URL')

# Create global logger
logger = logging.getLogger(__name__)


async def fetch_schedule_games(start_date: date, end_date: date) -> list[dict]:
    '''
    Fetch MLB schedule games in a date range.

    Args:
        start_date (date): first date in schedule window
        end_date (date): last date in schedule window

    Returns:
        list[dict]: flattened list of game payloads
    '''
    # Store URL for schedule call
    url = f'{MLB_STATS_API_BASE_URL}/schedule'
    params = {
        'sportId': 1,
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
    }

    logger.info(
        'Fetching MLB schedule: start_date=%s end_date=%s',
        params['startDate'],
        params['endDate'],
    )

    # Send async GET request for /schedule endpoint
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        payload = response.json()

    # Parse games from response
    games: list[dict] = []
    for schedule_date in payload.get('dates', []):
        games.extend(schedule_date.get('games', []))

    logger.info('Fetched %s MLB games from schedule endpoint', len(games))
    return games


async def fetch_venue_city(venue_id: int | None) -> str | None:
    '''
    Fetch venue city by venue id.

    Args:
        venue_id (int | None): MLB venue identifier

    Returns:
        str | None: city name when available
    '''
    # Validate venue identifier
    if venue_id is None:
        return None

    # Store URL for venues request
    url = f'{MLB_STATS_API_BASE_URL}/venues/{venue_id}'
    logger.debug('Fetching venue details: venue_id=%s', venue_id)

    # Send async GET request for /venues endpoint
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()

    # Validate response
    venues = payload.get('venues', [])
    if not venues:
        return None

    # Parse venues response and return
    location = venues[0].get('location') or {}
    return location.get('city')
