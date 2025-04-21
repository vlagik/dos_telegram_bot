import logging
import os

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("ddos_bot")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler("logs/attacks.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def attack_summary(user_id, attack_id, method, target, success, total, duration):
    logger.info(
        f"[ID-{attack_id}] [{user_id}] Метод: {method} | Цель: {target} | "
        f"Успешных: {success}/{total} | ⏱ Длительность: {duration:.2f} сек"
    )

def attack_warning(attack_id, method, target):
    logger.warning(
        f"[ID-{attack_id}] Ошибка запроса ({method.upper()}): {target}"
    )

def attack_start(user_id, attack_id, method, target, total, concurrency=None, spoof=False, agent=False):
    base = f"[ID-{attack_id}] [{user_id}] Старт атаки: Метод={method} | Цель={target} | Кол-во={total}"

    if method.lower() == "http":
        extra = f" | Concurrency={concurrency} | User-Agent={agent}"
    elif method.lower() == "udp":
        extra = f" | IP-Spoofing={spoof}"
    else:
        extra = ""

    logger.info(base + extra)