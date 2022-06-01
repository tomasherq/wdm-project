
from common.tools import *
from common.node_service import NodeService, process_before_request, process_after_request
import sys
import logging
from common.async_calls import send_requests, asyncio
# I want to make the API directions variables accessible by every service!
# Keep loggin of the files

app = Flask(f"order-service-{ID_NODE}", "/orders")
logging.basicConfig(filename=f"/var/log/order-service-{ID_NODE}", level=logging.INFO,
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

serviceNode = NodeService("order")


@app.before_request
def preprocess():
    return process_before_request(request, serviceNode)


@app.get('/getHash')
def getHash():
    d = serviceNode.database.command("dbHash")
    return response(200, d["md5"])


def get_order(order_id):
    return serviceNode.collection.find_one({"_id": order_id})


@ app.route('/')
def ping_service():

    return json.dumps(serviceNode.coordinators)


@ app.post('/create/<user_id>')
def create_order(user_id):
    order_id = str(getAmountOfItems(serviceNode.collection))

    serviceNode.collection.insert_one({"_id": order_id,  "paid": False,
                                      "items": [], "user": user_id, "total_cost": 0})
    app.logger.info(f"Created order with orderid: {order_id} and userid: {user_id}.")
    return response(200, f"Correctly added, orderid {order_id}", request.headers['Id-request'])


@ app.delete('/remove/<order_id>')
def remove_order(order_id):

    if get_order(order_id) == None:
        app.logger.error(f"Order with orderid: {order_id} was not found.")
        return response(404, "Order not found", request.headers['Id-request'])

    serviceNode.collection.delete_one({"_id": order_id})
    app.logger.info(f"Order with orderid: {order_id} was successfully removed.")
    return response(200, f"Correctly deleted, orderid {order_id}", request.headers['Id-request'])


@ app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):

    order = get_order(order_id)
    if order == None:
        app.logger.error(f"Order with orderid: {order_id} was not found.")
        return response(404, "Order not found", request.headers['Id-request'])

    url = f"/check_availability/{item_id}"

    item_info = serviceNode.sendMessageCoordinator(url, "stock", "GET")
    app.logger.info(f"Sending message to coordinator: {serviceNode.coordinators}")

    item = item_info["message"]

    if item[0] == 0:
        app.logger.error(f"No stock for item with itemid: {item_id}")
        return response(404, "No stock available", request.headers['Id-request'])

    items = order["items"]
    items.append(item_id)

    newvalues = {"$set": {"items": items, "total_cost": order["total_cost"] + int(item[1])}}

    serviceNode.collection.update_one({"_id": order_id}, newvalues)
    app.logger.info(f"Successfully added item with itemid: {item_id} to order with orderid: {order_id}.")

    return response(200, "Successfully added", request.headers['Id-request'])


@ app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order = get_order(order_id)

    if order == None:
        app.logger.error(f"Order with orderid: {order_id} was not found.")
        return response(404, "Order not found", request.headers['Id-request'])

    if item_id not in order["items"]:
        app.logger.error(f"Item with itemid: {item_id} was not found.")
        return response(404, "Item not in order", request.headers['Id-request'])

    newvalues = {"$set": {"items": order["items"] - [item_id]}}

    serviceNode.collection.update_one({"_id": order_id}, newvalues)

    app.logger.info(f"Successfully deleted item with itemid: {item_id} from order with orderid: {order_id}.")
    return response(200, "Successfully removed", request.headers['Id-request'])


@ app.get('/find/<order_id>')
def find_order(order_id: str):
    result = get_order(order_id)
    if result == None:
        app.logger.error(f"Order with orderid: {order_id} was not found.")
        return response(404, "Order not found", request.headers['Id-request'])
    app.logger.info(f"Successfully retrieved order with orderid {order_id}.")
    return response(200, result, request.headers['Id-request'])


@ app.post('/checkout/<order_id>')
def checkout(order_id):
    result = get_order(order_id)

    if result["paid"]:
        app.logger.error(f"Order with orderid: {order_id} is already paid.")
        return response(402, "Order already paid", request.headers['Id-request'])

    # This is to have the order done!
    url = f'/pay/{result["user"]}/{order_id}/{result["total_cost"]}'

    pay_info = serviceNode.sendMessageCoordinator(url, "payment", "POST")
    app.logger.info(f"Sending payment information to serviceNode.coordinators: {serviceNode.coordinators}.")
    pay_status = pay_info["status"]

    if pay_status != 200:
        app.logger.error(f"There is not enough money")
        return response(401, "Not enough money", request.headers['Id-request'])

    items = encodeBase64(json.dumps(result["items"]))

    url = f'/substract_multiple/{items}'

    # Remove the stock
    stock_info = serviceNode.sendMessageCoordinator(url, "stock", "POST")
    stock_status = stock_info["status"]

    app.logger.info(f"Removing items from stock for order with orderid: {order_id}.")

    if stock_status != 200:
        # Reimburse payment
        url = f'/add_funds/{result["user"]}/{result["total_cost"]}'
        pay_info = serviceNode.sendMessageCoordinator(url, "payment", "POST")
        app.logger.info(f"Not enough stock! Reimburse payment for order with orderid: {order_id}.")
        return response(501, "Not enough stock for the request", request.headers['Id-request'])

    newvalues = {"$set": {"paid": True}}

    serviceNode.collection.update_one({"_id": order_id}, newvalues)

    app.logger.info(f"Order with orderid: {order_id} is successfully paid.")
    return response(200, "Order successful", request.headers['Id-request'])


@app.after_request
def after_request_func(returned_response):
    return process_after_request(returned_response, serviceNode)


app.run(host=serviceNode.ip_address, port=2801)
