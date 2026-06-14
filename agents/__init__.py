from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError(
        "MONGO_URI not found in .env file"
    )

client = MongoClient(MONGO_URI)

db = client["robotic_arm"]

memory_collection = db["memory"]
history_collection = db["history"]