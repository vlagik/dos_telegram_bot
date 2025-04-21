import aiohttp
import asyncio
import time

INPUT_FILE = "proxies.txt"
OUTPUT_FILE = "work_proxies.txt"

TIMEOUT = 1.5
CONCURRENT_CONNECTIONS = 1000
TEST_URL = "http://httpbin.org/post"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

post_data = {"test": "proxy_check"}

with open(INPUT_FILE, "r") as f:
    proxies = list(set([line.strip() for line in f if line.strip()]))

print(f"Проверяю прокси на POST: {len(proxies)}")

alive_proxies = []
semaphore = asyncio.Semaphore(CONCURRENT_CONNECTIONS)

async def check_proxy(proxy):
    async with semaphore:
        try:
            conn = aiohttp.TCPConnector(ssl=False)
            timeout = aiohttp.ClientTimeout(total=TIMEOUT)
            async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
                async with session.post(TEST_URL, proxy=f"http://{proxy}", headers=headers, data=post_data) as response:
                    if response.status == 200:
                        alive_proxies.append(proxy)
        except:
            pass

async def main():
    tasks = [check_proxy(proxy) for proxy in proxies]
    await asyncio.gather(*tasks)

start = time.time()
asyncio.run(main())
end = time.time()


with open(OUTPUT_FILE, "w") as f:
    for proxy in alive_proxies:
        f.write(proxy + "\n")


print("✅ POST-проверка завершена!")
print(f"🟢 Рабочих (POST) прокси: {len(alive_proxies)}")
print(f"🔴 Мёртвых или неподходящих: {len(proxies) - len(alive_proxies)}")
print(f"Время выполнения: {round(end - start, 2)} сек")