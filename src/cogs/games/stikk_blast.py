import discord
from discord.ext import commands
from discord_components import *
from src.constants.vars import MONGO_CLIENT
import random
import time
import asyncio

STIKKD_INTRO = "This game is called STIKK'D. Half of you will be given a stikk which you can hold or pass. Each stikk" \
               " has a 50/50 chance of either exploding and eliminating you or dropping `150` points. However, you " \
               "won't earn any **idling points** during the time you're holding the stikk.**Idling points** are the " \
               "points awarded to you every second you are not holding a stikk(between `1` to `3` points per second)" \
               "The top 50% users with respect to their points will make it to the next round. Good luck ;)."

STIKKD_EMBED = discord.Embed(
    title="STIKK'D",
    description="You have been Stikk'd. Hold the stikk or pass it. It can explode anytime. And if you're "
                "holding it at that time, there is a 50/50 chance that it will explode or give you `100` points. ",
    colour=discord.Colour.blue()
).set_footer(text="Note: You won't earn any idling points while holding the stikk.")

STIKKD_BUTTONS = [
    Button(label="Pass", custom_id="pass", style=ButtonStyle.green, emoji="🎁")
]


async def stikk(ctx, client: commands.Bot, users: list[discord.Member]):
    stikkholders = users[:len(users) // 2]
    rest = users[len(users) // 2:]
    timeout = random.randint(10, 15)
    stikks = [{"user": user, "at": time.time()} for user in stikkholders]
    eliminated = []

    print(f"{timeout=}")

    await ctx.send(STIKKD_INTRO)
    scores = {user: {'score': 0, 'time': 0} for user in users}

    for user in stikkholders:
        await user.create_dm()
        msg = await user.dm_channel.send(embed=STIKKD_EMBED, components=STIKKD_BUTTONS)

    start = time.time()
    time_delta = time.time() - start

    while time_delta < timeout:
        try:
            _i = await client.wait_for("button_click", timeout=timeout - time_delta,
                                       check=lambda x: x.user in stikkholders and x.custom_id == "pass")
        except asyncio.TimeoutError:
            for stikk in stikks:
                c = random.randint(0, 1)
                if c == 0:
                    await stikk["user"].dm_channel.send("The stikk exploded!! You're eliminated.")
                    eliminated.append(stikk["user"])
                    stikkholders.remove(stikk["user"])
                else:
                    await stikk["user"].dm_channel.send("The stikk exploded. But it dropped a `150` points. Woohoo!")
                    scores[stikk["user"]]['score'] += 150
        else:
            new_stikkholder = random.choice(rest)
            _score = int(time.time() - start - scores[_i.user]['time'])

            await _i.respond(
                type=7,
                embed=discord.Embed(
                    description=f"{new_stikkholder.name} Has been STIKK'D",
                    color=discord.Colour.red()
                ),
                components=[]

            )

            stikkholders.remove(_i.user)
            rest.append(_i.user)
            rest.remove(new_stikkholder)
            stikkholders.append(new_stikkholder)

            for stikk in stikks:
                if stikk["user"] == _i.user:
                    stikk["user"] = new_stikkholder
                    break
            await new_stikkholder.create_dm()
            await new_stikkholder.dm_channel.send(embed=STIKKD_EMBED, components=STIKKD_BUTTONS)
        finally:
            for stikk in stikks:
                scores[stikk['user']]['time'] += time.time() - stikk['at']
                stikk["at"] = time.time()
            time_delta = time.time() - start

    for u in scores:
        if u not in eliminated:
            delta = time.time() - start
            delta *= random.randint(100, 300) / 100
            scores[u]['score'] += int(delta - scores[u]['time'])
        else:
            del scores[u]

    _s = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
    _s = dict(_s[:len(_s) // 2])
    print(_s)
    await ctx.send(f"Users who made it to next round -> {' '.join([_u.mention for _u in _s])}")
