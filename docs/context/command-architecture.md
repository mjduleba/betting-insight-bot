# Command Architecture

## Goal
Refactor the bot from a single hard-coded MLB command path into a small command architecture that stays simple but makes additional sports and subcommands additive.

The immediate requirement is to preserve the current `/mlb game team:<team>` user flow while moving the runtime toward a registry-based design.

## Command Routing Approach
The runtime should treat a Discord slash command as two levels of identity:

- `sport`: the top-level command name, such as `mlb`
- `subcommand`: the nested subcommand name, such as `game`

Routing should happen in one shared place:

1. Parse the Discord interaction payload into a normalized command identity.
2. Look up a handler by `(sport, subcommand)`.
3. Invoke the handler with the raw interaction payload or a small typed request wrapper.
4. Return a Discord response payload built by the handler.

The router should own only cross-cutting concerns:

- extracting command identity
- standardized unsupported-command errors
- delegating to the correct handler

The router should not contain sport-specific branching after the refactor is complete.

## Registry Pattern
Use a central registry keyed by `(sport, subcommand) -> handler`.

Design constraints:
- registration should be explicit and easy to inspect
- adding a new command should not require editing router logic
- duplicate registrations should fail fast
- unsupported commands should produce a consistent user-facing response

Recommended shape:

```text
registry[(sport, subcommand)] = handler
```

The registry can be built from sport modules at import time or from a small collector function. The important part is that the router reads from one authoritative map instead of hard-coded conditionals.

## Handler Contract
Each command handler should implement the same narrow contract:

- accept the Discord interaction payload, or a small parsed wrapper derived from it
- validate required options for that command
- call sport-specific services
- format the result into a Discord response payload
- handle expected fallback paths without leaking internal exceptions to the user

Practical expectations for handlers:
- keep Discord option parsing close to the command
- keep sport-specific orchestration in sport services
- keep embed construction in sport formatters
- return already-formed Discord payloads or a small response model that shared Discord helpers can serialize

## Command Registration Strategy
Runtime routing and Discord command registration should come from the same source of truth.

That means each command module needs two related pieces:

- a runtime handler registration
- a Discord slash-command spec used by `scripts/register_commands.py`

The preferred structure is:

1. Each sport module declares its command specs.
2. A shared collector gathers those specs for registration.
3. The runtime registry registers the matching handlers from the same module set.

This avoids drift between:
- commands Discord knows about
- commands the runtime can actually route

## Behavior Preservation Rules
During the refactor:

- `/mlb game` must keep the same command name and required option behavior
- current fallback messaging should remain stable unless there is a deliberate improvement
- MLB remains the only real sport implementation until the pattern is proven

## Non-Goals
This refactor is not meant to introduce:

- a large plugin framework
- dynamic command loading from user config
- complex dependency injection
- premature abstractions for many sports before a second one exists

The target is a small, legible architecture that makes the next command mostly additive.
