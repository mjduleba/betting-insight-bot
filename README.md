# betting-insight-bot

Personal Discord MLB bot built with FastAPI. The current bootstrap phase wires Discord
interactions end to end and returns a mock `/mlb game` embed while the real data sources
are still being built.

## Prerequisites

- Python 3.11+
- A Discord application with:
  - `DISCORD_APPLICATION_ID`
  - `DISCORD_BOT_TOKEN`
  - `DISCORD_PUBLIC_KEY`
  - `DISCORD_GUILD_ID`
- `ngrok` configured for local HTTPS forwarding

## Setup

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Create your local env file:

```bash
cp .env.example .env
```

Populate `.env` with your Discord values.

## Run The App

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --port 8000
```

In a second terminal, start `ngrok`:

```bash
ngrok http 8000
```

Copy the HTTPS forwarding URL and set the Discord application's Interactions Endpoint URL to:

```text
https://<your-ngrok-domain>/interactions
```

## Register Slash Commands

Register the guild-scoped command:

```bash
python3 scripts/register_commands.py
```

This registers:

```text
/mlb game away_team:<team> home_team:<team>
```

## Manual Test

1. Start the app locally.
2. Start `ngrok`.
3. Save the `ngrok` URL to the Discord Interactions Endpoint field.
4. Run the registration script.
5. In your private Discord server, invoke:

```text
/mlb game away_team:Yankees home_team:Red Sox
```

The bot should return a mock embed containing matchup, venue, weather, pitcher, and line placeholders.
