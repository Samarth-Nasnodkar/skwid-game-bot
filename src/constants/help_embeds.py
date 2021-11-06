import discord

from src.cogs.glass import glass_steps, game_time
from src.constants.timeouts import rlgl_min_score, rlgl_timeout, honeycomb_reply_timeout
from src.constants.urls import bot_icon
from src.utils.textStyles import *
from src.constants.cmds import cmds

redgreen = f"This game is {bold('`Red Light, Green Light`')}\n" \
           f"Each participant has to send {rlgl_min_score} messages in the next `{rlgl_timeout}s`" \
           f"\nYou can send the message when the I say **__Green Light__**. If you send a message after" \
           f" I say **__Red Light__** you are eliminated.\nThe participants who are not able to send" \
           f"the {rlgl_min_score} messages in the given time are eliminated too."

honeycomb = f"This game is called {bold('HoneyComb')}. You will be {highlight('DMed')} a scrambled" \
            f" word. You have to un-scramble it and send it within `{honeycomb_reply_timeout}s`.\n" \
            f"The participants who fail to send the correct answer via DMS within the given time will be eliminated."

marbles = "This is the game of Marbles. Each one of you will be given 10 marbles. This game will last a maximum" \
          "of 3 minutes. If within 3 minutes, you're able to win all 10 of your opponent's marbles, you WIN. If not" \
          "then the user with more marbles after the end of the round wins.\n The game is as follows:\nYou have " \
          "to wage a particular number of marbles(> 0) less than or equal to the marbles left with you and so " \
          "will be your opponent. If it is your turn, you have to guess whether the number of marbles your opponent" \
          " has waged is/are odd or even. If you get it right, you win the number of marbles you waged from your " \
          "opponent, but if you get it wrong, your opponent wins the marbles you waged. The participant who loses " \
          "all his/her marbles will be eliminated. But if none of you lose all your marbles within the next 3 " \
          "minutes then the participant with the lesser number of marbles is eliminated. If both participants end " \
          "up with equal number of marbles then both are eliminated."

glass_i = f"This is the game of {bold('Glass Walk')}, You will be assigned a random serial " \
          f"number, You will be called in order and will be presented with two glass panels. One will be " \
          f"{highlight('Tempered Glass')} and will be prone to breaking, while the other will be " \
          f"{highlight('Durable Glass')} and will be able to carry your weight. If you choose the tempered " \
          f"glass, you're Eliminated. But if you choose the Durable glass, you survive and are presented with " \
          f"another pair of glass. There will be {glass_steps} rounds. The participants who cross the bridge " \
          f"before the timer ends({game_time} s) will be the winners, and rest will be Eliminated."

tug_d = f"This is {bold('Tug Of War')}, All the players will be split into two teams. If there are odd number of " \
      f"players, then one of the players will directly make it to the next round for not finding a partner.\n" \
      f"You will be then DMed a message with two buttons, A green and a red button. Each user has to click the green " \
      f"button for their team to get `+1` points, clicking the red button will result in their team getting `-1` " \
      f"points. If you don't click a button, the team will be rewarded `0` points. After everyone has done with " \
      f"this, the points will be calculated. The team with more points wins. But if both teams score equal points " \
      f"then the time taken by each user to click the button will be taken into consideration and the team who's " \
      f"total time will be lesser, will be the winner. So click the buttons as fast as possible.(Not clicking a " \
      f"button will be counted as `60s`)"


def get_cmd_embed(prefix: str) -> discord.Embed:
    commands = ""
    for cmd in cmds:
        commands += f"""{highlight(f'{prefix}{cmd["name"]}')} ➜ {cmd['desc']}\n"""

    cmd_emb = discord.Embed(title="Bot Commands",
                            description=commands, color=discord.Colour.purple())

    cmd_emb.set_thumbnail(url=bot_icon)

    return cmd_emb


red_green = discord.Embed(title="Rules of Red Light, Green Light",
                          description=redgreen, color=discord.Colour.purple())
red_green.set_thumbnail(url=bot_icon)
red_green.set_footer(text="Click a button to get more info on games.")

hc = discord.Embed(title="Rules of Honeycomb",
                   description=honeycomb, color=discord.Colour.purple())
hc.set_thumbnail(url=bot_icon)
hc.set_footer(text="Click a button to get more info on games.")

tug = discord.Embed(title="Rules of Tug of War",
                    description=tug_d, color=discord.Colour.purple())

tug.set_thumbnail(url=bot_icon)
tug.set_footer(text="Click a button to get more info on games.")

mar = discord.Embed(title="Rules of Marbles",
                    description=marbles, color=discord.Colour.purple())
mar.set_thumbnail(url=bot_icon)
mar.set_footer(text="Click a button to get more info on games.")

glass = discord.Embed(title="Rules of Glass Walk",
                      description=glass_i, color=discord.Colour.purple())
glass.set_thumbnail(url=bot_icon)
glass.set_footer(text="Click a button to get more info on games.")

embeds = {
    'rlgl': {
        'embed': red_green,
        'name': 'Red Light Green Light'
    },
    'honeycomb': {
        'embed': hc,
        'name': 'HoneyComb'
    },
    'marbles': {
        'embed': mar,
        'name': 'Marbles'
    },
    'glass': {
        'embed': glass,
        'name': 'Glass Walk'
    },
    'tug': {
        'embed': tug,
        'name': 'Tug of War'
    }
}
