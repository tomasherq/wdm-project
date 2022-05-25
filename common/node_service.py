from common.tools import *
from collections import defaultdict

import asyncio
import aiohttp
import time


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def get_async(url, session, results):
    async with session.get(url) as response:
        i = url.split('/')[-1]
        obj = await response.text()
        results[i] = obj


async def send_async_request(urls):
    connection = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
    session = aiohttp.ClientSession(connector=connection)
    results = {}

    conc_req = 40
    now = time.time()
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls])
    time_taken = now-time.time()

    await session.close()

    return results


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

    def sendMessageCoordinator(self, info):
        json_info = json.dumps(info)

        idInfo = checksum(json_info)
        info["id"] = idInfo
        infoEncoded = encodeBase64(json.dumps(info))
        coordinatorAddress = self.coordinators[getIndexFromCheck(len(self.coordinators), idInfo)]

        url = f'{coordinatorAddress}/{infoEncoded}'

        return requests.post(url)

    def forwardRequest(self, url):

        print(url)

        urls = list()
        for node in self.peer_nodes:
            urls.append(f"{node}/{url}")
        results = send_async_request(urls)

        print(urls)
        print(results)
