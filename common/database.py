from pymongo import MongoClient


class DatabaseMongo:

    def __init__(self, database, collection):
        self.client = MongoClient('localhost', 27017)
        self.database = self.client[database]
        self.collection = self.database[collection]

    def insert(self, elements):
        self.collection.insert_many(elements)

    def find(self, query, limit=-1):
        return self.collection.find(query).limit(limit) if limit > -1 else self.collection.find(query)

    def deleteOne(self, query):
        self.collection.delete_one(query)

    def deleteMany(self, query):
        self.collection.delete_many(query)

    def updateOne(self, query, values):
        self.collection.update_one(query, values)

    def updateMany(self, query, values):
        self.collection.update_many(query, values)

    def changeDatabase(self, database):
        self.database = self.client[database]

    def changeCollection(self, collection):
        self.database = self.client[collection]

    def dropCollection(self):
        self.collection.drop()
