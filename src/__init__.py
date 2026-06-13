"""AtomEve — a serverless Discord bot built on the HTTP Interactions API.

The package is split into small, single-responsibility modules:

* ``config``       — loads and validates environment variables.
* ``security``     — verifies Ed25519 request signatures from Discord.
* ``embeds``       — reusable embed builders and the bot's visual theme.
* ``facts``        — static data used by the ``/fact`` command.
* ``discord_api``  — thin wrapper over the Discord REST API.
* ``commands``     — routes slash commands to their handlers.
"""

__version__ = "1.0.0"
