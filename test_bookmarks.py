#!/usr/bin/env python3
"""
EN: Test script for bookmarks module
RU: Тестовый скрипт для модуля закладок
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.bookmarks import BookmarkManager
from pathlib import Path

# Initialize manager
test_db = Path(__file__).parent / 'test_bookmarks.db'
manager = BookmarkManager(str(test_db))

print("=" * 50)
print("Тестирование модуля закладок")
print("=" * 50)

# Test 1: Add bookmark
print("\n✓ Тест 1: Добавление закладки")
success = manager.add_bookmark(
    user_id=123456,
    chat_id=-1001234567890,
    message_id=999,
    message_text="Это важное сообщение",
    author_id=111111,
    author_name="@testuser"
)
print(f"  Результат: {'✅ Закладка добавлена' if success else '❌ Ошибка'}")

# Test 2: Check if bookmarked
print("\n✓ Тест 2: Проверка наличия закладки")
is_bookmarked = manager.is_bookmarked(123456, -1001234567890, 999)
print(f"  Результат: {'✅ Закладка существует' if is_bookmarked else '❌ Закладка не найдена'}")

# Test 3: Get user bookmarks
print("\n✓ Тест 3: Получение всех закладок пользователя")
bookmarks = manager.get_user_bookmarks(123456)
print(f"  Количество закладок: {len(bookmarks)}")
if bookmarks:
    for bm in bookmarks:
        print(f"    - ID: {bm[0]}, Message: {bm[4]}, Author: {bm[6]}")

# Test 4: Add duplicate bookmark
print("\n✓ Тест 4: Попытка добавить дублирующуюся закладку")
success = manager.add_bookmark(
    user_id=123456,
    chat_id=-1001234567890,
    message_id=999,
    message_text="Дублирующаяся закладка",
    author_id=111111,
    author_name="@testuser"
)
print(f"  Результат: {'❌ Дублирующаяся закладка не добавлена (ожидаемо)' if not success else '❌ Ошибка логики'}")

# Test 5: Remove bookmark
print("\n✓ Тест 5: Удаление закладки")
deleted = manager.remove_bookmark(123456, -1001234567890, 999)
print(f"  Результат: {'✅ Закладка удалена' if deleted else '❌ Ошибка удаления'}")

# Test 6: Verify bookmark removed
print("\n✓ Тест 6: Проверка удаления закладки")
is_bookmarked = manager.is_bookmarked(123456, -1001234567890, 999)
print(f"  Результат: {'✅ Закладка действительно удалена' if not is_bookmarked else '❌ Закладка всё ещё существует'}")

print("\n" + "=" * 50)
print("Все тесты завершены!")
print("=" * 50)

# Cleanup
if test_db.exists():
    test_db.unlink()
    print(f"\n✓ Тестовая БД удалена: {test_db}")
