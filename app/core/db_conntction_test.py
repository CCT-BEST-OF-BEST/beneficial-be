import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("No MONGO_URI environment variable set.")
DB_NAME = "beneficial_db"
COLLECTION_NAME = "chat_logs"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def mongo_test():
    test_doc = {"msg": "hello, world!"}
    inserted_id = collection.insert_one(test_doc).inserted_id
    result = collection.find_one({"_id": inserted_id})
    if result and "_id" in result:
        result["_id"] = str(result["_id"])
    return {
        "inserted_id": str(inserted_id),
        "fetched_doc": result
    }

