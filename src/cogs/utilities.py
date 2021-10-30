import discord
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def clear(self, ctx, amount=5):
        if amount > 100:
            await ctx.send("You can only delete 100 messages at a time.")
            return

        try:
            await ctx.channel.purge(limit=amount)
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.")
        except discord.HTTPException:
            await ctx.send("I couldn't delete messages.")
        else:
            msg = await ctx.send(f"Deleted `{amount}` messages.")
            try:
                await msg.delete(delay=5)
            except discord.HTTPException:
                pass

    @commands.command(name="stats")
    async def stats(self, ctx):
        """
        Get some stats about the bot.
        """
        guilds = len(self.client.guilds)
        users = len(set(self.client.get_all_members()))
        channels = len(self.client.get_all_channels())
        emojis = len(self.client.emojis)
        embed = discord.Embed(
            title="Stats",
            description=f"{guilds} guilds, {users} users, {channels} channels, and {emojis} emojis.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Utilities(client))
