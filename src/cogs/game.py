import discord
from discord.ext import commands
import asyncio
import random
import time


class Game(commands.Cog):
    checkmark = "✅"
    green_light = "🟢"
    red_light = "🔴"
    reaction_timeout = 5
    rlgl_timeout = 30
    players = {}
    eliminated: discord.User = None
    last = "rl"

    def __init__(self, client):
        self.client: commands.Bot = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online.")

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

        print(users)s
        msgs = {str(usr.id): 0 for usr in users}
        red_light = False

        async def snd_ann_msg(rlgl: bool):
            if rlgl:
                if self.last != "rl":
                    await ctx.send(f"{self.red_light} Red Light")
            else:
                if self.last != "gl":
                    await ctx.send(f"{self.green_light} Green Light")

        def check(message):
            if not red_light:
                if message.author in users:
                    msgs[str(message.author.id)] += 1
                return False

            if message.author in users:
                users.remove(message.author)
                self.eliminated = message.author

        start_time = time.time()
        while time.time() - start_time < 30:
            if self.eliminated:
                await ctx.send(f"{self.eliminated.mention} Eliminated")
                self.eliminated = None

            await snd_ann_msg(red_light)
            try:
                msg = await self.client.wait_for('message', check=check, timeout=0.1)
            except asyncio.TimeoutError:
                pass

            if self.last == "rl" and not red_light:
                self.last = "gl"
            elif self.last == "gl" and red_light:
                self.last = "rl"

            if random.randint(5, 20) < 10:
                red_light = True
                print("red light")
            else:
                red_light = False
                print("green light")

        await ctx.send(msgs)
        print(users)


def setup(client):
    client.add_cog(Game(client))
