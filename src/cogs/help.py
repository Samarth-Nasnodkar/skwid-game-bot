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

    @commands.command(name="help", aliases=["h", "halp", "commands", "cmds"])
    async def help(self, ctx):  # New Help command.
        supportServer = self.client.get_guild(900056168716701696)
        menuEmoji = await supportServer.fetch_emoji(904785389418602516)
        rlglEmoji = await supportServer.fetch_emoji(904782170499981322)
        marblesEmoji = await supportServer.fetch_emoji(904783089996279884)
        honeycombEmoji = await supportServer.fetch_emoji(904782927060148224)
        glassEmoji = await supportServer.fetch_emoji(903272838822240268)
        cmdsEmoji = await supportServer.fetch_emoji(905000304951586857)
        menu_embed = discord.Embed(
            title="Help Menu",
            description=f"Click a button below to get more info on games.\n"
            f"{menuEmoji} **➜** Shows this Menu\n"
            f"{rlglEmoji} **➜** Rules of Red Light Green Light\n"
            f"{honeycombEmoji} **➜** Rules of Honeycomb\n"
            f"{marblesEmoji} **➜** Rules of Marbles\n"
            f"{glassEmoji} **➜** Rules of Glass Walk",
            color=discord.Color.purple(),
        )
        embeds["menu"] = {
            'embed': menu_embed,
            'name': 'menu'
        }
        current_embed = menu_embed
        menu_embed.set_thumbnail(url=bot_icon)
        menu_embed.set_footer(text="Click a button to get more info on games.")
        msg = await ctx.send(
            embed=current_embed,
            components=[
                ActionRow(*[
                    Button(label="‏‏‎ ‎", emoji=menuEmoji, custom_id="menu",
                           style=ButtonStyle.green),
                    Button(label="‏‏‎ ‎", emoji=rlglEmoji, custom_id="rlgl",
                           style=ButtonStyle.blue),
                    Button(label="‏‏‎ ‎", emoji=honeycombEmoji,
                           custom_id="honeycomb", style=ButtonStyle.blue),
                    Button(label="‏‏‎ ‎", emoji=marblesEmoji,
                           custom_id="marbles", style=ButtonStyle.blue),
                    Button(label="‏‏‎ ‎", emoji=glassEmoji,
                           custom_id="glass", style=ButtonStyle.blue),
                ]),
                ActionRow(*[
                    Button(label="‏‏‎ ‎", emoji=cmdsEmoji,
                           style=ButtonStyle.green, custom_id="cmds"),
                    Button(label="Vote", style=ButtonStyle.URL,
                           url="https://top.gg/bot/900054290784190507/vote", custom_id="vote"),
                    Button(label="Join the support server", style=ButtonStyle.URL,
                           custom_id="invite", url="https://discord.gg/zyyjWAjxdD")
                ])
            ])
        while True:
            try:
                i = await self.client.wait_for("button_click", timeout=60, check=lambda x: x.message.id == msg.id)
            except asyncio.TimeoutError:
                await msg.edit(
                    embed=current_embed,
                    components=[
                        ActionRow([
                            Button(label="‎‏‏‎ ‎", emoji=menuEmoji, custom_id="menu",
                                   style=ButtonStyle.green, disabled=True),
                            Button(label="‏‏‎ ‎", emoji=rlglEmoji, custom_id="rlgl",
                                   style=ButtonStyle.blue, disabled=True),
                            Button(label="‏‏‎ ‎", emoji=honeycombEmoji, custom_id="honeycomb",
                                   style=ButtonStyle.blue,    disabled=True),
                            Button(label="‏‏‎ ‎", emoji=marblesEmoji, custom_id="marbles",
                                   style=ButtonStyle.blue, disabled=True),
                            Button(label="‏‏‎ ‎", emoji=glassEmoji,
                                   custom_id="glass", style=ButtonStyle.blue, disabled=True),
                            Button(label="‏‏‎ ‎", emoji=cmdsEmoji,
                                   style=ButtonStyle.green, custom_id="cmds", disabled=True)
                        ]),
                        ActionRow([
                            Button(label="‏‏‎ ‎", emoji=cmdsEmoji,
                                   style=ButtonStyle.green, custom_id="cmds", disabled=True)
                        ])
                    ])
                return
            except Exception as e:
                print(e)
            else:
                if i.custom_id != "vote" and i.custom_id != "invite":
                    current_embed = embeds[i.component.custom_id]['embed']

                await i.respond(type=7, ephemeral=False, embed=current_embed,
                                components=[
                                    ActionRow([
                                        Button(label="‏‏‎ ‎", emoji=menuEmoji, custom_id="menu",
                                               style=ButtonStyle.green),
                                        Button(label="‏‏‎ ‎", emoji=rlglEmoji, custom_id="rlgl",
                                               style=ButtonStyle.blue),
                                        Button(label="‏‏‎ ‎", emoji=honeycombEmoji,
                                               custom_id="honeycomb", style=ButtonStyle.blue),
                                        Button(label="‏‏‎ ‎", emoji=marblesEmoji,
                                               custom_id="marbles", style=ButtonStyle.blue),
                                        Button(label="‏‏‎ ‎", emoji=glassEmoji,
                                               custom_id="glass", style=ButtonStyle.blue),
                                        Button(label="‏‏‎ ‎", emoji=cmdsEmoji,
                                               style=ButtonStyle.green, custom_id="cmds")
                                    ]),
                                    ActionRow([
                                        Button(label="‏‏‎ ‎", emoji=cmdsEmoji,
                                               style=ButtonStyle.green, custom_id="cmds"),
                                        Button(label="Vote", style=ButtonStyle.URL,
                                               url="https://top.gg/bot/900054290784190507/vote", custom_id="vote"),
                                        Button(label="Join the support server", style=ButtonStyle.URL,
                                               custom_id="invite", url="https://discord.gg/zyyjWAjxdD")
                                    ])
                                ])


def setup(client):
    client.add_cog(Help(client))
