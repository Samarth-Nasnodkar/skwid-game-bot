from src.constants.vars import MONGO_CLIENT


def is_present(user_id):
    db = MONGO_CLIENT["discord_bot"]["voters"]
    voters = db.find_one({"_id": 0})["voters"]
    return user_id in voters


