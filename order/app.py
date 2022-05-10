import os
import atexit

from flask import Flask
from common.database import DatabaseMongo


gateway_url = os.environ['GATEWAY_URL']

app = Flask("order-service")

collection = DatabaseMongo("orders", "order")


@app.post('/create/<user_id>')
def create_order(user_id):
    order_id = collection.find()

    collection.insert([{"name": user_id, "address": "Highway 37"}])


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
    collection.find()


@app.post('/checkout/<order_id>')
def checkout(order_id):
    pass
