"""A very thin wrapper over the parts of the Discord REST API we use.

Only ``/serverinfo`` needs live data that is not already present in the
interaction payload, so this module is intentionally tiny.
"""

from __future__ import annotations

from typing import Any

import requests

from . import config

API_BASE = "https://discord.com/api/v10"
_TIMEOUT = 2.5  # seconds — interaction replies must be sent within 3s.


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bot {config.BOT_TOKEN}",
        "User-Agent": "AtomEve (https://github.com/TuskFrihida/AtomEve, 1.0.0)",
    }


def get_guild(guild_id: str) -> dict[str, Any] | None:
    """Fetch a guild with approximate member counts, or ``None`` on failure."""
    if not config.BOT_TOKEN or not guild_id:
        return None
    try:
        resp = requests.get(
            f"{API_BASE}/guilds/{guild_id}",
            headers=_headers(),
            params={"with_counts": "true"},
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        return None
    return None
