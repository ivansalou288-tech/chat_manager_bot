import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import types
from main.config import about_user_sdk, klan, dp, bot
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
#from config import *
import sqlite3
from aiogram.utils.exceptions import *


curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'


# token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
# api_id =21842840
# api_hash ="1db0b6e807c90e6364287ad8af7fa655"
# bot = Bot(token=token)
# dp = Dispatcher(bot)

class Person:
    def __init__(self, user_id, card):
        self.user_id = user_id
        self.card = card


@dp.message_handler(commands=["мафия", " мафия"], commands_prefix=["!", '.', '/'])
async def get_ref(message: types.Message):
  if message.from_user.id == message.from_user.id:
      await message.answer("В разработке")
      return
  link = 'https://t.me/for_klan_tests_bot?start=registr_maf'
  button = types.InlineKeyboardButton(text="Присоединиться", url=link)
  keyboard = types.InlineKeyboardMarkup(row_width=1).add(button)
  await message.answer("Новая игра создана", reply_markup=keyboard)



# хендлер для расшифровки ссылки
@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    args = message.get_args()
    if args == '':
        await start(message)
        return
    

    await message.answer(f"Вы зарегестрированны")
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.full_name






async def start(message):
    if message.chat.id != message.from_user.id:
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    about = await about_user_sdk(message.from_user.id, klan)
    if about == '' or about == None:
        is_in_klan = '❌ Ты не участник клана'
    else:
        is_in_klan = f'✅ Ты участник клана\n\n<b>Твое описание</b>\n{about}'
    buttons = [
        types.InlineKeyboardButton(text="☎️  Менеджер", url='https://t.me/werty_pub'),
        types.InlineKeyboardButton(text="📝  Регистрация", url="https://t.me/werty_clan_helper_bot"),
        types.InlineKeyboardButton(text="Канал WERTY", url="https://t.me/Werty_Metro"),
        types.InlineKeyboardButton(text="👨‍💻Нашел баг!(админ бота)", url="https://t.me/zzoobank")

    ]

    commands = types.InlineKeyboardButton(text='⚒️ Команды', callback_data='commands')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons).add(commands)

    await bot.send_photo(message.chat.id,photo=open(f'{curent_path}/photos/klan_ava.jpg', 'rb'), caption=f'Приветсвуем тебя в <b>WERTY | Чат-менеджер</b>\n\n{is_in_klan}\n\nЧто ты хочешь сделать?', parse_mode='html',reply_markup=keyboard)

@dp.callback_query_handler(text="commands")
async def successful_recom1(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('commands',)).fetchall()[0][0]
    await bot.send_message(call.from_user.id, f'🗓<b>Список команд чата:</b>\n\n{text}', parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await bot.answer_callback_query(call.id, text='')



#
# if __name__ == "__main__":
#     executor.start_polling(dp)