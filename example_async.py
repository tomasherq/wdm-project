
import asyncio
import aiohttp
import json


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
            return await task
    # * is to unpack the tuple so the gather function can be correctly used
    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def post_async(url, session):
    # Post the request
    async with session.post(url) as response:
        # This method delays the reading of the text
        text = await response.text()
        return text


async def get_async(url, session):
    async with session.get(url) as response:
        text = await response.text()
        return text


async def delete_async(url, session):
    async with session.delete(url) as response:
        text = await response.text()
        return text


def get_urls(url):
    urls = list()
    numbers = [10, 11, 12]

    for number in numbers:
        urls.append(url.replace("$end", str(number)))
    return urls


url_create = "http://192.168.124.$end:2801/create/1"
url_find = "http://192.168.124.$end:2801/find/1"
url_delete = "http://192.168.124.$end:2801/remove/1"


async def send_requests(urls, method):
    # TCP connection object
    conn = aiohttp.TCPConnector(limit=None, ttl_dns_cache=300)
    # Used to create the session object
    session = aiohttp.ClientSession(connector=conn)

    conc_req = len(urls)

    print(urls)

    results = {}
    if method == 'POST':
        results = await gather_with_concurrency(conc_req, *[post_async(url, session) for url in urls])
    elif method == "GET":
        results = await gather_with_concurrency(conc_req, *[get_async(url, session) for url in urls])
    elif method == "DELETE":
        results = await gather_with_concurrency(conc_req, *[delete_async(url, session) for url in urls])
    else:
        return (401, f"Used invalid method")

    await session.close()
    return results


def send_things():
    results = asyncio.get_event_loop().run_until_complete(send_requests(get_urls(url_create), "POST"))
    print(results)
    results = asyncio.get_event_loop().run_until_complete(send_requests(get_urls(url_find), "GET"))
    print(results)
    results = asyncio.get_event_loop().run_until_complete(send_requests(get_urls(url_delete), "DELETE"))
    print(results)


send_things()
