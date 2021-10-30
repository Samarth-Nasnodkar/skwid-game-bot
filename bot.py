import os
from discord.ext import commands

client = commands.Bot(command_prefix="s!", case_insensitive=True)
client.remove_command("help")
TOKEN = os.environ.get("discord_bot_token")


@client.event
async def on_ready():
    print("Bot online.")


client.load_extension("src.cogs.game")
client.load_extension("src.cogs.utilities")
client.run(TOKEN)
