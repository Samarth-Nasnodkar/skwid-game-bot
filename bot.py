from discord import user, webhook
from src.utils.textStyles import *
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from src.constants.vars import TOKEN, MONGO_URL, INSTANCE, DEFAULT_PREFIX
from src.constants.urls import bot_icon
from src.constants.urls import invite_url
from discord_components import *


def get_prefix(bot: commands.Bot, message):
    try:
        db = mongoCluster["discord_bot"]
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
    db = mongoCluster["discord_bot"]
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
client = commands.Bot(command_prefix=get_prefix,
                      case_insensitive=True, intents=intents)
DiscordComponents(client)
mongoCluster = MongoClient(MONGO_URL)
client.remove_command("help")
COGS = [
    "game",
    "topgg",
    "help",
    "global",
    "utilities",
    # "settings"
]


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                           name="s!help"))
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
        _prefs = get_prefix(client, ctx.message)
        pref = _prefs[-1]
        return await ctx.send("My prefix is `{}`".format(pref))
    set_prefix(ctx.guild.id, _p)
    await ctx.send("Prefix set to `{}`".format(_p))
    # await ctx.send("This command is not available yet.")


# @client.command(name="push_update")
async def push_update(ctx):
    if INSTANCE == "primary":
        return

    if ctx.author.id != 727539383405772901:
        return

    embed = discord.Embed(
        title="Urgent Notice!",
        description="This bot was meant to be the secondary bot to the original squid game unofficial bot until it was"
                    " verified by discord(a bot cannot join more than `100` servers until it is). And since now it has "
                    "been verified, we urge you to invite that bot using the button below and kick this bot.\n"
                    "**__This Bot will go offline after 7 days. Please invite the primary bot before that.__**\n"
                    "Thanks!,\nDevs.",
        color=discord.Colour.green()
    )
    embed.set_thumbnail(url=bot_icon)
    invite_button = Button(label="Invite!", style=ButtonStyle.URL, url=invite_url)
    server: discord.Guild
    for server in client.guilds:
        await server.system_channel.send(embed=embed, components=[invite_button])


for cog in COGS:
    client.load_extension(".".join(("src", "cogs", cog)))

client.run(TOKEN)
