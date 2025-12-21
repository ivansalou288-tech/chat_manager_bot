"""
ПРИМЕР: Как интегрировать API в admin_bot.py

Это показывает, как добавить запуск API сервера вместе с ботом.
Скопируйте нужные части в ваш admin_bot.py
"""

# ============= ВАРИАНТ 1: Простой (рекомендуется) =============
# Добавьте эти строки в начало admin_bot.py, после импортов:

"""
from admin_integration import start_api_server
from admin_config import can_admin_panel

# Запускаем API сервер для Mini App
if can_admin_panel:
    admin_id = can_admin_panel[0]  # Берем ID первого админа
    start_api_server(user_id=admin_id, host='0.0.0.0', port=8080)
    print(f'API запущен для пользователя {admin_id}')
"""


# ============= ВАРИАНТ 2: С конфигурацией =============
# Если вы хотите больше контроля:

"""
from admin_integration import APIServer
from admin_config import can_admin_panel

# Конфигурация
API_HOST = '0.0.0.0'  # Доступен всем
API_PORT = 8080
API_USER_ID = can_admin_panel[0] if can_admin_panel else None

# Запускаем API
api_server = APIServer(
    user_id=API_USER_ID,
    host=API_HOST,
    port=API_PORT
)
api_server.start()
print(f'API запущен на http://{API_HOST}:{API_PORT}')
"""


# ============= ВАРИАНТ 3: С Flask вместо aiohttp =============
# Если хотите использовать Flask вместо aiohttp:

"""
from flask import Flask, jsonify, request
from admin_config import main_path, can_admin_panel, klan, sost_1, sost_2
import sqlite3
import threading

app = Flask(__name__)

# Функции из admin_api.py...
CHATS = {'klan': klan, 'sost-1': sost_1, 'sost-2': sost_2}

@app.route('/api/users/<chat>')
def get_users(chat):
    # Реализация получения пользователей
    pass

@app.route('/api/permissions/<chat>')
def get_permissions(chat):
    # Реализация получения разрешений
    pass

# Запуск в отдельном потоке
def run_flask():
    app.run(host='0.0.0.0', port=8080, threaded=True)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
"""


# ============= ВАРИАНТ 4: С переменной окружения =============
# Для более гибкой конфигурации:

"""
import os
from admin_integration import start_api_server
from admin_config import can_admin_panel

# Конфигурация из переменных окружения
API_ENABLED = os.getenv('ADMIN_API_ENABLED', 'true').lower() == 'true'
API_PORT = int(os.getenv('ADMIN_API_PORT', '8080'))
API_HOST = os.getenv('ADMIN_API_HOST', '0.0.0.0')

if API_ENABLED and can_admin_panel:
    admin_id = can_admin_panel[0]
    start_api_server(user_id=admin_id, host=API_HOST, port=API_PORT)
    print(f'API включен на {API_HOST}:{API_PORT}')
else:
    print('API отключен')
"""


# ============= ПОЛНЫЙ ПРИМЕР MODIFIED admin_bot.py =============

FULL_EXAMPLE = """
from admin_config import *
from admin_integration import start_api_server

print('start')

# Запускаем API сервер для Mini App
try:
    if can_admin_panel:
        admin_id = can_admin_panel[0]
        start_api_server(user_id=admin_id, host='0.0.0.0', port=8080)
        print(f'✓ API сервер запущен для пользователя {admin_id}')
except Exception as e:
    print(f'✗ Ошибка запуска API: {e}')

#? EN: Handles /start command and shows admin bot main menu
#* RU: Обрабатывает команду /start и показывает главное меню админ-бота
@dp.message_handler(commands="start")
async def start(message: types.Message):
    print(message.from_user.id)
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check"),
        types.InlineKeyboardButton(text="📱 Mini App", url='https://t.me/YOUR_BOT/admin'),  # Добавьте ссылку на Mini App
        types.InlineKeyboardButton(text="📚 Документация", url='https://ivansalou288-tech.github.io/chat_manager_bot/html/admin_guide.html'),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.answer("Приветствуем в админ боте\\n\\nЧто хочешь сделать?", reply_markup=keyboard)

print('start2')
from new_link import *
from admin.recommend import *
from admin.admin_panel import *

#? EN: Main entry point for the admin bot
#* RU: Главная точка входа для админ-бота
if __name__ == "__main__":
    print('\\n=== Админ Бот запущен ===')
    print(f'API доступно на: http://localhost:8080')
    print(f'Mini App доступно на: /admin/app/index.html\\n')
    executor.start_polling(dp)
"""


# ============= ТРЕБОВАНИЯ К requirements.txt =============

REQUIREMENTS = """
# Для API сервера
aiohttp>=3.8.0

# Для Flask альтернативы (опционально)
# flask>=2.0.0
"""


# ============= ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ =============

INTEGRATION_STEPS = """
ШАГИ ДЛЯ ИНТЕГРАЦИИ:

1. Установите зависимости:
   pip install aiohttp

2. В admin_bot.py добавьте в начало (после импортов):
   
   from admin_integration import start_api_server
   from admin_config import can_admin_panel
   
   if can_admin_panel:
       admin_id = can_admin_panel[0]
       start_api_server(user_id=admin_id, host='0.0.0.0', port=8080)

3. Обновите URL Mini App в index.html:
   
   const API_BASE_URL = 'http://your-server-ip:8080/api';

4. Запустите админ-бот как обычно:
   
   python admin_bot.py

5. Проверьте что API работает:
   
   curl http://localhost:8080/api/users/klan

6. Используйте Mini App через команду /start в боте
   или добавьте кнопку "📱 Mini App" в главное меню


КОНФИГУРАЦИЯ NGINX (для production):

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /admin/ {
        alias /path/to/admin/app/;
        try_files $uri $uri/ =404;
    }
}
"""


print(__doc__)
print(INTEGRATION_STEPS)
