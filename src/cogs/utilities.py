import discord
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(name="clear", aliases=["purge", "delete"])
    async def del_messages(self, ctx, amount=5):
        if amount > 100:
            await ctx.send("Cannot delete more than 100 messages")
            return
        if amount < 0:
            await ctx.send("The number of messages to be deleted should be greater than 0.")
            return
        try:
            await ctx.channel.purge(amount)
            p_msg = await ctx.send(f"Purged `{amount}` messages.")
            try:
                await p_msg.delete(delay=5)
            except discord.NotFound:
                pass
        except discord.Forbidden:
            await ctx.send("Please give the bot `manage messages` permissions and try again.")
        except discord.HTTPException:
            await ctx.send("Purging messages failed.")


def setup(client):
    client.add_cog(Utilities(client))
