from typing import Union

import discord
from discord.ext import commands
import asyncio
from discord_components import *
from src.constants.timeouts import *
from src.cogs.games.marbles import marbles_collected
from src.cogs.games.rlgl import rlgl_collected
from src.cogs.games.glass import glass_game
from src.cogs.games.honeycomb import honey_collected
from src.cogs.games.tugofwar import tug_collected
from src.constants.urls import bot_icon
from src.constants.owners import owners
from src.constants.vars import MONGO_CLIENT, TOPGG_TOKEN, INSTANCE
from src.constants.ids import SUPPORT_SERVER_ID
from src.constants.player_join_options import JoinOptions
from src.utils.textStyles import *
from src.cogs.games.stikk_blast import stikk
from time import time
import topgg
from typing import Tuple, List

from src.utils.fetchEmojis import fetchEmojis

ongoing_games = {
    "ongoing": 0,
    "games": []
}


def default_stats():
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    collection.update_one({"_id": 0}, {"$set": {"ongoing": 0}})


def game_started(start_time, server_id, channel_id):
    global ongoing_games
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    collection.find_one_and_update({"_id": 0}, {"$inc": {"totalGames": 1}})
    ongoing_games["ongoing"] += 1
    ongoing_games["games"].append({
        "start_time": start_time,
        "channel_id": channel_id,
        "server_id": server_id
    })


def game_over(start_time, server_id, channel_id):
    global ongoing_games
    # db = MONGO_CLIENT["discord_bot"]
    # collection = db["realTimeStats"]
    # collection.find_one_and_update({"_id": 0}, {"$inc": {"ongoing": -1}})
    ongoing_games["ongoing"] -= 1
    ongoing_games["games"].remove({
        "start_time": start_time,
        "channel_id": channel_id,
        "server_id": server_id
    })


def log_game(data):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["logs"]
    # logs = collection.find_one({"_id": 0})
    # logs["games"].append(data)
    # logs['length'] += 1
    collection.find_one_and_update({'_id': 0}, {'$push': {'games': data}, '$inc': {'length': 1}})
    # collection.update_one({'_id': 0}, {'$set': {'games': logs['games'], 'length': logs['length']}})


async def update_vote(topgg_client, user_id: int):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["votes"]
    _vote = await topgg_client.get_user_vote(user_id)
    # if _vote:


class Game(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.topgg_client = topgg.DBLClient(self.client, TOPGG_TOKEN)
        default_stats()
        DiscordComponents(self.client)

    async def skip_game(self, game: str, ctx, host: discord.User) -> bool:
        buttons = [Button(label="Skip", custom_id="skip", style=ButtonStyle.blue)]

        embed = discord.Embed(
            description=f"Next game : **{game}**",
            color=discord.Colour.blue()
        ).set_footer(text="The Host can skip this game by clicking the button below. You have 10s.")

        def check(_i):
            return _i.user == host and _i.channel.id == ctx.channel.id

        await ctx.send(embed=embed, components=buttons)
        try:
            _i = await self.client.wait_for('button_click', check=check, timeout=10)
        except asyncio.TimeoutError:
            return False
        else:
            await _i.respond(content=f"{game} has been skipped")
            return True

    @commands.command(name="stikk")
    async def stikk_launcher(self, ctx):
        if ctx.author.id not in owners and INSTANCE == "primary":
            return
        users, err = await self.player_join(ctx)
        await stikk(ctx, self.client, users)

    @commands.command(name="play")
    async def play_single_game(self, ctx):
        supportServer = self.client.get_guild(SUPPORT_SERVER_ID)
        EMOJIS = await fetchEmojis(supportServer)

        embed = discord.Embed(
            title="Choose the Game",
            description=f"Click a button below to choose that game\n"
                        f"{EMOJIS['RLGL']} - Red Light Green Light\n"
                        f"{EMOJIS['MARBLES']} - Marbles\n"
                        f"{EMOJIS['HONEYCOMB']} - Honeycomb\n"
                        f"{EMOJIS['TEAM']} - Tug Of War\n"
                        f"{EMOJIS['GLASS']} - Glass",
            colour=discord.Colour.purple()
        )

        embed.set_footer(text="Click a button below to choose the game")

        buttons = [
            Button(emoji=EMOJIS['RLGL'], style=ButtonStyle.green, custom_id="rlgl"),
            Button(emoji=EMOJIS['MARBLES'], style=ButtonStyle.green, custom_id="marbles"),
            Button(emoji=EMOJIS['HONEYCOMB'], style=ButtonStyle.green, custom_id="honeycomb"),
            Button(emoji=EMOJIS['TEAM'], style=ButtonStyle.green, custom_id="tug"),
            Button(emoji=EMOJIS['GLASS'], style=ButtonStyle.green, custom_id="glass"),
            Button(label="Cancel", style=ButtonStyle.red, custom_id="cancel")
        ]
        msg = await ctx.send(
            embed=embed,
            components=[ActionRow(*buttons[:5]), ActionRow(*buttons[5:])]
        )

        custom_ids = ["rlgl", "marbles", "honeycomb", "glass", "tug", "cancel"]
        try:
            _interaction = await self.client.wait_for(
                'button_click',
                timeout=30,
                check=lambda x: x.custom_id in custom_ids and
                                x.user.id == ctx.author.id and
                                x.channel.id == ctx.channel.id
            )

        except asyncio.TimeoutError:
            for i in range(len(buttons)):
                buttons[i].disabled = True

            await msg.edit(
                embed=embed,
                components=[
                    ActionRow(*buttons[:5]), ActionRow(*buttons[5:])
                ]
            )

            await ctx.send("You took too long to respond. Try again later.")
        else:
            for i in range(len(buttons)):
                buttons[i].disabled = True

            await _interaction.respond(
                type=7,
                embed=embed,
                components=[
                    ActionRow(*buttons[:5]), ActionRow(*buttons[5:])
                ]
            )

            if _interaction.custom_id == "cancel":
                await ctx.send("Game cancelled.")
                return

            users, err = await self.player_join(ctx)
            if not users:
                if err == JoinOptions.NO_ERROR:
                    await ctx.send("No one joined, game ended.")
                elif err == JoinOptions.ENDED_BY_HOST:
                    await ctx.send("Game ended by host.")
                return

            if _interaction.custom_id == "rlgl":
                users = await rlgl_collected(ctx, self.client, users)

            elif _interaction.custom_id == "marbles":
                if len(users) == 1:
                    await ctx.send("You need at least 2 players to play this game.")
                    return
                users = await marbles_collected(self.client, ctx.channel, users)

            elif _interaction.custom_id == "honeycomb":
                # users = await self.honeycomb(ctx, users)
                users = await honey_collected(self.client, ctx, users)
            elif _interaction.custom_id == "tug":
                users = await tug_collected(self.client, ctx, users)
            elif _interaction.custom_id == "glass":
                users = await glass_game(self.client, ctx.channel, users)

            if len(users) == 1:
                await ctx.send(f"Congratulations {users[0].mention} on winning game!")
            elif len(users) == 0:
                await ctx.send("No one passed the game.")
            else:
                await ctx.send(f"Congratulations {', '.join([x.mention for x in users])} on winning game!")

    @commands.command(name="start")
    async def game_launcher(self, ctx: commands.Context, skip_: str = "0") -> None:
        global ongoing_games

        for game in ongoing_games["games"]:
            if game["channel_id"] == ctx.channel.id:
                await ctx.send("There is already a game running in this channel.")
                return

        time_started = time()
        game_started(time_started, ctx.guild.id, ctx.channel.id)

        try:
            skip_to = 0
            override = False
            if skip_.lower() == "skip-1":
                skip_to = 1
                override = True
            elif skip_.isnumeric():
                skip_to = int(skip_)
            data = await self.game(ctx, skip_to, override)
        except Exception as e:
            print(e)
        else:
            pass
            # data['duration'] = time() - data['start']
            # log_game(data)

        game_over(time_started, ctx.guild.id, ctx.channel.id)

    @commands.command(name="ongoing")
    async def ongoing_games(self, ctx: commands.Context) -> None:
        if ctx.author.id not in owners:
            return
        global ongoing_games
        games = ongoing_games["games"]
        embed = discord.Embed(title="Ongoing Games", colour=discord.Colour.blue())
        for game in games:
            embed.add_field(name=f'Server ID: {game["server_id"]}',
                            value=f"`{time() - game['start_time']}`s", inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx):
        """
        Get some stats about the bot.
        """
        if ctx.author.id not in owners:
            return

        global ongoing_games

        db = MONGO_CLIENT["discord_bot"]
        collection = db["realTimeStats"]

        stats = collection.find_one({'_id': 0})

        total_games = stats['totalGames']
        ongoing = ongoing_games["ongoing"]

        guilds = len(self.client.guilds)
        users = 0

        for guild in self.client.guilds:
            users += guild.member_count

        embed = discord.Embed(
            title="Bot Stats",
            description=f"{bold('Stats as given below')}",
            color=discord.Color.purple()
        )

        embed.set_thumbnail(url=bot_icon)
        embed.add_field(name=f"{bold('Servers')}", value=f"`{guilds}`", inline=True)
        embed.add_field(name=f"{bold('Users')}  ", value=f"`{users}`", inline=True)
        embed.add_field(name=f"{bold('Total games')}", value=f"`{total_games}`", inline=True)
        embed.add_field(name=f"{bold('Ongoing')}", value=f"`{ongoing}`", inline=True)

        await ctx.send(embed=embed)

    async def game(self, ctx, skip_to=0, override: bool = False) -> dict:
        data = {"start": time(), "server": ctx.guild.id}
        skipped = False

        if ctx.author.id not in owners and not override:
            skip_to = 0

        users, err = await self.player_join(ctx)
        if len(users) == 0:
            if err == JoinOptions.NO_ERROR:
                await ctx.send("No one joined. Game ended :(")
            elif err == JoinOptions.ENDED_BY_HOST:
                await ctx.send("Game ended by host.")
            return {}

        data["players"] = len(users)

        initial_players = len(users)
        if skip_to == 0:
            if len(users) > 10:
                skipped = await self.skip_game("Red Light Green Light", ctx, host=ctx.author)
            if not skipped:
                users = await rlgl_collected(ctx, self.client, users)

            skipped = False

        if not users:
            await ctx.send("None made it to the next round. Sed :(")
            data['winners'] = len(users)
            return data

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")
        if skip_to <= 1:
            # users = await self.honeycomb(ctx, users)
            if len(users) > 10:
                skipped = await self.skip_game("HoneyComb", ctx, host=ctx.author)
            if not skipped:
                users = await honey_collected(self.client, ctx, users)

            skipped = False

        if not users:
            await ctx.send("None made it to the next round. Sed :(")
            data['winners'] = len(users)
            return data

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(
                    f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                    f"*DEFINITELY Not because the other games needed more than one player and you don't"
                    f" have friends for that* ..."
                )

            data['winners'] = len(users)
            return data

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")

        if skip_to <= 2:
            if len(users) > 10:
                skipped = await self.skip_game("Tug Of War", ctx, host=ctx.author)
            if not skipped:
                users = await tug_collected(self.client, ctx, users)
            skipped = False

        if not users:
            await ctx.send("None made it to the next round. Game Ended.")
            data['winners'] = len(users)
            return data

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(
                    f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                    f"*DEFINITELY Not because the other games needed more than one player and you don't"
                    f" have friends for that* ..."
                )

            data['winners'] = len(users)
            return data
        else:
            congts_str = "Congratulations "
            for usr in users:
                congts_str += f"{usr.mention} "

            await ctx.send(f"{congts_str}\nYou have made it to the next round.")

        if skip_to <= 3:
            if len(users) > 10:
                skipped = await self.skip_game("Marbles", ctx, host=ctx.author)
            if not skipped:
                users = await marbles_collected(self.client, ctx.channel, users)

            skipped = False

        if not users:
            await ctx.send("None made it to the next round. Game Ended.")
            data['winners'] = len(users)
            return data

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(
                    f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                    f"*DEFINITELY Not because the other games needed more than one player and you don't"
                    f" have friends for that* ..."
                )

            data['winners'] = len(users)
            return data
        else:
            congts_str = "Congratulations "
            for usr in users:
                congts_str += f"{usr.mention} "

            await ctx.send(f"{congts_str}\nYou have made it to the next round.")
        # if len(users) > 10:
        #     skipped = await self.skip_game("Glass Walk", ctx, host=ctx.author)
        # if not skipped:
        users = await glass_game(self.client, ctx.channel, users)

        if users:
            await ctx.send(f"Congratulations {', '.join([usr.mention for usr in users])} on Winning the SKWID GAME.")
        else:
            await ctx.send("None managed to cross the glass bridge. Game Ended.")

        data['winners'] = len(users)
        return data

    async def player_join(self, ctx) -> Tuple[List[discord.Member], JoinOptions]:
        err = JoinOptions.UNKNOWN_EXCEPTION
        host = ctx.author
        embed = discord.Embed(
            title="Join the game",
            color=discord.Colour.blue(),
            description=f"Those who want to join the game click the Join button below"
        )

        embed.add_field(
            name="You have : ",
            value=f"`{reaction_timeout}` s"
        )
        embed.set_thumbnail(url=bot_icon)
        embed.set_footer(text="Host should click the start button to start the game!")

        buttons = [
            Button(label="Join", style=ButtonStyle.blue, emoji="🪤"),
            Button(label="Leave", style=ButtonStyle.blue),
            Button(label="Start", style=ButtonStyle.green),
            Button(label="End", style=ButtonStyle.red)
        ]

        msg = await ctx.send(embed=embed, components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])])
        labels = ["Join", "Leave", "Start", "End"]
        users = []

        def usr_check(_i):
            return _i.component.label in labels and _i.channel.id == ctx.channel.id

        def get_players_embed(_started=False):
            title = "Game Started" if _started else "Join the game"
            if len(users) <= 15:
                return discord.Embed(
                    title=title,
                    description=f"**Players joined** : `{len(users)}`\n\n"
                                f"{' '.join([u.mention for u in users])}",
                    colour=discord.Colour.blue()
                )
            else:
                return discord.Embed(
                    title=title,
                    description=f"**Players joined** : `{len(users)}`\n\n"
                                f"{' '.join([u.mention for u in users[:15]])}...and `{len(users) - 15}` more",
                    colour=discord.Colour.blue()
                )

        started = False

        while not started:
            try:
                interation = await self.client.wait_for(
                    'button_click',
                    check=usr_check,
                    timeout=30
                )

            except asyncio.TimeoutError:
                started = True
            else:
                try:
                    if interation.component.label == "Join":
                        if interation.user not in users:
                            users.append(interation.user)
                        await interation.respond(
                            type=7,
                            embed=get_players_embed(),
                            components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])]
                        )

                    elif interation.component.label == "Leave":
                        if interation.user in users:
                            users.remove(interation.user)
                        await interation.respond(
                            type=7,
                            embed=get_players_embed(),
                            components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])]
                        )

                    elif interation.component.label == "Start":
                        if interation.user == host:
                            started = True
                            for i in range(len(buttons)):
                                buttons[i].disabled = True
                            await interation.respond(
                                type=7,
                                embed=get_players_embed(_started=True),
                                components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])]
                            )

                        else:
                            await interation.respond(content="Please wait for the host to start the game")
                    elif interation.component.label == "End":
                        if interation.user == host:
                            started = True
                            for i in range(len(buttons)):
                                buttons[i].disabled = True
                            await interation.respond(
                                type=7,
                                embed=get_players_embed(),
                                components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])]
                            )
                            err = JoinOptions.ENDED_BY_HOST
                        else:
                            await interation.respond(content="Please ask the host to end the game")
                except discord.NotFound:
                    pass

        res = []
        for usr in users:
            if usr not in res:
                res.append(usr)

        users = res

        if len(users) == 0:
            await msg.edit(
                embed=discord.Embed(
                    title="Game Ended!",
                    description=f"No One joined :(",
                    color=discord.Colour.blue()
                ),
                components=[ActionRow(*buttons[:2]), ActionRow(*buttons[2:])]
            )
            err = JoinOptions.NO_ERROR
            return [], err

        return users, err


def setup(client):
    client.add_cog(Game(client))
