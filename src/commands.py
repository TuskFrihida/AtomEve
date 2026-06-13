"""Slash-command routing and handlers.

Each handler receives the raw interaction payload and returns the ``data``
object for a *CHANNEL_MESSAGE_WITH_SOURCE* (type 4) response. The public
entry point is :func:`handle_command`, which dispatches by command name.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from . import discord_api, embeds, facts

# --- Discord epoch helpers -------------------------------------------------

DISCORD_EPOCH = 1420070400000  # 2015-01-01T00:00:00Z, in milliseconds.


def _snowflake_to_dt(snowflake: str) -> datetime:
    """Convert a Discord ID (snowflake) into its creation timestamp (UTC)."""
    ms = (int(snowflake) >> 22) + DISCORD_EPOCH
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def _discord_timestamp(dt: datetime, style: str = "F") -> str:
    """Format a datetime as a Discord dynamic timestamp (renders client-side)."""
    return f"<t:{int(dt.timestamp())}:{style}>"


# --- Option / payload helpers ----------------------------------------------


def _options(interaction: dict[str, Any]) -> dict[str, Any]:
    """Flatten a command's options into a ``{name: value}`` mapping."""
    data = interaction.get("data", {})
    return {opt["name"]: opt.get("value") for opt in data.get("options", [])}


def _avatar_url(user: dict[str, Any]) -> str:
    """Build the best available avatar URL for a resolved user object."""
    user_id = user["id"]
    avatar = user.get("avatar")
    if avatar:
        ext = "gif" if avatar.startswith("a_") else "png"
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.{ext}?size=1024"
    # Fallback to one of Discord's default avatars.
    index = (int(user_id) >> 22) % 6
    return f"https://cdn.discordapp.com/embed/avatars/{index}.png"


def _resolved_user(interaction: dict[str, Any], option_name: str) -> dict[str, Any]:
    """Return the user referenced by an option, or the invoking user."""
    data = interaction.get("data", {})
    opts = _options(interaction)
    resolved_users = data.get("resolved", {}).get("users", {})

    target_id = opts.get(option_name)
    if target_id and target_id in resolved_users:
        return resolved_users[target_id]

    # No option given -> fall back to the person who ran the command.
    member = interaction.get("member") or {}
    return member.get("user") or interaction.get("user", {})


def _message(data: dict[str, Any], ephemeral: bool = False) -> dict[str, Any]:
    """Wrap response data, optionally marking it ephemeral (flag 1 << 6)."""
    if ephemeral:
        data["flags"] = 1 << 6
    return data


# --- Command handlers ------------------------------------------------------


def _ping(_: dict[str, Any]) -> dict[str, Any]:
    embed = embeds.base_embed(
        "🏓 Pong!",
        "AtomEve is online and responding through Vercel's serverless edge.",
        embeds.SUCCESS_COLOR,
    )
    return _message({"embeds": [embed]})


def _fact(_: dict[str, Any]) -> dict[str, Any]:
    embed = embeds.base_embed("🔬 Did you know?", facts.random_fact())
    return _message({"embeds": [embed]})


def _avatar(interaction: dict[str, Any]) -> dict[str, Any]:
    user = _resolved_user(interaction, "user")
    name = user.get("global_name") or user.get("username", "Unknown")
    url = _avatar_url(user)
    embed = embeds.base_embed(f"🖼️ {name}'s avatar")
    embed["image"] = {"url": url}
    embed["description"] = f"[Open original]({url})"
    return _message({"embeds": [embed]})


def _userinfo(interaction: dict[str, Any]) -> dict[str, Any]:
    user = _resolved_user(interaction, "user")
    name = user.get("global_name") or user.get("username", "Unknown")
    created = _snowflake_to_dt(user["id"])

    embed = embeds.base_embed(f"👤 {name}")
    embed["thumbnail"] = {"url": _avatar_url(user)}
    embeds.add_field(embed, "Username", f"@{user.get('username', 'unknown')}")
    embeds.add_field(embed, "User ID", f"`{user['id']}`")
    embeds.add_field(embed, "Bot account", "Yes" if user.get("bot") else "No")
    embeds.add_field(
        embed, "Account created", _discord_timestamp(created, "F"), inline=False
    )
    return _message({"embeds": [embed]})


def _serverinfo(interaction: dict[str, Any]) -> dict[str, Any]:
    guild_id = interaction.get("guild_id")
    if not guild_id:
        return _message(
            {"embeds": [embeds.error_embed("This command can only be used in a server.")]},
            ephemeral=True,
        )

    guild = discord_api.get_guild(guild_id)
    if not guild:
        return _message(
            {
                "embeds": [
                    embeds.error_embed(
                        "Couldn't fetch server details. Make sure the bot token is "
                        "configured and the bot is a member of this server."
                    )
                ]
            },
            ephemeral=True,
        )

    created = _snowflake_to_dt(guild["id"])
    embed = embeds.base_embed(f"🌐 {guild.get('name', 'This server')}")
    if guild.get("icon"):
        embed["thumbnail"] = {
            "url": f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png?size=512"
        }
    embeds.add_field(embed, "Server ID", f"`{guild['id']}`")
    embeds.add_field(
        embed, "Members", str(guild.get("approximate_member_count", "—"))
    )
    embeds.add_field(
        embed, "Online", str(guild.get("approximate_presence_count", "—"))
    )
    if guild.get("description"):
        embeds.add_field(embed, "Description", guild["description"], inline=False)
    embeds.add_field(embed, "Created", _discord_timestamp(created, "F"), inline=False)
    return _message({"embeds": [embed]})


def _say(interaction: dict[str, Any]) -> dict[str, Any]:
    opts = _options(interaction)
    message = (opts.get("message") or "").strip()
    if not message:
        return _message(
            {"embeds": [embeds.error_embed("You need to provide a message.")]},
            ephemeral=True,
        )
    embed = embeds.base_embed("📣 Announcement", message)
    return _message({"embeds": [embed]})


def _poll(interaction: dict[str, Any]) -> dict[str, Any]:
    opts = _options(interaction)
    question = (opts.get("question") or "").strip()
    answers = [
        opts[key].strip()
        for key in ("option1", "option2", "option3", "option4")
        if opts.get(key) and opts[key].strip()
    ]
    if not question or len(answers) < 2:
        return _message(
            {
                "embeds": [
                    embeds.error_embed(
                        "Provide a question and at least two options to create a poll."
                    )
                ]
            },
            ephemeral=True,
        )

    # Use Discord's native poll object so votes are tracked by the platform.
    return _message(
        {
            "poll": {
                "question": {"text": question[:300]},
                "answers": [
                    {"poll_media": {"text": ans[:55]}} for ans in answers
                ],
                "duration": 24,  # hours
                "allow_multiselect": False,
            }
        }
    )


def _help(_: dict[str, Any]) -> dict[str, Any]:
    embed = embeds.base_embed(
        "🤖 AtomEve — Command Guide",
        "A fast, serverless Discord assistant. Here's what I can do:",
    )
    embeds.add_field(embed, "/ping", "Check that the bot is online.", inline=False)
    embeds.add_field(embed, "/fact", "Get a random science or space fact.", inline=False)
    embeds.add_field(embed, "/avatar [user]", "Show a user's avatar in full size.", inline=False)
    embeds.add_field(embed, "/userinfo [user]", "Show details about a user.", inline=False)
    embeds.add_field(embed, "/serverinfo", "Show details about this server.", inline=False)
    embeds.add_field(embed, "/poll", "Create a native poll (2–4 options).", inline=False)
    embeds.add_field(embed, "/say <message>", "Post a clean announcement embed.", inline=False)
    return _message({"embeds": [embed]})


# --- Dispatch table --------------------------------------------------------

_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "ping": _ping,
    "fact": _fact,
    "avatar": _avatar,
    "userinfo": _userinfo,
    "serverinfo": _serverinfo,
    "poll": _poll,
    "say": _say,
    "help": _help,
}


def handle_command(interaction: dict[str, Any]) -> dict[str, Any]:
    """Dispatch an APPLICATION_COMMAND interaction to its handler."""
    name = interaction.get("data", {}).get("name", "")
    handler = _HANDLERS.get(name)
    if handler is None:
        return _message(
            {"embeds": [embeds.error_embed(f"Unknown command: `{name}`.")]},
            ephemeral=True,
        )
    return handler(interaction)
