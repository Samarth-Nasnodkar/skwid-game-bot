import time
import discord
from discord.ext import commands
from discord_components import *
import asyncio
import random


async def tug(client: commands.Bot, ctx: commands.Context, user: discord.User):
    """
    Tug of War
    """
    await user.create_dm()
    green_button = Button(label="Click!", style=ButtonStyle.green, custom_id="green", disabled=True)
    red_button = Button(label="Click!", style=ButtonStyle.red, custom_id="red", disabled=True)
    embed = discord.Embed(
        title="Tug of War",
        description=f"The buttons below will be enabled after a random interval. Be sure to click the green button"
                    f" and as fast as possible. A green button click will give your team `+1` points, but a red "
                    f"button click will give `-1` points. If both teams tie, then the team who's users took the least "
                    f"time to click the green button will win."
    )
    org_msg = await user.dm_channel.send(embed=embed, components=ActionRow([green_button, red_button]))
    time_interval = random.randint(10, 15)
    await asyncio.sleep(time_interval)
    green_button.disabled = False
    red_button.disabled = False
    start = time.time()
    time_interval = 30
    await org_msg.edit(embed=embed, components=ActionRow([green_button, red_button]))
    try:
        click = await client.wait_for('button_click', timeout=time_interval,
                                      check=lambda x: x.custom_id == "green" or x.custom_id == "red")
    except asyncio.TimeoutError:
        green_button.disabled = True
        red_button.disabled = True
        await org_msg.edit(embed=embed, components=ActionRow([green_button, red_button]))
        await user.dm_channel.send("You took too long to respond. Guess you didn't want the point")
        return {
            "points": 0,
            "time": 30
        }
    else:
        green_button.disabled = True
        red_button.disabled = True
        await org_msg.edit(embed=embed, components=ActionRow([green_button, red_button]))
        time_interval = time.time() - start
        points = 1 if click.custom_id == "green" else -1
        if click.custom_id == "green":
            await click.respond(type=4, content="You got the point!, Time Taken : `{}s`".format(time_interval))
        else:
            await click.respond(type=4,
                                content="And that's a negative point for the team. Your teammates will definitely "
                                        "be proud of you. DEFINITELY.")

        return {
            "points": points,
            "time": time_interval
        }


async def tug_collected(client: commands.Bot, ctx: commands.Context, users: list) -> list:
    length = len(users)
    if length == 1:
        await ctx.send("You need at least 2 people to play tug of war")
        return []
    bye = None
    players = users
    if length % 2 == 1:
        bye = users[-1]
        players.pop(-1)

    team_one = users[:int(length / 2)]
    team_two = users[int(length / 2):-1] if length % 2 == 1 else users[int(length / 2):]

    await ctx.send("Team One consists of {}".format(", ".join([x.mention for x in team_one])))
    await ctx.send("Team Two consists of {}".format(", ".join([x.mention for x in team_two])))

    games = await asyncio.gather(*[tug(client, ctx, user) for user in players])
    team_one_points = sum([x["points"] for x in games[:int(len(games) / 2)]])
    team_two_points = sum([x["points"] for x in games[int(len(games) / 2):]])
    team_one_time = sum([x["time"] for x in games[:int(len(games) / 2)]])
    team_one_time = round(team_one_time, 2)
    team_two_time = sum([x["time"] for x in games[int(len(games) / 2):]])
    team_two_time = round(team_two_time, 2)
    winners = []
    if team_one_points > team_two_points:
        await ctx.send("Team One wins with `{}` points over Team Two's `{}`".format(team_one_points, team_two_points))
        winners = team_one
    elif team_one_points < team_two_points:
        await ctx.send("Team Two wins with `{}` points over Team One's `{}`".format(team_two_points, team_one_points))
        winners = team_two
    else:
        if team_one_time < team_two_time:
            await ctx.send(f"Both Teams scored equal points. But Team One Wins by finishing the task in "
                           f"`{team_one_time}s` over Team Two's `{team_two_time}s`")
            winners = team_one
        elif team_one_time > team_two_time:
            await ctx.send(f"Both Teams scored equal points. But Team Two Wins by finishing the task in "
                           f"`{team_two_time}s` over Team One's `{team_one_time}s`")
            winners = team_two

    if bye:
        winners.append(bye)

    return winners
