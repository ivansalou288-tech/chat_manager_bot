import asyncio
import sqlite3
from datetime import datetime
from random import randint
from aiogram import executor, Bot, Dispatcher, types
from django.db.transaction import commit

token="8514363728:AAGNqftzIiVUx83I8oJ36q0ZSotDzpAG8tM"
bot = Bot(token=token)
dp = Dispatcher(bot)
klan = -1003012971064




async def quests_funk(message: types.Message):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    while True:
        a = cursor.execute('SELECT text FROM quests').fetchall()

        quests = [a[0][0], a[1][0], a[2][0]]
        now_time = datetime.now().strftime("%H:%M:%S")
        await asyncio.sleep(1)
        if now_time == "10:00:00":
            if datetime.today().weekday() == 0:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[0]}', parse_mode='html')
            if datetime.today().weekday() == 1:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')
            if datetime.today().weekday() == 2:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[1]}', parse_mode='html')
            if datetime.today().weekday() == 3:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')
            if datetime.today().weekday() == 4:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[2]}', parse_mode='html')
            if datetime.today().weekday() == 5:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')





if __name__ == "__main__":
    executor.start_polling(dp)
