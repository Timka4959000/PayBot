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
    return(countr)
    for i in range(countr):
        print(rows[i][0])
    c.commit()
	
@dp.message_handler(Command("start"))
async def buy(message: types.Message):
  c.execute(f"SELECT id FROM users WHERE id={message.from_user.id}")
  row = c.fetchone()
  if row:
    pass
  else:
    await bot.send_message(chat_id=5118955808, text=f"""Новый пользователь в боте!
  
  Юзернейм: @{message.from_user.username}
  Айди: {message.from_user.id}
  Упоминание: {message.from_user.mention}""")
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
        merchant_id = merchant_id1 # ID Вашего магазина
        amount = b[0] # Сумма к оплате
        currency = 'RUB'  # Валюта заказа
        secret = one # Секретный ключ №1
        order_id = f'{message.message_id}_{message.from_user.id}_{random.randint(1, 10000000000)}'  # Идентификатор заказа в Вашей системе
        desc = b[1] # Описание заказа
        lang = 'ru'  # Язык формы
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
          buy.add(InlineKeyboardButton("Оплатить счёт", url=URL)).add(InlineKeyboardButton("Проверить статус счёта", callback_data=f"buy_{id}"))
          await message.answer(f"""
Счёт на оплату
  
Цена: {b[0]}
Описание: {b[1]}
            """, reply_markup=buy)
  else:
        await message.answer("""
Вам нужно перейти по реферальной ссылке
        """, parse_mode="HTML")
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

Сумма: {count}
Описание: {capt}
Айди: {id}
Ссылка, чтобы делится: <code>t.me/{me.username}?start=Pay_{id}</code>
""", parse_mode="HTML")
    else:
        await message.reply("Вы не админ!")
    conn.commit()

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
        	await message.answer("Счёт просрочен.")
        elif '<span class="mb-2">Заказ успешно был оплачен<span>' in response.content.decode():
        	await message.answer("Данный счёт был оплачен")
        else:	
            await message.answer("Данный счёт ожидает оплаты")
            
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

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
