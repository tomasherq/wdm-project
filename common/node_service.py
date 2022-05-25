from common.tools import *
from collections import defaultdict

import asyncio
import aiohttp
import time


# async def gather_with_concurrency(n, *tasks):
#     semaphore = asyncio.Semaphore(n)

#     async def sem_task(task):
#         async with semaphore:
#             return await task

#     return await asyncio.gather(*(sem_task(task) for task in tasks))


# async def get_async(url, session, results):
#     async with session.get(url) as response:
#         i = url.split('/')[-1]
#         obj = await response.text()
#         results[i] = obj


# async def main():
#     connection = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
#     session = aiohttp.ClientSession(connector=connection)
#     results = {}
#     urls = [f"http://192.168.124.10:2801/user/{i}" for i in range(1000)]

#     conc_req = 40
#     now = time.time()
#     await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])

#     print(time_taken)
#     await session.close()


# asyncio.run(main())


class NodeService():

    def __init__(self, service, ip_address):

        self.collection = getCollection(service+"s", service)

        self.service = service.upper()
        self.ip_address = ip_address
        self.coordinators = getAddresses(f"{self.service}_COORD_ADDRESS", 2802)
        self.peer_nodes = getAddresses(f"{self.service}_NODES_ADDRESS")

        print(self.peer_nodes)
        print(ip_address)

        self.peer_nodes.remove("http://"+ip_address+":2801")

        self.currentRequests = defaultdict(list)

    def sendMessageCoordinator(self, info):
        json_info = json.dumps(info)

        idInfo = checksum(json_info)
        info["id"] = idInfo
        infoEncoded = encodeBase64(json.dumps(info))
        coordinatorAddress = self.coordinators[getIndexFromCheck(len(self.coordinators), idInfo)]

        url = f'{coordinatorAddress}/{infoEncoded}'

        return requests.post(url)

    # def forwardRequest(self, url, nodes):

    #     async def sendRequest():
    #         response = await loop.run_in_executor(executor, requests.get, url)
    #         return response.text

    #     idUrl = checksum(url)

    #     self.currentRequests[idUrl]

    #     async_list = []
    #     counter = 1
    #     for node in self.peer_nodes:
    #         executor = ThreadPoolExecutor(counter)
    #         # The "hooks = {..." part is where you define what you want to do
    #         #
    #         # Note the lack of parentheses following do_something, this is
    #         # because the response will be used as the first argument automatically
    #         action_item = requests.async.get(u, hooks={'response': do_something})

    #         # Add the task to our list of things to do via async
    #         async_list.append(action_item)
    #         counter += 1

    #     # Do our list of things to do via async
    #     async.map(async_list)
