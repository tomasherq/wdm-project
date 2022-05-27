from common.tools import *

from collections import defaultdict
import time


serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}-internal")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.

replies = defaultdict(lambda: {})
nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")


@app.before_request()
def check_address_node():

    dir_node = "http://"+request.remote_addr+":2801"
    if dir_node not in nodesDirections:

        return response(403, "Not authorized.")


@app.post('/request/<request_info>')
def catch_all(request_info):

    requestInfo = {}
    try:
        requestInfo = json.loads(decodeBase64(request_info))
    except:
        print("JSON decoding error", file=sys.stdout, flush=True)
        return response(500, "Invalid format")

    serviceToCall = requestInfo["service"].upper()
    idRequest = requestInfo["id"]

    coordinatorsService = getAddresses(f"{serviceToCall}_COORD_ADDRESS")

    prefixUrl = requestInfo["service"]

    if prefixUrl == "order":
        prefixUrl = "orders"

    # This will forward the same answer to all servers
    if idRequest in replies:
        replies[idRequest]['counter'] += 1

        while "content" not in replies[idRequest]:
            time.sleep(0.1)

        content = replies[idRequest]['content']
        if replies[idRequest]["counter"] == len(nodesDirections):
            replies.pop(idRequest, None)

        return content

    replies[idRequest]['counter'] = 1

    # We could make them talk directly through this port but it complicates a lot the logic
    url = f'{coordinatorsService[getIndexFromCheck(len(coordinatorsService),idRequest)]}/{prefixUrl}{requestInfo["url"]}'

    replies[idRequest]['content'] = process_reply(requests.request(requestInfo["method"], url), True)

    return replies[idRequest]['content']


@app.post('/check_consistency')
def check_consistency():
    # This is the place where the node calls if there is an inconsistency
    return response(200, "Is fixed now")


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2802)
