import discord
from discord.ext import commands
from discord_components import *
import time
import asyncio
from src.utils.textStyles import *
import random
from src.constants.urls import bot_icon

glass_steps = 16
game_time = 180
wait_time = 5
support_server_id = 900056168716701696
glass_emoji_id = 903272838822240268
falling_gif_url = "https://tenor.com/view/cholito-falling-down-float-gif-15396007"
thumbs_up_gif_url = "https://tenor.com/view/boy-kid-computer-thumbs-up-face-gif-9548945"

intro_message = f"Welcome participants to this game of {bold('Glass Walk')}, You will be assigned a random serial " \
                f"number, You will be called in order and will be presented with two glass panels. One will be " \
                f"{highlight('Tempered Glass')} and will be prone to breaking, while the other will be " \
                f"{highlight('Durable Glass')} and will be able to carry your weight. If you choose the tempered " \
                f"glass, you're Eliminated. But if you choose the Durable glass, you survive and are presented with " \
                f"another pair of glass. There will be {glass_steps} rounds. The participants who cross the bridge " \
                f"before the timer ends({game_time} s) will be the winners, and rest will be Eliminated. Good luck"


async def glass_game(
        client: commands.Bot,
        channel,
        users: list
) -> list:
    support_server: discord.Guild = client.get_guild(support_server_id)
    glass_emoji = await support_server.fetch_emoji(glass_emoji_id)
    # await channel.send(intro_message)
    embed = discord.Embed(title="Welcome Glass walk",
                          color=discord.Colour.purple(), description=intro_message)
    embed.set_thumbnail(url=bot_icon)
    embed.set_footer(text=f"The game begins in {wait_time} seconds.")
    await channel.send(embed=embed)

    await asyncio.sleep(wait_time)
    glasses_passed = 0
    start = time.time()
    finishers = users
    i = 0
    last_i = i - 1
    time_delta = time.time() - start
    while i < len(users) and int(time_delta) < game_time and glasses_passed < glass_steps:
        print(f"{time_delta=}")
        if last_i != i:
            await channel.send(f"{users[i].mention} Your turn to choose. Choose wisely. {glass_steps - glasses_passed - 1} more to go")

        def check_button_press(_interaction):
            return _interaction.user == users[i]

        await channel.send(content="Choose your Glass Panel",
                           components=ActionRow([
                               Button(style=ButtonStyle.green,
                                      emoji=glass_emoji, custom_id="glass1"),
                               Button(style=ButtonStyle.blue,
                                      emoji=glass_emoji, custom_id="glass2")
                           ]))
        try:
            interaction = await client.wait_for('button_click',
                                                timeout=int(
                                                    game_time - time_delta),
                                                check=check_button_press)
        except asyncio.TimeoutError:
            await channel.send(f"You took too long to respond and failed to cross the bridge. Players Eliminated.")
            return []
        else:
            glass_broke = random.choice((True, False))
            if glass_broke:
                await interaction.respond(content=falling_gif_url, ephemeral=False)
                await channel.send(f"Unfortunately, the Glass broke. {users[i].mention} Eliminated.")
                finishers.remove(users[i])
                i += 1
                last_i = i - 1
            else:
                await interaction.respond(content=thumbs_up_gif_url, ephemeral=False)
                glasses_passed += 1

        time_delta = time.time() - start

    if not finishers:
        await channel.send(f"{bold('All players have failed to cross the bridge')}")
        return []

    if time_delta >= game_time:
        await channel.send(f"{bold('Time is up!')}, Everyone Eliminated.")
        return []

    return finishers
