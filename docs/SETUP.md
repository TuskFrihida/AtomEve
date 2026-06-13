# AtomEve — Setup Guide

This guide walks through configuring the Discord application, deploying to
Vercel, and registering the slash commands. Follow it top to bottom.

---

## 1. Discord Developer Portal

Open <https://discord.com/developers/applications> and select your existing
**AtomEve** application.

### 1.1 Collect three values

You will need these for the environment variables later.

| Value              | Where to find it                                                        |
| ------------------ | ----------------------------------------------------------------------- |
| **Application ID** | *General Information* → **Application ID** (click *Copy*).               |
| **Public Key**     | *General Information* → **Public Key** (click *Copy*).                   |
| **Bot Token**      | *Bot* → **Reset Token** → *Copy*. Shown only once — store it safely.     |

> ⚠️ The **bot token** is a password for your bot. Never commit it, never paste
> it in chat or screenshots. If it ever leaks, click *Reset Token* immediately.

### 1.2 Bot settings (the "Bot" tab)

- **Privileged Gateway Intents** — leave **all three OFF** (Presence, Server
  Members, Message Content). AtomEve uses HTTP interactions, not the gateway,
  so it needs none of them. Keeping them off is the secure, least-privilege
  choice and avoids Discord's verification requirements.
- **Public Bot** — your choice. ON lets others invite it; OFF keeps it private
  to servers you add it to.

### 1.3 Which permissions are actually necessary

AtomEve is deliberately low-privilege. When you build the invite link
(next step), select **only** these:

**Scopes**
- ✅ `applications.commands` — *required* so slash commands work.
- ✅ `bot` — needed so the bot can be a member (used by `/serverinfo` and to
  post messages/polls).

**Bot Permissions**
- ✅ View Channels
- ✅ Send Messages
- ✅ Embed Links
- ✅ Use Slash Commands

You do **not** need: Administrator, Manage Server, Kick/Ban, Manage Messages,
Mention Everyone, or any voice permissions. Granting less keeps the bot safe
and easier to get approved.

### 1.4 Invite the bot to your server

1. Go to *Installation* (or *OAuth2 → URL Generator*).
2. Select the scopes and permissions listed in 1.3.
3. Copy the generated URL, open it in your browser, pick your server, and
   click **Authorize**.

The **Interactions Endpoint URL** (also on *General Information*) is filled in
*after* you deploy to Vercel — see section 3.

---

## 2. Environment variables

The bot reads four variables (see [`.env.example`](../.env.example)):

| Variable             | Required | Purpose                                            |
| -------------------- | -------- | -------------------------------------------------- |
| `DISCORD_APP_ID`     | yes      | Identifies your application for command registration. |
| `DISCORD_PUBLIC_KEY` | yes      | Verifies incoming request signatures.              |
| `DISCORD_BOT_TOKEN`  | yes      | Authenticates REST calls + command registration.  |
| `DISCORD_GUILD_ID`   | no       | If set, commands register instantly to one server. |

To get your **Guild (server) ID**: in Discord, enable *Settings → Advanced →
Developer Mode*, then right-click your server icon → *Copy Server ID*.

---

## 3. Deploy to Vercel

1. Push this repository to GitHub (see the project README / git history).
2. Go to <https://vercel.com> → **Add New… → Project** → import `AtomEve`.
3. Framework preset: **Other** (Vercel auto-detects the Python function).
4. Open **Settings → Environment Variables** and add the four variables from
   section 2 (at minimum the three required ones). Apply them to *Production*.
5. Click **Deploy**. When it finishes, note your domain, e.g.
   `https://atom-eve.vercel.app`.
6. Your interactions endpoint is:
   `https://<your-domain>/api/interactions`
7. Back in the **Developer Portal → General Information**, paste that URL into
   **Interactions Endpoint URL** and click **Save Changes**.
   - Discord immediately sends a signed test request. If signature
     verification is wired correctly, it saves successfully. If it fails,
     double-check `DISCORD_PUBLIC_KEY` in Vercel.

---

## 4. Register the slash commands

Run this once locally (with your `.env` filled in) after the endpoint is saved:

```bash
pip install -r requirements-dev.txt
python scripts/register_commands.py
```

- With `DISCORD_GUILD_ID` set → commands appear in that server **instantly**.
- Without it → commands register **globally** and may take up to ~1 hour.

---

## 5. Verify

In your Discord server, type `/` and you should see AtomEve's commands. Try:

```
/ping
/help
/fact
/poll question:"Best language?" option1:"Python" option2:"Rust"
```

If `/ping` replies, the full pipeline (Discord → Vercel → signature check →
handler → response) is working. 🎉

---

## Troubleshooting

| Symptom                                   | Likely cause / fix                                         |
| ----------------------------------------- | ---------------------------------------------------------- |
| Endpoint URL won't save in the portal     | Wrong `DISCORD_PUBLIC_KEY`, or it isn't deployed yet.      |
| Commands don't appear                     | Registration not run, or global propagation delay.        |
| `/serverinfo` shows an error              | `DISCORD_BOT_TOKEN` missing, or bot not in the server.     |
| `401` on every request                    | Signature mismatch — re-copy the Public Key into Vercel.   |
