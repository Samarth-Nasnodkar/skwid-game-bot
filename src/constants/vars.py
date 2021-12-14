import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PREFIX = "s!"
MONGO_URL = os.environ.get("mongo_db_auth")
TOKEN = os.environ.get("discord_bot_token")
TOPGG_TOKEN = os.environ.get("topgg_token")
INSTANCE = os.environ.get("instance")
MONGO_CLIENT = MongoClient(MONGO_URL)
