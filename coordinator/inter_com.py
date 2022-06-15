from common.tools import *
from common.coordinator_service import *
from collections import defaultdict, Counter
import time

DEBUG = True

serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}-internal")

# Each one of the services will run an instance, run in a different port and have different clients

replies = defaultdict(lambda: {})
coordinatorService = CoordinatorService(serviceID)


@app.before_request
def check_address_node():
    coordinatorService.loadUpNodes("inter")
    dir_node = "http://"+request.remote_addr+":2801"
    if dir_node not in coordinatorService.nodesUp and not DEBUG:

        return response(403, "Not authorized.")


@app.post('/request/<request_info>')
def catch_all(request_info):

    requestInfo = {}
    try:
        requestInfo = json.loads(decodeBase64(request_info))
    except:
        debug_print("JSON decoding error")
        return response(500, "Invalid format")
    serviceToCall = requestInfo["service"].upper()
    idRequest = requestInfo["id"]

    coordinatorsService = getAddresses(f"{serviceToCall}_COORD_ADDRESS")

    prefixUrl = requestInfo["service"]

    if prefixUrl == "order":
        prefixUrl = "orders"

    # This will forward the same answer to all nodes
    if idRequest in replies:
        replies[idRequest]['counter'] += 1
        # Wait for the answer before forwarding.
        while "content" not in replies[idRequest]:
            time.sleep(0.1)

        content = replies[idRequest]['content']
        if replies[idRequest]["counter"] == len(coordinatorService.nodesUp):
            replies.pop(idRequest, None)

        return content

    replies[idRequest]['counter'] = 1

    reply = {"status_code": 505}
    while is_invalid_reply(reply) and len(coordinatorsService) > 0:

        coordinator_choosen = coordinatorsService[getIndexFromCheck(len(coordinatorsService), idRequest)]

        url = f'{coordinator_choosen}/{prefixUrl}{requestInfo["url"]}'

        reply = process_reply(make_request(requestInfo["method"], url, {}))
        if is_invalid_reply(reply) and coordinator_choosen in coordinatorsService:
            coordinatorsService.remove(coordinator_choosen)
        else:
            break
    replies[idRequest]['content'] = reply

    return replies[idRequest]['content']


@app.post('/down_nodes/<nodes_down_raw>')
def report_down_nodes(nodes_down_raw: str):
    nodes_down = json.loads(decodeBase64(nodes_down_raw))

    if len(nodes_down) > 0:
        coordinatorService.removeNodes(nodes_down)

        if int(request.headers["Forwarding-coordinator"]) == ID_NODE:

            coordinatorService.sendRemoveNodes(nodes_down_raw)
    return response(200, {"msg": "Nodes fixed"})


@app.post('/fix_consistency')
def fix_consistency():

    # Get all hashes of databases with the corresponding node directions
    node_dir, responses = get_hash(coordinatorService.nodesUp)

    hashes = list()
    for item in responses:
        hashes.append(item["hash"])

    # Find the most common hash
    counter_responses = Counter(hashes)
    common_hash = max(hashes, key=hashes.count)
    times_common_hash = counter_responses[common_hash]

    # Find the consistent and inconsistent nodes
    consistent_nodes = []
    inconsistent_nodes = []

    # Check if more than one databases have the same common hash
    count = 0
    for ele in counter_responses:
        if counter_responses[ele] == times_common_hash:
            count = count+1
    if count <= 1:
        for n in range(len(node_dir)):
            if hashes[n] == common_hash:
                consistent_nodes.append(node_dir[n])
            else:
                inconsistent_nodes.append(node_dir[n])

    else:
        # Check time of last update
        timestamps = list()
        for item in responses:
            timestamps.append(item["timestamp"])

        last_timestamp = max(timestamps)
        pos_last_timestamp = timestamps.index(last_timestamp)
        node_last_updated = node_dir[pos_last_timestamp]

        consistent_nodes.append(node_last_updated)
        inconsistent_nodes = node_dir
        inconsistent_nodes.remove(node_last_updated)

    # Create an id for the restoring process using the current timestamp
    timestamp = str(time.time())
    restoring_id = getIdRequest(timestamp)
    # One of the consistent nodes will have to dump the db
    # The inconsistent ones will use it to restore
    dump_db(consistent_nodes, inconsistent_nodes, restoring_id)
    restore_db(inconsistent_nodes, restoring_id)

    return response(200, {"msg": "Consistency is fixed now"})


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2802)
