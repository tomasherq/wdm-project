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

    def forwardRequest(self, url, method, id_request):

        urls = list()
        for node in self.peer_nodes:
            urls.append(f"{node}{url}")

        return asyncio.new_event_loop().run_until_complete(send_requests(urls, method, {"Id-request": id_request}))

    def sendCheckConsistencyMsg(self, idInfo):
        coordinatorAddress = self.coordinators[getIndexFromCheck(len(self.coordinators), idInfo)]

        url = f'{coordinatorAddress}/check_consistency'
        content = process_reply(requests.post(url))
        return content
