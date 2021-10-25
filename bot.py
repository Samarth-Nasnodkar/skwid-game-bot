import os
from discord.ext import commands

client = commands.Bot(command_prefix="s!", case_insensitive=True)
#TOKEN = os.environ.get("discord_bot_token")


@client.event
async def on_ready():
    print("Bot online.")

client.load_extension("src.cogs.game")
client.run("OTAwMDU0MjkwNzg0MTkwNTA3.YW7u4Q.ExvJVezj77_LAzxJFVZxrP3rv_U")
