import sys

from itsdangerous import base64_encode


from common.tools import *
from common.coordinator_service import *

serviceID = sys.argv[2]
app = Flask(f"coord-service-{serviceID}-{ID_NODE}")

coordinatorService = CoordinatorService(serviceID)


@app.before_request
def load_up_nodes():
    coordinatorService.loadUpNodes("general")
    coordinatorService.checkUpNodes()

    if request.remote_addr in coordinatorService.nodesDirections:
        return response(403, "Not authorized.")


@app.route('/ping')
def ping_service():
    return f'Hello, I am ping service!'


@app.get('/consistency')
def check_consistency():

    node_dir, responses = get_hash(coordinatorService.nodesUp)

    result = responses.count(responses[0]) == len(responses)

    return response(200, f"Consistency: {result}")


@app.route(f'/{coordinatorService.service}/<path:path>', methods=['POST', 'GET', 'DELETE'])
def catch_all(path):

    idRequest = getIdRequest(path)

    headers = {"Id-request": idRequest}
    isReadRequest = request_is_read(request)

    # Problem with hash, the request goes always to the same
    reply = {"status_code": 505}
    while is_invalid_reply(reply):

        nodeDir = coordinatorService.getNodeToSend(isReadRequest, idRequest)

        if not isReadRequest:
            headers["Redirect"] = "1"
            idObject = getIdRequest(str(time.time())+"-"+nodeDir)
            headers["Id-object"] = idObject

        url = f'{nodeDir}/{path}'

        reply = process_reply(make_request(request.method, url, headers=headers))

        if is_invalid_reply(reply):
            coordinatorService.removeNodes([nodeDir], "inter")
            coordinatorService.sendRemoveNodes(encodeBase64(json.dumps([nodeDir])))

    return response(reply["status_code"], reply)


app.run(host=getIPAddress(f"{serviceID}_COORD_ADDRESS"), port=2801)
