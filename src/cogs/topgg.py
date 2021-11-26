import discord
from discord.ext import commands, tasks
import topgg
from src.constants.vars import TOPGG_TOKEN, INSTANCE


class TopGG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # set this to your DBL token
        self.token = TOPGG_TOKEN
        self.topgg_client = topgg.DBLClient(self.bot, self.token)
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count."""
        await self.bot.wait_until_ready()
        if INSTANCE != "primary":
            return
        try:
            server_count = len(self.bot.guilds)
            await self.topgg_client.post_guild_count(server_count)
            print("Posted server count ({})".format(server_count))
        except Exception as e:
            print("Failed to post server count\n{}: {}".format(type(e).__name__, e))


def setup(client):
    client.add_cog(TopGG(client))
