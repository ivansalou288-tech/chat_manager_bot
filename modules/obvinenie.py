import sys
import os
import random
import sqlite3
import html
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode

from main.config import dp, bot, chats


curent_path = (Path(__file__)).parent.parent
main_path = curent_path / "databases" / "Base_bot.db"


_OBVINENIE_TEMPLATES = [
    "🚨 @user подозревается в тайном поедании пиццы ночью без приглашения остальных.",
    "🕵️ @user слишком часто пишет «ща» и никогда не возвращается.",
    "🍪 @user виделся рядом с последним печеньем. Совпадение? Не думаем.",
    "🔋 @user обвиняется в разрядке атмосферы фразой «ну, понятно».",
    "💤 @user виновен в чтении чата и молчаливом осуждении.",
    "🎧 @user притворяется, что слушает, но на самом деле думает о мемах.",
    "📉 @user подозревается в снижении онлайна своим «я пошёл».",
    "🧃 @user выпил последний сок из холодильника чата.",
    "🧠 @user знает ответ, но молчит ради драмы.",
    "🕰 @user приходит в чат именно тогда, когда разговор заканчивается.",
    "🧻 @user использует сарказм без инструкции.",
    "🐢 @user печатает сообщение 5 минут… и отправляет «ок».",
    "🔔 @user читает уведомления, но делает вид, что не видел.",
    "🪑 @user украл свободное место в беседе и никому не сказал.",
    "📱 @user обвиняется в случайной отправке сообщения «не туда».",
    "🌚 @user появляется только тогда, когда начинается что-то интересное.",
    "🧊 @user заморозил чат своим молчанием.",
    "🎭 @user слишком часто меняет настроение без обновления версии.",
    "🧃 @user сделал глоток чая и пропал на 3 часа.",
    "🧠 @user обвиняется в том, что думает быстрее, чем пишет.",
]


def _user_mention_html(user_id: int, username: str | None, name: str | None, nik: str | None) -> str:
    """
    Returns HTML mention where the visible text starts with '@'.
    """
    if username and username != "all":
        visible = f"@{username}"
    else:
        # Prefer nick/name for display if username отсутствует
        display = nik or name or "user"
        display = html.escape(str(display).strip() or "user")
        visible = f"@{display}"
    return f'<a href="tg://user?id={int(user_id)}">{visible}</a>'


async def _pick_random_user_from_db(chat_id: int) -> tuple[int, str | None, str | None, str | None] | None:
    """
    Reads random user from Base_bot.db chat table: [-(chat_id)].
    Expected columns (by admin panel): tg_id, username, name, ..., nik, ...
    Returns (tg_id, username, name, nik) or None.
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        row = cursor.execute(
            f"""
            SELECT tg_id, username, name, nik
            FROM [{-(chat_id)}]
            WHERE (username IS NULL OR username != ?)
            ORDER BY RANDOM()
            LIMIT 1
            """,
            ("all",),  # service row in DB
        ).fetchone()
    except sqlite3.OperationalError:
        row = None
    finally:
        connection.close()

    if not row:
        return None
    tg_id, username, name, nik = row
    return int(tg_id), (username or None), (name or None), (nik or None)


@dp.message_handler(
    Text(startswith=["обвинение", "!обвинение", "! обвинение", ".обвинение", "/обвинение"], ignore_case=True),
    content_types=ContentType.TEXT,
    is_forwarded=False,
)
async def obvinenie(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return
    # Только групповые чаты
    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return
    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    # 1) Если команда написана ответом — обвиняем адресата reply
    if message.reply_to_message and message.reply_to_message.from_user:
        u = message.reply_to_message.from_user
        # Не обвиняем ботов (на всякий случай)
        if getattr(u, "is_bot", False):
            picked = await _pick_random_user_from_db(message.chat.id)
            if not picked:
                await message.answer("Не нашёл участников для обвинения 😔")
                return
            user_id, username, name, nik = picked
            user_tag = _user_mention_html(user_id=user_id, username=username, name=name, nik=nik)
        else:
            user_tag = _user_mention_html(
                user_id=int(u.id),
                username=(u.username or None),
                name=(u.full_name or None),
                nik=None,
            )
    # 2) Иначе — случайный участник из базы
    else:
        picked = await _pick_random_user_from_db(message.chat.id)
        if not picked:
            await message.answer("Не нашёл участников для обвинения 😔")
            return
        user_id, username, name, nik = picked
        user_tag = _user_mention_html(user_id=user_id, username=username, name=name, nik=nik)

    template = random.choice(_OBVINENIE_TEMPLATES)
    text = template.replace("@user", user_tag)
    await bot.send_message(message.chat.id, text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


