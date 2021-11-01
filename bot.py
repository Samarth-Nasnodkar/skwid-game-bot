import os
from discord.ext import commands
import pymongo
from pymongo import MongoClient


def get_prefix(bot, message):
    db = mongoCLuster["discord_bot"]
    collection = db["prefixes"]
    prefixes = collection.find_one({"_id": 0})
    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or("s!")(bot, message)
    else:
        return commands.when_mentioned_or(prefixes[str(message.guild.id)])(bot, message)


def set_prefix(guild_id, prefix):
    db = mongoCLuster["discord_bot"]
    collection = db["prefixes"]
    collection.update_one({"_id": 0}, {"$set": {str(guild_id): prefix}}, upsert=True)


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
mongoCLuster = MongoClient(os.environ.get('mongo_db_auth'))
client.remove_command("help")
TOKEN = os.environ.get("discord_bot_token")


@client.event
async def on_ready():
    print("Bot online.")


@client.command(name="prefix", pass_context=True)
async def prefix(ctx, _p=None):
    if not ctx.author.guild_permissions.manage_guild:
        return await ctx.send("You don't have permission to use this command.")

    if _p is None:
        pref = get_prefix(client, ctx.message)
        if len(pref) > 1:
            return await ctx.send(f"My prefixes are {', '.join(pref)}")
        else:
            return await ctx.send("My prefix is {}".format(pref))
    set_prefix(ctx.guild.id, _p)
    await ctx.send("Prefix set to `{}`".format(_p))


client.load_extension("src.cogs.game")
# client.load_extension("src.cogs.topgg")
client.load_extension("src.cogs.utilities")
client.run(TOKEN)
