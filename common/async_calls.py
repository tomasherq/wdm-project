
from common.tools import debug_print
import asyncio
import aiohttp
import json
import sys
from time import time


async def gather_with_concurrency(n, *tasks):
    '''_summary_

    Args:
        n (int): Number of concurrent threads
        tasks (list): Is a list of tasks
    Returns:
        _type_: _description_
    '''
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        '''This will wait for the task to finish

        Args:
            task (): To be performed

        Returns:
            JSON: Results from the execution
        '''
        async with semaphore:
            try:
                result = await task
            except Exception as e:
                debug_print(e)

                return json.dumps({"host": str(e.host), "port": str(e.port)})
            return result
    # * is to unpack the tuple so the gather function can be correctly used

    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def request_async(url, session, method, headers):

    async with session.request(method, url, headers=headers) as response:
        text = await response.text()
        return text


async def send_requests(urls, method, headers):
    # TCP connection object
    conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
    # Used to create the session object
    session = aiohttp.ClientSession(connector=conn)
    conc_req = len(urls)

    results = await gather_with_concurrency(conc_req, *[request_async(url, session, method, headers) for url in urls])

    await session.close()
    return results
