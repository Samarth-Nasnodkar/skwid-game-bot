from asyncio.tasks import current_task
import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord_components import *
from discord_components.dpy_overrides import send_files
from src.cogs.utilities import setup
from src.constants.help_embeds import embeds
from src.constants.urls import bot_icon
import asyncio


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.menuEmoji = self.client.get_emoji(904785389418602516)
        self.rlglEmoji = self.client.get_emoji(904782170499981322)
        self.marblesEmoji = self.client.get_emoji(904783089996279884)
        self.honeycombEmoji = self.client.get_emoji(904782927060148224)
        self.glassEmoji = self.client.get_emoji(903272838822240268)

    @commands.command()
    async def help(self, ctx):
        menu_embed = discord.Embed(
            title="Help Menu",
            description=f"Click a button below to get more info on games.\n"
            f"{self.menuEmoji} **➜** Shows this Menu\n"
            f"{self.rlglEmoji} **➜** Rules of Red Light Green Light\n"
            f"{self.honeycombEmoji} **➜** Rules of Honeycomb\n"
            f"{self.marblesEmoji} **➜** Rules of Marbles\n"
            f"{self.glassEmoji} **➜** Rules of Glass Walk",
            color=discord.Color.purple(),
        )
        current_embed = menu_embed
        menu_embed.set_thumbnail(url=bot_icon)
        menu_embed.set_footer(text="Click a button to get more info on games.")
        msg = await ctx.send(
            embed=current_embed,
            components=[
                Button(emoji=self.menuEmoji, custom_id="menu",
                       style=ButtonStyle.green),
                Button(emoji=self.rlglEmoji, custom_id="rlgl",
                       style=ButtonStyle.blue),
                Button(emoji=self.honeycombEmoji,
                       custom_id="honeycomb", style=ButtonStyle.blue),
                Button(emoji=self.marblesEmoji,
                       custom_id="marbles", style=ButtonStyle.blue),
            ])
        while True:
            try:
                i = await self.client.wait_for("button_click", timeout=60, check=lambda x: x.message.id == msg.id)
            except asyncio.TimeoutError:
                await msg.edit(
                    embed=current_embed,
                    components=[
                        Button(emoji=self.menuEmoji, custom_id="menu",
                               style=ButtonStyle.green, disabled=True),
                        Button(emoji=self.rlglEmoji, custom_id="rlgl",
                               style=ButtonStyle.blue, disabled=True),
                        Button(emoji=self.honeycombEmoji, custom_id="honeycomb",
                               style=ButtonStyle.blue,    disabled=True),
                        Button(emoji=self.marblesEmoji, custom_id="marbles",
                               style=ButtonStyle.blue, disabled=True),
                    ])
                return
            else:
                current_embed = embeds[i.custom_id]
                await msg.edit(
                    embed=current_embed,
                    components=[
                        Button(emoji=self.menuEmoji, custom_id="menu",
                               style=ButtonStyle.green),
                        Button(emoji=self.rlglEmoji, custom_id="rlgl",
                               style=ButtonStyle.blue),
                        Button(emoji=self.honeycombEmoji,
                               custom_id="honeycomb", style=ButtonStyle.blue),
                        Button(emoji=self.marblesEmoji,
                               custom_id="marbles", style=ButtonStyle.blue),
                    ])


def setup(client):
    client.add_cog(Help(client))
