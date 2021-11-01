import os
from src.utils.textStyles import *
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient


def get_prefix(bot, message):
    return commands.when_mentioned_or("s!")(bot, message)
    # try:
    #     db = mongoCLuster["discord_bot"]
    #     collection = db["prefixes"]
    #     prefixes = collection.find_one({"_id": 0})
    #     if str(message.guild.id) not in prefixes:
    #         return commands.when_mentioned_or("s!")(bot, message)
    #     else:
    #         return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)
    # except Exception as e:
    #     print(e)
    #     return commands.when_mentioned_or("s!")(bot, message)


def set_prefix(guild_id, prefix):
    db = mongoCLuster["discord_bot"]
    collection = db["prefixes"]
    collection.update_one(
        {"_id": 0}, {"$set": {str(guild_id): prefix}}, upsert=True)


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.dm_messages = True
intents.guild_messages = True
intents.emojis = True
client = commands.Bot(command_prefix=get_prefix,
                      case_insensitive=True, intents=intents)
logs_channel = client.get_channel(904637131736121375)
mongoCLuster = MongoClient(os.environ.get('mongo_db_auth'))
client.remove_command("help")
TOKEN = os.environ.get("discord_bot_token")


@client.event
async def on_ready():
    print("Bot online.")


@client.command(name="et")
async def emoji_test(ctx):
    emj = discord.utils.get(ctx.guild.emojis, name="sunglasses")
    await ctx.send(emj)


@client.event
async def on_guild_join(guild: discord.Guild):
    await logs_channel.send(f"Joined guild: {bold(guild.name)}")


@client.event
async def on_guild_remove(guild: discord.Guild):
    await logs_channel.send(f"Left guild: {bold(guild.name)}")


@client.command(name="prefix", pass_context=True)
async def prefix(ctx, _p=None):
    if not ctx.author.guild_permissions.manage_guild and _p is not None:
        return await ctx.send("You don't have permission to use this command.")

    if _p is None:
        pref = get_prefix(client, ctx.message)
        if len(pref) > 1:
            return await ctx.send(f"My prefixes are {', '.join(pref)}")
        else:
            return await ctx.send("My prefix is {}".format(pref))
    # set_prefix(ctx.guild.id, _p)
    # await ctx.send("Prefix set to `{}`".format(_p))
    await ctx.send("This command is not available yet.")


client.load_extension("src.cogs.game")
client.load_extension("src.cogs.topgg")
client.load_extension("src.cogs.help")
client.load_extension("src.cogs.utilities")
client.run(TOKEN)
