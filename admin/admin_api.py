"""
API для Telegram Mini App админ-панели
Обеспечивает доступ к данным участников и разрешений команд
"""

from aiohttp import web
import sqlite3
import json
from admin_config import main_path, can_admin_panel, klan, sost_1, sost_2

# Маппинг названий команд
COMMAND_NAMES = {
    'ban': 'Блокировка пользователей',
    'mut': 'Ограничение пользователей',
    'warn': 'Предупреждение пользователей',
    'all': 'Созыв пользователей',
    'rang': 'Изменение ранга пользователей',
    'dk': 'Изменение доступа вызова команд',
    'change_pravils': 'Изменение правил чата',
    'close_chat': 'Изменение ограничений чата',
    'change_priv': 'Изменение приветствия чата',
    'obavlenie': 'Создание объявления',
    'tur': 'Создание турниров',
    'dell': 'Удаление сообщений'
}

RANK_NAMES = (
    'Обычный участник',
    'Младший Модератор',
    'Модератор',
    'Старший Модератор',
    'Заместитель',
    'Менеджер',
    'Владелец'
)

CHATS = {
    'klan': klan,
    'sost-1': sost_1,
    'sost-2': sost_2
}

CHATS_DK = {
    'klan': 'klan',
    'sost-1': 'sostav',
    'sost-2': 'sostav'
}


def check_access(user_id: int) -> bool:
    """Проверяет, есть ли у пользователя доступ к админ-панели"""
    return user_id in can_admin_panel


def get_chat_users(chat_key: str):
    """
    Получает список пользователей из указанного чата
    
    Args:
        chat_key: ключ чата (klan, sost-1, sost-2)
    
    Returns:
        dict с данными пользователей или ошибкой
    """
    if chat_key not in CHATS:
        return {'error': 'Неверный ключ чата'}
    
    try:
        connection = sqlite3.connect(str(main_path), check_same_thread=False)
        cursor = connection.cursor()
        
        chat_id = CHATS[chat_key]
        
        # Получаем количество зарегистрированных пользователей
        users_count_reg = int(cursor.execute(f'SELECT COUNT(*) FROM [{-chat_id}]').fetchone()[0]) - 1
        
        # Получаем количество всех пользователей
        users_count = int(cursor.execute(f'SELECT count FROM count_users WHERE chat_id = ?', (chat_id,)).fetchone()[0])
        
        # Получаем данные пользователей
        cursor.execute(f'SELECT * FROM [{-chat_id}]')
        users = cursor.fetchall()
        connection.close()
        
        users_list = []
        for idx, user in enumerate(users, 1):
            if user[1] == 'all':  # Пропускаем служебные записи
                continue
            
            user_data = {
                'number': idx,
                'tg_id': user[0],
                'username': user[1],
                'name': user[2],
                'age': user[3],
                'pubg_nick': user[4],
                'pubg_id': user[5],
                'nik': user[6],
                'rang': user[7],
                'rang_name': RANK_NAMES[user[7]] if user[7] < len(RANK_NAMES) else 'Неизвестный ранг',
                'last_date': user[8],
                'date_vhod': user[9],
                'mess_count': user[10]
            }
            users_list.append(user_data)
        
        return {
            'success': True,
            'chat': chat_key,
            'users_count_reg': users_count_reg,
            'users_count': users_count,
            'users': users_list
        }
    
    except Exception as e:
        return {'error': str(e)}


def get_chat_permissions(chat_key: str):
    """
    Получает разрешения команд (ДК) для указанного чата
    
    Args:
        chat_key: ключ чата (klan, sost-1, sost-2)
    
    Returns:
        dict с разрешениями команд или ошибкой
    """
    if chat_key not in CHATS_DK:
        return {'error': 'Неверный ключ чата'}
    
    try:
        connection = sqlite3.connect(str(main_path), check_same_thread=False)
        cursor = connection.cursor()
        
        table_name = CHATS_DK[chat_key]
        
        cursor.execute(f'SELECT * FROM [{table_name}]')
        dks = cursor.fetchall()
        connection.close()
        
        permissions = []
        for command, access in dks:
            permissions.append({
                'command': command,
                'command_name': COMMAND_NAMES.get(command, command),
                'access': access
            })
        
        return {
            'success': True,
            'chat': chat_key,
            'permissions': permissions
        }
    
    except Exception as e:
        return {'error': str(e)}


# Обработчики API запросов

async def get_users(request: web.Request):
    """GET /api/users/{chat}"""
    user_id = int(request.app.get('user_id', 0))
    
    if not check_access(user_id):
        return web.json_response({'error': 'Access denied'}, status=403)
    
    chat = request.match_info.get('chat', '')
    result = get_chat_users(chat)
    
    if 'error' in result:
        return web.json_response(result, status=400)
    
    return web.json_response(result)


async def get_permissions(request: web.Request):
    """GET /api/permissions/{chat}"""
    user_id = int(request.app.get('user_id', 0))
    
    if not check_access(user_id):
        return web.json_response({'error': 'Access denied'}, status=403)
    
    chat = request.match_info.get('chat', '')
    result = get_chat_permissions(chat)
    
    if 'error' in result:
        return web.json_response(result, status=400)
    
    return web.json_response(result)


async def check_user_access(request: web.Request):
    """GET /api/check-access"""
    # Telegram Mini App передает user_id через запрос
    try:
        data = await request.json()
        user_id = int(data.get('user_id', 0))
        
        has_access = check_access(user_id)
        
        return web.json_response({
            'user_id': user_id,
            'has_access': has_access
        })
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)


def create_app():
    """Создает и конфигурирует приложение aiohttp"""
    app = web.Application()
    
    # Добавляем маршруты
    app.router.add_get('/api/users/{chat}', get_users)
    app.router.add_get('/api/permissions/{chat}', get_permissions)
    app.router.add_post('/api/check-access', check_user_access)
    
    # CORS middleware
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == 'OPTIONS':
                return web.Response()
            return await handler(request)
        return middleware_handler
    
    return app


if __name__ == '__main__':
    """
    Запуск API сервера
    
    Использование:
    python admin_api.py --port 8080 --user-id <telegram_user_id>
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='API для админ-панели Mini App')
    parser.add_argument('--port', type=int, default=8080, help='Порт для запуска сервера')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Хост для запуска сервера')
    parser.add_argument('--user-id', type=int, default=0, help='ID пользователя для проверки доступа')
    
    args = parser.parse_args()
    
    app = create_app()
    app['user_id'] = args.user_id
    
    print(f'API сервер запущен на http://{args.host}:{args.port}')
    print(f'Пользователь: {args.user_id}')
    
    web.run_app(app, host=args.host, port=args.port)
