import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import executor, Bot, Dispatcher
from aiogram.dispatcher.filters import Text

from aiogram.utils.exceptions import *
from main.utils import CopyTextButton
from path import Path


#? EN: Bot initialization
#* RU: Инициализация бота
token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
api_id =21842840
api_hash ="1db0b6e807c90e6364287ad8af7fa655"
bot = Bot(token=token)
dp = Dispatcher(bot)

@dp.message_handler(Text(startswith='!тест', ignore_case=True))
async def set_new_chat(message):
    with open('docs/USER_GUIDE.md', 'r', encoding='utf-8') as f:
        text = f.read()
    await message.answer(text, parse_mode = 'markdown')  # Telegram message limit
        
if __name__ == "__main__":
    executor.start_polling(dp)