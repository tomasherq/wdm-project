from distutils.log import debug
from email import message
from common.tools import *
from common.node_service import NodeService, process_before_request, process_after_request

app = Flask(f"stock-service-{ID_NODE}")

serviceNode = NodeService("stock")


@app.before_request
def preprocess():
    return process_before_request(request, serviceNode)


@app.get('/getHash')
def getHash():
    return serviceNode.getHash()


@app.get('/dumpDB/<id>/<inconsistent_nodes>')
def dumpDB(id: str, inconsistent_nodes: str):
    return serviceNode.dumpDB(id, inconsistent_nodes)


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


def get_item(item_id):
    return serviceNode.collection.find_one({"_id": item_id})


@app.post('/item/create/<price>')
def create_item(price: float):

    price = float(price)
    item_id = request.headers["Id-object"]
    timestamp = request.headers["Timestamp"]
    serviceNode.collection.insert_one({"_id": item_id, "price": price, "stock": 0, "timestamp": timestamp})

    return response(200, {"status_code": 200, "item_id": item_id}, request.headers['Id-request'])


@app.get('/find/<item_id>')
def find_item(item_id: str):
    result = serviceNode.collection.find_one({"_id": item_id})
    if result == None:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    return response(200, {"status_code": 200, "stock": result["stock"], "price": result["price"]}, request.headers['Id-request'])


@app.post('/add/<item_id>/<int:amount>')
def add_stock(item_id: str, amount: int):

    if get_item(item_id) == None:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    if amount < 0:
        return response(400, {'status_code': 400, 'message': "Invalid amount"}, request.headers['Id-request'])

    query = {"_id": item_id, }
    newvalues = {"$set": {"stock": amount}}

    serviceNode.collection.update_one(query, newvalues)
    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.post('/subtract/<item_id>/<int:amount>')
def remove_stock(item_id: str, amount: int):

    data_object = serviceNode.collection.find_one({"_id": item_id})

    if data_object == None:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    stock = int(data_object["stock"])
    if stock < amount:
        return response(401, {'status_code': 401, 'message': "Not enough stock"}, request.headers['Id-request'])

    if amount < 0:
        return response(400, {'status_code': 400, 'message': "Invalid amount"}, request.headers['Id-request'])

    query = {"_id": item_id, }
    newvalues = {"$set": {"stock": stock-amount}}
    print(newvalues)
    serviceNode.collection.update_one(query, newvalues)
    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.post('/substract_multiple/<items_json>')
def remove_multiple_stock(items_json: str):
    items = []
    try:
        items = json.loads(decodeBase64(items_json))
    except:
        return response(500, {'status_code': 500, 'message': "Invalid format"}, request.headers['Id-request'])

    deleted_items = []
    for item in set(items):

        amount = items.count(item)
        result = remove_stock(item, amount)
        if result.status_code != 200:
            for deleted_item in deleted_items:
                add_stock(deleted_item, amount)
            return response(result.status_code, {'status_code': result.status_code, 'message': result.message}, request.headers['Id-request'])
        else:
            deleted_items.append(item)

    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.get("/check_availability/<item_id>")
def check_availability(item_id: str):
    result = serviceNode.collection.find_one({"_id": item_id})
    if result == None:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    return response(200, {"status_code": 200, "stock": result["stock"], "price": result["price"]}, request.headers['Id-request'])


@app.after_request
def after_request_func(returned_response):
    return process_after_request(returned_response, serviceNode)


app.run(host=serviceNode.ip_address, port=2801)
