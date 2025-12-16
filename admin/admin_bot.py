from admin_config import *

print('start')
@dp.message_handler(commands="start")
async def start(message: types.Message):
    print(message.from_user.id)
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check")

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.answer("Приветствуем в админ боте\n\nЧто хочешь сделать?", reply_markup=keyboard)
print('start2')
from new_link import *
from admin.recommend import *
from admin.admin_panel import *

if __name__ == "__main__":
    executor.start_polling(dp)


