from modules.bookmarks import BookmarkManager

# Инициализировать менеджер
manager = BookmarkManager()

# Добавить закладку
manager.add_bookmark(
    user_id=123456,
    chat_id=-1001234567890,
    message_id=999,
    message_text="Важное сообщение",
    author_id=111111,
    author_name="@username"
)

# Получить все закладки
bookmarks = manager.get_user_bookmarks(123456)

# Удалить закладку
manager.remove_bookmark(123456, -1001234567890, 999)
