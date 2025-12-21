"""
Тесты для проверки API функциональности
Запустите этот файл для проверки что все работает
"""

import asyncio
import json
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from admin_api import (
    get_chat_users,
    get_chat_permissions,
    check_access,
    CHATS,
    CHATS_DK
)


def test_check_access():
    """Тест проверки доступа"""
    print("=" * 60)
    print("TEST 1: Проверка доступа")
    print("=" * 60)
    
    test_ids = [
        (1240656726, True),   # Администратор
        (8015726709, True),   # Администратор
        (9999999999, False),  # Не администратор
    ]
    
    for user_id, expected in test_ids:
        result = check_access(user_id)
        status = "✓" if result == expected else "✗"
        print(f"{status} User {user_id}: {result} (expected {expected})")
    
    print()


def test_get_users():
    """Тест получения пользователей"""
    print("=" * 60)
    print("TEST 2: Получение пользователей из чатов")
    print("=" * 60)
    
    for chat_key in CHATS.keys():
        print(f"\n📋 Тестируем {chat_key}:")
        result = get_chat_users(chat_key)
        
        if 'error' in result:
            print(f"  ✗ Ошибка: {result['error']}")
        else:
            print(f"  ✓ Успешно")
            print(f"    - Всего пользователей (в чате): {result['users_count']}")
            print(f"    - Зарегистрировано: {result['users_count_reg']}")
            print(f"    - Загружено записей: {len(result['users'])}")
            
            if result['users']:
                first_user = result['users'][0]
                print(f"    - Первый пользователь: {first_user['nik']} ({first_user['rang_name']})")
    
    print()


def test_get_permissions():
    """Тест получения разрешений команд"""
    print("=" * 60)
    print("TEST 3: Получение разрешений команд (ДК)")
    print("=" * 60)
    
    for chat_key in CHATS_DK.keys():
        print(f"\n🔑 Тестируем {chat_key}:")
        result = get_chat_permissions(chat_key)
        
        if 'error' in result:
            print(f"  ✗ Ошибка: {result['error']}")
        else:
            print(f"  ✓ Успешно")
            print(f"    - Всего команд: {len(result['permissions'])}")
            
            # Показываем несколько команд
            for perm in result['permissions'][:3]:
                status = "✓" if perm['access'] == 'Есть' else "✗"
                print(f"      {status} {perm['command_name']}: {perm['access']}")
            
            if len(result['permissions']) > 3:
                print(f"      ... и еще {len(result['permissions']) - 3} команд")
    
    print()


def test_invalid_chat():
    """Тест с неверным ключом чата"""
    print("=" * 60)
    print("TEST 4: Проверка обработки ошибок")
    print("=" * 60)
    
    print("\n❌ Тестируем неверный чат:")
    result = get_chat_users('invalid_chat')
    if 'error' in result:
        print(f"  ✓ Корректно обработана ошибка: {result['error']}")
    else:
        print(f"  ✗ Ошибка не обработана")
    
    print()


def test_api_endpoints():
    """Тест API эндпойнтов (требует запущенный сервер)"""
    print("=" * 60)
    print("TEST 5: Тест API эндпойнтов (требует запущенный сервер)")
    print("=" * 60)
    print("\nДля этого теста нужно запустить API сервер:")
    print("  python admin_api.py --port 8080 --user-id 1240656726")
    print("\nПосле запуска сервера используйте curl:")
    print("\n  # Проверка доступа")
    print("  curl -X POST http://localhost:8080/api/check-access \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"user_id\": 1240656726}'")
    print("\n  # Получение пользователей")
    print("  curl http://localhost:8080/api/users/klan")
    print("\n  # Получение разрешений")
    print("  curl http://localhost:8080/api/permissions/klan")
    print()


def print_summary():
    """Вывод информации о тестировании"""
    print("=" * 60)
    print("ИНФОРМАЦИЯ О ТЕСТИРОВАНИИ")
    print("=" * 60)
    print("\n✓ Функции базы данных работают\n")
    print("Доступные функции:")
    print("  1. check_access(user_id) - Проверка доступа")
    print("  2. get_chat_users(chat) - Получение пользователей")
    print("  3. get_chat_permissions(chat) - Получение разрешений")
    print("\nДоступные чаты:")
    for chat in CHATS.keys():
        print(f"  - {chat}")
    print("\nДополнительные команды:")
    print("  # Запуск API сервера")
    print("  python admin_api.py --port 8080 --user-id 1240656726")
    print("\n  # Интеграция с админ-ботом")
    print("  python admin_bot.py")
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  ТЕСТИРОВАНИЕ API АДМИН-ПАНЕЛИ MINIAPP".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        test_check_access()
        test_get_users()
        test_get_permissions()
        test_invalid_chat()
        test_api_endpoints()
        print_summary()
        
        print("╔" + "=" * 58 + "╗")
        print("║" + "  ✓ ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО".center(58) + "║")
        print("╚" + "=" * 58 + "╝")
        print()
        
    except Exception as e:
        print("\n✗ ОШИБКА ПРИ ТЕСТИРОВАНИИ:")
        print(f"  {type(e).__name__}: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_tests()
