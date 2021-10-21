import discord
from discord.ext import commands
import asyncio
import random
import time
import datetime
from src.constants.scramble_words import words


def scramble(word: str) -> str:
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
    reaction_timeout = 10
    rlgl_timeout = 30
    rlgl_min_score = 20
    honeycomb_reply_timeout = 10
    players = {}
    red_lights = {}
    scores = {}
    eliminated: discord.User = None
    is_red_light = False
    last = {}
    honeycomb_words = {}
    honeycomb_replied = {}
    rlts = datetime.datetime.now()

    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel):
            if str(message.author.id) in self.honeycomb_words:
                if message.content.lower() == self.honeycomb_words[str(message.author.id)]:
                    self.honeycomb_replied[str(message.author.id)] = True

        if str(message.guild.id) in self.red_lights:
            if self.red_lights[str(message.guild.id)]:
                if str(message.guild.id) in self.players:
                    if message.author in self.players[str(message.guild.id)]:
                        if message.created_at < self.rlts:
                            self.players[str(message.guild.id)].remove(message.author)
                            await message.channel.send(f"{message.author.mention} Eliminated.")
                        else:
                            scores = self.scores[str(message.guild.id)]
                            if str(message.author.id) in scores:
                                self.scores[str(message.guild.id)][str(message.author.id)] += 1
            else:
                scores = self.scores[str(message.guild.id)]
                if str(message.author.id) in scores:
                    self.scores[str(message.guild.id)][str(message.author.id)] += 1

    @commands.command(name="start")
    async def start_game(self, ctx, max_users: int = -1):
        bypass = True
        if max_users != -1 and max_users < 3:
            return ctx.send("There should be at least 3 users")

        announce_msg = await ctx.send(f"Those who want to join the game react with {self.checkmark} "
                                      f"to this message. You have `{self.reaction_timeout}` s")
        await announce_msg.add_reaction(self.checkmark)
        await asyncio.sleep(self.reaction_timeout)
        announce_msg = await ctx.channel.fetch_message(announce_msg.id)
        users = []
        for reaction in announce_msg.reactions:
            if reaction.emoji == self.checkmark:
                async for _ in reaction.users():
                    if _ != ctx.guild.me:
                        users.append(_)

        if not bypass:
            scores = {str(usr.id): 0 for usr in users}
            self.scores[str(ctx.guild.id)] = scores

            await ctx.send("All Participants, get ready. The first game is `Red Light, Green Light`\n"
                           f"Each participant has to send {self.rlgl_min_score} messages in the next `{self.rlgl_timeout}s`"
                           f"\nYou can send the message when the I say **__Green Light__**. If you send a message after"
                           f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send"
                           f"the {self.rlgl_min_score} messages in the given time are eliminated too. Good luck!")
            await asyncio.sleep(2)
            self.last[str(ctx.guild.id)] = "gl"
            self.players[str(ctx.guild.id)] = users
            start_time = time.time()
            await ctx.send(f"{self.green_light_emote} Green Light")
            while time.time() - start_time < self.rlgl_timeout:
                await asyncio.sleep(random.randint(3, 6))
                last = self.last[str(ctx.guild.id)]
                if last == "gl":
                    await ctx.send(f"{self.red_light_emote} Red Light")
                    self.rlts = datetime.datetime.now()
                    self.last[str(ctx.guild.id)] = "rl"
                    self.red_lights[str(ctx.guild.id)] = True
                else:
                    await ctx.send(f"{self.green_light_emote} Green Light")
                    self.last[str(ctx.guild.id)] = "gl"
                    self.red_lights[str(ctx.guild.id)] = False

            self.red_lights[str(ctx.guild.id)] = False
            scores = self.scores[str(ctx.guild.id)]
            print(scores)
            users = self.players[str(ctx.guild.id)]
            print(users)
            for usr_id, score in scores.items():
                if score < self.rlgl_min_score:
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
        users = await self.honeycomb(ctx, users)
        if not users:
            return await ctx.send("None made it to the next round. Sed :(")

        congts_str = "Congratulations "
        for usr in users:
            congts_str += f"{usr.mention} "

        await ctx.send(f"{congts_str}\nYou have made it to the next round.")

    async def honeycomb(self, ctx, players: list) -> list:
        await ctx.send(f"All participants get ready. The second game is called HoneyComb. You will be DMed a scrambled"
                       f" word. You have to un-scramble it and send it within `{self.honeycomb_reply_timeout}s`.\n"
                       f"The participants who fail to send the correct answer within the given time will be eliminated."
                       f" Good Luck!")
        await asyncio.sleep(3)
        self.players[str(ctx.guild.id)] = players
        for player in players:
            word = random.choice(words)
            await player.create_dm()
            await player.dm_channel.send(f"Your word is `{scramble(word)}`. You have `{self.honeycomb_reply_timeout}s`")
            self.honeycomb_words[str(player.id)] = word

        await asyncio.sleep(10)
        final_players = []
        for player in players:
            if str(player.id) in self.honeycomb_replied:
                if self.honeycomb_replied[str(player.id)]:
                    final_players.append(player)
                    self.honeycomb_replied[str(player.id)] = False
                else:
                    await ctx.send(f"{player.mention} Eliminated.")
            else:
                await ctx.send(f"{player.mention} Eliminated.")

        return final_players


def setup(client):
    client.add_cog(Game(client))
