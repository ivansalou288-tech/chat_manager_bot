# Admin Mini App API

Этот модуль предоставляет REST API для Telegram Mini App админ-панели, позволяя просматривать участников и разрешения команд в разных чатах.

## Структура

- `admin_api.py` - REST API сервер на aiohttp
- `admin/app/index.html` - Telegram Mini App интерфейс

## Установка

### Требования

```bash
pip install aiohttp
```

## Запуск API сервера

### Основной способ (вместе с админ-ботом)

Добавьте в `admin_bot.py`:

```python
from admin_api import create_app
from aiohttp import web
import threading

# Создаем приложение
api_app = create_app()
api_app['user_id'] = 1240656726  # ID вашего пользователя

# Запускаем в отдельном потоке
def run_api():
    web.run_app(api_app, host='0.0.0.0', port=8080, print=lambda *args: None)

api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()
```

### Командная строка

```bash
python admin_api.py --port 8080 --host 0.0.0.0 --user-id 1240656726
```

Параметры:
- `--port` - Порт для запуска (по умолчанию 8080)
- `--host` - Хост для запуска (по умолчанию 127.0.0.1)
- `--user-id` - ID пользователя для проверки доступа

## Конфигурация Mini App

В файле `admin/app/index.html` найдите строку и измените URL на ваш сервер:

```javascript
const API_BASE_URL = 'http://localhost:8080/api'; // Измените на ваш адрес
```

Для production используйте:
```javascript
const API_BASE_URL = 'https://your-domain.com/api';
```

## API Endpoints

### 1. Проверка доступа

**POST** `/api/check-access`

```json
{
    "user_id": 123456789
}
```

Ответ:
```json
{
    "user_id": 123456789,
    "has_access": true
}
```

### 2. Получение участников чата

**GET** `/api/users/{chat}`

Параметры пути:
- `chat` - Ключ чата: `klan`, `sost-1`, `sost-2`

Ответ:
```json
{
    "success": true,
    "chat": "klan",
    "users_count_reg": 50,
    "users_count": 55,
    "users": [
        {
            "number": 1,
            "tg_id": 123456789,
            "username": "username",
            "name": "Имя Фамилия",
            "age": 25,
            "pubg_nick": "PUBG_Nick",
            "pubg_id": "pubg_id",
            "nik": "Никнейм",
            "rang": 0,
            "rang_name": "Обычный участник",
            "last_date": "2024-01-01",
            "date_vhod": "2024-01-01",
            "mess_count": 100
        }
    ]
}
```

### 3. Получение разрешений команд

**GET** `/api/permissions/{chat}`

Параметры пути:
- `chat` - Ключ чата: `klan`, `sost-1`, `sost-2`

Ответ:
```json
{
    "success": true,
    "chat": "klan",
    "permissions": [
        {
            "command": "ban",
            "command_name": "Блокировка пользователей",
            "access": "Есть"
        },
        {
            "command": "mut",
            "command_name": "Ограничение пользователей",
            "access": "Нет"
        }
    ]
}
```

## Команды доступа (ДК)

Поддерживаемые команды:
- `ban` - Блокировка пользователей
- `mut` - Ограничение пользователей
- `warn` - Предупреждение пользователей
- `all` - Созыв пользователей
- `rang` - Изменение ранга пользователей
- `dk` - Изменение доступа вызова команд
- `change_pravils` - Изменение правил чата
- `close_chat` - Изменение ограничений чата
- `change_priv` - Изменение приветствия чата
- `obavlenie` - Создание объявления
- `tur` - Создание турниров
- `dell` - Удаление сообщений

## Ранги участников

0. Обычный участник
1. Младший Модератор
2. Модератор
3. Старший Модератор
4. Заместитель
5. Менеджер
6. Владелец

## Интеграция с админ-ботом

Если вы хотите запустить API одновременно с основным ботом, добавьте в `admin_bot.py`:

```python
from admin_api import create_app
from aiohttp import web
import asyncio
import threading

def start_api_server(user_id):
    """Запускает API сервер в отдельном потоке"""
    app = create_app()
    app['user_id'] = user_id
    
    async def run():
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        print('API сервер запущен на http://0.0.0.0:8080')
        await asyncio.Event().wait()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())

# В главной программе
api_thread = threading.Thread(
    target=start_api_server, 
    args=(1240656726,),  # ID админа
    daemon=True
)
api_thread.start()

# Запуск бота
executor.start_polling(dp)
```

## Безопасность

⚠️ **Важно:**

1. **Проверка доступа**: API проверяет, входит ли user_id в список `can_admin_panel`
2. **HTTPS**: Используйте HTTPS в production окружении
3. **CORS**: Если у вас другой домен для Mini App, настройте CORS в API
4. **Переменные окружения**: Не храните чувствительные данные в коде

## Отладка

Для локального тестирования используйте:

```bash
# Запуск API
python admin_api.py --port 8080 --user-id 1240656726

# В другом терминале - тест API
curl http://localhost:8080/api/users/klan
```

## Лицензия

Часть проекта chat_manager_bot
