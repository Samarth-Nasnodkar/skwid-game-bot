import discord
from discord.ext import commands
from discord_components import *
import asyncio
from src.constants.timeouts import honeycomb_reply_timeout
from src.constants.scramble_words import words, easy_words
from src.constants.urls import bot_icon, bot_vote_url
from src.constants.vars import MONGO_CLIENT
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


def get_user_vote(user_id: int) -> bool:
    db = MONGO_CLIENT["discord_bot"]["votes"]
    voters = db.find_one({"_id": 0})["voters"]
    return user_id in voters


def remove_user_from_db(user_id: int) -> None:
    db = MONGO_CLIENT["discord_bot"]["votes"]
    db.find_one_and_update({"_id": 0}, {"$pull": {"voters": user_id}})


async def honey_solo(client: commands.Bot, ctx: commands.Context, word: str, user: discord.User, count_vote=True):
    scrambled_word = scramble(word)
    vote_button = Button(label="Vote", url=bot_vote_url, style=ButtonStyle.URL)
    await user.create_dm()
    try:
        if count_vote:
            await user.dm_channel.send(f"**Your word is `{scrambled_word}`. You have `{honeycomb_reply_timeout}s`**.\n"
                                       f"*Click the button below to vote the bot to get an easier word. Once voted DM "
                                       f"`voted`*",
                                       components=[vote_button])
        else:
            await user.dm_channel.send(f"**Your new word is `{scrambled_word}`. You have `{honeycomb_reply_timeout}s`"
                                       f"**")
    except discord.Forbidden:
        await ctx.send(f"{user.mention} is not accepting DMs. Excluding them from the game.")
        return None
    while True:
        try:
            msg = await client.wait_for('message', timeout=honeycomb_reply_timeout,
                                        check=lambda x: x.author == user and isinstance(x.channel, discord.DMChannel))
        except asyncio.TimeoutError:
            await ctx.send(f"{user.mention} Took too long to respond. Player Eliminated!")
            return None
        else:
            if msg.content.lower() == "voted" and count_vote:
                voted = get_user_vote(user.id)
                if voted:
                    remove_user_from_db(user.id)
                    return await honey_solo(client, ctx, random.choice(easy_words), user, count_vote=False)
                else:
                    await user.dm_channel.send(f"Looks like you didn't vote or might have voted already in the past 12 "
                                               f"hours. Un-scramble this word. You have `{honeycomb_reply_timeout}s`.")
                    continue

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
