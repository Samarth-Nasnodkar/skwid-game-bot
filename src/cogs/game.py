import discord
from discord.ext import commands
import asyncio
from discord_components import *
from src.constants.timeouts import *
from src.cogs.marbles import marbles_collected
from src.cogs.rlgl import rlgl_collected
from src.cogs.glass import glass_game
from src.cogs.honeycomb import honey_collected
from src.cogs.tugofwar import tug_collected
from src.constants.urls import bot_icon
from src.constants.owners import owners
from src.constants.vars import INSTANCE, MONGO_CLIENT
from src.cogs.stikk_blast import stikk


def default_stats():
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    collection.update_one({"_id": 0}, {"$set": {"ongoing": 0}})


def game_started():
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    stats = collection.find_one({"_id": 0})
    ongoing = stats["ongoing"]
    totalGames = stats["totalGames"]
    ongoing = ongoing if ongoing > 0 else 0
    collection.update_one(
        {"_id": 0}, {"$set": {"ongoing": ongoing + 1, "totalGames": totalGames + 1}})


def game_over():
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    stats = collection.find_one({"_id": 0})
    ongoing = stats["ongoing"]
    ongoing = ongoing - 1 if ongoing > 0 else 0
    collection.update_one({"_id": 0}, {"$set": {"ongoing": ongoing}})


class Game(commands.Cog):

    def __init__(self, client):
        self.client: commands.Bot = client
        default_stats()
        DiscordComponents(self.client)

    @commands.command(name="stikk")
    async def stikk_launcher(self, ctx):
        if ctx.author.id not in owners:
            return
        users = await self.player_join(ctx)
        await stikk(ctx, self.client, users)

    @commands.command(name="play")
    async def play_single_game(self, ctx):
        supportServer = self.client.get_guild(900056168716701696)
        rlglEmoji = await supportServer.fetch_emoji(904782170499981322)
        marblesEmoji = await supportServer.fetch_emoji(904783089996279884)
        honeycombEmoji = await supportServer.fetch_emoji(904782927060148224)
        glassEmoji = await supportServer.fetch_emoji(903272838822240268)
        teamEmoji = await supportServer.fetch_emoji(906440335893356544)

        embed = discord.Embed(
            title="Choose the Game",
            description=f"Click a button below to choose that game\n"
                        f"{rlglEmoji} - Red Light Green Light\n"
                        f"{marblesEmoji} - Marbles\n"
                        f"{honeycombEmoji} - Honeycomb\n"
                        f"{teamEmoji} - Tug Of War\n"
                        f"{glassEmoji} - Glass",
            colour=discord.Colour.purple()
        )
        embed.set_footer(text="Click a button below to choose the game")
        buttons = [
            Button(emoji=rlglEmoji,
                   style=ButtonStyle.green, custom_id="rlgl"),
            Button(emoji=marblesEmoji,
                   style=ButtonStyle.green, custom_id="marbles"),
            Button(emoji=honeycombEmoji,
                   style=ButtonStyle.green, custom_id="honeycomb"),
            Button(emoji=teamEmoji,
                   style=ButtonStyle.green, custom_id="tug"),
            Button(emoji=glassEmoji,
                   style=ButtonStyle.green, custom_id="glass"),
            Button(label="Cancel", style=ButtonStyle.red,
                   custom_id="cancel")
        ]
        msg = await ctx.send(
            embed=embed,
            components=[ActionRow(*buttons[:5]), ActionRow(*buttons[5:])]
        )
        custom_ids = ["rlgl", "marbles", "honeycomb", "glass", "tug", "cancel"]
        try:
            _interaction = await self.client.wait_for('button_click', timeout=30,
                                                      check=lambda x: x.custom_id in custom_ids and
                                                                      x.user.id == ctx.author.id and
                                                                      x.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            for i in range(len(buttons)):
                buttons[i].disabled = True
            await msg.edit(embed=embed, components=[ActionRow(*buttons[:5]),
                                                    ActionRow(*buttons[5:])])
            await ctx.send("You took too long to respond. Try again later.")
        else:
            for i in range(len(buttons)):
                buttons[i].disabled = True
            await _interaction.respond(type=7, embed=embed, components=[ActionRow(*buttons[:5]),
                                                                        ActionRow(*buttons[5:])])

            if _interaction.custom_id == "cancel":
                await ctx.send("Game cancelled.")
                return

            users = await self.player_join(ctx)
            if not users:
                await ctx.send("No one joined, game ended.")
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
    async def game_launcher(self, ctx: commands.Context, skip_to=0) -> None:
        game_started()
        try:
            await self.game(ctx, skip_to)
        except Exception as e:
            print(e)
        finally:
            game_over()

    async def game(self, ctx, skip_to=0) -> None:
        if ctx.author.id not in owners:
            skip_to = 0

        users = await self.player_join(ctx)
        if len(users) == 0:
            return await ctx.send("No one joined. Game ended :(")

        initial_players = len(users)
        if skip_to == 0:
            users = await rlgl_collected(ctx, self.client, users)

        if not users:
            await ctx.send("None made it to the next round. Sed :(")
            return

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")
        if skip_to <= 1:
            # users = await self.honeycomb(ctx, users)
            users = await honey_collected(self.client, ctx, users)
        if not users:
            return await ctx.send("None made it to the next round. Sed :(")

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                               f"*DEFINITELY Not because the other games needed more than one player and you don't"
                               f" have friends for that* ...")
            return

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")

        if skip_to <= 2:
            users = await tug_collected(self.client, ctx, users)

        if not users:
            await ctx.send("None made it to the next round. Game Ended.")
            return

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                               f"*DEFINITELY Not because the other games needed more than one player and you don't"
                               f" have friends for that* ...")
            return

        if skip_to <= 3:
            users = await marbles_collected(self.client, ctx.channel, users)

        if not users:
            await ctx.send("None made it to the next round. Game Ended.")
            return

        if len(users) == 1:
            if initial_players != 1:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            else:
                await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.\n"
                               f"*DEFINITELY Not because the other games needed more than one player and you don't"
                               f" have friends for that* ...")
            return

        users = await glass_game(self.client, ctx.channel, users)

        if users:
            await ctx.send(f"Congratulations {', '.join([usr.mention for usr in users])} on Winning the SKWID GAME.")
        else:
            await ctx.send("None managed to cross the glass bridge. Game Ended.")

    async def player_join(self, ctx):
        host = ctx.author
        embed = discord.Embed(title="Join the game", color=discord.Colour.blue(),
                              description=f"Those who want to join the game click the Join button below")
        embed.add_field(name="You have : ",
                        value=f"`{reaction_timeout}` s")
        embed.set_thumbnail(url=bot_icon)
        embed.set_footer(text="Host should click the start button to start the game!")
        buttons = [
            Button(label="Join", style=ButtonStyle.blue, emoji="🪤"),
            Button(label="Leave", style=ButtonStyle.red),
            Button(label="Start", style=ButtonStyle.green)
        ]
        msg = await ctx.send(embed=embed, components=ActionRow(buttons))
        labels = ["Join", "Leave", "Start"]
        users = []

        def usr_check(_i):
            return _i.component.label in labels and _i.channel.id == ctx.channel.id

        def get_players_embed(_started=False):
            title = "Game Started" if _started else "Join the game"
            return discord.Embed(title=title,
                                 description=f"**Players joined** : `{len(users)}`\n\n"
                                             f"{' '.join([u.mention for u in users])}",
                                 colour=discord.Colour.blue())

        started = False

        while not started:
            try:
                interation = await self.client.wait_for('button_click', check=usr_check,
                                                        timeout=30)
            except asyncio.TimeoutError:
                pass
            else:
                try:
                    if interation.component.label == "Join":
                        if interation.user not in users:
                            users.append(interation.user)
                        await interation.respond(type=7,
                                                 embed=get_players_embed(),
                                                 components=ActionRow(buttons))
                    elif interation.component.label == "Leave":
                        if interation.user in users:
                            users.remove(interation.user)
                        await interation.respond(type=7,
                                                 embed=get_players_embed(),
                                                 components=ActionRow(buttons))
                    elif interation.component.label == "Start":
                        if interation.user == host:
                            started = True
                            for i in range(len(buttons)):
                                buttons[i].disabled = True
                            await interation.respond(type=7,
                                                     embed=get_players_embed(_started=True),
                                                     components=ActionRow(buttons))
                        else:
                            await interation.respond(content="Please wait for the host to start the game")
                except discord.NotFound:
                    pass

        res = []
        for usr in users:
            if usr not in res:
                res.append(usr)

        users = res

        if len(users) == 0:
            await msg.edit(embed=discord.Embed(
                title="Game Ended!",
                description=f"No One joined :(",
                color=discord.Colour.blue()
            ),
                components=ActionRow(buttons))
            return []

        return users


def setup(client):
    client.add_cog(Game(client))
