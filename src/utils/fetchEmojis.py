from discord import Guild
from src.constants.ids import EMOJI_IDS

# cached fetch
fetched_emojis = dict()

async def fetchEmojis(supportServer: Guild):
    for emoji in EMOJI_IDS:
        if emoji not in fetched_emojis:
            fetched_emojis[emoji] = await supportServer.fetch_emoji(EMOJI_IDS[emoji])

    return fetched_emojis