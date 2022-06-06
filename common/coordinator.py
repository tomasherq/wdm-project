from distutils.log import debug
from common.tools import *

FILE_DOWN_PREFIX = "nodes_info/nodes_down_"


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


def check_nodes_down_exist(service):
    return os.path.exists(f"{FILE_DOWN_PREFIX}{service}.json")


def save_nodes_down(nodes_down, service):

    with open(f"{FILE_DOWN_PREFIX}{service}.json", "w") as file:
        file.write(json.dumps(nodes_down))
        debug_print(nodes_down)


def delete_nodes_down(service):
    if check_nodes_down_exist(service):
        os.remove(f"{FILE_DOWN_PREFIX}{service}.json")


def load_nodes_down(service):
    if check_nodes_down_exist(service):
        with open(f"{FILE_DOWN_PREFIX}{service}.json", "r") as file:
            return json.load(file)
    else:
        return list()


def get_up_nodes(nodesDirections, service):

    nodesDown = load_nodes_down(service)

    return list(set(nodesDirections)-set(nodesDown))
