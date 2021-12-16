from src.constants.vars import MONGO_CLIENT, TOPGG_TOKEN, INSTANCE

def default_stats():
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    collection.update_one({"_id": 0}, {"$set": {"ongoing": 0}})


def game_started(start_time, server_id):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["realTimeStats"]
    collection.find_one_and_update({"_id": 0}, {"$inc": {"totalGames": 1}})


def game_over(start_time, server_id):
    # db = MONGO_CLIENT["discord_bot"]
    # collection = db["realTimeStats"]
    # collection.find_one_and_update({"_id": 0}, {"$inc": {"ongoing": -1}})
    return None


def log_game(data):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["logs"]
    # logs = collection.find_one({"_id": 0})
    # logs["games"].append(data)
    # logs['length'] += 1
    collection.find_one_and_update({'_id': 0}, {'$push': {'games': data}, '$inc': {'length': 1}})
    # collection.update_one({'_id': 0}, {'$set': {'games': logs['games'], 'length': logs['length']}})


async def update_vote(topgg_client, user_id: int):
    db = MONGO_CLIENT["discord_bot"]
    collection = db["votes"]
    _vote = await topgg_client.get_user_vote(user_id)
    # if _vote:

