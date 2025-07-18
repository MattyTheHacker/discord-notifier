"""Module to handle discordn-notifier"""

import discord
import dotenv
import os


dotenv.load_dotenv()

bot_token = str(os.getenv("TOKEN"))

notifier: discord.Bot = discord.Bot(  # type: ignore[no-untyped-call]
    intents=discord.Intents.default(),
)


