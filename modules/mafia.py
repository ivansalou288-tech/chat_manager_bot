import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import types

from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
#from config import *
import sqlite3
from aiogram.utils.exceptions import *


token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
api_id =21842840
api_hash ="1db0b6e807c90e6364287ad8af7fa655"
bot = Bot(token=token)
dp = Dispatcher(bot)

class Person:
    def __init__(self, user_id, card):
        self.user_id = user_id
        self.card = card


@dp.message_handler(commands=["ref"])
async def get_ref(message: types.Message):
  link = 'https://t.me/for_klan_tests_bot?start=registr_maf'
  # result: 'https://t.me/MyBot?start='
  ## после знака = будет закодированный никнейм юзера, который создал реф ссылку, вместо него можно вставить и его id 
  await message.answer(f"Ваша реф. ссылка {link}")



# хендлер для расшифровки ссылки
@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    args = message.get_args()
    if args == '':
        await message.answer("Привет")
        return
    await message.answer(f"Ваш реферал {args}")


if __name__ == "__main__":
    executor.start_polling(dp)