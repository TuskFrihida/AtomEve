<h1 align="center">🌌 AtomEve</h1>

<p align="center">
  A fast, secure, <strong>serverless</strong> Discord bot built on the Discord
  HTTP Interactions API and deployed on Vercel — always available, zero
  always-on server cost.
</p>

<p align="center">
  <img alt="Python"  src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Flask"   src="https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white">
  <img alt="Vercel"  src="https://img.shields.io/badge/Deploy-Vercel-000000?logo=vercel&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## ✨ What it does

AtomEve is a utility assistant for Discord servers. Every feature is a slash
command:

| Command            | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `/ping`            | Health check — confirms the bot is online.             |
| `/help`            | Lists every available command.                         |
| `/fact`            | Sends a random science or space fact.                  |
| `/avatar [user]`   | Shows a user's avatar at full resolution.              |
| `/userinfo [user]` | Shows account details (ID, creation date, …).          |
| `/serverinfo`      | Shows live server stats (members, online, created).    |
| `/say <message>`   | Posts a clean, branded announcement embed.             |
| `/poll`            | Creates a native Discord poll with up to four options. |

## 🧠 Why serverless (and why not a "normal" bot)

A traditional `discord.py` bot keeps a **persistent gateway WebSocket** open,
which needs an always-running process. Vercel is **serverless** — functions
start on demand and stop afterwards — so a gateway bot cannot run there.

AtomEve instead uses Discord's **HTTP Interactions** model: Discord sends each
slash command as a signed HTTPS request to a single endpoint, and the function
replies. This is the architecture Discord recommends for serverless hosts, and
it means AtomEve is **available 24/7 with no idle cost** and no server to babysit.

## 🏗️ Architecture

```
Discord  ──HTTPS POST──▶  Vercel Function (api/interactions.py)
                          │
                          ├─ src/security.py     verify Ed25519 signature
                          ├─ src/commands.py     route /command → handler
                          ├─ src/embeds.py       consistent embed styling
                          ├─ src/discord_api.py  REST calls (/serverinfo)
                          └─ src/facts.py        data for /fact
```

```
AtomEve/
├── api/
│   └── interactions.py      # Vercel serverless entry point (Flask app)
├── src/                     # Reusable, testable bot logic
│   ├── config.py
│   ├── security.py
│   ├── commands.py
│   ├── embeds.py
│   ├── discord_api.py
│   └── facts.py
├── scripts/
│   └── register_commands.py # One-time slash-command registration
├── requirements.txt
├── vercel.json
└── .env.example
```

## 🔐 Security

- **Signature verification** — every request is validated with Ed25519 against
  the application public key (`src/security.py`). Forged requests get `401`.
- **No secrets in code** — tokens live only in environment variables; `.env` is
  git-ignored and never committed.
- **Least privilege** — the bot needs only the `applications.commands` scope and
  a minimal `bot` scope; no privileged gateway intents are required.

## 🚀 Quick start

### 1. Configure the Discord application
See [`docs/SETUP.md`](docs/SETUP.md) for the full Developer Portal walkthrough.

### 2. Run locally (optional)

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows
pip install -r requirements-dev.txt
copy .env.example .env           # then fill in the values
```

### 3. Deploy to Vercel
1. Import this repository on [vercel.com](https://vercel.com).
2. Add the environment variables from `.env.example` in the project settings.
3. Deploy. Your endpoint will be `https://<project>.vercel.app/api/interactions`.
4. Paste that URL into **Developer Portal → General Information → Interactions
   Endpoint URL** and save.

### 4. Register the commands

```bash
python scripts/register_commands.py
```

## 🛠️ Built with

Python · Flask · PyNaCl (Ed25519) · Requests · Discord Interactions API · Vercel

## 📄 License

Released under the [MIT License](LICENSE).
