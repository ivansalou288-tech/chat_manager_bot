from admin_config import *

print('start')

#? EN: Start Mini App API server for admin panel
#* RU: Запуск API сервера для Mini App админ-панели
# ⚙️ КОНФИГУРАЦИЯ:
# - Для локального запуска: host='0.0.0.0', port=8080
# - Для production на GitHub Pages: Разместите на своем сервере и обновите URL в index.html
try:
    from admin_integration import start_api_server
    if can_admin_panel:
        admin_id = can_admin_panel[0]
        # 🌍 Используйте эту конфигурацию для локальной разработки
        start_api_server(user_id=admin_id, host='0.0.0.0', port=8080)
        print(f'✓ API сервер запущен на http://0.0.0.0:8080 для пользователя {admin_id}')
        print(f'📱 Mini App доступен по адресу: https://ivansalou288-tech.github.io/chat_manager_bot/admin/app/index.html')
        print(f'⚠️  Убедитесь, что в index.html указан правильный API_BASE_URL')
except Exception as e:
    print(f'✗ Ошибка запуска API сервера: {e}')
    print('  Mini App функционал недоступен, но админ-панель работает')

#? EN: Handles /start command and shows admin bot main menu with available actions.
#* RU: Обрабатывает команду /start и показывает главное меню админ-бота с доступными действиями.
@dp.message_handler(commands="start")
async def start(message: types.Message):
    print(message.from_user.id)
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check"),
        types.InlineKeyboardButton(text="📚 Документация", url='https://ivansalou288-tech.github.io/chat_manager_bot/html/admin_guide.html'),
        types.InlineKeyboardButton(text="не тыкать сюда", web_app=types.WebAppInfo(url='https://ivansalou288-tech.github.io/chat_manager_bot/admin/app/index.html')),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.answer("Приветствуем в админ боте\n\nЧто хочешь сделать?", reply_markup=keyboard)
print('start2')
from new_link import *
from admin.recommend import *
from admin.admin_panel import *

#? EN: Main entry point for the admin bot.
#* RU: Главная точка входа для админ-бота.
if __name__ == "__main__":
    executor.start_polling(dp)


