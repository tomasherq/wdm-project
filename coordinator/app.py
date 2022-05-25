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

    print(path, file=sys.stdout, flush=True)

    if ip_addr in nodesDirections:
        return response(403, "Not authorized.")

    responses = []
    print("NodesDirections: ", file=sys.stdout, flush=True )
    print(nodesDirections, file=sys.stdout, flush=True)
    for nodeDir in nodesDirections:
        url = f'{nodeDir}/{path}'
        print("URL:", file=sys.stdout, flush=True )
        print(url, file=sys.stdout, flush=True)
        if request.method == 'POST':
            print("POST REQUEST OBJECT:", file=sys.stdout, flush=True)
            print(request, file=sys.stdout, flush=True)

            print("requests object to decode:", file=sys.stdout, flush=True )
            print(requests.post(url).text, file=sys.stdout, flush=True)
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
