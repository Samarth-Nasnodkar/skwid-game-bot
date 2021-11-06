from discord import user, webhook
from src.utils.textStyles import *
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from src.constants.vars import TOKEN, MONGO_URL


def get_prefix(bot, message):
    try:
        db = mongoCluster["discord_bot"]
        collection = db["prefixes"]
        prefixes = collection.find_one({"_id": 0})
        if str(message.guild.id) not in prefixes:
            return "s!"
        else:
            return prefixes[str(message.guild.id)]
    except Exception as e:
        print(e)
        return "s!"


def set_prefix(guild_id, prefix):
    db = mongoCluster["discord_bot"]
    collection = db["prefixes"]
    collection.update_one(
        {"_id": 0}, {"$set": {str(guild_id): prefix}}, upsert=True)


intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.dm_messages = True
intents.guild_messages = True
intents.members = True
intents.emojis = True
client = commands.Bot(command_prefix=get_prefix,
                      case_insensitive=True, intents=intents)
mongoCluster = MongoClient(MONGO_URL)
client.remove_command("help")
COGS = [
    "game",
    "topgg",
    "help",
    "utilities",
    "settings"
]


@client.event
async def on_ready():
    print("Bot online.")


@client.event
async def on_guild_join(guild: discord.Guild):
    supportServer = client.get_guild(900056168716701696)
    logs_channel = supportServer.get_channel(904637131736121375)
    await logs_channel.send(f"Joined {bold(guild.name)}")


@client.event
async def on_guild_remove(guild: discord.Guild):
    supportServer = client.get_guild(900056168716701696)
    logs_channel = supportServer.get_channel(904637131736121375)
    await logs_channel.send(f"Left {bold(guild.name)}")


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
    set_prefix(ctx.guild.id, _p)
    await ctx.send("Prefix set to `{}`".format(_p))
    # await ctx.send("This command is not available yet.")


for cog in COGS:
    client.load_extension(".".join(("src", "cogs", cog)))

client.run(TOKEN)
