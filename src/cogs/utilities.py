import discord
from discord.ext import commands
from discord_components import *
from src.utils.textStyles import *
from src.constants.urls import bot_icon, invite_url, support_server_invite
from src.constants.owners import owners
from src.constants.vars import MONGO_URL, INSTANCE, MONGO_CLIENT

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

    @commands.command(name="ping")
    async def ping(self, ctx):
        """
        Get the bot's ping.
        """
        await ctx.send(f"Bot ping : `{round(self.client.latency * 1000)}`ms")

    @commands.command(name="invite")
    async def invite(self, ctx):
        """Command for inviting the bot."""
        embed = discord.Embed(
            title="Invite the bot",
            description="Invite the bot using the button below and help us by voting on top.gg",
            color=discord.Colour.purple()
        )
        embed.set_thumbnail(url=bot_icon)

        await ctx.send(
            embed=embed,
            components=ActionRow([
                Button(
                    label="Invite Me",
                    style=ButtonStyle.URL,
                    custom_id="invite",
                    url=invite_url
                ),
                Button(
                    label="Join Support Server",
                    style=ButtonStyle.URL,
                    custom_id="server",
                    url=support_server_invite
                )
            ])
        )

    # @commands.command(name="stats")
    # async def stats(self, ctx):
    #     """
    #     Get some stats about the bot.
    #     """
    #     if ctx.author.id not in owners:
    #         return
    #
    #     db = MONGO_CLIENT["discord_bot"]
    #     collection = db["realTimeStats"]
    #
    #     stats = collection.find_one({'_id': 0})
    #
    #     total_games = stats['totalGames']
    #     ongoing = stats['ongoing']
    #
    #     guilds = len(self.client.guilds)
    #     users = 0
    #
    #     for guild in self.client.guilds:
    #         users += guild.member_count
    #
    #     embed = discord.Embed(
    #         title="Bot Stats",
    #         description=f"{bold('Stats as given below')}",
    #         color=discord.Color.purple()
    #     )
    #
    #     embed.set_thumbnail(url=bot_icon)
    #     embed.add_field(name=f"{bold('Servers')}", value=f"`{guilds}`", inline=True)
    #     embed.add_field(name=f"{bold('Users')}  ", value=f"`{users}`", inline=True)
    #     embed.add_field(name=f"{bold('Total games')}", value=f"`{total_games}`", inline=True)
    #     embed.add_field(name=f"{bold('Ongoing')}", value=f"`{ongoing}`", inline=True)
    #
    #     await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Utilities(client))
