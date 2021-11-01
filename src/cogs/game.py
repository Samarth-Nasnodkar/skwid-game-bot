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

    def __init__(self, client):
        self.client: commands.Bot = client
        DiscordComponents(self.client)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if str(message.author.id) in self.honeycomb_words:
                print(list(message.content))
                if message.content.lower() == self.honeycomb_words[str(message.author.id)].lower():
                    time_delta = message.created_at - \
                        self.honeycomb_ts[str(message.author.id)]
                    print(time_delta)
                    print(time_delta.total_seconds())
                    if time_delta.seconds < honeycomb_reply_timeout:
                        self.honeycomb_replied[str(message.author.id)] = True
                        await message.author.dm_channel.send(f"That is correct! You made it to the next round.")
                        print(f"{message.author.id} Took {time_delta.seconds}s")

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

    @commands.command(name="start")
    async def start_game(self, ctx, skip_to=0):
        if not ctx.author.id in owners:
            skip_to = 0
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

        await msg.edit(embed=discord.Embed(
            title="Game Started!",
            description=f"`{len(users)}` Joined",
            color=discord.Colour.blue()
        ),
            components=[Button(label="Join", style=ButtonStyle.blue, emoji="🎫", disabled=True)])
        if skip_to == 0:
            scores = {str(usr.id): 0 for usr in users}
            self.scores[str(ctx.guild.id)] = scores

            red_green_intro = f"All Participants, get ready. The first game is `Red Light, Green Light`\n"\
                              f"Each participant has to send {rlgl_min_score} messages in the next `{rlgl_timeout}s`"\
                              f"\nYou can send the message when the I say **__Green Light__**. If you send a message after"\
                              f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send"\
                              f"the {rlgl_min_score} messages in the given time are eliminated too. Good luck!"
            red_green = discord.Embed(title="Welcome to Red Light, Green Light", description=red_green_intro, color=discord.Colour.purple())
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
                    return

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
            print(users)
            for usr_id, score in scores.items():
                if score < rlgl_min_score:
                    usr = await ctx.guild.fetch_member(int(usr_id))
                    try:
                        users.remove(usr)
                        await ctx.send(f"{usr.mention} Eliminated(Insufficient score).")
                    except ValueError:
                        print(usr.id, " not found")

        if not users:
            return await ctx.send("None made it to the next round. Sed :(")

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
            print(users)

        users = await glass_game(self.client, ctx.channel, users)

        if users:
            await ctx.send(f"Congratulations {', '.join([usr.mention for usr in users])} on Winning the SKWID GAME.")

    async def tugofword(self, ctx, players: list) -> list:
        embed = discord.Embed(title="Welcome to Tug Of Words", description="All participants get ready. The third game is called Tug-Of-Word. You will be divided into"
                              f" two teams. You will have to form a chain. The bot will call your name and you have to reply "
                              f"with a word(may or may not be in the dictionary) which starts with the last word of your "
                              f"team member who replied just before you and must be at least 5 characters long."
                              f" The team which can form the longest chain, wins",  color=discord.Colour.purple())
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
        honeycomb_intro = f"All participants get ready. The second game is called HoneyComb. You will be DMed a scrambled"\
                          f" word. You have to un-scramble it and send it within `{honeycomb_reply_timeout}s`.\n"\
                          f"The participants who fail to send the correct answer within the given time will be eliminated."\
                          f" Good Luck!"
        embed = discord.Embed(title="Welcome to the Honeycomb game.", description=honeycomb_intro, color=discord.Colour.purple())
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
