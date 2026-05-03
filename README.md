# betting-insight-bot

Personal Discord MLB bot built with FastAPI. The app receives Discord slash-command
interactions, routes them through a shared command registry, and returns an MLB game
snapshot for `/mlb game team:<team>`.

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
/mlb game team:<team>
```

## Manual Test

1. Start the app locally.
2. Start `ngrok`.
3. Save the `ngrok` URL to the Discord Interactions Endpoint field.
4. Run the registration script.
5. In your private Discord server, invoke:

```text
/mlb game team:Yankees
```

The bot should return an embed containing matchup, game time, venue, weather, team form,
probable pitchers, recent starts, and line placeholders. If the MLB data lookup fails or no
game is found in the lookup window, the bot falls back to a placeholder snapshot instead of
failing the interaction.

## Command Architecture

The runtime is now organized around shared command definitions:

- sport modules define their commands and handlers
- the shared registry builds runtime routing from those definitions
- the registration script builds the Discord slash-command payload from those same definitions

Current live command:

```text
/mlb game team:<team>
```

## Project Structure

```text
app/
├── main.py
├── config.py
├── logging_config.py
├── discord/
│   ├── auth.py
│   ├── command_specs.py
│   ├── parsing.py
│   └── responses.py
├── commands/
│   ├── registry.py
│   ├── router.py
│   └── types.py
├── shared/
│   ├── errors.py
│   └── time.py
└── sports/
    └── mlb/
        ├── command_specs.py
        ├── models.py
        ├── normalization.py
        ├── clients/
        │   └── stats_api.py
        ├── commands/
        │   └── game.py
        ├── formatters/
        │   └── game.py
        └── services/
            └── game.py
```

Supporting docs for the refactor live in:

- `docs/context/architecture-index.md`
- `docs/context/command-architecture.md`
- `docs/context/file-structure-refactor.md`
