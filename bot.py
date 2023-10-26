import pip

requirements = [
    "install",
    "logging",
    "aiogram==2.25.1",
    "asyncio",
    "requests",
    "utils",
    "aiohttp",
    "--upgrade"
]
pip.main(requirements)
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import os
import asyncio
import datetime
from aiogram.utils.exceptions import ChatNotFound, UserDeactivated, BotBlocked
import time
import hashlib
from urllib.parse import urlencode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import os
import requests
from datetime import datetime
from aiogram.utils.exceptions import *
from config import *
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, InlineKeyboardMarkup
import hashlib
import asyncio
import html
import subprocess
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import Optional, Tuple, Union
from time import perf_counter
from traceback import print_exc
import aiohttp
import shutil

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('dataBase.sqlite')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS pay (caption TEXT, count INTEGER, id INTEGER)')

c.execute('CREATE TABLE IF NOT EXISTS pay2 (id INTEGER, url TEXT)')

c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER)')

conn.commit()


class help:
    async def get_id():
        id = random.randint(1, 1000000000)
        c.execute(f"SELECT id FROM pay WHERE id={id}")
        row = c.fetchone()
        if row:
            await help.get_id()
        else:
            return id


def uids():
    rows = c.execute("SELECT id FROM users").fetchall()
    c.execute("SELECT * FROM users")
    countr = int(len(c.fetchall()))
    print(countr)
    return (countr)
    for i in range(countr):
        print(rows[i][0])
    c.commit()

async def aexec(code, *args, timeout=None):
    exec(
        f"async def __todo(message, *args):\n"
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )
    f = StringIO()
    with redirect_stdout(f):
        await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)

    return f.getvalue()

async def shell_exec(
    command: str,
    timeout: Optional[Union[int, float]] = None,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
) -> Tuple[int, str, str]:
    """Executes shell command and returns tuple with return code, decoded stdout and stderr"""
    process = await asyncio.create_subprocess_shell(
        cmd=command, stdout=stdout, stderr=stderr, shell=True, executable=None
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except asyncio.exceptions.TimeoutError as e:
        process.kill()
        raise e

    return process.returncode, stdout.decode(), stderr.decode()

async def paste_neko(code: str):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(
                "https://nekobin.com/api/documents",
                json={"content": code},
            ) as paste:
                paste.raise_for_status()
                result = await paste.json()
    except Exception:
        return "Pasting failed"
    else:
        return f"nekobin.com/{result['result']['key']}.py"


@dp.message_handler(Command("start"))
async def buy(message: types.Message):
    c.execute(f"SELECT id FROM users WHERE id={message.from_user.id}")
    row = c.fetchone()
    if row:
        pass
    else:
        for id in admins_id:
            await bot.send_message(chat_id=id, text=f"""Новый пользователь в боте!

Юзернейм: @{message.from_user.username}
Айди: {message.from_user.id}
Упоминание: {message.from_user.get_mention(as_html=True)}""", parse_mode="HTML")
        c.execute('INSERT INTO users (id) values (?)', (message.from_user.id,))
    a = message.get_args()
    if a:
        if a == "decline":
            await message.answer("Оплата отменена или не прошла.")
        elif "Pay_" in a:
            id = a.replace("Pay_", "")
            c.execute(f"SELECT count, caption FROM pay WHERE id={id}")
            b = c.fetchone()
            if not b:
                await message.answer("Данный счёт не найден!")
            else:
                merchant_id = merchant_id1
                amount = b[0]
                currency = 'RUB'
                secret = one
                order_id = f'{message.message_id}_{message.from_user.id}_{random.randint(1, 10000000000)}'
                desc = b[1]
                lang = 'ru'
                sign = f':'.join([
                    str(merchant_id),
                    str(amount),
                    str(currency),
                    str(secret),
                    str(order_id)
                ])
                params = {
                    'merchant_id': merchant_id,
                    'amount': amount,
                    'currency': currency,
                    'order_id': order_id,
                    'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
                    'desc': desc,
                    'lang': lang
                }
                URL = "https://aaio.io/merchant/pay?" + urlencode(params)
                id = await help.get_id()
                c.execute('INSERT INTO pay2 (id, url) values (?, ?)', (id, URL))
                conn.commit()
                buy = InlineKeyboardMarkup()
                buy.add(
                    InlineKeyboardButton("Оплатить", url=URL),
                    InlineKeyboardButton("Статус", callback_data=f"buy_{id}")
                ).add(
                    InlineKeyboardButton("------------", callback_data="-")
                ).add(
                    InlineKeyboardButton("Исходник бота [github]", url="https://github.com/Timka4959000/PayBot")
                )
                await message.answer(f"""
Счёт на оплату

📝 Информация о счёте:
├ Цена: {b[0]}₽
└ Описание: {b[1]}
            """, reply_markup=buy)
    else:
        keyboard = InlineKeyboardMarkup()
        for count in donations:
            keyboard.add(InlineKeyboardButton(f"{count}₽", callback_data=str(count)))
        await message.answer("Выберите сумму доната:", reply_markup=keyboard)
    conn.commit()


@dp.message_handler(Command("add"))
async def add_pay(message: types.Message):
    text = message.text.split()
    count = int(text[1])
    capt = ' '.join(text[2:])
    if not capt:
        await message.reply("Использование:\n/add [сумма] [описание]")
        return
    if message.chat.id in admins_id:
        id = await help.get_id()
        c.execute('INSERT INTO pay (caption, count, id) values (?, ?, ?)', (capt, count, id))
        conn.commit()
        me = await bot.get_me()
        await message.answer(f"""Счёт успешно создан.

Сумма: {count}₽
Описание: {capt}
Айди: {id}
Ссылка, чтобы делится: <code>t.me/{me.username}?start=Pay_{id}</code>
""", parse_mode="HTML")
    else:
        await message.reply("Вы не админ!")
    conn.commit()


@dp.inline_handler()
async def test(query):
    global capt, count
    keyboard = InlineKeyboardMarkup()
    if query.from_user.id in admins_id:
        me = await bot.get_me()
        text1 = query.query.split(" ")
        if text1 == ['']:
            return
        try:
            count = query.query.split(maxsplit=1)[0]
        except:
            return
        try:
            if not text1[1]:
                return
            if len(text1[1]) == 0:
                return
        except:
            pass
        try:
            capt = query.query.split(maxsplit=1)[1]
        except:
            return
        id = await help.get_id()
        c.execute('INSERT INTO pay (caption, count, id) values (?, ?, ?)', (capt, count, id))
        conn.commit()
        merchant_id = merchant_id1
        amount = count
        currency = 'RUB'
        secret = one
        order_id = f'{query.from_user.id}_{random.randint(1, 10000000000)}'
        desc = capt
        lang = 'ru'
        sign = f':'.join([
            str(merchant_id),
            str(amount),
            str(currency),
            str(secret),
            str(order_id)
        ])
        params = {
            'merchant_id': merchant_id,
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
            'desc': desc,
            'lang': lang
        }
        URL = "https://aaio.io/merchant/pay?" + urlencode(params)
        response = requests.get(URL)
        id = await help.get_id()
        c.execute('INSERT INTO pay2 (id, url) values (?, ?)', (id, URL))
        conn.commit()
        text_to_send = f"""
Счёт на оплату

📝 Информация о счёте:
├ Цена: {count}₽
└ Описание: {capt}
                    """
        keyboard.add(
            InlineKeyboardButton("Оплатить", url=URL),
            InlineKeyboardButton("Статус", callback_data=f"buy_{id}")
        ).add(
            InlineKeyboardButton("------------", callback_data="-")
        ).add(
            InlineKeyboardButton("Исходник бота [github]", url="https://github.com/Timka4959000/PayBot")
        )
    else:
        text_to_send = "Вы не админ!"
    text = query.query or "."
    result = hashlib.md5(text.encode()).hexdigest()
    imc = "."

    item = InlineQueryResultArticle(
        title="Создать счёт",
        description="Ипользование: [сумма] [описание]",
        id=result,
        reply_markup=keyboard,
        input_message_content=InputTextMessageContent(f"{text_to_send}")
    )
    await query.answer([item])


@dp.callback_query_handler(lambda c: True)
async def button_callback_handler(callback_query: types.CallbackQuery):
    message = callback_query.message
    data = callback_query.data
    if "buy_" in data:
        id = data.replace("buy_", "")
        c.execute(f"SELECT url FROM pay2 WHERE id={id}")
        row = c.fetchone()
        response = requests.get(row[0])
        if '<span class="mb-2">Заказ просрочен. Оплатить заказ необходимо было' in response.content.decode():
            await callback_query.answer("Счёт просрочен.")
        elif '<span class="mb-2">Заказ успешно был оплачен<span>' in response.content.decode():
            await message.delete()
            for id in admins_id:
                await bot.send_message(chat_id=id,
                                       text=f"{callback_query.from_user.get_mention(as_html=True)} Успешно оплатил счёт\n\n{row[0]}",
                                       parse_mode="HTML")
            await callback_query.answer("Данный счёт был оплачен! Спасибо за оплату. Администраторы оповещены")
        else:
            await callback_query.answer("Данный счёт ожидает оплаты")
    else:
        try:
            data = int(data)
        except:
            await callback_query.answer("Ай! Не трогай, извращенец!")
            return
        merchant_id = merchant_id1
        amount = data
        currency = 'RUB'
        secret = one
        order_id = f'{message.message_id}_{message.from_user.id}_{random.randint(1, 10000000000)}'
        desc = "Донат"
        lang = 'ru'
        sign = f':'.join([
            str(merchant_id),
            str(amount),
            str(currency),
            str(secret),
            str(order_id)
        ])
        params = {
            'merchant_id': merchant_id,
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
            'desc': desc,
            'lang': lang
        }
        URL = "https://aaio.io/merchant/pay?" + urlencode(params)
        response = requests.get(URL)
        if '<span class="mb-2">Заказ просрочен. Оплатить заказ необходимо было' in response.content.decode():
            await message.answer("Счёт просрочен.")
        elif '<span class="mb-2">Заказ успешно был оплачен<span>' in response.content.decode():
            await message.answer("Данный счёт уже был оплачен")
        else:
            id = await help.get_id()
            c.execute('INSERT INTO pay2 (id, url) values (?, ?)', (id, URL))
            conn.commit()
            buy = InlineKeyboardMarkup()
            buy.add(
                InlineKeyboardButton("Оплатить", url=URL),
                InlineKeyboardButton("Статус", callback_data=f"buy_{id}")
            ).add(
                InlineKeyboardButton("------------", callback_data="-")
            ).add(
                InlineKeyboardButton("Исходник бота [github]", url="https://github.com/Timka4959000/PayBot")
            )
            await message.answer(f"""
Счёт на оплату

📝 Информация о счёте:
├ Цена: {data}₽
└ Описание: не определено
            """, reply_markup=buy)


class rass(StatesGroup):
    getmsg = State()
    sendmsg = State()


@dp.message_handler(commands=['alert'])
async def sends(message):
    if message.forward_sender_name != None:
        await message.answer('ты не админ)')
    else:
        await bot.send_message(message.from_user.id, 'Enter password:')
        uids()
        await rass.getmsg.set()


@dp.message_handler(state=rass.getmsg)
async def st2(message: types.Message, state: FSMContext):
    passwd = message.text
    if passwd == password:
        if message.from_user.id in admins_id:
            await bot.send_message(message.from_user.id, 'Введите сообщение')
            await rass.sendmsg.set()
        else:
            await bot.send_message(message.from_user.id, 'Ошибка!')
            await state.finish()
    else:
        await bot.send_message(message.from_user.id, 'Ошибка!')
        await state.finish()


@dp.message_handler(state=rass.sendmsg)
async def st2(message: types.Message, state: FSMContext):
    rasstxt = message.text
    if rasstxt == 'q':
        await bot.send_message(message.from_user.id, 'Отмена')
        await state.finish()
    elif rasstxt == 'й':
        await bot.send_message(message.from_user.id, 'Отмена')
        await state.finish()
    else:
        fail = 0
        suc = 0
        now = datetime.now().date()
        f = open(f"alert_{now}.txt", 'w')
        for id in admins_id:
            await bot.send_message(id, f'Через 10 секунд всем пользователям будет отправлено сообщение \n \n{rasstxt}')
        await asyncio.sleep(10)
        for id in admins_id:
            await bot.send_message(id, f'Началась рассылка. Текст: \n \n{rasstxt}')
        rows = c.execute("SELECT id FROM users").fetchall()
        c.execute("SELECT * FROM users")
        countr = int(len(c.fetchall()))
        for i in range(countr):
            try:
                await bot.send_message(rows[i][0], rasstxt, parse_mode="HTML")
                f.write(f'{rows[i][0]} сообщение отправлено\n')
                suc = suc + 1
            except:
                fail = fail + 1
                uban = str(rows[i][0]) + ' добавил бота в чс и был удален\n'
                f.write(uban)
        f.write(f'\n \n \nУдачных отправок: {suc}\nНеудачных отправок: {fail}')
        f.close()
        for id in admins_id:
            await bot.send_document(id, open(f"alert_{now}.txt", 'rb'), caption=f'Отчет по рассылке.')
        os.remove(f"alert_{now}.txt")
        await state.finish()

@dp.message_handler(commands=["py"])
async def python_exec(message: types.Message):
    code_result = (
        "<b>🌐 Language:</b>\n"
        "<code>Python</code>\n\n"
        "<b>💻 Code:</b>\n"
        '<pre language="python">{code}</pre>\n\n'
        "{result}"
    )
    if message.from_user.id not in admins_id:
        await message.answer('ты не админ')
        return
    code = message.text.split(maxsplit=1)[1]
    exe = await message.reply("<b>🔃 Executing...</b>", parse_mode="HTML")
    try:
        start_time = perf_counter()
        result = await aexec(code, message, timeout=60)
        stop_time = perf_counter()
        await bot.delete_message(message.chat.id, exe.message_id)
        if len(result) > 3072:
            result = html.escape(await paste_neko(result))
        else:
            result = f"<code>{html.escape(result)}</code>"

        return await message.reply(
            code_result.format(
                code=code,
                result=f"<b>✨ Result</b>:\n"
                f"{result}\n"
                f"<b>Completed in {round(stop_time - start_time, 5)}s.</b>",
            ),
            parse_mode="HTML"
        )
    except asyncio.TimeoutError:
        return await message.reply(
            code_result.format(
                language="Python",
                pre_language="python",
                code=code,
                result="<b>❌ Timeout Error!</b>",
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        err = StringIO()
        with redirect_stderr(err):
            print_exc()

        return await message.reply(
            code_result.format(
                language="Python",
                pre_language="python",
                code=code,
                result=f"<b>❌ {e.__class__.__name__}: {e}</b>\n"
                f"Traceback: {html.escape(await paste_neko(err.getvalue()))}",
            ),
            parse_mode="HTML"
        )

@dp.message_handler(commands=["shell"])
async def shell(message: types.Message):
    if message.from_user.id not in admins_id:
        await message.answer('ты не админ')
        return
    exe = await message.reply("<b>🔃 Executing...</b>", parse_mode="HTML")
    cmd_text = message.text.split(maxsplit=1)[1]
    text = (
        "<b>🌐 Language:</b>\n<code>Shell</code>\n\n"
        "<b>💻 Command:</b>\n"
        f'<pre language="sh">{html.escape(cmd_text)}</pre>\n\n'
    )

    try:
        start_time = perf_counter()
        rcode, stdout, stderr = await shell_exec(
            command=cmd_text, timeout=100
        )
    except asyncio.exceptions.TimeoutError:
        text += (
            "<b>❌ Error!</b>\n"
            f"<b>Timeout expired (100 seconds)</b>"
        )
    else:
        stop_time = perf_counter()
        text += (
            "<b>✨ Result</b>:\n"
            f"<code>{html.escape(stderr or stdout)}</code>"
        )
        text += f"<b>Completed in {round(stop_time - start_time, 5)} seconds with code {rcode}</b>"
    await bot.delete_message(message.chat.id, exe.message_id)
    await message.reply(text, parse_mode="HTML")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
