import discord
from discord.ext import commands

from src.constants.vars import MONGO_CLIENT
from src.constants.owners import owners
from src.constants.urls import bot_icon

from src.utils.textStyles import *

async def stats(client: discord.Client, ctx: commands.Context, ongoing_games):
    """
    Get some stats about the bot.
    """
    if ctx.author.id not in owners:
        return

    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]

    stats = collection.find_one({'_id': 0})

    total_games = stats['totalGames']
    ongoing = ongoing_games["ongoing"]

    guilds = len(client.guilds)
    users = 0

    for guild in client.guilds:
        users += guild.member_count

    embed = discord.Embed(
        title="Bot Stats",
        description=f"{bold('Stats as given below')}",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=bot_icon)
    embed.add_field(name=f"{bold('Servers')}", value=f"`{guilds}`", inline=True)
    embed.add_field(name=f"{bold('Users')}  ", value=f"`{users}`", inline=True)
    embed.add_field(name=f"{bold('Total games')}", value=f"`{total_games}`", inline=True)
    embed.add_field(name=f"{bold('Ongoing')}", value=f"`{ongoing}`", inline=True)

    await ctx.send(embed=embed)