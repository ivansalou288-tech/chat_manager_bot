import sys
import os
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode

from main.config import dp, bot, chats, main_path

TRIPLES = {1: "бар", 64: "777", 22: "ягоды", 43: "лимон"}

@dp.message_handler(
    Text(startswith=["!рулетка", "! рулетка"], ignore_case=True),
    content_types=ContentType.TEXT,
    is_forwarded=False,
)
async def slot_roulette(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list = []
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return

    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    user = message.from_user
    user_id = user.id
    user_mention = user.get_mention(as_html=True)

    if getattr(user, "is_bot", False):
        await message.answer("🤖 Боты не могут играть в рулетку!")
        return

    bet = None
    for part in message.text.replace(",", " ").split():
        if part.isdigit():
            bet = int(part)
            break

    if bet is None or bet <= 0:
        await message.answer("📝Укажи ставку: !рулетка {число}")
        return

    try:
        row = cursor.execute("SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchone()
        meshok = row[0] if row is not None else 0
    except sqlite3.Error:
        connection.close()
        await message.answer("⚠️Ошибка доступа к базе данных.")
        return

    if meshok < bet:
        await message.answer(f"💰 У тебя недостаточно монет.\\nВ мешке: 🍊 {meshok} eZ¢\\nСтавка: 🍊 {bet} eZ¢")
        connection.close()
        return

    dice_msg = await bot.send_dice(message.chat.id, emoji="🎰")
    dice_value = dice_msg.dice.value

    triple_name = TRIPLES.get(dice_value)
    
    if triple_name:
        win_amount = bet * 10
        new_meshok = meshok + win_amount
        cursor.execute("UPDATE farma SET meshok = ? WHERE user_id = ?", (new_meshok, user_id))
        connection.commit()
        result_text = (
            f"🎰 <b>Рулетка</b>\\n\\n"
            f"{user_mention} ставит 🍊 <b>{bet} eZ¢</b>\\n\\n"
            f"🎉 <b>ТРИПЛЛ {triple_name.upper()}!</b>\\n"
            f"✅ Выигрыш: 🍊 <b>{win_amount} eZ¢</b> (x10)\\n\\n"
            f"💼 В мешке: 🍊 <b>{new_meshok} eZ¢</b>"
        )
    else:
        new_meshok = meshok - bet
        cursor.execute("UPDATE farma SET meshok = ? WHERE user_id = ?", (new_meshok, user_id))
        connection.commit()
        result_text = (
            f"🎰 <b>Рулетка</b>\\n\\n"
            f"{user_mention} ставит 🍊 <b>{bet} eZ¢</b>\\n\\n"
            f"❌ Не повезло. Ставка сгорела.\\n\\n"
            f"💼 В мешке: 🍊 <b>{new_meshok} eZ¢</b>"
        )

    connection.close()
    await bot.send_message(message.chat.id, result_text, parse_mode=ParseMode.HTML)
