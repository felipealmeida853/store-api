import pymongo
from pymongo import mongo_client

from app.config import settings

client = mongo_client.MongoClient(settings.DATABASE_URL)

db = client[settings.MONGO_INITDB_DATABASE]
User = db.users
File = db.files
Folder = db.folder
User.create_index([("username", pymongo.ASCENDING)], unique=True)
File.create_index([("name", pymongo.ASCENDING)], unique=False)
Folder.create_index([("name", pymongo.ASCENDING)], unique=False)
