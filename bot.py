import os
from discord.ext import commands

client = commands.Bot(command_prefix="s!", case_insensitive=True)
TOKEN = os.environ.get("discord_bot_token")


@client.event
async def on_ready():
    print("Bot online.")


#@commands.command(name="ping", pass_context=True)
#async def ping(ctx):
#    await ctx.send(f"Pong! {client.latency}")

client.load_extension("src.cogs.game")
client.load_extension("src.cogs.utilities")
client.run(TOKEN)
