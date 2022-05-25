import sys

from common.tools import *

serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.


@app.route('/ping')
def ping_service():
    return f'Hello, I am ping service!'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST', 'GET', 'DELETE'])
def catch_all(path):

    nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")

    ip_addr = request.remote_addr

    if ip_addr in nodesDirections:
        return response(403, "Not authorized.")

    responses = []

    for nodeDir in nodesDirections:
        url = f'{nodeDir}/{path}'

        if request.method == 'POST':
            reply = json.loads(requests.post(url).text)
        elif request.method == "GET":
            reply = json.loads(requests.get(url).text)
        elif request.method == "DELETE":
            reply = json.loads(requests.delete(url).text)
        else:
            return response(401, f"Used invalid method")

        responses.append(reply)

    if all(reply == responses[0] for reply in responses):
        return responses[0]
    else:
        return response(501, f"Server error occured")


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2801)
