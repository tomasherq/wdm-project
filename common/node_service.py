from common.tools import *
from collections import defaultdict
from common.async_calls import send_requests, asyncio


class NodeService():

    def __init__(self, service):

        self.database = getDatabase(service+"s")
        self.collection = getCollection(self.database, service)

        self.service = service.upper()

        self.ip_address = getIPAddress(f"{self.service}_NODES_ADDRESS")

        self.coordinators = getAddresses(f"{self.service}_COORD_ADDRESS", 2802)
        self.peer_nodes = getAddresses(f"{self.service}_NODES_ADDRESS")

        self.peer_nodes.append("http://192.168.124.200:2801")

        self.isInRecover = False

        self.peer_nodes.remove("http://"+self.ip_address+":2801")

        self.dropCollection()

    def dropCollection(self):
        self.collection.drop()

    def sendMessageCoordinator(self, url, service, method):
        info_for_coord = {"url": url, "service": service, "method": method}

        idInfo = getIdRequest(json.dumps(info_for_coord))
        info_for_coord["id"] = idInfo
        infoEncoded = encodeBase64(json.dumps(info_for_coord))
        coordinatorAddress = self.coordinators[getIndexFromCheck(len(self.coordinators), idInfo)]

        url = f'{coordinatorAddress}/request/{infoEncoded}'
        content = process_reply(requests.post(url))
        return content

    def forwardRequest(self, url, method, headers):

        urls = list()
        for node in self.peer_nodes:
            urls.append(f"{node}{url}")

        return asyncio.new_event_loop().run_until_complete(send_requests(urls, method, headers))

    def sendFixConsistencyMsg(self, idInfo, nodes_down_report):

        debug_print("Quw?")
        coordinatorAddress = self.coordinators[getIndexFromCheck(len(self.coordinators), idInfo)]

        nodes_down = encodeBase64(json.dumps(nodes_down_report))

        url = f'{coordinatorAddress}/fix_consistency/{nodes_down}'
        content = process_reply(requests.post(url))
        return content


responses = defaultdict(lambda: {})


def process_before_request(request, serviceNode):

    if "Id-request" in request.headers:
        id_request = request.headers["Id-request"]

        if id_request in responses and responses[id_request]["forward"] is True:
            return response(200, {"status_code": 200, "message": "The request was already made."})

        responses[id_request]["forward"] = "Redirect" in request.headers
        if responses[id_request]["forward"] is True:

            headers = {"Id-object": request.headers["Id-object"], "Id-request": id_request}

            results = {}
            try:
                results = serviceNode.forwardRequest(request.path, request.method, headers)
            except Exception as e:
                print(str(e), file=sys.stdout, flush=True)

            responses[id_request]["results"] = results


def process_after_request(returned_response, serviceNode):

    # This is to start the recovery
    if (serviceNode.isInRecover or serviceNode.collection.is_queue_empty()) is False:
        serviceNode.collection.process_queue()

    if "Id-request" in returned_response.headers:
        id_request = returned_response.headers["Id-request"]
        if responses[id_request]["forward"] is True:
            responses[id_request]["results"].append(returned_response.get_data().decode())

            unique_responses = set(responses.pop(id_request)["results"])
            if len(unique_responses) > 1:

                for response_node in unique_responses:

                    nodes_down_report = []

                    if "host" in response_node and "port" in response_node:
                        response_node = json.loads(response_node)
                        node_down = f'http://{response_node["host"]}:{response_node["port"]}'
                        nodes_down_report.append(node_down)
                serviceNode.sendFixConsistencyMsg(id_request, nodes_down_report)
                # Here we announce an inconsistency to the coordinator
                pass

    return returned_response
