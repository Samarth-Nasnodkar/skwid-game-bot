import pymongo
from pymongo import MongoClient
from src.constants.vars import MONGO_URL

mongoCluster = MongoClient(MONGO_URL)


def update_wins(user_id: int):
    db = mongoCluster["discord_bot"]
    collection = db["leaderboard"]
    stats = collection.find_one({"_id": 0})
    wins = 1
    if str(user_id) in stats:
        wins = stats[str(user_id)] + 1

    collection.update_one({"_id": 0}, {"$set": {str(user_id): wins}}, upsert=True)


def fetch_wins(user_id: int):
    db = mongoCluster["discord_bot"]
    collection = db["leaderboard"]
    stats = collection.find_one({"_id": 0})
    if str(user_id) in stats:
        return stats[str(user_id)]
    return 0


def fetch_all_wins():
    db = mongoCluster["discord_bot"]
    collection = db["leaderboard"]
    stats = collection.find_one({"_id": 0})
    return stats
