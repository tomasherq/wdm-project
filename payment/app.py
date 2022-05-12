import os
import atexit

from flask import Flask
import sys

import requests


sys.path.insert(1, os.getcwd())
if True:
    from common.tools import *

app = Flask("payment-service")

collection = getCollection("users", "user")

collection.drop()


def helper_find_user(user_id):
    user_object = collection.find_one({"user_id": user_id})
    if user_object == None:
        return response(404, "User not found")
    return user_object


def helper_find_order(order_id):
    url = f"http://localhost:2801/find/{order_id}"
    orderInfo = requests.get(url)
    code = json.loads(orderInfo.text)["status"]
    if code == 404:
        return 404

    order_collection = json.loads(orderInfo.text)["message"]
    return order_collection


@app.post('/create_user')
def create_user():
    user_id = str(getAmountOfItems(collection))
    collection.insert_one({"user_id": user_id, "credit": 0})
    return response(200, f"Correctly added, userid {user_id}")


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    result = collection.find_one({"user_id": user_id}, {"_id": 0})
    if result == None:
        return response(404, "User not found")

    return response(200, result)


@app.post('/add_funds/<user_id>/<int:amount>')
def add_credit(user_id: str, amount: int):
    user_object = helper_find_user(user_id)
    print(user_object)

    user_credit = int(user_object["credit"])

    query = {"user_id": user_id}
    newvalues = {"$set": {"credit": user_credit+amount}}

    collection.update_one(query, newvalues)
    return response(200, f"Updated, new credit: {user_credit}")


@app.post('/pay/<user_id>/<order_id>/<int:amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    user_object = helper_find_user(user_id)

    order_collection = helper_find_order(order_id)

    if user_object == 404:
        return response(404, "No order found")  # Response has to be done here!

    user_credit = int(user_object["credit"])
    if user_credit < amount:
        return response(401, "Not enough credit")

    query = {"user_id": user_id}
    newvalues = {"$set": {"credit": user_credit-amount}}
    collection.update_one(query, newvalues)

    return response(200, f"Payment made, new credit: {user_credit}")


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    user_object = helper_find_user(user_id)

    order_collection = helper_find_order(order_id)

    newvalues = {"order_id": order_id}

    collection.delete_one(newvalues)
    return response(200, "Order deleted")


@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):
    user_object = helper_find_user(user_id)

    order_collection = helper_find_order(order_id)
    order_status = order_collection["paid"]

    return response(200, f"Order status: {order_status}")


app.run(port=1102)
