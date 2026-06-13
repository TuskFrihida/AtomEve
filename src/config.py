"""Centralised configuration loaded from environment variables.

On Vercel these are provided through the project's *Environment Variables*
settings. Locally they are read from a ``.env`` file (see ``.env.example``)
when the optional ``python-dotenv`` package is installed.
"""

from __future__ import annotations

import os

# Load a local .env file when developing. This is a no-op in production
# (Vercel injects real environment variables) and is wrapped in a try/except
# so the bot never crashes if python-dotenv is not installed.
try:  # pragma: no cover - convenience only
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass


APP_ID: str = os.environ.get("DISCORD_APP_ID", "")
PUBLIC_KEY: str = os.environ.get("DISCORD_PUBLIC_KEY", "")
BOT_TOKEN: str = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD_ID: str = os.environ.get("DISCORD_GUILD_ID", "")


def require(name: str) -> str:
    """Return an environment variable or raise a clear error if it is missing.

    Used by scripts (e.g. command registration) where a missing value should
    fail loudly rather than silently send an unauthenticated request.
    """
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in your .env file or in the Vercel project settings."
        )
    return value
