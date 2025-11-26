#from config import *
from new_link import *
from admin_panel import *
@dp.message_handler(commands="start")
async def start(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check")

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.reply("Приветствуем в админ - боте\n\nЧто хочешь сделать?", reply_markup=keyboard)
from recommend import *

if __name__ == "__main__":
    executor.start_polling(dp)


