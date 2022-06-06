import sys

from random import randint

from common.tools import *
from common.coordinator import *

serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}")
nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")
nodesUp = nodesDirections

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.


@app.route('/ping')
def ping_service():
    return f'Hello, I am ping service!'


service = serviceID.lower()
if service == "order":
    service = "orders"


@app.before_request
def load_up_nodes():
    nodesUp = get_up_nodes(nodesDirections, serviceID)
    if request.remote_addr in nodesDirections:
        return response(403, "Not authorized.")


@app.get('/consistency')
def check_consistency():

    node_dir, responses = get_hash(nodesUp)

    result = responses.count(responses[0]) == len(responses)

    return response(200, f"Consistency: {result}")


@app.route(f'/{service}/<path:path>', methods=['POST', 'GET', 'DELETE'])
def catch_all(path):

    idRequest = getIdRequest(path)

    headers = {"Id-request": idRequest}

    # Problem with hash, the request goes always to the same

    if request_is_read(request):

        indexNode = randint(0, len(nodesUp)-1)
    else:
        headers["Redirect"] = "1"
        indexNode = getIndexFromCheck(len(nodesUp), idRequest)

    nodeDir = nodesUp[indexNode]

    idObject = getIdRequest(str(time.time())+"-"+nodeDir)
    headers["Id-object"] = idObject

    url = f'{nodeDir}/{path}'

    reply = process_reply(requests.request(request.method, url, headers=headers))

    return response(reply["status_code"], reply)


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2801)
