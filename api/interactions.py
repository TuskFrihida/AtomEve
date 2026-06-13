"""Vercel serverless entry point for AtomEve.

Discord delivers every interaction as an HTTPS ``POST`` to this endpoint.
The function:

1. Verifies the Ed25519 signature (rejecting anything not from Discord).
2. Replies to Discord's ``PING`` (type 1) health checks with a ``PONG``.
3. Routes application commands (type 2) to the command handlers.

Vercel exposes the module-level Flask ``app`` object as the function handler.
"""

from __future__ import annotations

import os
import sys

# Make the sibling ``src`` package importable when Vercel bundles the function.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request  # noqa: E402

from src import commands, config  # noqa: E402
from src.security import verify_signature  # noqa: E402

app = Flask(__name__)

# Discord interaction type constants.
PING = 1
APPLICATION_COMMAND = 2

# Response type constants.
PONG = 1
CHANNEL_MESSAGE_WITH_SOURCE = 4


@app.route("/api/interactions", methods=["POST"])
def interactions():
    """Validate and handle a single Discord interaction."""
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    raw_body = request.get_data()  # raw bytes — required for signature checks.

    if not verify_signature(config.PUBLIC_KEY, signature, timestamp, raw_body):
        # Discord expects exactly 401 for invalid signatures.
        return "invalid request signature", 401

    interaction = request.get_json(silent=True) or {}
    interaction_type = interaction.get("type")

    if interaction_type == PING:
        return jsonify({"type": PONG})

    if interaction_type == APPLICATION_COMMAND:
        data = commands.handle_command(interaction)
        return jsonify({"type": CHANNEL_MESSAGE_WITH_SOURCE, "data": data})

    # Any other interaction type is acknowledged but not acted upon.
    return jsonify({"type": PONG})


@app.route("/api/interactions", methods=["GET"])
def health():
    """A simple health page so visiting the URL in a browser is friendly."""
    return jsonify({"name": "AtomEve", "status": "online"})
