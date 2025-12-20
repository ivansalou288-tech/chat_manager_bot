"""
EN: Bookmarks module - allows users to save messages by replying to them
RU: Модуль закладок - позволяет пользователям сохранять сообщения, отвечая на них
"""

import sqlite3
from datetime import datetime
from aiogram import types
from aiogram.types import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from main.config import dp, bot, main_path


class BookmarkManager:
    """
    EN: Manager class for handling bookmark operations
    RU: Класс-менеджер для управления операциями с закладками
    """
    
    def __init__(self, db_path=main_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """
        EN: Initialize bookmarks table in the database
        RU: Инициализирует таблицу закладок в базе данных
        """
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                message_text TEXT,
                author_id INTEGER,
                author_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chat_id, message_id)
            )
        ''')
        connection.commit()
        connection.close()
    
    def add_bookmark(self, user_id, chat_id, message_id, message_text=None, author_id=None, author_name=None):
        """
        EN: Add a new bookmark
        RU: Добавить новую закладку
        
        Args:
            user_id: ID пользователя, который сохраняет закладку
            chat_id: ID чата, где находится сообщение
            message_id: ID сообщения
            message_text: Текст сообщения (опционально)
            author_id: ID автора сообщения
            author_name: Имя/юзернейм автора
        
        Returns:
            bool: True если успешно, False если закладка уже существует
        """
        try:
            connection = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = connection.cursor()
            
            cursor.execute('''
                INSERT INTO bookmarks 
                (user_id, chat_id, message_id, message_text, author_id, author_name) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, chat_id, message_id, message_text, author_id, author_name))
            
            connection.commit()
            connection.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def remove_bookmark(self, user_id, chat_id, message_id):
        """
        EN: Remove a bookmark
        RU: Удалить закладку
        
        Returns:
            bool: True если удалена, False если не найдена
        """
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        cursor.execute('''
            DELETE FROM bookmarks 
            WHERE user_id = ? AND chat_id = ? AND message_id = ?
        ''', (user_id, chat_id, message_id))
        
        deleted = cursor.rowcount > 0
        connection.commit()
        connection.close()
        return deleted
    
    def get_user_bookmarks(self, user_id):
        """
        EN: Get all bookmarks for a user
        RU: Получить все закладки пользователя
        
        Returns:
            list: Список закладок [(id, user_id, chat_id, message_id, message_text, author_id, author_name, created_at), ...]
        """
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        bookmarks = cursor.execute('''
            SELECT id, user_id, chat_id, message_id, message_text, author_id, author_name, created_at
            FROM bookmarks
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()
        
        connection.close()
        return bookmarks
    
    def is_bookmarked(self, user_id, chat_id, message_id):
        """
        EN: Check if message is already bookmarked by user
        RU: Проверить, сохранена ли закладка пользователем
        
        Returns:
            bool: True если закладка существует
        """
        connection = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        result = cursor.execute('''
            SELECT id FROM bookmarks
            WHERE user_id = ? AND chat_id = ? AND message_id = ?
        ''', (user_id, chat_id, message_id)).fetchone()
        
        connection.close()
        return result is not None


# Initialize the BookmarkManager
bookmark_manager = BookmarkManager()


# EN: Add bookmark by replying with 📌 emoji to a message
# RU: Добавить закладку, ответив на сообщение эмодзи 📌
@dp.message_handler(lambda message: message.reply_to_message is not None and message.text and message.text.lower() == '📌')
async def add_bookmark_handler(message: types.Message):
    """Add bookmark by replying with 📌"""
    replied_msg = message.reply_to_message
    
    # Get author info
    author_id = replied_msg.from_user.id if replied_msg.from_user else None
    author_name = replied_msg.from_user.first_name if replied_msg.from_user else "Unknown"
    if replied_msg.from_user and replied_msg.from_user.username:
        author_name = f"@{replied_msg.from_user.username}"
    
    # Get message text
    message_text = replied_msg.text or replied_msg.caption or ""
    if replied_msg.photo:
        message_text = f"[Фото] {message_text}"
    elif replied_msg.video:
        message_text = f"[Видео] {message_text}"
    elif replied_msg.document:
        message_text = f"[Файл] {message_text}"
    elif replied_msg.sticker:
        message_text = "[Стикер]"
    
    # Add bookmark
    success = bookmark_manager.add_bookmark(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        message_id=replied_msg.message_id,
        message_text=message_text[:500],
        author_id=author_id,
        author_name=author_name
    )
    
    if success:
        await message.reply('✅ Закладка добавлена!', reply=False)
    else:
        await message.reply('⚠️ Эта закладка уже сохранена!', reply=False)


# EN: Show user's bookmarks
# RU: Показать закладки пользователя
@dp.message_handler(commands=['bookmarks', 'закладки'])
async def show_bookmarks_handler(message: types.Message):
    """Show user's bookmarks"""
    bookmarks = bookmark_manager.get_user_bookmarks(message.from_user.id)
    
    if not bookmarks:
        await message.answer('📌 У тебя нет закладок\n\nЧтобы добавить закладку, ответь на сообщение сообщением <code>📌</code>',
                           parse_mode=ParseMode.HTML)
        return
    
    # Create inline buttons for each bookmark
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for bookmark in bookmarks:
        bookmark_id, user_id, chat_id, msg_id, msg_text, author_id, author_name, created_at = bookmark
        
        # Create display text
        display_text = msg_text[:30] if msg_text else "Сообщение"
        if len(msg_text or "") > 30:
            display_text += "..."
        
        # Add button to go to message
        button_text = f"📌 {display_text} - {author_name}"
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                # callback_data=f"bookmark_go_{chat_id}_{msg_id}
                url=f"https://t.me/c/{str(chat_id)[4:]}/{msg_id}"
            ),
            InlineKeyboardButton(
                text="❌",
                callback_data=f"bookmark_del_{bookmark_id}"
            )
        )
    
    await message.answer(
        f'📌 <b>Твои закладки ({len(bookmarks)})</b>\n\nНажми на закладку чтобы перейти к сообщению:',
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )


# EN: Handle going to a bookmarked message
# RU: Перейти к сохраненному сообщению
@dp.callback_query_handler(lambda call: call.data.startswith('bookmark_go_'))
async def go_to_bookmark_handler(call: types.CallbackQuery):
    """Handle going to bookmarked message"""
    try:
        data = call.data.split('_')
        chat_id = int(data[2])
        message_id = int(data[3])
        
        await bot.forward_message(
            call.from_user.id,
            chat_id,
            message_id
        )
        await call.answer('✅ Сообщение отправлено в личные сообщения', show_alert=False)
    except Exception as e:
        print(f"Error going to bookmark: {e}")
        await call.answer('❌ Не удалось получить сообщение (возможно оно было удалено)', show_alert=True)


# EN: Handle deleting a bookmark
# RU: Удалить закладку
@dp.callback_query_handler(lambda call: call.data.startswith('bookmark_del_'))
async def delete_bookmark_handler(call: types.CallbackQuery):
    """Handle deleting a bookmark"""
    try:
        bookmark_id = int(call.data.split('_')[2])
        
        connection = sqlite3.connect(bookmark_manager.db_path, check_same_thread=False)
        cursor = connection.cursor()
        
        # Get bookmark info first
        bookmark = cursor.execute(
            'SELECT user_id, chat_id, message_id FROM bookmarks WHERE id = ?',
            (bookmark_id,)
        ).fetchone()
        
        if not bookmark:
            await call.answer('❌ Закладка не найдена', show_alert=True)
            connection.close()
            return
        
        user_id, chat_id, msg_id = bookmark
        
        # Verify that the user owns this bookmark
        if user_id != call.from_user.id:
            await call.answer('❌ Это не твоя закладка', show_alert=True)
            connection.close()
            return
        
        # Delete the bookmark
        bookmark_manager.remove_bookmark(user_id, chat_id, msg_id)
        
        await call.answer('✅ Закладка удалена', show_alert=False)
        
        # Refresh the list
        bookmarks = bookmark_manager.get_user_bookmarks(call.from_user.id)
        
        if not bookmarks:
            await call.message.edit_text('📌 У тебя больше нет закладок')
        else:
            keyboard = InlineKeyboardMarkup(row_width=1)
            
            for bm in bookmarks:
                bm_id, user_id_bm, chat_id_bm, msg_id_bm, msg_text, author_id, author_name, created_at = bm
                
                display_text = msg_text[:30] if msg_text else "Сообщение"
                if len(msg_text or "") > 30:
                    display_text += "..."
                
                button_text = f"📌 {display_text} - {author_name}"
                keyboard.add(
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"bookmark_go_{chat_id_bm}_{msg_id_bm}"
                    ),
                    InlineKeyboardButton(
                        text="❌",
                        callback_data=f"bookmark_del_{bm_id}"
                    )
                )
            
            await call.message.edit_text(
                f'📌 <b>Твои закладки ({len(bookmarks)})</b>\n\nНажми на закладку чтобы перейти к сообщению:',
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        
        connection.close()
    except Exception as e:
        print(f"Error deleting bookmark: {e}")
        await call.answer('❌ Ошибка при удалении закладки', show_alert=True)

