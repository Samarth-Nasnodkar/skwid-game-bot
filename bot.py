from discord import user, webhook
from src.utils.textStyles import *
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from src.constants.vars import TOKEN, MONGO_URL, INSTANCE, DEFAULT_PREFIX, MONGO_CLIENT
from src.constants.ids import SUPPORT_SERVER_ID
from src.constants.urls import bot_icon
from src.constants.urls import invite_url
from discord_components import *

from src.utils.fetchEmojis import fetchEmojis


def get_prefix(bot: commands.Bot, message):
    if INSTANCE == "beta":
        return "t!"
    try:
        db = MONGO_CLIENT["discord_bot"]
        collection = db["prefixes"]
        prefixes = collection.find_one({"_id": 0})
        if str(message.guild.id) not in prefixes:
            return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)
        else:
            return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)
    except Exception as e:
        print(e)
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)


def set_prefix(guild_id, prefix):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["prefixes"]
    collection.update_one(
        {"_id": 0}, {"$set": {str(guild_id): prefix}}, upsert=True)


intents = discord.Intents.default()
intents.guilds = True
# intents.messages = True
intents.dm_messages = True
# intents.guild_messages = True
intents.members = True
intents.emojis = True
# to stop caching. :)
client = commands.AutoShardedBot(command_prefix=get_prefix,
                                 case_insensitive=True, intents=intents, max_messages=None,
                                 member_cache_flags=discord.MemberCacheFlags.none())
DiscordComponents(client)
client.remove_command("help")
COGS = [
    "game",
    "topgg",
    "help",
    "global",
    "utilities",
    "debugging"
]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                           name="s!help"))

    print("Bot online.")

    support_server = await client.fetch_guild(SUPPORT_SERVER_ID)
    await fetchEmojis(support_server)


# @client.event
# async def on_message(message: discord.Message):
#     _p = get_prefix(client, message)
#     prfx = _p[-1].lower()
#     if message.content.lower().startswith(prfx):
#         t = 0
#         if message.content[len(prfx)] == " ":
#             t = 1
#
#         message.content = message.content[:len(prfx)].lower() + message.content[len(prfx) + t:]
#
#     await client.process_commands(message)


@client.command(name="prefix", pass_context=True)
async def prefix(ctx, _p=None):
    if INSTANCE == "beta":
        await ctx.send("No prefix changes can be done to the `BETA` instance.")
        return
    if not ctx.author.guild_permissions.manage_guild and _p is not None:
        return await ctx.send("You don't have permission to use this command.")

    if _p is None:
        _prefs = get_prefix(client, ctx.message)
        pref = _prefs[-1]
        return await ctx.send("My prefix is `{}`".format(pref))
    set_prefix(ctx.guild.id, _p)
    await ctx.send("Prefix set to `{}`".format(_p))
    # await ctx.send("This command is not available yet.")


for cog in COGS:
    client.load_extension(".".join(("src", "cogs", cog)))

client.run(TOKEN)
