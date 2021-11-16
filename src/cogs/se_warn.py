import discord
from discord.ext import commands
from discord_components import *
from src.constants.urls import invite_url


async def se_warn(ctx):
    """
    Will give the user a pop-up to invite the primary bot.
    """
    inv_button = Button(
        label="Invite Bot!",
        style=ButtonStyle.URL,
        url=invite_url
    )
    await ctx.send(embed=discord.Embed(
        title="This bot has been deprecated",
        description="This bot was made as a replacement for the primary bot until it got verified by "
                    "Discord. It has now been verified by discord. So please invite that bot using the button "
                    "below and kick me. Thanks :)",
        color=discord.Color.red()
    ), components=[inv_button])
