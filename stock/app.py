from common.tools import *
from common.node_service import NodeService, process_before_request, process_after_request

app = Flask(f"stock-service-{ID_NODE}")

serviceNode = NodeService("stock")


@app.before_request
def preprocess():
    return process_before_request(request, serviceNode)


@app.get('/getHash')
def getHash():
    d = serviceNode.database.command("dbHash")
    return response(200, d["md5"])


def get_item(item_id):
    return serviceNode.collection.find_one({"_id": item_id})


@app.post('/item/create/<int:price>')
def create_item(price: int):
    item_id = str(getAmountOfItems(serviceNode.collection))
    serviceNode.collection.insert_one({"_id": item_id, "price": price, "stock": 0})

    return response(200, item_id, request.headers['Id-request'])


@app.get('/find/<item_id>')
def find_item(item_id: str):
    result = serviceNode.collection.find_one({"_id": item_id})
    if result == None:
        return response(404, "Item not found", request.headers['Id-request'])

    return response(200, result, request.headers['Id-request'])


@app.post('/add/<item_id>/<int:amount>')
def add_stock(item_id: str, amount: int):

    if get_item(item_id) == None:
        return response(404, "Item not found", request.headers['Id-request'])

    if amount < 0:
        return response(400, "Invalid amount", request.headers['Id-request'])

    query = {"_id": item_id, }
    newvalues = {"$set": {"stock": amount}}

    serviceNode.collection.update_one(query, newvalues)
    return response(200, "Updated", request.headers['Id-request'])


@app.post('/subtract/<item_id>/<int:amount>')
def remove_stock(item_id: str, amount: int):

    data_object = serviceNode.collection.find_one({"_id": item_id})

    if data_object == None:
        return response(404, "Item not found", request.headers['Id-request'])

    stock = int(data_object["stock"])
    if stock < amount:
        return response(401, "Not enough stock", request.headers['Id-request'])

    if amount < 0:
        return response(400, "Invalid amount", request.headers['Id-request'])

    query = {"_id": item_id, }
    newvalues = {"$set": {"stock": stock-amount}}
    print(newvalues)
    serviceNode.collection.update_one(query, newvalues)
    return response(200, "Stock substracted", request.headers['Id-request'])


@app.post('/substract_multiple/<items_json>')
def remove_multiple_stock(items_json: str):
    items = []
    try:
        items = json.loads(decodeBase64(items_json))
    except:
        return response(500, "Invalid format", request.headers['Id-request'])

    deleted_items = []
    for item in set(items):

        amount = items.count(item)
        result = remove_stock(item, amount)
        if json.loads(result)["status"] != 200:
            for deleted_item in deleted_items:
                add_stock(deleted_item, amount)
            return response(400, "No stock", request.headers['Id-request'])
        else:
            deleted_items.append(item)

    return response(200, "Done", request.headers['Id-request'])


@app.get("/check_availability/<item_id>")
def check_availability(item_id: str):
    result = serviceNode.collection.find_one({"_id": item_id})
    if result == None:
        return response(404, "Item not found", request.headers['Id-request'])

    return response(200, (result["stock"], result["price"]), request.headers['Id-request'])

# This is the detection of inconsistencies


@app.after_request
def after_request_func(returned_response):
    return process_after_request(returned_response, serviceNode)


app.run(host=serviceNode.ip_address, port=2801)
