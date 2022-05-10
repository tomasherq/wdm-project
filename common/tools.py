from pymongo import MongoClient
import json
import os

PASSWORD = os.environ.get('MONGO_PASSWORD')


def response(code, text):
    return json.dumps({"status": code, "message": text})


def getCollection(database, collection):
    client = MongoClient("mongodb+srv://user:" + PASSWORD + "@gala.iykme.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", 27017)
    database = client[database]
    collection = database[collection]

    return collection


def getAmountOfItems(collection):
    return len(list(collection.find({})))
