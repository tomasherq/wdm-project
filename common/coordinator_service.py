from common.tools import *
from random import randint
from common.async_calls import send_requests, asyncio
import random

'''This file contains common functions used by the coordinators.'''


class CoordinatorService():
    def __init__(self, serviceID):
        self.serviceID = sys.argv[2]
        self.nodesDirections = getAddresses(f"{serviceID}_NODES_ADDRESS")
        self.nodesUp = self.nodesDirections
        self.nodesDown = list()

        self.service = serviceID.lower()
        if self.service == "order":
            self.service = "orders"
        self.file_up_dir = f"nodes_up_{self.service}_{ID_NODE}"

        self.check_alive_limiter = 0

    def getNodeToSend(self, isReadRequest, idRequest):

        if isReadRequest:
            indexNode = randint(0, len(self.nodesUp)-1)
        else:
            indexNode = getIndexFromCheck(len(self.nodesUp), idRequest)

        return self.nodesUp[indexNode]

    def checkUpNodes(self):

        if self.check_alive_limiter <= 0:
            urls = list()
            for node in self.nodesDown:
                urls.append(f"{node}/alive")

            replies = asyncio.new_event_loop().run_until_complete(send_requests(urls, "GET", {}))
            save_new = False

            for reply in replies:

                if "alive" in reply:
                    nodeUp = json.loads(reply)["alive"]

                    if nodeUp not in self.nodesUp:
                        save_new = True
                        self.nodesUp.append(nodeUp)
            if save_new:
                self.saveUpNodes("inter")

            if self.check_alive_limiter == 0:
                self.check_alive_limiter += 5
            else:
                self.check_alive_limiter += int(self.check_alive_limiter*0.1)
        else:
            self.check_alive_limiter -= 1

    def saveUpNodes(self, option):
        # We use the option to know if it was the general API
        # or the intercomunication API the one that saved the new nodes.

        with open(self.file_up_dir+"_"+option+".json", "w") as file:
            file.write(json.dumps(self.nodesUp))

    def loadUpNodes(self, option):

        filename = self.file_up_dir+"_"+option+".json"
        if os.path.exists(filename):

            with open(filename, "r") as file:
                self.nodesUp = json.load(file)
            self.nodesDown = list(set(self.nodesDirections)-set(self.nodesUp))
            os.remove(filename)

    def sendRemoveNodes(self, nodes_down):

        urls = list()
        for node in self.nodesUp:
            urls.append(f"{node}/remove_nodes/{nodes_down}")

        return asyncio.new_event_loop().run_until_complete(send_requests(urls, "POST", {}))

    def removeNodes(self, nodesDown, option="general"):
        self.nodesUp = list(set(self.nodesDirections)-set(nodesDown))
        self.saveUpNodes(option)


def get_hash(nodesDirections):
    responses = []
    node_dirs = []
    url = ''
    for nodeDir in nodesDirections:
        url = f'{nodeDir}/getHash'
        hash = process_reply(requests.get(url))
        responses.append(hash)
        node_dirs.append(nodeDir)

    return node_dirs, responses


def dump_db(coNodesDirections, incoNodesDirections, id_node):
    # prepare the list of inconsistent nodes
    inconsistent_list = [s.replace("http://", "") for s in incoNodesDirections]
    inconsistent_nodes = ';'.join(inconsistent_list)
    # from the consistent dbs select a random one to dump the db to a file
    nodeDir = random.choice(coNodesDirections)
    url = f'{nodeDir}/dumpDB/{id_node}/{inconsistent_nodes}'
    process_reply(requests.get(url))


def restore_db(nodesDirections, id_node):
    urls = []
    for nodeDir in nodesDirections:
        urls.append(f'{nodeDir}/restoreDB/{id_node}')
    asyncio.new_event_loop().run_until_complete(send_requests(urls, "GET", {}))
