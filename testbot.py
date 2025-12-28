import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import main_token as token
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
#?from config import *
import sqlite3
from aiogram.utils.exceptions import *
from main.utils import CopyTextButton
from path import Path
from aiogram.utils.exceptions import CantInitiateConversation, MessageNotModified 
from aiogram.types import ContentType
from telebot.types import CopyTextButton
from password_generator import PasswordGenerator

token = '8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q'
bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['rulet'])
async def start(message):
    if message.chat.id == message.from_user.id:
        return
    if message.from_user.id!=1240656726:
        return
    
    
    # res1 = (await bot.send_dice(message.chat.id, emoji='🎰'))['dice']['value']
    res2 = (await bot.send_dice(message.chat.id, emoji='🎯'))['dice']['value']

    await message.answer(f'{res2}')

if __name__ == "__main__":
    executor.start_polling(dp)