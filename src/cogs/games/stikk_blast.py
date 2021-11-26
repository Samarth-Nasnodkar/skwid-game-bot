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


async def stikk(ctx, client: commands.Bot, users: list[discord.User]):
    stikkholders = users[:len(users) // 2]
    rest = users[len(users) // 2:]
    timeout = random.randint(30, 60)
    stikks = [{"user": user, "at": time.time()} for user in stikkholders]
    eliminated = []
    print(f"{timeout=}")
    await ctx.send("**Round** : `STIKK BLAST`")
    # msgs = []
    scorecard = await ctx.send(embed=discord.Embed(
        title="Scoreboard : ",
        description="```{}```".format('\n'.join(f"{u.display_name} : 0" for u in users)),
        color=discord.Colour.blue()
    ))
    scores = {user: 0 for user in users}
    for user in stikkholders:
        await user.create_dm()
        msg = await user.dm_channel.send(embed=STIKKD_EMBED, components=STIKKD_BUTTONS)
        # msgs.append({
        #     "msg": msg,
        #     "to": user
        # })

    start = time.time()
    time_delta = time.time() - start

    def emj(user: discord.User):
        if user in stikkholders:
            return '⭐'
        elif user in eliminated:
            return '💥'
        else:
            return ' '
    while time_delta < timeout:
        try:
            _i = await client.wait_for("button_click", timeout=timeout - time_delta,
                                       check=lambda x: x.user in stikkholders and x.custom_id == "pass")
        except asyncio.TimeoutError:
            for stikk in stikks:
                await stikk["user"].dm_channel.send("The stikk exploded!! You're eliminated.")
                eliminated.append(stikk["user"])
                stikkholders.remove(stikk["user"])

            # for msg in msgs:
            #     if msg["to"] not in stikkholders:
            #         await msg["msg"].delete()
            #         msgs.remove(msg)
        else:
            new_stikkholder = random.choice(rest)
            await _i.respond(type=7, embed=discord.Embed(
                description=f"{new_stikkholder.name} Has been STIKK'D",
                color=discord.Colour.red()
            ),
                             components=[])
            stikkholders.remove(_i.user)
            rest.append(_i.user)
            rest.remove(new_stikkholder)
            stikkholders.append(new_stikkholder)
            for stikk in stikks:
                if stikk["user"] == _i.user:
                    stikk["user"] = new_stikkholder
                    break
            # for msg in msgs:
            #     if msg["to"] not in stikkholders:
            #         await msg["msg"].delete()
            #         msgs.remove(msg)
            await new_stikkholder.create_dm()
            await new_stikkholder.dm_channel.send(embed=STIKKD_EMBED, components=STIKKD_BUTTONS)
        finally:
            for stikk in stikks:
                scores[stikk["user"]] += int(time.time() - stikk["at"])
                stikk["at"] = time.time()

            await scorecard.edit(embed=discord.Embed(
                title="Scoreboard : ",
                description="```{}```".format('\n'.join(f"{u.display_name} : {scores[u]}"
                                                        f" {emj(u)}"for u in users)),
                colour=discord.Colour.blue()
            ))
            time_delta = time.time() - start

    # for msg in msgs:
    #     await msg["msg"].delete()
    await ctx.send(f"Users who made it to next round -> {' '.join([_u.mention for _u in rest])}")
