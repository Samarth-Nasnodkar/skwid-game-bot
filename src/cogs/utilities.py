import discord
from discord.ext import commands
from discord_components import *
from pymongo import collection
from src.utils.textStyles import *
from src.constants.urls import bot_icon, invite_url, support_server_invite
import pymongo
from pymongo import MongoClient
import os


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongoCluster = MongoClient(os.environ.get('mongo_db_auth'))

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

    @commands.command(ame="invite")
    async def invite(self, ctx):
        """Command for inviting the bot."""

        embed = discord.Embed(title="Invite the bot",
                              description="Invite the bot using the button below and help us by voting on top.gg",
                              color=discord.Colour.purple())
        embed.set_thumbnail(url=bot_icon)

        await ctx.send(embed=embed, components=ActionRow(*[
            Button(label="Invite Me",
                   style=ButtonStyle.URL,
                   custom_id="invite",
                   url=invite_url),
            Button(label="Join Support Server",
                   style=ButtonStyle.URL,
                   custom_id="server",
                   url=support_server_invite)]))

    @commands.command(name="stats")
    async def stats(self, ctx):
        """
        Get some stats about the bot.
        """
        db = self.mongoCluster["discord_bot"]
        collection = db["realTimeStats"]
        stats = collection.find_one({'_id': 0})
        total_games = stats['totalGames']
        ongoing = stats['ongoing']
        guilds = len(self.client.guilds)
        users = 0
        for guild in self.client.guilds:
            users += guild.member_count

        embed = discord.Embed(
            title="Bot Stats",
            description=f"============\n{bold('Servers')} : `{guilds}`\n{bold('Users')} : `{users}`\n{bold('Total games')} : `{total_games}`\n{bold('Ongoing')} : `{ongoing}`\n============",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=bot_icon)
        await ctx.send(embed=embed)

    # @commands.command(name="help")
    # async def help(self, ctx):
    #     embed = discord.Embed(
    #         title="Bot Help!",
    #         description=f"{bold('Commands')}\n`help` ➜ Shows this command\n`start` ➜ Starts the game\n"
    #                     f"`prefix <new prefix>` ➜ updates the bot's prefix",
    #     )
    #     embed.set_footer(text="More commands & games coming soon.")
    #     await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Utilities(client))
