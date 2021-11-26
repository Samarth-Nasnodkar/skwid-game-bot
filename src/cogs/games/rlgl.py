import discord
from discord.ext import commands
import asyncio
from src.constants.timeouts import rlgl_min_score, rlgl_timeout
import time
import random

embeds = [
    discord.Embed(description="🟢 Green Light", color=discord.Colour.green()),
    discord.Embed(description="🔴 Red Light", color=discord.Colour.red())
]


def get_timeout(rl: False) -> int:
    p = random.randint(1, 10)
    if p <= 7:
        return 8 if not rl else 2
    elif p <= 9:
        return 6 if not rl else 3
    else:
        return 4 if not rl else 4


def get_timeouts(length: int) -> list:
    rl = False
    timeouts = []
    for i in range(length):
        timeouts.append(get_timeout(rl))
        rl = not rl

    return timeouts


async def rlgl(ctx, client: commands.Bot, user: discord.User, timeout: int = 0,
               red_light=False,
               score=0):
    start = time.time()
    time_delta = time.time() - start
    count = score

    def check(message: discord.Message):
        return message.author == user and message.channel == ctx.channel

    while int(time_delta) < timeout:
        try:
            msg = await client.wait_for('message', timeout=timeout - int(time_delta),
                                        check=check)
        except asyncio.TimeoutError:
            time_delta = time.time() - start
        else:
            if red_light and count < rlgl_min_score:
                await ctx.send(f"{user.mention} Eliminated! (Red Light, score : `{count}`)")
                return None
            count += 1
            time_delta = time.time() - start

    return {
        'user': user,
        'score': count
    }


async def rlgl_collected(ctx: commands.Context, client: commands.Bot, users: list):
    red_green_intro = f"All Participants, get ready. The first game is `Red Light, Green Light`\n" \
                      f"Each participant has to send {rlgl_min_score} messages in the next `{rlgl_timeout}s`" \
                      f"\nYou can send the message when the I say **__Green Light__**. If you send a message after" \
                      f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send" \
                      f"the {rlgl_min_score} messages in the given time are eliminated too. Good luck!"

    red_green = discord.Embed(title="Welcome to Red Light, Green Light",
                              description=red_green_intro, color=discord.Colour.purple())

    await ctx.send(embed=red_green)
    timeouts = get_timeouts(4)
    print(timeouts)
    await asyncio.sleep(5)
    i = 0
    start = time.time()
    red_light = False
    finalists = [{'user': user, 'score': 0} for user in users]
    winners = []

    while time.time() - start < rlgl_timeout:
        await ctx.send(embed=embeds[int(red_light)])
        timeout = timeouts[i]
        _finalists = await asyncio.gather(
            *[rlgl(ctx, client, fin['user'],
                   timeout, red_light, fin['score']) for fin in finalists])
        red_light = not red_light
        i = (i + 1) % 4
        finalists = []
        for f in _finalists:
            if f is not None:
                if f['score'] >= rlgl_min_score:
                    if f['user'] not in winners:
                        winners.append(f['user'])
                else:
                    finalists.append(f)

        if len(finalists) == 0:
            return winners

    for f in finalists:
        await ctx.send(f"{f['user'].mention} Eliminated! Insufficient score.")

    return winners
