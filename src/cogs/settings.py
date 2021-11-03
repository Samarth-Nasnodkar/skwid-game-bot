import discord
from discord.ext import commands
from discord.ext.commands import bot
from discord_components import *
import pymongo
from pymongo import MongoClient
import os
from src.constants.global_settings import default_settings, settingTypes
from src.utils.textStyles import bold, italics
from src.constants.urls import bot_icon


class Settings(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.mongoCluster = MongoClient(os.environ.get('mongo_db_auth'))

    def get_settings(self, guild_id: int):
        db = self.mongoCluster["discord_bot"]
        collection = db["settings"]
        settings = collection.find_one({"_id": 0})
        if settings is None:
            return default_settings
        elif str(guild_id) not in settings:
            return default_settings
        else:
            _sets = default_settings
            for k in _sets.keys():
                if k in settings[str(guild_id)]:
                    _sets[k]["value"] = settings[str(guild_id)][k]

            return _sets

    def update_settings(self, guild_id: int, key: str, value):
        if not key in default_settings.keys():
            return False

        db = self.mongoCluster["discord_bot"]
        collection = db["settings"]
        settings = collection.find_one({"_id": 0})
        if str(guild_id) in settings:
            settings = settings[str(guild_id)]
            settings[key] = value
            collection.update_one(
                {"_id": 0}, {"$set": {str(guild_id): settings}})
            return True
        else:
            collection.update_one(
                {"_id": 0}, {"$set": {str(guild_id): {key: value}}}, upsert=True)
            return True

    @commands.command(name="settings", aliases=["set", "config"])
    async def settings_command(self, ctx: commands.Context):
        desc = ""
        settings = self.get_settings(ctx.guild.id)
        for k in settings.keys():
            if settings[k]["type"] == settingTypes.MAIN_COMMAND:
                desc += f"{bold(k)} **➜** {settings[k]['value']}\n{italics(settings[k]['desc'])}\n"

        settings_embed = discord.Embed(
            title=f"Bot setting for {ctx.guild.name}",
            description=desc,
            color=discord.Color.blue()
        )
        settings_embed.set_thumbnail(url=bot_icon)
        await ctx.send(embed=settings_embed)


def setup(client: commands.Bot):
    client.add_cog(Settings(client))
