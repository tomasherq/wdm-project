from pymongo import MongoClient
import json


def response(code, text):
    return json.dumps({"status": code, "message": text})


def getCollection(database, collection):
    client = MongoClient('localhost', 27017)
    database = client[database]
    collection = database[collection]

    return collection


def getAmountOfItems(collection):
    return len(list(collection.find({})))
