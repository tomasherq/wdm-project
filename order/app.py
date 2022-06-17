
from common.tools import *
from common.node_service import NodeService, process_before_request, process_after_request
from common.async_calls import send_requests, asyncio
# I want to make the API directions variables accessible by every service!
# Keep loggin of the files

app = Flask(f"order-service-{ID_NODE}", "/orders")


serviceNode = NodeService("order")


def get_order(order_id):
    return serviceNode.collection.find_one({"_id": order_id})


@app.before_request
def preprocess():
    return process_before_request(request, serviceNode)


@app.get('/getHash')
def getHash():
    return serviceNode.getHash()


@app.get('/alive')
def alive():
    return serviceNode.aliveResponse()


@app.get('/dumpDB/<id>')
def dumpDB(id: str):
    return serviceNode.dumpDB(id)


@app.get('/restoreDB/<id>')
def restoreDB(id: str):
    return serviceNode.restoreDB(id)


@app.post('/remove_nodes/<nodes_down>')
def remove_nodes_api(nodes_down: str):
    reply = serviceNode.remove_peer_nodes(nodes_down)

    return response(200, {"message": reply})


@ app.route('/ping')
def ping_service():
    return "Hello there (°▽°)/"


# Check the user id
@ app.post('/create/<user_id>')
def create_order(user_id):

    url = f"/find_user/{user_id}"

    user_info = serviceNode.sendMessageCoordinator(url, "payment", "GET")

    if user_info['status_code'] == 404:
        return response(404, user_info, request.headers['Id-request'])

    order_id = request.headers["Id-object"]
    timestamp = request.headers["Timestamp"]
    serviceNode.collection.insert_one({"_id": order_id,  "paid": False,
                                       "items": [], "user": user_id, "total_cost": 0, "timestamp": timestamp})

    return response(200, {'status_code': 200, 'order_id': order_id}, request.headers['Id-request'])


@ app.delete('/remove/<order_id>')
def remove_order(order_id):

    if get_order(order_id) == None:
        return response(404, {'status_code': 404, 'message': "Order not found"}, request.headers['Id-request'])

    serviceNode.collection.delete_one({"_id": order_id})

    return response(200, {'status_code': 200, 'order_id': order_id}, request.headers['Id-request'])


@ app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):

    order = get_order(order_id)

    if order == None:
        return response(404, {'status_code': 404, 'message': "Order not found"}, request.headers['Id-request'])

    url = f"/check_availability/{item_id}"

    item_info = serviceNode.sendMessageCoordinator(url, "stock", "GET")

    if item_info['stock'] == 0:
        return response(400, {'status_code': 400, 'message': "No stock for this item"}, request.headers['Id-request'])

    items = order["items"]
    items.append(item_id)

    newvalues = {"$set": {"items": items, "total_cost": order["total_cost"] + float(item_info['price'])}}
    serviceNode.collection.update_one({"_id": order_id}, newvalues)

    return response(200, {'status_code': 200}, request.headers['Id-request'])


@ app.delete('/removeItem/<order_id>/<item_id>')
def remove_item(order_id, item_id):
    order = get_order(order_id)

    if order == None:
        return response(404, {'status_code': 404, 'message': "Order not found"}, request.headers['Id-request'])

    if item_id not in order["items"]:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    newvalues = {"$set": {"items": order["items"] - [item_id]}}

    serviceNode.collection.update_one({"_id": order_id}, newvalues)

    return response(200, {'status_code': 200}, request.headers['Id-request'])


@ app.get('/find/<order_id>')
def find_order(order_id: str):
    result = get_order(order_id)
    if result == None:
        return response(404, {'status_code': 404, 'message': "Order not found"}, request.headers['Id-request'])

    return response(200, {'status_code': 200, 'order_id': order_id, 'paid': result['paid'], 'items': result['items'],
                          'user_id': result['user'], 'total_cost': result['total_cost']}, request.headers['Id-request'])


@ app.post('/checkout/<order_id>')
def checkout(order_id):
    result = get_order(order_id)

    if result["paid"]:
        app.logger.error(f"Order with orderid: {order_id} is already paid.")

        return response(402, {'status_code': 402, 'message': "Order already paid"}, request.headers['Id-request'])
    # This is to have the order done!
    url = f'/pay/{result["user"]}/{order_id}/{float(result["total_cost"])}'

    pay_info = serviceNode.sendMessageCoordinator(url, "payment", "POST")
    pay_status = pay_info["status_code"]

    if pay_status != 200:
        return response(401, {'status_code': 401, 'message': "Not enough credit"}, request.headers['Id-request'])

    items = encodeBase64(json.dumps(result["items"]))

    url = f'/substract_multiple/{items}'

    # Remove the stock
    stock_info = serviceNode.sendMessageCoordinator(url, "stock", "POST")
    stock_status = stock_info["status_code"]

    if stock_status != 200:
        # Reimburse payment
        url = f'/add_funds/{result["user"]}/{float(result["total_cost"])}'
        pay_info = serviceNode.sendMessageCoordinator(url, "payment", "POST")
        return response(501, {'status_code': 501, 'message': "Not enough stock for the request"}, request.headers['Id-request'])

    newvalues = {"$set": {"paid": True}}

    serviceNode.collection.update_one({"_id": order_id}, newvalues)

    return response(200, {'status_code': 200}, request.headers['Id-request'])


@app.after_request
def after_request_func(returned_response):
    return process_after_request(returned_response, serviceNode)


app.run(host=serviceNode.ip_address, port=2801)
