import discord
from discord.ext import commands
from discord_components import *
from src.constants.vars import MONGO_CLIENT
import random
import time
import asyncio

STIKKD_EMBED = discord.Embed(
    title="STIKK'D",
    description="You have been Stikk'd. Hold the stikk for points or pass it. It can explode anytime. And if you're "
                "holding it at that time, you'll be eliminated.",
    colour=discord.Colour.blue()
)

STIKKD_BUTTONS = [
    Button(label="Pass", custom_id="pass", style=ButtonStyle.green, emoji="🎁")
]


async def ind_stikk(client: commands.Bot, user: discord.User, timeout: int) -> dict:
    await user.create_dm()
    msg = await user.dm_channel.send(embed=STIKKD_EMBED, components=STIKKD_BUTTONS)
    start = time.time()
    try:
        await client.wait_for('button_click', timeout=timeout,
                              check=lambda x: x.user == user and x.custom_id == "pass")
    except asyncio.TimeoutError:
        return {
            "user": user,
            "result": False,
            "time": 0
        }
    else:
        btns = STIKKD_BUTTONS
        for i in range(len(btns)):
            btns[i].disabled = True
        await msg.edit(embed=STIKKD_EMBED, components=btns)
        return {
            "user": user,
            "result": True,
            "time": time.time() - start
        }


async def stikk_blast_collected(ctx, client: commands.Bot, users: list):
    users_length = len(users)
    players = users
    split_index = users_length // 2
    stikk_holders = users[:split_index]
    stikk_timeouts = []
    for user in stikk_holders:
        stikk_timeouts.append({
            "user": user,
            "timeout": random.randint(5, 30)
        })
    rest = users[split_index:]
    for stikk_holder in stikk_holders:
        res = await asyncio.gather(*[ind_stikk(client, stikk_holder, timeout=10) for stikk_holder in stikk_holders])
        for r in res:
            if not r["result"]:
                players.remove(r["user"])

