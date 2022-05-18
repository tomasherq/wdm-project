import base64
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv
load_dotenv('env/mongo.env')

# test if sync works
PASSWORD = os.environ.get('MONGO_PASSWORD')

# test if sync works from pc to container
def response(code, text):
    return json.dumps({"status": code, "message": text})


def getCollection(database, collection):
    client = MongoClient("mongodb+srv://user:" + PASSWORD +
                         "@gala.iykme.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", 27017)
    database = client[database]
    collection = database[collection]

    return collection


def getAmountOfItems(collection):
    return len(list(collection.find({})))


def encodeBase64(string):
    encodedBytes = base64.b64encode(string.encode("utf-8"))
    return str(encodedBytes, "utf-8")


def decodeBase64(string):
    return base64.b64decode(string)
