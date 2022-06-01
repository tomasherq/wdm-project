from distutils.log import debug
from common.tools import *

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
