# File Structure Refactor

## Current Structure
The current app keeps most logic in a small set of global modules:

```text
app/
├── main.py
├── commands.py
├── discord_utils.py
├── services.py
├── api_clients.py
├── formatters.py
└── helpers.py
```

This is workable for the first MVP, but MLB-specific logic now lives in generic files and command dispatch is coupled to one hard-coded flow.

## Target Structure
The refactor should move the project toward a sport-first layout with a small shared layer:

```text
app/
├── main.py
├── config.py
├── logging_config.py
├── discord/
│   ├── auth.py
│   ├── responses.py
│   ├── parsing.py
│   └── command_specs.py
├── commands/
│   ├── router.py
│   ├── registry.py
│   └── types.py
├── shared/
│   ├── errors.py
│   ├── http.py
│   └── time.py
└── sports/
    └── mlb/
        ├── command_specs.py
        ├── models.py
        ├── normalization.py
        ├── commands/
        │   └── game.py
        ├── services/
        │   └── game.py
        ├── clients/
        │   └── stats_api.py
        └── formatters/
            └── game.py
```

## Responsibility Split

### Shared Discord Modules
`app/discord/` should contain Discord-specific helpers that are not tied to MLB:

- request signature verification
- interaction parsing helpers
- response payload builders
- shared slash-command spec collection

### Shared Command Modules
`app/commands/` should contain the runtime command architecture:

- handler types
- central registry
- shared router

These files should know how to route commands, but not how to execute MLB-specific business logic.

### Shared Utility Modules
`app/shared/` should contain only generic helpers that are truly reusable across sports:

- generic error types
- date and time formatting
- shared HTTP helpers if they become necessary

### Sport Modules
Each sport should own its own implementation under `app/sports/<sport>/`.

For MLB, that means:
- models for sport-specific request and snapshot data
- normalization for team aliases and similar input cleanup
- API clients for MLB data sources
- services for MLB game orchestration
- formatters for MLB embeds
- command handlers for MLB slash-command behavior
- command specs for Discord registration

## Migration Direction
The refactor should happen in small phases:

1. Add the new shared and sport-first structure.
2. Move MLB behavior into the new module layout.
3. Switch routing to the shared registry.
4. Unify runtime registration and Discord slash-command registration.
5. Remove dead code from the old global files.

## Design Constraint
The target structure should stay small. The point is not to maximize the file count; the point is to separate shared infrastructure from sport-specific behavior so future commands can be added without reopening unrelated MLB internals.
