import sys

from random import randint

from common.tools import *

serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}")
nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.


@app.route('/ping')
def ping_service():
    return f'Hello, I am ping service!'


service = serviceID.lower()
if service == "order":
    service = "orders"


@app.before_request
def check_address_node():
    if request.remote_addr in nodesDirections:
        return response(403, "Not authorized.")


@app.route(f'/{service}/<path:path>', methods=['POST', 'GET', 'DELETE'])
def catch_all(path):

    idRequest = getIdRequest(path)

    headers = {"Id-request": idRequest}
    if request_is_read(request):

        indexNode = randint(0, len(nodesDirections)-1)
    else:
        headers["Redirect"] = "1"
        indexNode = getIndexFromCheck(len(nodesDirections), idRequest)

    nodeDir = nodesDirections[indexNode]

    url = f'{nodeDir}/{path}'

    reply = process_reply(requests.request(request.method, url, headers=headers))

    return response(reply["status"], reply["message"])


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2801)
