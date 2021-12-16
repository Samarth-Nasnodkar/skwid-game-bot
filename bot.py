import os
from discord.ext import commands

<<<<<<< Updated upstream
client = commands.Bot(command_prefix="s!", case_insensitive=True)
TOKEN = os.environ.get("discord_bot_token")
=======
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
client = commands.Bot(command_prefix=get_prefix,
                      case_insensitive=True, intents=intents)
DiscordComponents(client)
client.remove_command("help")
COGS = [
    "game",
    # "topgg",
    # "help",
    # "global",
    # "utilities"
]
>>>>>>> Stashed changes


@client.event
async def on_ready():
<<<<<<< Updated upstream
=======
    # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
    #                                                        name="s!help"))

>>>>>>> Stashed changes
    print("Bot online.")

client.load_extension("src.cogs.game")
client.load_extension("src.cogs.utilities")
client.run(TOKEN)
