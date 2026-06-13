"""Reusable embed builders that give AtomEve a consistent visual identity.

Keeping all presentation logic here means command handlers stay focused on
*what* to say while this module decides *how* it looks.
"""

from __future__ import annotations

from typing import Any

# Brand colour (a cosmic indigo) used across every embed for a cohesive look.
BRAND_COLOR = 0x5865F2  # Discord blurple — recognisable and on-theme.
SUCCESS_COLOR = 0x57F287
ERROR_COLOR = 0xED4245
FOOTER_TEXT = "AtomEve • serverless Discord bot"


def base_embed(title: str, description: str = "", color: int = BRAND_COLOR) -> dict[str, Any]:
    """Create an embed pre-filled with the bot's standard footer and colour."""
    embed: dict[str, Any] = {
        "title": title,
        "color": color,
        "footer": {"text": FOOTER_TEXT},
    }
    if description:
        embed["description"] = description
    return embed


def error_embed(message: str) -> dict[str, Any]:
    """A red embed used to surface user-facing errors politely."""
    return base_embed("Something went wrong", message, ERROR_COLOR)


def add_field(embed: dict[str, Any], name: str, value: str, inline: bool = True) -> None:
    """Append a field to an embed, creating the ``fields`` list on demand."""
    embed.setdefault("fields", []).append(
        {"name": name, "value": value, "inline": inline}
    )
