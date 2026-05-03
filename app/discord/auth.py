from __future__ import annotations

import logging

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

logger = logging.getLogger(__name__)


def verify_discord_signature(
    public_key: str,
    signature: str | None,
    timestamp: str | None,
    body: bytes,
) -> bool:
    '''
    Verify Discord request signature with Ed25519.

    Args:
        public_key (str): Discord application public key
        signature (str | None): Discord request signature header
        timestamp (str | None): Discord request timestamp header
        body (bytes): raw request body

    Returns:
        bool: True if signature is valid, else False
    '''
    if not signature or not timestamp:
        logger.warning('Missing Discord signature headers')
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(timestamp.encode('utf-8') + body, bytes.fromhex(signature))
        logger.debug('Discord signature verification passed')
    except (BadSignatureError, ValueError):
        logger.warning('Discord signature verification failed')
        return False
    return True
