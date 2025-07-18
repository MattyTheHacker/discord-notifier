"""Module to handle discordn-notifier"""

import discord
import dotenv
import os
import logging
import contextlib

from typing import Final, override


dotenv.load_dotenv()

notifier_ids: set[int] = set()

logger: Final[logging.Logger] = logging.getLogger("notifier")

logger.setLevel(logging.DEBUG)

console_logging_handler: logging.Handler = logging.StreamHandler()
console_logging_handler.setFormatter(
    logging.Formatter("{asctime} | {name} | {levelname:^8} - {message}", style="{")
)

logger.addHandler(console_logging_handler)


discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
discord_logger.addHandler(handler)


bot_token = os.getenv("BOT_TOKEN")

notifier: discord.Bot = discord.Bot(  # type: ignore[no-untyped-call]
    intents=discord.Intents.default(),
)


@notifier.event
async def on_ready() -> None:
    """Event handler for when the bot is ready."""
    logger.info(f"Logged in as {notifier.user}")
    logger.debug("Attempting to fetch notifier members...")

    try:
        with open("notifier_members.txt", "r") as file:
            notifier_ids.update(int(line.strip()) for line in file if line.strip().isdigit())
    except FileNotFoundError:
        logger.warning("notifier_members.txt not found. Starting with an empty set.")
        with open("notifier_members.txt", "w") as file:
            pass


@notifier.event
async def on_message(message: discord.Message) -> None:
    """Event handler for when a message is received."""
    logger.info(f"Message from {message.author}: {message.content}")

    if not message.guild or message.author.bot or message.author.id not in notifier_ids or (not isinstance(message.channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.Thread))):
        return

    for id in notifier_ids:
        user = await notifier.get_or_fetch_user(id)
        if not user:
            continue

        try:
            await user.send(f"New messages in: {message.channel.mention} on {message.guild.name}")
            logger.info(f"Sent notification to {user.name}")
        except discord.Forbidden:
            logger.warning(f"Could not send message to {user.name}, they might have DMs disabled.")


@notifier.slash_command(name="notify", description="Sign user up for notifications.")  # type: ignore[no-untyped-call, misc]
async def notify(ctx: discord.ApplicationContext):  # type: ignore[no-untyped-def, misc]
    """Slash command to register a user for notifications."""

    if ctx.author.id in notifier_ids:
        await ctx.respond("You are already registered for notifications.")
    else:
        notifier_ids.add(ctx.author.id)
        await ctx.respond("You have been registered for notifications.")
        logger.info(f"{ctx.author} has been registered for notifications.")


notifier.run(bot_token)

