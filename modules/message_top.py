import html
import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Optional


from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram import Bot, Dispatcher, executor, types
from main.config import main_path, chats
token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
api_id =21842840
api_hash ="1db0b6e807c90e6364287ad8af7fa655"
bot = Bot(token=token)
dp = Dispatcher(bot)

_REGISTERED = False


def _parse_limit(text: Optional[str], default: int = 10, max_limit: int = 50) -> int:
    if not text:
        return default
    parts = text.strip().split()
    if not parts:
        return default
    # поддержка: "топ сообщений 20"
    last = parts[-1]
    if last.isdigit():
        try:
            val = int(last)
            if val < 1:
                return default
            return min(val, max_limit)
        except Exception:
            return default
    return default


def _detect_message_counter_column(cursor: sqlite3.Cursor, table_name: str) -> Optional[str]:
    try:
        cols = [row[1] for row in cursor.execute(f"PRAGMA table_info([{table_name}])").fetchall()]
    except sqlite3.OperationalError:
        return None
    for candidate in ("mess_count", "message_count", "messages_count", "msg_count", "messages"):
        if candidate in cols:
            return candidate
    return None

@dp.message_handler(Text(startswith=["топ вся", "!топ сообщений"], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def show_messages_top_all_time(message: types.Message) -> None:
    # Только в группах
    if message.chat.id == message.from_user.id:
        await message.answer("📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!")
        return

    # Только в рабочих чатах
    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    limit = _parse_limit(message.text)
    table_name = str(-(message.chat.id))

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        counter_col = _detect_message_counter_column(cursor, table_name)
        if not counter_col:
            await message.reply("📝В базе не найдено поле счётчика сообщений (ожидаю `mess_count`).")
            return

        try:
            rows = cursor.execute(
                f"""
                SELECT tg_id, username, nik, name, {counter_col}
                FROM [{table_name}]
                ORDER BY {counter_col} DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        except sqlite3.OperationalError:
            await message.reply("📝Не найдена таблица пользователей этого чата в базе.")
            return

        lines = []
        place = 0
        for tg_id, username, nik, name, cnt in rows:
            # служебная строка, которую иногда кладут как "all"
            if username == "all":
                continue
            try:
                tg_id_int = int(tg_id)
            except Exception:
                continue
            try:
                cnt_int = int(cnt or 0)
            except Exception:
                cnt_int = 0

            display = nik or name or (f"@{username}" if username else None) or "Пользователь"
            place += 1
            if place == 1:
                mest = '🥇'
            elif place == 2:
                mest = '🥈'
            elif place == 3:
                mest = '🥉'
            else:
                mest = place
            lines.append(
                f"<b>{mest}.</b> <a href=\"tg://user?id={tg_id_int}\">{html.escape(str(display))}</a> — <b>{cnt_int}</b>"
            )

            if place >= limit:
                break

        if not lines:
            await message.reply("📝Пока нет данных для топа сообщений.")
            return

        text = "🏆 <b>Топ сообщений за всё время</b>\n\n" + "\n".join(lines)
        await message.reply(text, parse_mode="HTML", disable_web_page_preview=True)
    finally:
        try:
            connection.close()
        except Exception:
            pass


def register(dp) -> None:
    """
    Регистрирует хендлер на переданном Dispatcher.
    Команда: "топ сообщений [N]"
    """
    global _REGISTERED
    if _REGISTERED:
        return
    _REGISTERED = True

    dp.register_message_handler(
        show_messages_top_all_time,
        Text(startswith=["топ сообщений", "топсообщений", "!топ сообщений", "!топсообщений"], ignore_case=True),
        content_types=ContentType.TEXT,
        is_forwarded=False,
    )


if __name__ == "__main__":
    executor.start_polling(dp)