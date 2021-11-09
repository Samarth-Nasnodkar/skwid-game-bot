import discord
from discord.ext import commands
from src.constants.urls import bot_icon
from discord_components import *


class Global(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="global")
    async def _global_launcher(self, ctx):
        """This will Launch the Global Menu"""
        buttons = [
            Button(label="🎯", custom_id="join", style=ButtonStyle.green),
            Button(label="🚀", custom_id="host", style=ButtonStyle.green),
        ]
        await ctx.send(embed=discord.Embed(
            title="Welcome to Global matchmaking!",
            description="Press the following buttons to join/host a game\n"
                        f"\🎯 **➜** Join Game\n"
                        f"\🚀 **➜** Host Game\n",
            colour=discord.Colour.blue()
        ).set_thumbnail(url=bot_icon),
                       components=ActionRow(buttons)
                       )


def setup(client):
    client.add_cog(Global(client))
