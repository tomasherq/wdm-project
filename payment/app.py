from common.node_service import NodeService
from common.node_service import NodeService, process_before_request, process_after_request
from responses import Response
from common.tools import *


app = Flask(f"payment-service-{ID_NODE}")


serviceNode = NodeService("payment")

# TODO:Remove all non used stuff from functions


@app.before_request
def preprocess():
    return process_before_request(request, serviceNode)


@app.get('/getHash')
def getHash():
    return serviceNode.getHash()


@app.get('/dumpDB/<id>')
def dumpDB(id: str):
    return serviceNode.dumpDB(id)


@app.get('/restoreDB/<id>')
def restoreDB(id: str):
    return serviceNode.restoreDB(id)


@app.get('/alive')
def alive():
    return serviceNode.aliveResponse()


@app.post('/remove_nodes/<nodes_down>')
def remove_nodes_api(nodes_down: str):
    reply = serviceNode.remove_peer_nodes(nodes_down)

    return response(200, {"message": reply})


@ app.route('/ping')
def ping_service():
    return "Hello there (°▽°)/"


def helper_find_user(user_id):
    user_object = serviceNode.collection.find_one({"_id": user_id})
    if user_object == None:
        return response(404, {"status_code": 404, 'message': "User not found"})
    return user_object


def helper_find_order(order_id):

    url = f"/find/{order_id}"
    service = "order"

    orderInfo = serviceNode.sendMessageCoordinator(url, service, "GET")

    code = orderInfo["status"]
    if code == 404:
        return 404

    order_collection = orderInfo["message"]
    return order_collection


@app.post('/create_user')
def create_user():
    user_id = request.headers["Id-object"]
    timestamp = request.headers["Timestamp"]

    serviceNode.collection.insert_one({"_id": user_id, "credit": 0.0, "timestamp": timestamp})
    return response(200, {"status_code": 200, "user_id": user_id}, request.headers['Id-request'])


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    result = serviceNode.collection.find_one({"_id": user_id})
    if result == None:
        return response(404, {'status_code': 404, 'message': "User not found"}, request.headers['Id-request'])
    return response(200, {"status_code": 200, "user_id": user_id, "credit": result["credit"]}, request.headers['Id-request'])


@app.post('/add_funds/<user_id>/<float:amount>')
def add_credit(user_id: str, amount: float):
    user_object = helper_find_user(user_id)
    if type(user_object) is Response:
        return user_object

    user_credit = float(user_object["credit"])

    query = {"_id": user_id}
    newvalues = {"$set": {"credit": user_credit+float(amount)}}

    serviceNode.collection.update_one(query, newvalues)
    return response(200, {"status_code": 200, "done": True}, request.headers['Id-request'])
    # return response(200, f"Updated, new credit: {user_credit}", request.headers['Id-request'])


@app.post('/pay/<user_id>/<order_id>/<float:amount>')
def remove_credit(user_id: str, order_id: str, amount: float):

    user_object = helper_find_user(user_id)

    if type(user_object) is Response:
        return user_object

    user_credit = float(user_object['credit'])
    if user_credit < float(amount):
        return response(401, {'status_code': 401, 'message': "Not enough credit"}, request.headers['Id-request'])

    query = {"_id": user_id}
    newvalues = {"$set": {"credit": user_credit-float(amount)}}
    serviceNode.collection.update_one(query, newvalues)

    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    serviceNode.collection.delete_one({"_id": order_id})
    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):

    order_collection = helper_find_order(order_id)
    order_status = order_collection["paid"]

    return response(200, {"status_code": 200, "paid": order_status}, request.headers['Id-request'])


@app.after_request
def after_request_func(returned_response):
    return process_after_request(returned_response, serviceNode)


app.run(host=serviceNode.ip_address, port=2801)
