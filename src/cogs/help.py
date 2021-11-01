import discord
from discord.ext import commands
from discord_components import *


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        pass
