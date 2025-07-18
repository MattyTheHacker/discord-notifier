"""Module to handle discordn-notifier"""

import discord
import dotenv
import os
import logging


dotenv.load_dotenv()


def startup() -> None:

    bot_token = os.getenv("BOT_TOKEN")

    notifier: discord.Bot = discord.Bot(  # type: ignore[no-untyped-call]
        intents=discord.Intents.default(),
    )

    notifier.run(bot_token)

    @notifier.event
    async def on_ready() -> None:
        """Event handler for when the bot is ready."""
        print(f"Logged in as {notifier.user} (ID: {notifier.user.id})")
        print("------")




if __name__ == "__main__":
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)



    startup()
