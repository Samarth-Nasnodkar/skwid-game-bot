import discord
from time import time
from discord.ext import commands

from src.constants.owners import owners

async def ongoing(ctx: commands.Context, ongoing_games) -> None:
        if ctx.author.id not in owners:
            return

        games = ongoing_games["games"]
        embed = discord.Embed(title="Ongoing Games", colour=discord.Colour.blue())

        for game in games:
            embed.add_field(
                name=f'Server ID: {game["server_id"]}',
                value=f"`{time() - game['start_time']}`s", inline=True
            )

        await ctx.send(embed=embed)