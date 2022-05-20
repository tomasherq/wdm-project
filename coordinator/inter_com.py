from platform import node
from common.tools import *

from collections import defaultdict

app = Flask("order-service")

# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.

serviceID = sys.argv[2]

replies = defaultdict(lambda: {})
nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")


@app.post('/request/<str:request_info>', methods=['POST'])
def catch_all(request_info):

    ip_addr = request.remote_addr

    if ip_addr not in nodesDirections:
        return response(403, "Not authorized.")

    requestInfo = {}
    try:
        requestInfo = json.loads(decodeBase64(request_info))
    except:
        return response(500, "Invalid format")

    serviceToCall = requestInfo["service"].upper()
    idRequest = requestInfo["id"]

    # This will only work if everything is synchronous
    if idRequest in replies:
        replies[idRequest]['counter'] += 1
        content = replies[idRequest]['content']
        if replies[idRequest]["counter"] == len(nodesDirections):
            replies.pop(idRequest, None)

        return content

    replies[idRequest]['counter'] = 1

    coordinatorsService = getAddresses(f"{serviceToCall}_COORD_ADDRESS")

    url = f'http://{coordinatorsService[0]}{requestInfo["url"]}'

    replies[idRequest]['content'] = requests.post(url)

    return replies[idRequest]['content']


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2802)
