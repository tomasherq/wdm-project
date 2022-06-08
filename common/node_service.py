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

        self.isInRecover = False

        self.full_address = f"http://"+self.ip_address+":2801"

        self.peer_nodes.remove("http://"+self.ip_address+":2801")

        self.dropCollection()

    def dropCollection(self):
        self.collection.drop()

    def sendMessageCoordinator(self, url, service, method):
        info_for_coord = {"url": url, "service": service, "method": method}

        idInfo = getIdRequest(json.dumps(info_for_coord))
        info_for_coord["id"] = idInfo
        infoEncoded = encodeBase64(json.dumps(info_for_coord))

        coordinators_available = self.coordinators

        # This code is everywhere and I kind of hate it
        # maybe we should create a wrapper for python.
        reply = {"status_code": 505}
        while is_invalid_reply(reply):

            coordinatorAddress = coordinators_available[getIndexFromCheck(len(self.coordinators), idInfo)]
            url = f'{coordinatorAddress}/request/{infoEncoded}'

            reply = process_reply(make_request("POST", url, {}))

            if is_invalid_reply(reply) and coordinatorAddress in coordinators_available:
                coordinators_available.remove(coordinatorAddress)

        return reply

    def forwardRequest(self, url, method, headers):

        urls = list()
        for node in self.peer_nodes:
            urls.append(f"{node}{url}")

        return asyncio.new_event_loop().run_until_complete(send_requests(urls, method, headers))

    def remove_peer_nodes(self, nodes_down):

        try:
            if isinstance(nodes_down, str):
                nodes_down = json.loads(decodeBase64(nodes_down))

            for node in nodes_down:
                if node in self.peer_nodes:
                    self.peer_nodes.remove(node)

            return "Success"
        except Exception as e:
            return str(e)

    def reportDownNodes(self, nodes_down_report):

        # We are aware that if this coordinator is down it will not be forwarded
        # But is way to complex to install that.
        coord_forward = str(getIndexFromCheck(len(self.coordinators), getIdRequest(str(time.time())))+1)

        nodes_down = encodeBase64(json.dumps(nodes_down_report))
        self.remove_peer_nodes(nodes_down_report)

        urls = list()
        for coordinator in self.coordinators:
            urls.append(f"{coordinator}/down_nodes/{nodes_down}")

        response = asyncio.new_event_loop().run_until_complete(
            send_requests(urls, "POST", {"Forwarding-coordinator": coord_forward}))
        return response

    def sendFixConsistencyMsg(self, idInfo):
        coordinators_available = self.coordinators
        reply = {"status_code": 505}
        while is_invalid_reply(reply):

            coordinatorAddress = coordinators_available[getIndexFromCheck(len(self.coordinators), idInfo)]
            url = f'{coordinatorAddress}/fix_consistency'
            reply = process_reply(make_request("POST", url, {}))

            if is_invalid_reply(reply) and coordinatorAddress in coordinators_available:
                coordinators_available.remove(coordinatorAddress)

        return reply

    def getHash(self):
        d = self.database.command("dbHash")
        last_update = list(self.collection.collection.find().sort("timestamp", -1))[0]
        timestamp = last_update.get('timestamp')

        return response(200, {'hash': d["md5"], 'timestamp': timestamp})

    def dumpDB(self, id):
        service = self.service.lower()
        command = f'sh common/db_restore/dump_db.sh {service} {id}'
        os.system(command)
    
    def restoreDB(self, id):
        service = self.service.lower()
        command = f'sh common/db_restore/restore_db.sh {service} {id}'
        os.system(command)

responses = defaultdict(lambda: {})


def process_before_request(request, serviceNode):

    if "Id-request" in request.headers:
        id_request = request.headers["Id-request"]

        if id_request in responses and responses[id_request]["forward"] is True:
            return response(405, {'status_code': 405, 'message': "The request was already made."})

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

                nodes_down_report = []
                for response_node in unique_responses:

                    if "host" in response_node and "port" in response_node:
                        response_node = json.loads(response_node)
                        node_down = f'http://{response_node["host"]}:{response_node["port"]}'
                        nodes_down_report.append(node_down)
                if len(nodes_down_report) > 0:
                    # If we only have nodes that are down, we do not need to check the consistency
                    serviceNode.reportDownNodes(nodes_down_report)

                if (len(nodes_down_report)-len(unique_responses)) == 1:
                    serviceNode.sendFixConsistencyMsg(id_request)
                # Here we announce an inconsistency to the coordinator
                pass

    return returned_response
