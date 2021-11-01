import discord

from src.cogs.glass import glass_steps, game_time
from src.constants.timeouts import rlgl_min_score, rlgl_timeout, honeycomb_reply_timeout
from src.constants.urls import bot_icon
from src.utils.textStyles import *


redgreen = f"All Participants, get ready. The first game is {bold('`Red Light, Green Light`')}\n"\
           f"Each participant has to send {rlgl_min_score} messages in the next `{rlgl_timeout}s`"\
           f"\nYou can send the message when the I say **__Green Light__**. If you send a message after"\
           f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send"\
           f"the {rlgl_min_score} messages in the given time are eliminated too. Good luck!"

honeycomb = f"All participants get ready. The second game is called {bold('HoneyComb')}. You will be {highlight('DMed')} a scrambled" \
                  f" word. You have to un-scramble it and send it within `{honeycomb_reply_timeout}s`.\n" \
                  f"The participants who fail to send the correct answer within the given time will be eliminated." \
                  f" Good Luck!"

tugw = f"All participants get ready. The third game is called {bold('Tug-Of-Word')}. You will be divided into"\
       f" two teams. You will have to form a chain. The bot will call your name and you have to reply "\
       f"with a word(may or may not be in the dictionary) which starts with the last word of your "\
       f"team member who replied just before you and must be at least 5 characters long."\
       f" The team which can form the longest chain, wins"

glass_i = f"Welcome participants to this game of {bold('Glass Walk')}, You will be assigned a random serial " \
        f"number, You will be called in order and will be presented with two glass panels. One will be " \
        f"{highlight('Tempered Glass')} and will be prone to breaking, while the other will be " \
        f"{highlight('Durable Glass')} and will be able to carry your weight. If you choose the tempered " \
        f"glass, you're Eliminated. But if you choose the Durable glass, you survive and are presented with " \
        f"another pair of glass. There will be {glass_steps} rounds. The participants who cross the bridge " \
        f"before the timer ends({game_time} s) will be the winners, and rest will be Eliminated. Good luck"

red_green = discord.Embed(title=f"{bold('Information on Red Light, Green Light.')}", description=redgreen, color=discord.Colour.purple())
red_green.set_thumbnail(url=bot_icon)

hc = discord.Embed(title=f"{bold('Information on the Honeycomb Game.')}", description=honeycomb, color=discord.Colour.purple())
hc.set_thumbnail(url=bot_icon)

tug = discord.Embed(title=f"{bold('Information on Tug of Words game.')}", description=tugw, color=discord.Colour.purple())
tug.set_thumbnail(url=bot_icon)

glass = discord.Embed(title=f"{bold('Information on Glass Panel game')}", description=glass_i, color=discord.Colour.purple())
glass.set_thumbnail(url=bot_icon)

embeds = {'game_0': red_green,
          'game_1': hc,
          'game_2': tug,
          'game_3': glass}