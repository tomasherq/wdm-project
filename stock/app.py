from flask import Flask
import os
import sys

sys.path.insert(1, os.getcwd())
if True:
    from common.tools import *


app = Flask("stock-service")
collection = getCollection("items", "stock")


def get_item(item_id):
    return collection.find_one({"item_id": item_id}, {"_id": 0})


@app.post('/item/create/<price>')
def create_item(price: int):
    item_id = str(getAmountOfItems(collection))
    collection.insert_one({"item_id": item_id, "price": price, "stock": 0})

    return response(200, item_id)


@app.get('/find/<item_id>')
def find_item(item_id: str):
    result = collection.find_one({"item_id": item_id}, {"_id": 0})
    if result == None:
        return response(404, "Item not found")

    return response(200, result)


@app.post('/add/<item_id>/<amount>')
def add_stock(item_id: str, amount: int):

    if get_item(item_id) == None:
        return response(404, "Item not found")

    if amount < 0:
        return response(400, "Invalid amount")

    query = {"item_id": item_id, }
    newvalues = {"$set": {"stock": amount}}

    collection.update_one(query, newvalues)
    return response(200, "Updated")


@app.post('/subtract/<item_id>/<int:amount>')
def remove_stock(item_id: str, amount: int):

    data_object = collection.find_one({"item_id": item_id})

    if data_object == None:
        return response(404, "Item not found")

    stock = int(data_object["stock"])
    if stock < amount:
        return response(401, "Not enough stock")

    if amount < 0:
        return response(400, "Invalid amount")

    query = {"item_id": item_id, }
    newvalues = {"$set": {"stock": stock-amount}}

    collection.update_one(query, newvalues)
    return response(200, "Stock substracted")


@app.post("/check_availability/<item_id>")
def check_availability(item_id: str):
    result = collection.find_one({"item_id": item_id}, {"_id": 0})
    if result == None:
        return response(404, "Item not found")

    return response(200, result["stock"])


app.run(port=8888)
