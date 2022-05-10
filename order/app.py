

from flask import Flask
import sys
import os


sys.path.insert(1, os.getcwd())
if True:
    from common.tools import *


app = Flask("order-service")

collection = getCollection("orders", "order")


@app.post('/create/<user_id>')
def create_order(user_id):

    order_id = len(list(collection.find({})))
    collection.insert_one({"order_id": order_id, "name": user_id, "address": "Highway 37"})
    return response(200, f"Correctly added, orderid {order_id}")


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    pass


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):
    pass


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    pass


@app.get('/find/<order_id>')
def find_order(order_id):
    order_id = int(order_id)
    return response(200, collection.find_one({"order_id": order_id}, {"_id": 0}))


@ app.post('/checkout/<order_id>')
def checkout(order_id):
    pass


app.run(port=2801)
