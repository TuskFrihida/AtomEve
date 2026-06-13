"""Request authentication for Discord HTTP interactions.

Every interaction Discord sends is signed with Ed25519. Discord **requires**
that we reject any request whose signature does not validate against our
application's public key (it actively probes the endpoint with bad
signatures and will refuse to save it otherwise). This module performs that
verification.
"""

from __future__ import annotations

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


def verify_signature(
    public_key: str,
    signature: str,
    timestamp: str,
    body: bytes,
) -> bool:
    """Return ``True`` only if ``signature`` is valid for the given request.

    Args:
        public_key: The application's hex-encoded Ed25519 public key.
        signature:  The hex value of the ``X-Signature-Ed25519`` header.
        timestamp:  The value of the ``X-Signature-Timestamp`` header.
        body:       The raw, unmodified request body bytes.

    The signed message is the concatenation of the timestamp and the raw
    body, so the body must be verified *before* it is parsed as JSON.
    """
    if not public_key or not signature or not timestamp:
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))
        message = timestamp.encode() + body
        verify_key.verify(message, bytes.fromhex(signature))
        return True
    except (BadSignatureError, ValueError):
        return False
