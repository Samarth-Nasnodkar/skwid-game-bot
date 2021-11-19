import discord
from discord.ext import commands
from src.constants.vars import MONGO_URL, MONGO_CLIENT
from src.constants.urls import bot_icon
from src.utils.textStyles import bold


class Leaderboard(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx: commands.Context, global_: bool = False):
        """
        Displays the leaderboard.
        """
        pass


def setup(client: commands.Bot):
    client.add_cog(Leaderboard(client))
