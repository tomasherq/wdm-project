from common.tools import *
from common.node_service import NodeService

app = Flask(f"payment-service-{ID_NODE}")


serviceNode = NodeService("payment")

# TODO:Remove all non used stuff from functions

@app.get('/getHash')
def getHash():
    d = serviceNode.database.command("dbHash")
    return response(200, d["md5"])


def helper_find_user(user_id):
    user_object = serviceNode.collection.find_one({"_id": user_id})
    if user_object == None:
        return response(404, "User not found", request.headers['Id-request'])
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


responses = defaultdict(lambda: {})


@app.before_request
def log_request_info():
    id_request = request.headers["Id-request"]

    responses[id_request]["forward"] = "Redirect" in request.headers
    if responses[id_request]["forward"] == True:

        results = {}
        try:
            results = serviceNode.forwardRequest(request.path, request.method, id_request)
        except Exception as e:
            print(str(e), file=sys.stdout, flush=True)

        responses[id_request]["results"] = results


@app.post('/create_user')
def create_user():
    user_id = str(getAmountOfItems(serviceNode.collection))
    serviceNode.collection.insert_one({"_id": user_id, "credit": 0})
    return response(200, f"Correctly added, userid {user_id}", request.headers['Id-request'])


@app.get('/find_user/<user_id>')
def find_user(user_id: str):
    result = serviceNode.collection.find_one({"_id": user_id})
    if result == None:
        return response(404, "User not found", request.headers['Id-request'])

    return response(200, result, request.headers['Id-request'])


@app.post('/add_funds/<user_id>/<int:amount>')
def add_credit(user_id: str, amount: int):
    user_object = helper_find_user(user_id)
    print(user_object)

    user_credit = int(user_object["credit"])

    query = {"_id": user_id}
    newvalues = {"$set": {"credit": user_credit+amount}}

    serviceNode.collection.update_one(query, newvalues)
    return response(200, f"Updated, new credit: {user_credit}", request.headers['Id-request'])


@app.post('/pay/<user_id>/<order_id>/<int:amount>')
def remove_credit(user_id: str, order_id: str, amount: int):
    user_object = helper_find_user(user_id)

    if user_object == 404:
        return response(404, "No order found", request.headers['Id-request'])  # Response has to be done here!

    user_credit = int(user_object["credit"])
    if user_credit < amount:
        return response(401, "Not enough credit", request.headers['Id-request'])

    query = {"_id": user_id}
    newvalues = {"$set": {"credit": user_credit-amount}}
    serviceNode.collection.update_one(query, newvalues)

    return response(200, f"Payment made, new credit: {user_credit}", request.headers['Id-request'])


@app.post('/cancel/<user_id>/<order_id>')
def cancel_payment(user_id: str, order_id: str):
    serviceNode.collection.delete_one({"_id": order_id})
    return response(200, "Order deleted", request.headers['Id-request'])


@app.post('/status/<user_id>/<order_id>')
def payment_status(user_id: str, order_id: str):

    order_collection = helper_find_order(order_id)
    order_status = order_collection["paid"]

    return response(200, f"Order status: {order_status}", request.headers['Id-request'])


@app.after_request
def after_request_func(returned_response):

    id_request = returned_response.headers["Id-request"]
    if responses[id_request]["forward"] is True:
        responses[id_request]["results"].append(returned_response.get_data().decode())

        if len(set(responses[id_request]["results"])) > 1:
            serviceNode.sendCheckConsistencyMsg(id_request)
            # Here we announce an inconsistency to the coordinator
            pass

    return returned_response


app.run(host=serviceNode.ip_address, port=2801)
