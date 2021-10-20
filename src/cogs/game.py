import discord
from discord.ext import commands
import asyncio
import random
import time
import datetime


class Game(commands.Cog):
    checkmark = "✅"
    green_light_emote = "🟢"
    red_light_emote = "🔴"
    reaction_timeout = 5
    rlgl_timeout = 30
    rlgl_min_score = 20
    players = {}
    red_lights = {}
    scores = {}
    eliminated: discord.User = None
    is_red_light = False
    last = {}
    rlts = datetime.datetime.now()

    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
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

        scores = {str(usr.id): 0 for usr in users}
        self.scores[str(ctx.guild.id)] = scores

        await ctx.send("All Participants, get ready. The first game is `Red Light, Green Light`\n"
                       f"Each participant has to send {self.rlgl_min_score} messages in the next `{self.rlgl_timeout}s`"
                       f"\nYou can send the message when the I say **__Green Light__**. If you send a message after I"
                       f" say **__Red Light__** you are eliminated.\nThe participants who are not able to send"
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


def setup(client):
    client.add_cog(Game(client))
