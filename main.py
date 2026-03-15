"""Module to handle discordn-notifier"""

import discord
import dotenv
import os
import logging

from typing import Final


dotenv.load_dotenv()

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

bot_token: Final[str] = os.getenv("BOT_TOKEN", "")

if not bot_token:
    logger.critical("BOT_TOKEN environment variable is not set.")
    raise EnvironmentError("BOT_TOKEN environment variable is required.")

user_id_to_notify: Final[int] = int(os.getenv("USER_ID_TO_NOTIFY", "0"))

notifier: discord.Bot = discord.Bot(  # type: ignore[no-untyped-call]
    intents=discord.Intents.default(),
)


@notifier.event
async def on_ready() -> None:
    """Event handler for when the bot is ready."""
    logger.info(f"Logged in as {notifier.user}")


@notifier.event
async def on_message(message: discord.Message) -> None:
    """Event handler for when a message is received."""
    logger.info(f"Message from {message.author}: {message.content}")

    if (
        not message.guild
        or message.author.bot
        or message.author.id == user_id_to_notify
        or (not isinstance(message.channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.Thread)))
    ):
        return

    user_to_notify: discord.User | None = await notifier.get_or_fetch_user(user_id_to_notify)
    if not user_to_notify:
        logger.error(f"User with ID {user_id_to_notify} not found.")
        return

    try:
        await user_to_notify.send(f"New messages in: {message.channel.mention} on {message.guild.name}")
        logger.info(f"Sent notification to {user_to_notify.name}")
    except discord.Forbidden:
        logger.warning(f"Could not send message to {user_to_notify.name}, they might have DMs disabled.")


@notifier.slash_command(  # type: ignore[no-untyped-call, misc]
    name="export",
    description="Export the last certain number of messages from the current channel.",
)
async def export_message(ctx: discord.ApplicationContext) -> None:  # type: ignore[misc]
    """Slash command to export messages from the current channel."""
    logger.info(f"Export command invoked by {ctx.author} in {ctx.channel}")

    if not ctx.channel:
        await ctx.respond("This command can only be used in a text channel.", ephemeral=True)
        return
    
    await ctx.defer(ephemeral=True)
    
    channel_messages: list[tuple[str, str, str]] = []

    channel: discord.TextChannel = ctx.channel
    message: discord.Message

    async for message in channel.history():
        channel_messages.append((message.author.name, message.content, message.created_at.isoformat()))

    with open("exported_messages.txt", "w", encoding="utf-8") as file:
        for author, content, timestamp in channel_messages:
            file.write(f"{timestamp} | {author}: {content}\n")

    file.close()
    
    await ctx.followup.send("Messages exported successfully!", ephemeral=True, file=discord.File("exported_messages.txt"))


notifier.run(bot_token)

