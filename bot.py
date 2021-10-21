import os

from discord.ext import commands

client = commands.Bot(command_prefix="s!", case_insensitive=True)
TOKEN = os.environ.get("discord_bot_token")


@client.command(name="hello")
async def _hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}")


client.load_extension("src.cogs.game")
client.run(TOKEN)
