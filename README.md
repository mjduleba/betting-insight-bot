# betting-insight-bot

Personal Discord MLB bot built with FastAPI. The app receives Discord slash-command
interactions, routes them through a shared command registry, and returns either an MLB game
snapshot for `/mlb game team:<team>` or a daily board view for `/mlb slate`.

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
/mlb slate
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

You can also invoke:

```text
/mlb slate
```

The bot should return the current Eastern Time MLB slate in start-time order. Upcoming games
include away/home records, probable pitchers, and probable pitcher win-loss records when
available. Live and final games prioritize score and status, while postponed or delayed games
render with their status label and scheduled time. If the full slate does not fit in one embed,
the bot automatically continues it into additional embeds at row boundaries.

## Command Architecture

The runtime is now organized around shared command definitions:

- sport modules define their commands and handlers
- the shared registry builds runtime routing from those definitions
- the registration script builds the Discord slash-command payload from those same definitions

Current live commands:

```text
/mlb game team:<team>
/mlb slate
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
        │   ├── game.py
        │   └── slate.py
        ├── formatters/
        │   ├── game.py
        │   └── slate.py
        └── services/
            ├── game.py
            └── slate.py
```

Supporting docs for the refactor live in:

- `docs/context/architecture-index.md`
- `docs/context/command-architecture.md`
- `docs/context/file-structure-refactor.md`
