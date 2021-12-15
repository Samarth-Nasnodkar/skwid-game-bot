import discord
from src.constants.urls import bot_icon
from src.utils.textStyles import *
from src.constants.cmds import cmds
from src.constants.games import games

def get_cmd_embed(prefix: str) -> discord.Embed:
    commands = ""
    for cmd in cmds:
        commands += f"""{highlight(f'{prefix}{cmd["name"]}')} ➜ {cmd['desc']}\n"""

    cmd_emb = discord.Embed(
        title="Bot Commands",
        description=commands,
        color=discord.Colour.purple()
    )

    cmd_emb.set_thumbnail(url=bot_icon)

    return cmd_emb

def get_game_embed(game_name: str, description: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"Rules of {game_name}",
        description=description,
        color=discord.Colour.purple()
    )

    embed.set_thumbnail(url=bot_icon)
    embed.set_footer(text="Click a button to get more info on games.")

    return embed

embeds = {}

for game in games:
    embeds[game] = dict()

    embeds[game]['embed'] = get_game_embed(games[game]['name'], games[game]['desc'])
    embeds[game]['name'] = games[game]['name']