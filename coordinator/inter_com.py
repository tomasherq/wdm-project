from common.tools import *
from common.coordinator import *

from collections import defaultdict, Counter 
import time

DEBUG=True


serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}-internal")
DEBUG = True
# Each one of the services will run an instance, run in a different port and have different clients

# I want to have the address and port of the clients.

replies = defaultdict(lambda: {})
nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")


@app.before_request
def check_address_node():

    dir_node = "http://"+request.remote_addr+":2801"
    if dir_node not in nodesDirections and not DEBUG:

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


@app.post('/fix_consistency')
def fix_consistency():

    nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")

    ip_addr = request.remote_addr
    if ip_addr in nodesDirections:
        return response(403, "Not authorized.")
    
    # get all hashes of databases with the corresponding node directions
    node_dir, responses = get_hash(nodesDirections)
    
    hashes = list()
    for item in responses:
        hashes.append(item["hash"])

    # find the most common hash
    counter_responses = Counter(hashes)
    common_hash = max(hashes,key=hashes.count)
    times_common_hash = counter_responses[common_hash]

    # find the consistent and inconsistent nodes
    consistent_nodes = []
    inconsistent_nodes = []

    # check if more than one databases have the same common hash
    count = 0
    for ele in counter_responses:
        if counter_responses[ele] == times_common_hash:
            count=count+1
    if count <= 1:
        # We found the most common hash. This is the variable common_hash"
        for n in range(len(node_dir)):
            if hashes[n] == common_hash:
                consistent_nodes.append(node_dir[n])
            else:
                inconsistent_nodes.append(node_dir[n])
        
    else:
        # Need to check time of last update

        timestamps = list()
        for item in responses:
            timestamps.append(item["timestamp"])

        last_timestamp = max(timestamps)
        pos_last_timestamp = timestamps.index(last_timestamp)
        node_last_updated = node_dir[pos_last_timestamp]
        
        consistent_nodes.append(node_last_updated)
        inconsistent_nodes = node_dir 
        inconsistent_nodes.remove(node_last_updated)
    
    debug_print(consistent_nodes)
    debug_print(inconsistent_nodes)
    
    return response(200, "Consistency is fixed now")


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2802)
