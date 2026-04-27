# Codex Project Context — Discord MLB Bot

## Project Summary
I am building a small **personal Discord bot** in Python for use in one or two private Discord servers with friends.

This is meant to be a **resume-friendly side project**, not a production-grade platform. The code should be clean and organized, but should **not be over-engineered**.

The goal is to build a bot that responds to a slash command and returns a quick MLB game snapshot.

---

## Core MVP Goal
Start with **MLB only** and one main slash command:

- `/mlb game away_team:<team> home_team:<team>`

The bot should return a Discord embed containing:

- away team and home team
- scheduled game time
- stadium / game location
- weather
- probable / starting pitchers
- brief recent-start recap for each pitcher
- game lines:
  - moneyline
  - run line if available
  - total if available

This MVP does **not** need:
- machine learning
- betting recommendations
- expected value calculations
- databases
- multiple sports
- a formal automated test suite
- large-scale production architecture

---

## Project Philosophy
Design this as a **small personal project** with these assumptions:

- only used by me and maybe a few friends
- one or two Discord servers max
- low traffic
- free or near-free tools only
- simple local setup
- readability and demo value matter more than enterprise patterns

That means:

- keep the architecture simple
- avoid unnecessary abstraction
- avoid creating lots of folders/files unless they clearly help
- do not add infrastructure I do not need yet
- do not assume scale
- prioritize a working end-to-end MVP first

---

## Preferred Tech Stack
Use these tools unless there is a strong reason not to:

- **Python**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **python-dotenv**

Helpful but optional:
- **Ruff**
- **ngrok** or **Cloudflare Tunnel** for local Discord testing

Do **not** introduce these in the MVP unless necessary:
- PostgreSQL
- Redis
- Celery
- Alembic
- SQLAlchemy
- Docker Compose
- CI/CD pipelines
- large observability setup
- full pytest suite

---

## High-Level Architecture
Keep the app simple:

```text
Discord Slash Command
    ↓
FastAPI /interactions endpoint
    ↓
Parse team inputs
    ↓
Call sports data APIs
    ↓
Format data into a Discord embed
    ↓
Return response
```

Internal flow:

1. Discord sends a slash command interaction
2. FastAPI receives it at `/interactions`
3. Validate the Discord request signature
4. Parse away team and home team inputs
5. Fetch:
   - game info
   - probable starters
   - recent pitcher starts
   - weather
   - betting lines
   - result history for each team
6. Format everything into a clean Discord embed
7. Return the response

---

## File Structure
Keep the codebase small and practical.

```text
discord-mlb-bot/
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── app/
│   ├── main.py
│   ├── config.py
│   ├── discord_utils.py
│   ├── commands.py
│   ├── services.py
│   ├── api_clients.py
│   ├── formatters.py
│   └── helpers.py
├── scripts/
│   └── register_commands.py
└── notes/
    └── ideas.md
```

---

## File Responsibilities

### `app/main.py`
FastAPI entry point.

Responsibilities:
- create the FastAPI app
- define `/health`
- define `/interactions`
- route incoming Discord commands

### `app/config.py`
Environment-variable loading and simple settings.

Examples:
- Discord public key
- bot token
- API keys
- log level

### `app/discord_utils.py`
Discord-specific helpers.

Examples:
- request signature validation
- interaction parsing helpers
- response payload helpers

### `app/commands.py`
Main command handling logic.

For MVP, this can focus on:
- `/mlb game`

### `app/services.py`
Main orchestration layer.

Examples:
- fetch game data
- fetch probable starters
- fetch pitcher recent-start summaries
- fetch weather
- fetch odds
- combine everything into one response object

### `app/api_clients.py`
External API calls.

Examples:
- MLB schedule / probable pitcher lookup
- pitcher game log lookup
- weather lookup
- odds lookup

### `app/formatters.py`
Format raw data into a readable Discord embed payload.

### `app/helpers.py`
Small utility functions.

Examples:
- team-name normalization
- datetime formatting
- fallback handling for missing values

### `scripts/register_commands.py`
Register slash commands with Discord.

### `notes/ideas.md`
Scratchpad for future enhancements.

---

## MVP Command Design

### Main command
`/mlb game away_team:<team> home_team:<team>`

### Inputs
- away team
- home team

### Output
Return a Discord embed with sections like:

**Game Info**
- matchup
- time
- stadium
- city

**Weather**
- temperature
- wind
- conditions

**Probable Pitchers**
- away starter
- home starter

**Recent Starts**
- short recap for each pitcher

**Lines**
- moneyline
- run line
- total

### Pitcher recap style
Do not dump raw tables unless necessary. Prefer a concise summary like:

- `Last 3 starts: 18.2 IP, 5 ER, 21 K, 2.41 ERA`
- `Coming off 6.0 innings, 2 earned runs, 7 strikeouts vs. Detroit`

---

## Team Name Handling
Users may enter team names in different forms, so normalize them with a simple alias dictionary.

Example:

```python
TEAM_ALIASES = {
    "yankees": "New York Yankees",
    "new york yankees": "New York Yankees",
    "guardians": "Cleveland Guardians",
    "guards": "Cleveland Guardians",
    "cleveland": "Cleveland Guardians",
}
```

This should live in `helpers.py` or `config.py`.

No database is needed for this.

---

## Data Requirements
The bot will likely need separate data sources for:

### 1. MLB game info
Needed for:
- matchup confirmation
- scheduled game time
- stadium / location
- probable starters

### 2. Pitcher recent starts
Needed for:
- recent game log summaries
- short recap of form

### 3. Weather
Needed for:
- temperature
- wind
- general conditions / rain if relevant

### 4. Betting lines
Needed for:
- moneyline
- run line
- total

It is completely acceptable to combine multiple external APIs into one response. That is part of the value of the project.

---

## Caching Strategy
Because this is a low-traffic personal project, caching should stay simple.

### MVP choice
- no cache at first, or
- a simple in-memory dictionary cache if needed

### Potential TTLs
- lines: 2 to 5 minutes
- weather: 10 to 15 minutes
- pitcher recap: 30 minutes

Do not add Redis for MVP.

---

## Logging Strategy
Keep logging basic.

Log:
- incoming command
- parsed matchup
- API failures
- successful response generation

Console logging is enough for now.

---

## Security / Config Basics
Even though this is a personal project, keep the basics correct.

### Must-have
- validate Discord request signatures
- keep tokens and API keys in environment variables
- never hardcode secrets

### Expected environment variables
```text
DISCORD_PUBLIC_KEY=
DISCORD_BOT_TOKEN=
DISCORD_APPLICATION_ID=
ODDS_API_KEY=
WEATHER_API_KEY=
MLB_DATA_API_KEY=
APP_ENV=
LOG_LEVEL=
```

---

## Testing Approach
Do **not** build a full test suite for the MVP.

Use practical spot testing instead:

- run FastAPI locally
- expose local app with ngrok or similar
- invoke slash commands in a private Discord server
- inspect logs
- manually verify returned data

Spot checks to perform:
- matchup resolves correctly
- probable starters are correct
- recent-start recap is readable
- weather populates correctly
- lines populate correctly
- missing data fails gracefully

Use temporary logs, sample payloads, and helper scripts as needed.

---

## Scope Guardrails
Please keep implementation decisions aligned to these constraints:

### Do
- keep code simple
- favor readability
- build the smallest working version first
- use a small number of files
- create clear helper functions where useful
- return polished Discord embeds
- make the project easy to demo and explain on a resume

### Do Not
- over-abstract
- create production-grade architecture
- add a database too early
- add background workers
- build a full analytics engine yet
- create unnecessary folders/modules
- add complex deployment concerns unless asked

---

## Implementation Phases

### Phase 1 — Basic shell
- create repo
- scaffold FastAPI app
- add `/health`
- add `/interactions`
- validate Discord signatures
- register `/mlb game`

### Phase 2 — Basic MLB response
- accept away/home team inputs
- fetch game info
- fetch probable starters
- return a simple embed

### Phase 3 — Add pitcher recaps
- fetch recent starts for both starters
- summarize recent performance
- include it in the embed

### Phase 4 — Add weather and lines
- fetch weather for game location
- fetch betting lines
- include them in the embed

### Phase 5 — Polish
- improve formatting
- improve team alias handling
- add light caching if helpful
- improve README for GitHub / resume use

---

## Definition of Done for MVP
The MVP is done when:

- the bot works in my Discord server
- `/mlb game` accepts team inputs
- it returns matchup, pitchers, location, weather, and lines
- recent-start recaps are readable
- incomplete data does not crash the response
- the project is clean enough to show on GitHub and discuss in interviews

---

## Future Ideas
These are explicitly **later**, not part of the first build:

- `/mlb lines`
- `/mlb pitchers`
- `/mlb weather`
- team trends
- bullpen notes
- batter splits
- daily slate command
- AI-generated matchup summary
- another sport

---

## Resume Framing
This project should eventually be describable like this:

> Built a personal Discord bot in Python using FastAPI and slash-command interactions to deliver MLB matchup snapshots with probable pitchers, recent starting-pitcher performance, weather conditions, and betting lines by combining multiple external APIs into a single user-facing response.

---

## Immediate Next Step
Start with the smallest vertical slice:

1. create the FastAPI app
2. add `/interactions`
3. implement Discord signature validation
4. add the `/mlb game` command
5. return a hardcoded mock embed first

After that, replace each mock section with real API data one piece at a time.
