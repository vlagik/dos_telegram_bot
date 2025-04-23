# 🚀 DoS Load Testing Bot

Телеграм-бот для нагрузочного тестирования веб-ресурсов с поддержкой различных техник HTTP и UDP атак.  
Создан в рамках для демонстрации уязвимостей и изучения DoS-методов в этичных целях.

---

## 📦 Возможности

- 🔜 🛰️ UDP Flood + Amplification (NTP, DNS, SSDP и др.) 🔜
- 🌐 HTTP POST/GET — поддержка 3 техник (от базовой до защищённой)
- 🔄 IP Spoofing для UDP
- 🎭 User-Agent маскировка
- ⚙️ Асинхронность (Aiogram + Aiohttp/Httpx)
- 📊 Расширенное логирование

---

## 🔧 Установка и запуск

1. Клонируй репозиторий:
   ```bash
    git clone https://github.com/vlagik/dos_telegram_bot.git
    cd dos_bot

2. Установи зависимости:

    pip install -r requirements.txt

3. Установи токен бота:

    BOT_TOKEN="ваш_токен_бота"

4. Запустить:

    python bot.py


## 📁 Структура
    ├── attacks/          # Реализация всех техник атак
    │   ├── http_post1.py
    │   ├── http_post2.py
    │   ├── http_post3.py
    │   └── udp.py
    ├── core/             # Утилиты и логгер
    │   ├── logger.py
    │   └── parser.py
    ├── logs/             # Логирование атак
    │   └── attacks.log
    ├── config.py         # Переменные окружения
    ├── bot.py            # Точка входа
    ├── handlers.py       # Обработчики Telegram-команд
    ├── keyboards.py      # Инлайн/реплай клавиатуры
    ├── check_HTTP-proxy.py # Проверка рабочих прокси
    ├── udp_attack.py     # Запуск отдельных UDP-атак
    ├── requirements.txt  # Зависимости
    ├── LICENSE           # Лицензия MIT
    └── README.md         # Документация



## ⚠️ Предупреждение
    🛡️ Бот создан только в учебных целях.
    Использование за пределами тестирования и согласованных экспериментов недопустимо. 
    Автор не несёт ответственности за ваши действия.
