from __future__ import annotations

import asyncio
import logging
import sys

import httpx

from app.config import get_settings
from app.logging_config import setup_logging

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
                        'name': 'team',
                        'description': 'Team name',
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
    # Configure script logger through centralized logging module
    setup_logging('INFO')

    try:
        asyncio.run(register_guild_commands())
    except RuntimeError as exc:
        logger.exception('Runtime error while registering Discord commands')
        raise SystemExit(1) from exc
