"""Discord bot implementation for the Lurk AI assistant."""

from __future__ import annotations

import asyncio
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

from .config import Settings
from .llm import ChatModel
from .memory import ConversationMemory


log = logging.getLogger(__name__)


class LurkBot(commands.Bot):
    """Custom Discord bot wired to an OpenAI chat model."""

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = False
        intents.presences = False

        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.settings = settings
        self.chat_model = ChatModel(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=settings.temperature,
            system_directives=settings.system_directives,
        )
        self.memory = ConversationMemory(max_turns=settings.max_context_turns)

    async def setup_hook(self) -> None:
        await self.add_cog(ChatCog(self))


class ChatCog(commands.Cog):
    """Cog that listens for messages and routes them to the language model."""

    def __init__(self, bot: LurkBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info("Logged in as %s (%s)", self.bot.user, self.bot.user and self.bot.user.id)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # Ignore the bot's own messages or other bots.
        if message.author.bot:
            return

        if not await self._should_respond(message):
            return

        channel_id = message.channel.id
        content = message.content.strip()

        # Store the user message in history prior to response generation.
        self.bot.memory.append_user_only(channel_id, content)

        async with message.channel.typing():
            try:
                history = self.bot.memory.iter_history(channel_id)
                response = await self.bot.chat_model.generate_reply(history, content)
            except Exception as exc:  # pragma: no cover - best-effort logging
                log.exception("Error while generating response: %s", exc)
                await message.reply(
                    "My brain just tripped over its own shoelaces. Give me a sec and try again."
                )
                return

        # Save the assistant response and send it.
        self.bot.memory.append_assistant_only(channel_id, response)
        await message.reply(response, mention_author=False)

    async def _should_respond(self, message: discord.Message) -> bool:
        """Check whether the bot should respond to this message."""

        if isinstance(message.channel, discord.DMChannel):
            return True

        if not self.bot.user:
            return False

        mentioned = any(user.id == self.bot.user.id for user in message.mentions)
        reply_to_bot = message.reference and isinstance(message.reference.resolved, discord.Message)
        if reply_to_bot and message.reference.resolved.author == self.bot.user:
            return True
        return mentioned

    @commands.command(name="reset")
    async def reset_history(self, ctx: commands.Context) -> None:
        """Slash-style command to clear the channel's stored conversation."""

        self.bot.memory.clear(ctx.channel.id)
        await ctx.reply("Alright, fresh slate. What chaos are we conjuring now?", mention_author=False)


async def run_bot() -> None:
    """Entrypoint for running the bot from an async context."""

    load_dotenv()
    settings = Settings.from_env()
    bot = LurkBot(settings)

    async with bot:
        await bot.start(settings.discord_token)


def main() -> None:
    """Synchronous wrapper used when running via ``python -m``."""

    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:  # pragma: no cover - interactive signal
        log.info("Bot shutdown requested by user")


if __name__ == "__main__":
    main()
