import discord
from discord.ext import commands
import random
import asyncio
from src.cogs.constants.scramble_words import words

reply_timeout = 10


def scramble(word: str):
    word = list(word)
    scrambled_word = ""
    while word:
        random_index = random.randint(0, len(word) - 1)
        scrambled_word += word[random_index]
        word.pop(random_index)

    return scrambled_word


async def honeycomb(client: commands.Bot, ctx, players: list):

    await ctx.send("Round 2: HoneyComb begins now.\n"
                   "Each of you will be DMed a word, you have to un-scramble that word and send it."
                   f"You will be given `{reply_timeout}s`. The participants who fail to send the corrent word"
                   f" will be eliminated. Good luck!")

    await asyncio.sleep(3)
    words_track = {}
    for player in players:
        def check(message):
            return message.author == player and message.content == words_track[str(player.id)] \
                   and isinstance(message.channel, discord.DMChannel)

        await player.create_dm()
        word = random.choice(words)
        words_track[str(player.id)] = word
        await player.dm_channel.send(f"Your word is `{scramble(word)}`. You have `{reply_timeout}s`.")
        try:
            msg = await client.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            players.remove(player)
            await player.dm_channel.send("Took too late to respond. Player Eliminated.")
            await ctx.send(f"{player.mention} Eliminated.")

    return players

if __name__ == "__main__":
    inp = input("Enter the word \n")
    print(scramble(inp))
