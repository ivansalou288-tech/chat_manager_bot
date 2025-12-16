import sqlite3

from aiogram import executor, Bot, Dispatcher, types
from path import Path
from password_generator import PasswordGenerator
import datetime
import aiogram
from aiogram.dispatcher.filters import Text


can_new_link_users = [8015726709, 1401086794, 1240656726]
can_recommend_users = [8015726709, 1401086794, 1240656726, 5714854312, 1803851598]
can_admin_panel = [8015726709, 1401086794, 1240656726]


curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'


token = "8156493008:AAF2QyOzc3rBAtDSq2sO5M1LFjNz4a7xTc8"
bot = Bot(token=token)
dp = Dispatcher(bot)



#импорт айди рабочих чатов
connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()
logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])

