from distutils.log import debug
from email import message
from common.tools import *
from flask import jsonify
from common.node_service import NodeService

app = Flask(f"stock-service-{ID_NODE}")

serviceNode = NodeService("stock")

@app.get('/getHash')
def getHash():
    d = serviceNode.database.command("dbHash")
    return response(200, d["md5"])


def get_item(item_id):
    return serviceNode.collection.find_one({"_id": item_id})


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


@app.post('/item/create/<int:price>')
def create_item(price: int):
    item_id = str(getAmountOfItems(serviceNode.collection))
    serviceNode.collection.insert_one({"_id": item_id, "price": price, "stock": 0})

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
            return response(400, {'status_code': 400, 'message': "No stock"}, request.headers['Id-request'])
        else:
            deleted_items.append(item)

    return response(200, {"status_code": 200}, request.headers['Id-request'])


@app.get("/check_availability/<item_id>")
def check_availability(item_id: str):
    result = serviceNode.collection.find_one({"_id": item_id})
    if result == None:
        return response(404, {'status_code': 404, 'message': "Item not found"}, request.headers['Id-request'])

    return response(200, {"status_code": 200, "stock": result["stock"], "price": result["price"]}, request.headers['Id-request'])

# This is the detection of inconsistencies


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
