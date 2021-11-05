import discord
from discord.ext import commands
import asyncio
import random
import time
import datetime
from src.constants.scramble_words import words
from discord_components import *
from src.constants.timeouts import *
from src.cogs.marbles import marbles_collected
from src.cogs.glass import glass_game
from src.constants.urls import bot_icon
from src.constants.owners import owners
import pymongo
from pymongo import MongoClient
import os


def scramble(word) -> str:
    """Scrambles a word"""
    scrambled_word = ""
    word = list(word)
    while word:
        random_index = random.randint(0, len(word) - 1)
        scrambled_word += word[random_index]
        word.pop(random_index)

    return scrambled_word


class Game(commands.Cog):
    checkmark = "✅"
    green_light_emote = "🟢"
    red_light_emote = "🔴"
    players = {}
    red_lights = {}
    scores = {}
    eliminated: discord.User = None
    is_red_light = False
    last = {}
    honeycomb_words = {}
    honeycomb_ts = {}
    honeycomb_replied = {}
    rlts = datetime.datetime.now()

    def game_over(self):
        db = self.mongoCluster["discord_bot"]
        collection = db["realTimeStats"]
        stats = collection.find_one({"_id": 0})
        ongoing = stats["ongoing"]
        ongoing = ongoing - 1 if ongoing > 0 else 0
        collection.update_one({"_id": 0}, {"$set": {"ongoing": ongoing}})

    def game_started(self):
        db = self.mongoCluster["discord_bot"]
        collection = db["realTimeStats"]
        stats = collection.find_one({"_id": 0})
        ongoing = stats["ongoing"]
        totalGames = stats["totalGames"]
        ongoing = ongoing if ongoing > 0 else 0
        collection.update_one({"_id": 0}, {"$set": {"ongoing": ongoing + 1, "totalGames": totalGames + 1}})

    def default_stats(self):
        db = self.mongoCluster["discord_bot"]
        collection = db["realTimeStats"]
        collection.update_one({"_id": 0}, {"$set": {"ongoing": 0}})

    def __init__(self, client):
        self.client: commands.Bot = client
        self.mongoCluster = MongoClient(os.environ.get("mongo_db_auth"))
        self.default_stats()
        DiscordComponents(self.client)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if str(message.author.id) in self.honeycomb_words:
                if message.content.lower() == self.honeycomb_words[str(message.author.id)].lower():
                    time_delta = message.created_at - \
                                 self.honeycomb_ts[str(message.author.id)]
                    if time_delta.seconds < honeycomb_reply_timeout:
                        self.honeycomb_replied[str(message.author.id)] = True
                        await message.author.dm_channel.send(f"That is correct!")

        try:
            if str(message.guild.id) in self.red_lights:
                if self.red_lights[str(message.guild.id)]:
                    if str(message.guild.id) in self.players:
                        if message.author in self.players[str(message.guild.id)]:
                            if message.created_at > self.rlts:
                                self.players[str(message.guild.id)].remove(
                                    message.author)
                                await message.channel.send(f"{message.author.mention} Eliminated.")
                            else:
                                scores = self.scores[str(message.guild.id)]
                                if str(message.author.id) in scores:
                                    self.scores[str(message.guild.id)][str(
                                        message.author.id)] += 1
                else:
                    scores = self.scores[str(message.guild.id)]
                    if str(message.author.id) in scores:
                        self.scores[str(message.guild.id)][str(
                            message.author.id)] += 1
        except Exception as e:
            pass

    @commands.command(name="play")
    async def play_single_game(self, ctx):
        supportServer = self.client.get_guild(900056168716701696)
        rlglEmoji = await supportServer.fetch_emoji(904782170499981322)
        marblesEmoji = await supportServer.fetch_emoji(904783089996279884)
        honeycombEmoji = await supportServer.fetch_emoji(904782927060148224)
        glassEmoji = await supportServer.fetch_emoji(903272838822240268)

        embed = discord.Embed(
            title="Choose the Game",
            description=f"Click a button below to choose that game\n"
                        f"{rlglEmoji} - Red Light Green Light\n"
                        f"{marblesEmoji} - Marbles\n"
                        f"{honeycombEmoji} - Honeycomb\n"
                        f"{glassEmoji} - Glass",
            colour=discord.Colour.purple()
        )
        embed.set_footer(text="Click a button below to choose the game")
        await ctx.send(
            embed=embed,
            components=ActionRow([
                Button(label="‏‏‎ ‎", emoji=rlglEmoji, style=ButtonStyle.green, custom_id="rlgl"),
                Button(label="‏‏‎ ‎", emoji=marblesEmoji, style=ButtonStyle.green, custom_id="marbles"),
                Button(label="‏‏‎ ‎", emoji=honeycombEmoji, style=ButtonStyle.green, custom_id="honeycomb"),
                Button(label="‏‏‎ ‎", emoji=glassEmoji, style=ButtonStyle.green, custom_id="glass")
            ])
        )
        custom_ids = ["rlgl", "marbles", "honeycomb", "glass"]
        try:
            i = await self.client.wait_for('button_click', timeout=30, check=lambda x: x.custom_id in custom_ids)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Try again later.")
        else:
            await i.respond(type=7, embed=embed, components=ActionRow([
                Button(label="‏‏‎ ‎", emoji=rlglEmoji, style=ButtonStyle.green, custom_id="rlgl",
                       disabled=True),
                Button(label="‏‏‎ ‎", emoji=marblesEmoji, style=ButtonStyle.green, custom_id="marbles",
                       disabled=True),
                Button(label="‏‏‎ ‎", emoji=honeycombEmoji, style=ButtonStyle.green, custom_id="honeycomb",
                       disabled=True),
                Button(label="‏‏‎ ‎", emoji=glassEmoji, style=ButtonStyle.green, custom_id="glass",
                       disabled=True)
            ]))
            users = await self.player_join(ctx)
            if not users:
                await ctx.send("No one joined, game ended.")
                return

            if i.custom_id == "rlgl":
                users = await self.redlight_greenlight(users, ctx)
            elif i.custom_id == "marbles":
                if len(users) == 1:
                    await ctx.send("You need at least 2 players to play this game.")
                    return
                users = await marbles_collected(self.client, ctx.channel, users)
            elif i.custom_id == "honeycomb":
                users = await self.honeycomb(ctx, users)
            elif i.custom_id == "glass":
                users = await glass_game(self.client, ctx.channel, users)

            if len(users) == 1:
                await ctx.send(f"Congratulations {users[0].mention} on winning game!")
            elif len(users) == 0:
                await ctx.send("No one passed the game.")
            else:
                await ctx.send(f"Congratulations {', '.join([x.mention for x in users])} on winning game!")

    @commands.command(name="start")
    async def game_launcher(self, ctx, skip_to=0):
        self.game_started()
        await self.game(ctx, skip_to)
        self.game_over()

    async def game(self, ctx, skip_to=0):
        if ctx.author.id not in owners:
            skip_to = 0

        users = await self.player_join(ctx)
        if skip_to == 0:
            users = await self.redlight_greenlight(users, ctx)

        if not users:
            await ctx.send("None made it to the next round. Sed :(")
            return

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")
        if skip_to <= 1:
            users = await self.honeycomb(ctx, users)

        if not users:
            return await ctx.send("None made it to the next round. Sed :(")

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")

        if skip_to <= 2:
            users = await marbles_collected(self.client, ctx.channel, users)

        if not users:
            await ctx.send("None made it to the next round. Game Ended.")
            return

        if len(users) == 1:
            await ctx.send(f"Congratulations {users[0].mention} You have won the SKWID game.")
            return

        users = await glass_game(self.client, ctx.channel, users)

        if users:
            await ctx.send(f"Congratulations {', '.join([usr.mention for usr in users])} on Winning the SKWID GAME.")
        else:
            await ctx.send("None managed to cross the glass bridge. Game Ended.")

    async def player_join(self, ctx):
        embed = discord.Embed(title="Join the game", color=discord.Colour.blue(),
                              description=f"Those who want to join the game click the Join button below")
        embed.add_field(name="You have : ",
                        value=f"`{reaction_timeout}` s")
        embed.set_thumbnail(url=bot_icon)
        msg = await ctx.send(embed=embed, components=[Button(label="Join", style=ButtonStyle.blue, emoji="🎫")])
        users = []

        def usr_check(i):
            return i.component.label == "Join"

        start = time.time()
        while time.time() - start < reaction_timeout:
            try:
                interation = await self.client.wait_for('button_click', check=usr_check, timeout=1)
            except asyncio.TimeoutError:
                pass
            else:
                users.append(interation.user)
                await interation.respond(content="You have successfully joined the game.")
        if len(users) >= 1:
            await msg.edit(embed=discord.Embed(
                title="Game Started!",
                description=f"`{len(users)}` Joined",
                color=discord.Colour.blue()
            ),
                components=[Button(label="Join", style=ButtonStyle.blue, emoji="🎫", disabled=True)])
        else:
            await msg.edit(embed=discord.Embed(
                title="Game Ended!",
                description=f"No One joined :(",
                color=discord.Colour.blue()
            ),
                components=[Button(label="Join", style=ButtonStyle.red, emoji="🎫", disabled=True)])
            return []

        return users

    async def redlight_greenlight(self, users, ctx) -> list:
        scores = {str(usr.id): 0 for usr in users}
        self.scores[str(ctx.guild.id)] = scores

        red_green_intro = f"All Participants, get ready. The first game is `Red Light, Green Light`\n" \
                          f"Each participant has to send {rlgl_min_score} messages in the next `{rlgl_timeout}s`" \
                          f"\nYou can send the message when the I say **__Green Light__**. If you send a message after" \
                          f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send" \
                          f"the {rlgl_min_score} messages in the given time are eliminated too. Good luck!"
        red_green = discord.Embed(title="Welcome to Red Light, Green Light",
                                  description=red_green_intro, color=discord.Colour.purple())
        red_green.set_thumbnail(url=bot_icon)
        red_green.set_footer(text="Game start in 2 seconds.")
        await ctx.send(embed=red_green)

        await asyncio.sleep(2)
        self.last[str(ctx.guild.id)] = "gl"
        self.players[str(ctx.guild.id)] = users
        start_time = time.time()
        embed = discord.Embed(
            description=f"{self.green_light_emote} Green Light", color=discord.Colour.green())
        await ctx.send(embed=embed)
        while time.time() - start_time < rlgl_timeout:
            if not users:
                await ctx.send("No one is left in the game. Better luck next time :)")
                return []

            await asyncio.sleep(random.randint(3, 6))
            last = self.last[str(ctx.guild.id)]
            if last == "gl":
                embed = discord.Embed(description=f"{self.red_light_emote} Red Light  ",
                                      color=discord.Colour.red())
                await ctx.send(embed=embed)
                self.rlts = datetime.datetime.now()
                self.last[str(ctx.guild.id)] = "rl"
                self.red_lights[str(ctx.guild.id)] = True
            else:
                embed = discord.Embed(description=f"{self.green_light_emote} Green Light",
                                      color=discord.Colour.green())
                await ctx.send(embed=embed)
                self.last[str(ctx.guild.id)] = "gl"
                self.red_lights[str(ctx.guild.id)] = False

        self.red_lights[str(ctx.guild.id)] = False
        scores = self.scores[str(ctx.guild.id)]
        print(scores)
        users = self.players[str(ctx.guild.id)]
        for usr_id, score in scores.items():
            if score < rlgl_min_score:
                usr = await ctx.guild.fetch_member(int(usr_id))
                try:
                    users.remove(usr)
                    await ctx.send(f"{usr.mention} Eliminated(Insufficient score).")
                except ValueError:
                    print(usr.id, " not found")

        return users

    async def tugofword(self, ctx, players: list) -> list:
        embed = discord.Embed(title="Welcome to Tug Of Words",
                              description="All participants get ready. The third game is called Tug-Of-Word. You will be divided into"
                                          f" two teams. You will have to form a chain. The bot will call your name and you have to reply "
                                          f"with a word(may or may not be in the dictionary) which starts with the last word of your "
                                          f"team member who replied just before you and must be at least 5 characters long."
                                          f" The team which can form the longest chain, wins",
                              color=discord.Colour.purple())
        embed.set_footer(text="All the best. Game starts in 10 seconds.")
        embed.set_thumbnail(url=bot_icon)
        embed.set_thumbnail(url=bot_icon)

        await ctx.send(embed=embed)

        '''await ctx.send(f"All participants get ready. The third game is called Tug-Of-Word. You will be divided into"
                       f" two teams. You will have to form a chain. The bot will call your name and you have to reply "
                       f"with a word(may or may not be in the dictionary) which starts with the last word of your "
                       f"team member who replied just before you and must be at least 5 characters long."
                       f" The team which can form the longest chain, wins.")'''
        await asyncio.sleep(10)
        l = len(players) // 2
        team_1 = players[:l]
        team_2 = players[l:]
        await ctx.send(f"The Team 1 is as follows: ")
        t_1_members = "** ** "
        for player in team_1:
            t_1_members += f"{player.mention}\n"

        await ctx.send(t_1_members)
        await ctx.send(f"The Team 2 is as follows: ")
        t_2_members = "** ** " \
                      ""
        for player in team_2:
            t_2_members += f"{player.mention}\n"

        await ctx.send(t_2_members)
        await ctx.send(f"It is TEAM ONE's turn")
        last_letter = ""
        team_1_chain = 0
        winners = ""
        for player in team_1:
            def msg_check(message):
                ct = list(message.content)
                while True:
                    try:
                        ct.remove(" ")
                    except ValueError:
                        break

                return message.author == player and message.channel == ctx.channel and len(ct) > 3

            if last_letter == "":
                await ctx.send(f"It's your turn {player.mention}. Send a word in 2s, not shorter than 4 letters.")
                try:
                    msg = await self.client.wait_for('message', check=msg_check, timeout=2)
                except asyncio.TimeoutError:
                    await ctx.send(f"Your Chain Ended at {team_1_chain}. TEAM TWO needs to form a longer chain to win")
                    break
                else:
                    team_1_chain += 1
                    last_letter = msg.content[-1]
            else:
                await ctx.send(f"It's your turn {player.mention}. Send a word starting with {last_letter} in 2s,"
                               f" not shorter than 4 letters.")
                try:
                    msg = await self.client.wait_for('message', check=msg_check, timeout=2)
                except asyncio.TimeoutError:
                    await ctx.send(f"Your Chain Ended at {team_1_chain}. TEAM TWO needs to form a longer chain to win")
                    break
                else:
                    team_1_chain += 1
                    last_letter = msg.content[-1]
                    if player == team_1[-1]:
                        await ctx.send(
                            f"Your Chain Ended at {team_1_chain}. TEAM TWO needs to form a longer chain to win")

        await ctx.send(f"It is TEAM TWO's turn")
        last_letter = ""
        team_2_chain = 0
        for player in team_2:
            def msg_check(message):
                ct = list(message.content)
                while True:
                    try:
                        ct.remove(" ")
                    except ValueError:
                        break

                return message.author == player and message.channel == ctx.channel and len(ct) > 3

            if last_letter == "":
                await ctx.send(f"It's your turn {player.mention}. Send a word in 2s, not shorter than 4 letters.")
                try:
                    msg = await self.client.wait_for('message', check=msg_check, timeout=2)
                except asyncio.TimeoutError:
                    if team_2_chain < team_1_chain:
                        await ctx.send(f"TEAM TWO Lost. TEAM ONE makes it to the next round.")
                        winners = "team 1"
                    break
                else:
                    team_2_chain += 1
                    last_letter = msg.content[-1]
                    if team_2_chain > team_1_chain:
                        await ctx.send(f"TEAM TWO Won. Congrats on making it to the next round.")
                        winners = "team 2"
            else:
                await ctx.send(f"It's your turn {player.mention}. Send a word starting with {last_letter} in 2s,"
                               f" not shorter than 4 letters.")
                try:
                    msg = await self.client.wait_for('message', check=msg_check, timeout=2)
                except asyncio.TimeoutError:
                    if team_2_chain < team_1_chain:
                        await ctx.send(f"TEAM TWO Lost. TEAM ONE makes it to the next round.")
                        winners = "team 1"
                    break
                else:
                    team_2_chain += 1
                    last_letter = msg.content[-1]
                    if team_2_chain > team_1_chain:
                        await ctx.send(f"TEAM TWO Won. Congrats on making it to the next round.")
                        winners = "team 2"

        if winners == "":
            await ctx.send("Game tied. Going Random.")
            if random.randint(0, 1) == 1:
                await ctx.send("TEAM TWO Eliminated.")
                winners = "team 1"
            else:
                await ctx.send("TEAM ONE Eliminated.")
                winners = "team 2"

        if winners == "team 1":
            for player in team_2:
                players.remove(player)
                await ctx.send(f"{player.mention} Eliminated.")
        elif winners == "team 1":
            for player in team_1:
                players.remove(player)
                await ctx.send(f"{player.mention} Eliminated.")

        return players

    async def honeycomb(self, ctx, players: list) -> list:
        honeycomb_intro = f"All participants get ready. The second game is called HoneyComb. You will be DMed a scrambled" \
                          f" word. You have to un-scramble it and send it within `{honeycomb_reply_timeout}s`.\n" \
                          f"The participants who fail to send the correct answer within the given time will be eliminated." \
                          f" Good Luck!"
        embed = discord.Embed(title="Welcome to the Honeycomb game.",
                              description=honeycomb_intro, color=discord.Colour.purple())
        embed.set_thumbnail(url=bot_icon)
        embed.set_footer(text="Game will begin in 10 seconds.")
        await ctx.send(embed=embed)

        await asyncio.sleep(10)
        self.players[str(ctx.guild.id)] = players
        for player in players:
            word = random.choice(words)
            await player.create_dm()
            await player.dm_channel.send(f"Your word is `{scramble(word)}`. You have `{honeycomb_reply_timeout}s`")
            self.honeycomb_words[str(player.id)] = word
            self.honeycomb_ts[str(player.id)] = datetime.datetime.utcnow()

        await asyncio.sleep(10)
        final_players = []
        for player in players:
            if str(player.id) in self.honeycomb_replied:
                if self.honeycomb_replied[str(player.id)]:
                    final_players.append(player)
                    del self.honeycomb_replied[str(player.id)]
                    del self.honeycomb_words[str(player.id)]
                    del self.honeycomb_ts[str(player.id)]
                else:
                    await ctx.send(f"{player.mention} Eliminated.")
                    del self.honeycomb_replied[str(player.id)]
                    del self.honeycomb_words[str(player.id)]
                    del self.honeycomb_ts[str(player.id)]
            else:
                await ctx.send(f"{player.mention} Eliminated.")
                del self.honeycomb_words[str(player.id)]
                del self.honeycomb_ts[str(player.id)]

        return final_players


def setup(client):
    client.add_cog(Game(client))
