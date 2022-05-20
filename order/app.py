from common.tools import *

# I want to make the API directions variables accessible by every service!
# Keep loggin of the files


app = Flask(f"order-service-{ID_NODE}")


orderCollection = getCollection("orders", "order")
coordinators = getAddresses("ORDER_COORD_ADDRESS")


# Change the field _id to be the order_id and so

def get_order(order_id):
    return orderCollection.find_one({"order_id": order_id}, {"_id": 0})


@app.route('/')
def ping_service():
    return f'Hello, I am ping service!'


@app.post('/create/<user_id>')
def create_order(user_id):
    # Maybe add security? --> I want an ngnix rather than this crap

    if not checkAccess(request, coordinators):
        return response(403, f"Access restricted")
    order_id = str(getAmountOfItems(orderCollection))
    orderCollection.insert_one({"order_id": order_id, "paid": False, "items": [], "user": user_id, "total_cost": 0})
    return response(200, f"Correctly added, orderid {order_id}")


@app.delete('/remove/<order_id>')
def remove_order(order_id):
    if not checkAccess(request, coordinators):
        return response(403, f"Access restricted")
    if get_order(order_id) == None:
        return response(404, "Order not found")

    orderCollection.delete_one({"order_id": order_id})
    return response(200, f"Correctly deleted, orderid {order_id}")


@app.post('/addItem/<order_id>/<item_id>')
def add_item(order_id, item_id):

    order = get_order(order_id)
    if order == None:
        return response(404, "Order not found")

    info = {"url": f"/check_availability/{item_id}", "service": "payment"}

    item_info = sendMessageCoordinator(info, coordinators)

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

# The services should only talk with their coordinator to prevent inconsistency


@app.post('/checkout/<order_id>')
def checkout(order_id):
    result = get_order(order_id)

    if result["paid"]:
        return response(402, "Order already paid")

    # This is to have the order done!
    info = {"url": f'/pay/{result["user"]}/{order_id}/{result["total_cost"]}', "service": "payment"}

    pay_info = sendMessageCoordinator(info, coordinators)

    pay_status = json.loads(pay_info.text)["status"]

    if pay_status != 200:
        return response(401, "Not enough money")

    items = encodeBase64(json.dumps(result["items"]))

    info = {"url": f'/substract_multiple/{items}', "service": "stock"}

    # Remove the stock
    stock_info = sendMessageCoordinator(info, coordinators)
    stock_status = json.loads(stock_info.text)["status"]

    if stock_status != 200:
        # Reimburse payment
        info = {"url": f'/add_funds/{result["user"]}/{result["total_cost"]}', "service": "payment"}
        pay_info = sendMessageCoordinator(info, coordinators)

        return response(501, "Not enough stock for the request")

    newvalues = {"$set": {"paid": True}}
    orderCollection.update_one({"order_id": order_id}, newvalues)

    return response(200, "Order successful")


app.run(host=getIPAddress("ORDER_NODES_ADDRESS"), port=2801)
