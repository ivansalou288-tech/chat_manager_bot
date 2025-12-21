#!/usr/bin/env python3
"""
БЫСТРАЯ СПРАВКА - Mini App Админ-Панель

Используйте эту справку для быстрого доступа к нужной информации
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════╗
║                    БЫСТРЫЙ СТАРТ                         ║
╚════════════════════════════════════════════════════════════╝

1️⃣  ЗАПУСК АДМИН-БОТА:
    python admin/admin_bot.py

2️⃣  В TELEGRAM:
    /start → Админ - панель → Mini App откроется 🎉

3️⃣  ВСЕ ГОТОВО!
    Просматривайте участников и разрешения команд 👥
"""

COMMANDS = """
╔════════════════════════════════════════════════════════════╗
║                  ПОЛЕЗНЫЕ КОМАНДЫ                        ║
╚════════════════════════════════════════════════════════════╝

📌 ЗАПУСК И ТЕСТИРОВАНИЕ:

  python admin/admin_bot.py
    → Запуск админ-бота с API

  python admin/admin_api.py --port 8080 --user-id 1240656726
    → Запуск только API (для отладки)

  python admin/setup_check.py
    → Проверка установки

  python admin/test_api.py
    → Запуск тестов

🧪 ТЕСТИРОВАНИЕ API (curl):

  # Проверка доступа
  curl -X POST http://localhost:8080/api/check-access \\
    -H "Content-Type: application/json" \\
    -d '{"user_id": 1240656726}'

  # Получение участников клана
  curl http://localhost:8080/api/users/klan

  # Получение разрешений
  curl http://localhost:8080/api/permissions/klan
"""

FILES_INFO = """
╔════════════════════════════════════════════════════════════╗
║              ИНФОРМАЦИЯ О ФАЙЛАХ                          ║
╚════════════════════════════════════════════════════════════╝

🆕 НОВЫЕ ФАЙЛЫ:

  admin_api.py
    → REST API сервер на aiohttp
    → 3 endpoints для получения данных
    → Проверка доступа пользователя

  admin_integration.py
    → Интеграция API с ботом
    → Запуск в отдельном потоке
    → Управление жизненным циклом

  app/index.html
    → Telegram Mini App интерфейс
    → Неоновый дизайн с сакурой
    → 100% мобильная поддержка

  ADMIN_API_README.md
    → Полная API документация
    → Все endpoints с примерами
    → Конфигурация для production

  README_MINIAPP.md
    → Руководство пользователя
    → Инструкции по установке
    → FAQ и поиск ошибок

  INTEGRATION_EXAMPLE.py
    → Примеры интеграции
    → Различные варианты запуска

  test_api.py
    → Тесты функциональности
    → Проверка БД и API

  setup_check.py
    → Проверка установки
    → Валидация файлов и зависимостей

✏️ ОБНОВЛЕННЫЕ ФАЙЛЫ:

  admin_bot.py
    → Добавлена интеграция API
    → Автозапуск API при старте

  app/index.html
    → Переработан интерфейс
    → Добавлена интерактивность
"""

TROUBLESHOOTING = """
╔════════════════════════════════════════════════════════════╗
║             РЕШЕНИЕ ПРОБЛЕМ                               ║
╚════════════════════════════════════════════════════════════╝

❌ "Port 8080 already in use"
   → Используйте другой порт:
     python admin/admin_api.py --port 9000

❌ "Access denied"
   → Проверьте ваш ID в can_admin_panel в admin_config.py

❌ "Database not found"
   → Проверьте путь к Base_bot.db в admin_config.py

❌ "aiohttp is not installed"
   → Установите:
     pip install aiohttp

❌ "API не отвечает"
   → Проверьте что API запущен:
     curl http://localhost:8080/api/users/klan

❌ "Mini App не загружается"
   → Обновите URL API в app/index.html:
     const API_BASE_URL = 'http://your-server:8080/api';

❌ "502 Bad Gateway"
   → Проверьте что API запущен и слушает порт
   → Проверьте логи при запуске бота
"""

API_DOCS = """
╔════════════════════════════════════════════════════════════╗
║              API ДОКУМЕНТАЦИЯ                             ║
╚════════════════════════════════════════════════════════════╝

📡 ENDPOINTS:

1. Проверка доступа
   POST /api/check-access
   Body: {"user_id": 123456789}
   Response: {"user_id": 123, "has_access": true}

2. Получить участников
   GET /api/users/{chat}
   Параметры: klan, sost-1, sost-2
   Response: {
     "success": true,
     "users_count_reg": 50,
     "users_count": 55,
     "users": [...]
   }

3. Получить разрешения
   GET /api/permissions/{chat}
   Параметры: klan, sost-1, sost-2
   Response: {
     "success": true,
     "permissions": [
       {
         "command": "ban",
         "command_name": "Блокировка...",
         "access": "Есть"
       }
     ]
   }
"""

FEATURES = """
╔════════════════════════════════════════════════════════════╗
║              ВОЗМОЖНОСТИ                                  ║
╚════════════════════════════════════════════════════════════╝

✅ ПРОСМОТР УЧАСТНИКОВ:
   • Список участников по чатам (Клан, Состав 1, Состав 2)
   • Информация: имя, возраст, PUBG ник, ранг
   • Ссылка на Telegram профиль
   • Количество сообщений

✅ ПРОСМОТР РАЗРЕШЕНИЙ (ДК):
   • Список команд и их доступность
   • Статус: ✓ Есть / ✗ Нет
   • Для разных чатов

✅ ИНТЕРФЕЙС:
   • Неоновый киберпанк дизайн
   • Плывущая сакура анимация
   • 100% мобильная поддержка
   • Плавные переходы

✅ БЕЗОПАСНОСТЬ:
   • Проверка доступа по ID
   • Только для администраторов
   • Telegram Mini App token

✅ ПРОИЗВОДИТЕЛЬНОСТЬ:
   • Быстрая загрузка данных
   • Асинхронный API (aiohttp)
   • Кеширование в браузере
"""

CONFIGURATION = """
╔════════════════════════════════════════════════════════════╗
║              КОНФИГУРАЦИЯ                                 ║
╚════════════════════════════════════════════════════════════╝

🔧 API ПАРАМЕТРЫ:

  Порт по умолчанию: 8080
  Хост по умолчанию: 0.0.0.0

  Изменение порта:
    python admin/admin_api.py --port 9000

  Изменение хоста:
    python admin/admin_api.py --host 127.0.0.1

🔧 MINI APP:

  Локальное тестирование:
    const API_BASE_URL = 'http://localhost:8080/api';

  Production:
    const API_BASE_URL = 'https://your-domain.com/api';

🔧 АДМИНИСТРАТОРЫ:

  Отредактируйте can_admin_panel в admin_config.py:
    can_admin_panel = [8015726709, 1401086794, 1240656726]

🔧 БАЗЫ ДАННЫХ:

  Путь к БД: main_path в admin_config.py
  Таблицы: [-klan], [-sost_1], [-sost_2]
           [klan], [sostav]
           count_users
"""

LINKS = """
╔════════════════════════════════════════════════════════════╗
║              ПОЛЕЗНЫЕ ССЫЛКИ                              ║
╚════════════════════════════════════════════════════════════╝

📚 ДОКУМЕНТАЦИЯ:

  • admin/README_MINIAPP.md
    → Полное руководство пользователя

  • admin/ADMIN_API_README.md
    → API документация и примеры

  • admin/INTEGRATION_EXAMPLE.py
    → Примеры интеграции

  • admin/PROJECT_STRUCTURE.md
    → Структура проекта

  • admin/SETUP_SUMMARY.md
    → Итоговый отчет

🔗 ВНЕШНИЕ ССЫЛКИ:

  • https://core.telegram.org/bots/webapps
    → Telegram Mini Apps документация

  • https://docs.aiohttp.org/
    → aiohttp документация

  • https://aiogram.dev/
    → aiogram документация
"""

EXAMPLES = """
╔════════════════════════════════════════════════════════════╗
║              ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ                        ║
╚════════════════════════════════════════════════════════════╝

📝 ИНТЕГРАЦИЯ С ADMIN_BOT:

  from admin_integration import start_api_server
  from admin_config import can_admin_panel

  if can_admin_panel:
      admin_id = can_admin_panel[0]
      start_api_server(user_id=admin_id, port=8080)

📝 ЗАПУСК API ОТДЕЛЬНО:

  from admin_api import create_app
  from aiohttp import web

  app = create_app()
  app['user_id'] = 1240656726
  web.run_app(app, host='0.0.0.0', port=8080)

📝 ИСПОЛЬЗОВАНИЕ В JAVASCRIPT:

  const response = await fetch('/api/users/klan');
  const data = await response.json();
  console.log(data.users);

📝 CURL ПРИМЕРЫ:

  curl http://localhost:8080/api/users/klan | python -m json.tool
  curl http://localhost:8080/api/permissions/klan | python -m json.tool
"""

MENU = f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║         СПРАВКА - MINI APP АДМИН-ПАНЕЛЬ                 ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

Выберите пункт:

1. Быстрый старт
2. Полезные команды
3. Информация о файлах
4. Решение проблем
5. API документация
6. Возможности
7. Конфигурация
8. Полезные ссылки
9. Примеры кода
0. Выход

Введите номер (1-9): 
"""

if __name__ == '__main__':
    sections = {
        '1': QUICK_START,
        '2': COMMANDS,
        '3': FILES_INFO,
        '4': TROUBLESHOOTING,
        '5': API_DOCS,
        '6': FEATURES,
        '7': CONFIGURATION,
        '8': LINKS,
        '9': EXAMPLES,
    }
    
    while True:
        print(MENU)
        choice = input().strip()
        
        if choice == '0':
            print("\n👋 До свидания!\n")
            break
        elif choice in sections:
            print(sections[choice])
            input("\n[Нажмите Enter чтобы продолжить...]")
        else:
            print("❌ Неверный выбор. Попробуйте снова.\n")
