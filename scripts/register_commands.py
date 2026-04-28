from __future__ import annotations

import asyncio
import logging
import sys

import httpx

from app.config import get_settings

# Create logger
logger = logging.getLogger(__name__)

# Standardize command payload
COMMAND_PAYLOAD = [
    {
        'name': 'mlb',
        'description': 'MLB matchup tools',
        'options': [
            {
                'type': 1,
                'name': 'game',
                'description': 'Get a pregame MLB matchup snapshot',
                'options': [
                    {
                        'type': 3,
                        'name': 'away_team',
                        'description': 'Away team name',
                        'required': True,
                    },
                    {
                        'type': 3,
                        'name': 'home_team',
                        'description': 'Home team name',
                        'required': True,
                    },
                ],
            }
        ],
    }
]


async def register_guild_commands() -> None:
    '''
    Register guild-scoped slash commands with Discord API.

    Raises:
        SystemExit: command registration failed
    '''
    # Store app settings
    settings = get_settings()

    # Build command registration endpoint
    url = (
        'https://discord.com/api/v10/applications/'
        f'{settings.discord_application_id}/guilds/{settings.discord_guild_id}/commands'
    )
    headers = {
        'Authorization': f'Bot {settings.discord_bot_token}',
        'Content-Type': 'application/json',
    }
    logger.info('Registering guild commands for guild_id=%s', settings.discord_guild_id)
    logger.debug('Discord register URL: %s', url)

    # Send command payload to Discord
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.put(url, headers=headers, json=COMMAND_PAYLOAD)

    # Return success when registration call succeeds
    if response.is_success:
        logger.info('Guild command registration succeeded with status=%s', response.status_code)
        return

    # Log and raise on registration failure
    logger.error('Guild command registration failed with status=%s', response.status_code)
    logger.error('Discord response body: %s', response.text)

    raise SystemExit(1)


if __name__ == '__main__':
    # Configure script logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )

    try:
        asyncio.run(register_guild_commands())
    except RuntimeError as exc:
        logger.exception('Runtime error while registering Discord commands')
        raise SystemExit(1) from exc
