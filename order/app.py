

from flask import Flask
import sys
import os
import requests

sys.path.insert(1, os.getcwd())
if True:
    from common.tools import *

# I want to make the API directions variables accessible by every service!


app = Flask("order-service")

orderCollection = getCollection("orders", "order")


# Change the field _id to be the order_id and so


def get_order(order_id):
    return orderCollection.find_one({"order_id": order_id}, {"_id": 0})


@app.post('/create/<user_id>')
def create_order(user_id):

    order_id = str(getAmountOfItems(orderCollection))
    orderCollection.insert_one({"order_id": order_id, "paid": False, "items": [], "user": user_id, "total_cost": 0})
    return response(200, f"Correctly added, orderid {order_id}")


@app.delete('/remove/<order_id>')
def remove_order(order_id):

    if get_order(order_id) == None:
        return response(404, "Order not found")

    orderCollection.delete_one({"order_id": order_id})
    return response(200, f"Correctly deleted, orderid {order_id}")


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):

    order = get_order(order_id)
    if order == None:
        return response(404, "Order not found")

    url = f"http://localhost:8888/check_availability/{item_id}"
    item_info = requests.post(url)
    item = json.loads(item_info.text)["message"]
    if item[0] == 0:
        return response(404, "No stock available")

    newvalues = {"$set": {"items": order["items"]+[item_id], "total_cost": order["total_cost"]+item[1]}}

    orderCollection.update_one({"order_id": order_id}, newvalues)

    return response(200, "Succesfully added")


@app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order = get_order(order_id)
    if order == None:
        return response(404, "Order not found")
    if item_id not in order["items"]:
        return response(404, "Item not in order")

    newvalues = {"$set": {"items": order["items"]-[item_id]}}

    orderCollection.update_one({"order_id": order_id}, newvalues)

    return response(200, "Succesfully removed")


@app.get('/find/<order_id>')
def find_order(order_id: str):
    result = get_order(order_id)
    if result == None:
        return response(404, "Order not found")

    return response(200, result)


@ app.post('/checkout/<order_id>')
def checkout(order_id):
    result = get_order(order_id)

    items = encodeBase64(json.dumps(result["items"]))
    url = f"http://localhost:8888/substract_multiple/{items}"

    # Remove the stock
    stock_info = requests.post(url)
    stock_status = json.loads(stock_info.text)["status"]

    if stock_status != 200:
        # Reimburse payment

        return response(501, "Not enough stock for the request")
        pass

    return response(200, "tst")


app.run(port=2801)
