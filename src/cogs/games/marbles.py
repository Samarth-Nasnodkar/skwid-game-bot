import asyncio
import discord
from discord.ext import commands
from src.constants.timeouts import marbles_total_time
from src.constants.urls import bot_icon
from src.constants.games import games
import time

rules_msg = games['marbles']['desc']

guesser_msg = "**It is your turn to guess**.\n Enter the number of marbles you want to wage against your opponent." \
              "You have `20s`"

wager_msg = "**It is your opponent's turn to guess**.\n Enter the number of marbles you want to wage against your " \
            "opponent.You have `20s`"

waiting_msg = "Waiting for your opponent to wage his/her marbles."

guess_msg = "**It is now your turn to guess** whether the number of marbles your opponent has waged is/are odd or " \
            "even. Send your guess. **(odd/even)**.\nYou have `20s`."

guess_waiting_msg = "Waiting for your opponent to do the odd/even guess."

rules_embed = discord.Embed(title="Welcome to the Game of Marbles",
                            description=rules_msg,
                            colour=discord.Colour.purple()).set_footer(text="Game will begin in 30s") \
    .set_thumbnail(url=bot_icon)


async def game_of_marbles(
        client: commands.Bot,
        user_one: discord.User,
        user_two: discord.User) -> discord.User:
    options = ["odd", "even"]
    users = [
        {
            "user": user_one,
            "marbles": 10
        },
        {
            "user": user_two,
            "marbles": 10
        }
    ]
    for _u in users:
        await _u["user"].create_dm()
        await _u["user"].dm_channel.send(embed=rules_embed)

    await asyncio.sleep(30)
    start = time.time()
    turn = 0

    def guesser_check(message: discord.Message):
        return isinstance(message.channel, discord.DMChannel) and message.author == users[turn]["user"] \
               and message.content.isnumeric()

    def wager_check(message: discord.Message):
        return isinstance(message.channel, discord.DMChannel) and message.author == users[1 - turn]["user"] \
               and message.content.isnumeric()

    while time.time() - start < marbles_total_time:
        guesser = users[turn]
        wager = users[1 - turn]

        await guesser["user"].dm_channel.send(guesser_msg)
        await wager["user"].dm_channel.send(waiting_msg)

        got_right = False

        guesser_wage = 0
        wager_wage = 0

        strikes = 3

        while not got_right:
            if strikes <= 0:
                await guesser["user"].dm_channel.send("Too many incorrect attempts. Player eliminated.")
                return wager["user"]
            try:
                guesser_wage_msg: discord.Message = await client.wait_for('message', check=guesser_check, timeout=20)
            except asyncio.TimeoutError:
                await guesser["user"].dm_channel.send("Failed to respond in time, you're eliminated.")
                return wager["user"]
            else:
                guesser_wage = int(guesser_wage_msg.content)
                if not 0 < guesser_wage <= guesser["marbles"]:
                    strikes -= 1
                else:
                    got_right = True

        await wager["user"].dm_channel.send(wager_msg)
        await guesser["user"].dm_channel.send(waiting_msg)

        got_right = False
        strikes = 3

        while not got_right:
            if strikes <= 0:
                await wager["user"].dm_channel.send("Too many incorrect attempts. Player eliminated.")
                return guesser["user"]
            try:
                wager_wage_msg: discord.Message = await client.wait_for('message', check=wager_check, timeout=20)
            except asyncio.TimeoutError:
                await wager["user"].dm_channel.send("Failed to respond in time, you're eliminated.")
                return guesser["user"]
            else:
                wager_wage = int(wager_wage_msg.content)
                if not 0 < wager_wage <= wager["marbles"]:
                    strikes -= 1
                else:
                    got_right = True

        def guess_check(message: discord.Message):
            return isinstance(message.channel, discord.DMChannel) and message.content.lower() in options \
                   and message.author == guesser["user"]

        await guesser["user"].send(guess_msg)
        got_right = False

        while not got_right:
            try:
                await wager["user"].dm_channel.send("**Waiting for your opponent to guess.**")
                oe_guess_msg = await client.wait_for('message', check=guess_check, timeout=20)

            except asyncio.TimeoutError:
                await guesser["user"].send("Failed to respond in time, you're eliminated.")
                return wager["user"]

            else:
                g = oe_guess_msg.content.lower()
                got_right = True

                if (wager_wage % 2 == 0 and g == "even") or (wager_wage % 2 == 1 and g == "odd"):
                    if wager["marbles"] > guesser_wage:
                        wager["marbles"] = wager["marbles"] - guesser_wage
                        guesser["marbles"] = guesser["marbles"] + guesser_wage

                        await guesser["user"].dm_channel.send(
                            f"You guessed it right! You won `{guesser_wage}` "
                            f"marbles. Marbles left : `{guesser['marbles']}`"
                        )

                        await wager["user"].dm_channel.send(
                            f"Your opponent guessed it right. You lost "
                            f"`{guesser_wage}` marbles. Marbles left : "
                            f"`{wager['marbles']}`"
                        )

                    else:
                        await guesser["user"].dm_channel.send(
                            "You guessed it right! It looks like your opponent has run out of marbles. You have made it to the next game"
                        )
                        await wager["user"].dm_channel.send(
                            "Your opponent guessed it right and unfortunately you "
                            "have run out of marbles. You're eliminated."
                            f"Marbles waged by opponent: `{guesser_wage}`"
                        )

                        return guesser["user"]
                else:
                    if guesser["marbles"] > guesser_wage:
                        wager["marbles"] = wager["marbles"] + guesser_wage
                        guesser["marbles"] = guesser["marbles"] - guesser_wage

                        await guesser["user"].dm_channel.send(
                            f"You guessed it wrong. You lost `{guesser_wage}` "
                            f"marbles. Marbles left : `{guesser['marbles']}`"
                        )
                        await wager["user"].dm_channel.send(
                            f"Your opponent guessed it wrong! You won "
                            f"`{guesser_wage}` marbles. Marbles left : "
                            f"`{wager['marbles']}`"
                        )
                    else:
                        await guesser["user"].dm_channel.send(
                            "You guessed it wrong. It looks like your have"
                            " run out of marbles. You're Eliminated."
                        )
                        await wager["user"].dm_channel.send(
                            "Your opponent guessed it wrong and has "
                            "run out of marbles. You have made it to the next game."
                            f"Marbles waged by opponent: `{guesser_wage}`"
                        )

                        return wager["user"]

        turn = 1 - turn
    for _u in users:
        await _u["user"].dm_channel.send(
            "Time up!! Lets see who's got more marbles. The participant with less "
            "marbles gets eliminated."
        )

    if users[0]["marbles"] > users[1]["marbles"]:
        await users[0]["user"].dm_channel.send("Congratulations. You have made it to the next game.")
        await users[1]["user"].dm_channel.send("You have been Eliminated.")

        return users[0]["user"]
    elif users[1]["marbles"] > users[0]["marbles"]:
        await users[1]["user"].dm_channel.send("Congratulations. You have made it to the next game.")
        await users[0]["user"].dm_channel.send("You have been Eliminated.")

        return users[1]["user"]
    else:
        return None


async def marbles_collected(
        client: commands.Bot,
        txt_channel: discord.TextChannel,
        users: list
):
    await txt_channel.send(
        "All participants get ready. This game is called marbles. The rules will be explained in "
        "DMs."
    )

    users_length = len(users)
    bye = None

    if users_length % 2 != 0:
        bye = users[-1]

    if bye:
        await txt_channel.send(f"{bye.mention} has made it to the next game for not finding a partner.")

    if len(users) == 1:
        await txt_channel.send("Only one participant left.")
        return [users[0]]

    pairings = ""
    for i in range(0, users_length - 1, 2):
        pairings += f"{users[i].mention} Vs {users[i + 1].mention}\n"

    await txt_channel.send(f"The pairings for this round are :\n{pairings}\nThe game will start in `20s`, get ready.")

    await asyncio.sleep(20)

    winners = await asyncio.gather(
        *[game_of_marbles(client, users[i], users[i + 1]) for i in range(0, users_length - 1, 2)]
    )

    _winners = []
    if bye:
        _winners.append(bye)

    for _w in winners:
        if _w:
            _winners.append(_w)

    return _winners
