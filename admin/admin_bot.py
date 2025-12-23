from admin_config import *
import asyncio
import sys

# Исправление для Windows asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print('✓ Админ-бот запускается...')

#? EN: Handles /start command and shows admin bot main menu with available actions.
#* RU: Обрабатывает команду /start и показывает главное меню админ-бота с доступными действиями.
@dp.message_handler(commands="start")
async def start(message: types.Message):
    print(f'Пользователь {message.from_user.id} запустил бота')
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.answer("Приветствуем в админ боте\n\nЧто хочешь сделать?", reply_markup=keyboard)
from new_link import *
from admin.recommend import *
from admin.admin_panel import *

#? EN: Main entry point for the admin bot.
#* RU: Главная точка входа для админ-бота.
if __name__ == "__main__":
    print('✓ Админ-бот готов к работе!')
    print('✓ Нажмите Ctrl+C для остановки')
    executor.start_polling(dp)


