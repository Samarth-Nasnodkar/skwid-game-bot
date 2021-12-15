import discord
from discord.ext import commands
import asyncio
from src.constants.timeouts import honeycomb_reply_timeout
from src.constants.scramble_words import words
from src.constants.urls import bot_icon
import random
from src.constants.games import games

def scramble(word) -> str:
    """Scrambles a word"""

    scrambled_word = ""
    word = list(word)

    while word:
        random_index = random.randint(0, len(word) - 1)
        scrambled_word += word[random_index]
        word.pop(random_index)

    return scrambled_word


async def honey_solo(client: commands.Bot, ctx: commands.Context, word: str, user: discord.User):
    scrambled_word = scramble(word)
    await user.create_dm()
    await user.dm_channel.send(f"Your word is `{scrambled_word}`. You have `{honeycomb_reply_timeout}s`")
    try:
        msg = await client.wait_for('message', timeout=honeycomb_reply_timeout,
                                    check=lambda x: x.author == user and isinstance(x.channel, discord.DMChannel))
    except asyncio.TimeoutError:
        await ctx.send(f"{user.mention} Took too long to respond. Player Eliminated!")
        return None
    else:
        if msg.content.lower() == word.lower():
            await user.dm_channel.send("That is correct!")
            return user
        else:
            await user.dm_channel.send("Oops. Wrong answer. Player Eliminated!")
            return None


async def honey_collected(client: commands.Bot, ctx: commands.Context, users: list):
    embed = discord.Embed(
        title="Welcome to the Honeycomb game.",
        description=games['honeycomb']['desc'],
        color=discord.Colour.purple()
    )

    embed.set_thumbnail(url=bot_icon)
    embed.set_footer(text="Game will begin in 10 seconds.")
    await ctx.send(embed=embed)

    _passed = await asyncio.gather(*[honey_solo(client, ctx, random.choice(words), user) for user in users])
    passed = [user for user in _passed if user is not None]
    return passed
