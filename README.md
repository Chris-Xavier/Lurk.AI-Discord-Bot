# Lurk AI Discord Bot

An opinionated Discord chatbot that leans into a "sassy-but-kind, chaotically smart" persona. The bot listens for direct mentions (or DMs) and responds using OpenAI's Chat Completion API while keeping a short rolling conversation memory per channel.

## Features

- **Custom Persona** – Carefully crafted system prompt to keep responses sharp, witty, and supportive.
- **Conversation Memory** – Maintains the last few user/assistant exchanges per channel for coherent replies.
- **Opt-in Responses** – Replies to DMs, direct mentions, or message replies to the bot.
- **Reset Command** – Use `!reset` to clear the stored history for a channel.

## Getting Started

### 1. Clone & Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file (or export the variables another way) with:

```env
DISCORD_TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-3.5-turbo  # optional override
MAX_CONTEXT_TURNS=6          # optional
OPENAI_TEMPERATURE=0.8       # optional
SYSTEM_DIRECTIVES=extra rule one||another directive  # optional, use || as separator
```

### 3. Run the Bot

```bash
python -m lurk_bot.bot
```

`python-dotenv` automatically loads the `.env` file when the bot starts, so no manual exporting is required unless you prefer it.

Invite the bot to your server, mention it, and enjoy the chaotic brainpower.

## Development Notes

- The project uses an in-memory conversation store; restarting the bot clears history.
- Error handling is intentionally light—check the console logs for stack traces when things break.
- Feel free to tweak the persona in `src/lurk_bot/persona.py` to better match your vibe.
