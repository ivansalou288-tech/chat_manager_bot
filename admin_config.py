import sqlite3
import random
import aiogram
import telebot
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
#from config import *
import sqlite3
from config import *
from aiogram.utils.exceptions import *

from password_generator import PasswordGenerator
from pyexpat.errors import messages

can_new_link_users = [8015726709, 1401086794, 1240656726]
can_recommend_users = [8015726709, 1401086794, 1240656726, 5714854312, 1803851598]
can_admin_panel = [8015726709, 1401086794, 1240656726]

token = "8156493008:AAF2QyOzc3rBAtDSq2sO5M1LFjNz4a7xTc8"
bot = Bot(token=token)
dp = Dispatcher(bot)


