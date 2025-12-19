import html
import sys
import os
import sqlite3
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from main.config import main_path, chats, bot, dp


@dp.message_handler(Text(startswith=["бот кто"], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def who_is_who(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list = []
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    # Только в группах
    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return

    # Только в рабочих чатах
    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    parts = message.text.split()
    if len(parts) < 3:
        await message.reply('Формат: бот кто {текст}')
        return

    descriptor = ' '.join(parts[2:]).strip()
    if descriptor == '':
        await message.reply('Формат: бот кто {текст}')
        return

    table_name = str(-(message.chat.id))
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        try:
            rows = cursor.execute(f"SELECT tg_id, nik, username, name FROM [{table_name}]").fetchall()
        except sqlite3.OperationalError:
            await message.reply('📝В базе не найдена таблица пользователей этого чата.')
            return

        candidates = []
        for tg_id, nik, username, name in rows:
            if username == 'all':
                continue
            if not tg_id:
                continue
            try:
                tg_id_int = int(tg_id)
            except Exception:
                continue
            display = nik or name or (f"@{username}" if username else "Пользователь")
            candidates.append((tg_id_int, display))

        if not candidates:
            await message.reply('📝Не удалось найти пользователей для выбора.')
            return

        tg_id_int, display = random.choice(candidates)
        reply_text = f'🔮 Я думаю что <a href="tg://user?id={tg_id_int}">{html.escape(display)}</a> {html.escape(descriptor)}'
        await message.reply(reply_text, parse_mode='HTML', disable_web_page_preview=True)
    finally:
        try:
            connection.close()
        except Exception:
            pass

