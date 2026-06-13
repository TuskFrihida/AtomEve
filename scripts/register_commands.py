"""Register (or update) AtomEve's slash commands with Discord.

Run this once after deploying, and again whenever the command list changes:

    python scripts/register_commands.py

If ``DISCORD_GUILD_ID`` is set, commands are registered for that single
server and appear instantly (ideal for development). Otherwise they are
registered globally, which can take up to an hour to propagate.

This is the *only* part of the project that uses the bot token directly, and
it runs on your machine / CI — never inside the serverless function.
"""

from __future__ import annotations

import sys
from pathlib import Path

import requests

# Allow running the script directly (``python scripts/register_commands.py``).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config  # noqa: E402

API_BASE = "https://discord.com/api/v10"

# Discord application command option types.
TYPE_STRING = 3
TYPE_USER = 6

COMMANDS: list[dict] = [
    {"name": "ping", "description": "Check that AtomEve is online and responding."},
    {"name": "help", "description": "List everything AtomEve can do."},
    {"name": "fact", "description": "Get a random science or space fact."},
    {
        "name": "avatar",
        "description": "Show a user's avatar in full size.",
        "options": [
            {
                "name": "user",
                "description": "The user whose avatar to show (defaults to you).",
                "type": TYPE_USER,
                "required": False,
            }
        ],
    },
    {
        "name": "userinfo",
        "description": "Show information about a user.",
        "options": [
            {
                "name": "user",
                "description": "The user to inspect (defaults to you).",
                "type": TYPE_USER,
                "required": False,
            }
        ],
    },
    {"name": "serverinfo", "description": "Show information about this server."},
    {
        "name": "say",
        "description": "Post a clean announcement embed.",
        "options": [
            {
                "name": "message",
                "description": "What should AtomEve announce?",
                "type": TYPE_STRING,
                "required": True,
            }
        ],
    },
    {
        "name": "poll",
        "description": "Create a native poll with up to four options.",
        "options": [
            {
                "name": "question",
                "description": "The poll question.",
                "type": TYPE_STRING,
                "required": True,
            },
            {
                "name": "option1",
                "description": "First option.",
                "type": TYPE_STRING,
                "required": True,
            },
            {
                "name": "option2",
                "description": "Second option.",
                "type": TYPE_STRING,
                "required": True,
            },
            {
                "name": "option3",
                "description": "Third option.",
                "type": TYPE_STRING,
                "required": False,
            },
            {
                "name": "option4",
                "description": "Fourth option.",
                "type": TYPE_STRING,
                "required": False,
            },
        ],
    },
]


def main() -> None:
    app_id = config.require("DISCORD_APP_ID")
    token = config.require("DISCORD_BOT_TOKEN")
    guild_id = config.GUILD_ID

    if guild_id:
        url = f"{API_BASE}/applications/{app_id}/guilds/{guild_id}/commands"
        scope = f"guild {guild_id}"
    else:
        url = f"{API_BASE}/applications/{app_id}/commands"
        scope = "globally"

    headers = {"Authorization": f"Bot {token}"}
    resp = requests.put(url, headers=headers, json=COMMANDS, timeout=15)

    if resp.status_code in (200, 201):
        print(f"Successfully registered {len(COMMANDS)} commands {scope}.")
    else:
        print(f"Failed to register commands ({resp.status_code}):")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    main()
