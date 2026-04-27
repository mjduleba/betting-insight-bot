"""Discord request validation and response helpers."""

from __future__ import annotations

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

PING_INTERACTION_TYPE = 1
APPLICATION_COMMAND_TYPE = 2
CHANNEL_MESSAGE_WITH_SOURCE = 4
EPHEMERAL_FLAG = 1 << 6
SUBCOMMAND_OPTION_TYPE = 1


def verify_discord_signature(
    public_key: str,
    signature: str | None,
    timestamp: str | None,
    body: bytes,
) -> bool:
    """Verify Discord's Ed25519 request signature."""

    if not signature or not timestamp:
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(timestamp.encode("utf-8") + body, bytes.fromhex(signature))
    except (BadSignatureError, ValueError):
        return False
    return True


def is_ping_interaction(payload: dict) -> bool:
    """Return True when the interaction is Discord's verification ping."""

    return payload.get("type") == PING_INTERACTION_TYPE


def discord_ping_response() -> dict:
    """Build the required ping acknowledgement payload."""

    return {"type": PING_INTERACTION_TYPE}


def discord_message_response(
    content: str | None = None,
    embeds: list[dict] | None = None,
    ephemeral: bool = False,
) -> dict:
    """Build a channel message response payload for Discord interactions."""

    data: dict[str, object] = {}
    if content:
        data["content"] = content
    if embeds:
        data["embeds"] = embeds
    if ephemeral:
        data["flags"] = EPHEMERAL_FLAG

    return {"type": CHANNEL_MESSAGE_WITH_SOURCE, "data": data}


def extract_command_identity(payload: dict) -> tuple[str | None, str | None]:
    """Extract top-level command and first subcommand names from an interaction."""

    data = payload.get("data") or {}
    command_name = data.get("name")
    subcommand_name = None

    for option in data.get("options", []):
        if option.get("type") == SUBCOMMAND_OPTION_TYPE:
            subcommand_name = option.get("name")
            break

    return command_name, subcommand_name
