"""
Модуль управления закладками чата (Чатбук)
Позволяет пользователям создавать, просматривать и удалять закладки на сообщения и темы
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Импорт aiogram для интеграции с ботом
try:
    from aiogram import types, Dispatcher
    from aiogram.dispatcher.filters import Text
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False


@dataclass
class Bookmark:
    """Класс для хранения информации о закладке"""
    id: int
    title: str
    author_id: int
    author_name: str
    description: str
    message_id: Optional[int] = None
    chat_id: Optional[int] = None
    created_at: str = ""
    is_public: bool = True
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class BookmarkManager:
    """Менеджер для управления закладками"""
    
    # Размер одной страницы в списке закладок
    PAGE_SIZE = 10
    
    def __init__(self, data_dir: str = "databases"):
        """
        Инициализация менеджера закладок
        
        Args:
            data_dir: Директория для хранения данных закладок
        """
        self.data_dir = data_dir
        self.bookmarks_file = os.path.join(data_dir, "bookmarks.json")
        self.bookmarks: Dict[int, Bookmark] = {}
        self.next_id = 1
        self._load_bookmarks()
    
    def _load_bookmarks(self) -> None:
        """Загрузить закладки из файла"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.next_id = data.get('next_id', 1)
                    for bm_data in data.get('bookmarks', []):
                        bm = Bookmark(**bm_data)
                        self.bookmarks[bm.id] = bm
            except Exception as e:
                print(f"Ошибка при загрузке закладок: {e}")
    
    def _save_bookmarks(self) -> None:
        """Сохранить закладки в файл"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            data = {
                'next_id': self.next_id,
                'bookmarks': [asdict(bm) for bm in self.bookmarks.values()]
            }
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении закладок: {e}")
    
    def create_bookmark(self, title: str, author_id: int, author_name: str, 
                       description: str, message_id: Optional[int] = None, 
                       chat_id: Optional[int] = None) -> Bookmark:
        """
        Создать новую закладку
        
        Args:
            title: Название закладки
            author_id: ID автора закладки
            author_name: Имя автора закладки
            description: Описание/содержание закладки
            message_id: ID сообщения, на которое указывает закладка (опционально)
            chat_id: ID чата, где расположено сообщение (опционально)
        
        Returns:
            Созданная закладка
        """
        bookmark = Bookmark(
            id=self.next_id,
            title=title,
            author_id=author_id,
            author_name=author_name,
            description=description,
            message_id=message_id,
            chat_id=chat_id
        )
        self.bookmarks[self.next_id] = bookmark
        self.next_id += 1
        self._save_bookmarks()
        return bookmark
    
    def get_bookmark(self, bookmark_id: int) -> Optional[Bookmark]:
        """
        Получить закладку по ID
        
        Args:
            bookmark_id: ID закладки
        
        Returns:
            Закладка или None если не найдена
        """
        return self.bookmarks.get(bookmark_id)
    
    def delete_bookmark(self, bookmark_id: int, user_id: int, is_moderator: bool = False) -> Tuple[bool, str]:
        """
        Удалить закладку
        
        Args:
            bookmark_id: ID закладки
            user_id: ID пользователя, который удаляет
            is_moderator: Является ли пользователь модератором
        
        Returns:
            Кортеж (успешность, сообщение)
        """
        bookmark = self.bookmarks.get(bookmark_id)
        if not bookmark:
            return False, "Закладка не найдена"
        
        if bookmark.author_id != user_id and not is_moderator:
            return False, "Вы не можете удалить чужую закладку"
        
        del self.bookmarks[bookmark_id]
        self._save_bookmarks()
        return True, "Закладка удалена"
    
    def exclude_bookmark(self, bookmark_id: int, user_id: int, is_moderator: bool = False) -> Tuple[bool, str]:
        """
        Исключить закладку из чатбука (не удаляя)
        
        Args:
            bookmark_id: ID закладки
            user_id: ID пользователя
            is_moderator: Является ли пользователь модератором
        
        Returns:
            Кортеж (успешность, сообщение)
        """
        bookmark = self.bookmarks.get(bookmark_id)
        if not bookmark:
            return False, "Закладка не найдена"
        
        if bookmark.author_id != user_id and not is_moderator:
            return False, "Вы не можете исключить чужую закладку"
        
        bookmark.is_public = False
        self._save_bookmarks()
        return True, "Закладка исключена из чатбука"
    
    def get_public_bookmarks(self, page: int = 1) -> Tuple[List[Bookmark], int]:
        """
        Получить список открытых закладок (Чатбук)
        
        Args:
            page: Номер страницы
        
        Returns:
            Кортеж (список закладок на странице, общее количество страниц)
        """
        public_bms = [bm for bm in self.bookmarks.values() if bm.is_public]
        public_bms.sort(key=lambda x: x.created_at, reverse=True)
        
        total_pages = (len(public_bms) + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        
        return public_bms[start:end], total_pages
    
    def get_user_bookmarks(self, author_id: int, page: int = 1) -> Tuple[List[Bookmark], int]:
        """
        Получить список закладок пользователя
        
        Args:
            author_id: ID автора
            page: Номер страницы
        
        Returns:
            Кортеж (список закладок на странице, общее количество страниц)
        """
        user_bms = [bm for bm in self.bookmarks.values() if bm.author_id == author_id]
        user_bms.sort(key=lambda x: x.created_at, reverse=True)
        
        total_pages = (len(user_bms) + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        start = (page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        
        return user_bms[start:end], total_pages
    
    def set_user_bookmarks_visibility(self, author_id: int, visible: bool) -> int:
        """
        Изменить видимость всех закладок пользователя в чатбуке
        
        Args:
            author_id: ID пользователя
            visible: True для добавления в чатбук, False для исключения
        
        Returns:
            Количество измененных закладок
        """
        count = 0
        for bookmark in self.bookmarks.values():
            if bookmark.author_id == author_id:
                bookmark.is_public = visible
                count += 1
        
        self._save_bookmarks()
        return count
    
    def format_bookmark(self, bookmark: Bookmark, include_id: bool = True) -> str:
        """
        Отформатировать закладку для вывода
        
        Args:
            bookmark: Закладка
            include_id: Включать ли ID закладки
        
        Returns:
            Отформатированная строка
        """
        id_str = f"#{bookmark.id} " if include_id else ""
        date_str = bookmark.created_at.split('T')[0]
        text = (f"{id_str}📌 <b>{bookmark.title}</b>\n"
                f"👤 Автор: {bookmark.author_name}\n"
                f"📅 {date_str}\n"
                f"📝 {bookmark.description}")
        
        # Добавляем информацию о ссылке на сообщение если оно есть
        if bookmark.message_id and bookmark.chat_id:
            text += f"\n🔗 <i>Ссылка на сообщение доступна</i>"
        
        return text
    
    def get_message_link(self, bookmark: Bookmark) -> Optional[str]:
        """
        Получить Telegram deep link на сообщение
        
        Args:
            bookmark: Закладка
        
        Returns:
            URL для перехода к сообщению или None
        """
        if not bookmark.message_id or not bookmark.chat_id:
            return None
        
        # Если это групповой чат (отрицательное ID)
        if bookmark.chat_id < 0:
            # Преобразуем ID для group link
            chat_id = str(bookmark.chat_id).replace('-', '')
            return f"https://t.me/c/{chat_id}/{bookmark.message_id}"
        else:
            # Для личных сообщений
            return f"tg://openmessage?chat_id={bookmark.chat_id}&message_id={bookmark.message_id}"
    
    def format_bookmarks_list(self, bookmarks: List[Bookmark], page: int, total_pages: int) -> str:
        """
        Отформатировать список закладок
        
        Args:
            bookmarks: Список закладок
            page: Текущая страница
            total_pages: Общее количество страниц
        
        Returns:
            Отформатированный список
        """
        if not bookmarks:
            return "Нет закладок"
        
        text = ""
        for bm in bookmarks:
            text += f"#{bm.id} 📌 <b>{bm.title}</b> - {bm.author_name}\n"
        
        if total_pages > 1:
            text += f"\n📄 Страница {page}/{total_pages}"
        
        return text
    
    def get_total_bookmarks(self) -> int:
        """Получить общее количество закладок"""
        return len(self.bookmarks)
    
    def get_user_bookmark_count(self, author_id: int) -> int:
        """Получить количество закладок пользователя"""
        return sum(1 for bm in self.bookmarks.values() if bm.author_id == author_id)


class BookmarkCommandHandler:
    """Обработчик команд для работы с закладками"""
    
    def __init__(self, manager: BookmarkManager):
        """
        Инициализация обработчика команд
        
        Args:
            manager: Экземпляр BookmarkManager
        """
        self.manager = manager
    
    def parse_create_command(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Распарсить команду создания закладки (+Закладка название [enter] текст)
        
        Args:
            text: Текст сообщения
        
        Returns:
            Кортеж (название, описание) или (None, None) если ошибка
        """
        # Удалить команду
        if text.startswith('+Закладка '):
            text = text[10:]
        else:
            return None, None
        
        # Разделить по переводу строки
        parts = text.split('\n', 1)
        if len(parts) < 2:
            return None, None
        
        title = parts[0].strip()
        description = parts[1].strip()
        
        if not title or not description:
            return None, None
        
        return title, description
    
    def parse_bookmark_number(self, text: str) -> Optional[int]:
        """
        Извлечь номер закладки из текста
        
        Args:
            text: Текст сообщения
        
        Returns:
            Номер закладки или None
        """
        try:
            # Попытаться получить число после команды
            parts = text.split()
            if len(parts) > 1:
                return int(parts[-1])
        except (ValueError, IndexError):
            pass
        return None
    
    def parse_page_number(self, text: str) -> int:
        """
        Извлечь номер страницы из текста
        
        Args:
            text: Текст сообщения
        
        Returns:
            Номер страницы (по умолчанию 1)
        """
        try:
            parts = text.split()
            if len(parts) > 1:
                return int(parts[-1])
        except (ValueError, IndexError):
            pass
        return 1


def register_bookmarks_handlers(dp: Dispatcher, manager: BookmarkManager = None, bot = None) -> None:
    """
    Регистрирует все обработчики команд для системы закладок в диспетчер aiogram
    
    Args:
        dp: Диспетчер aiogram
        manager: Экземпляр BookmarkManager (если None, создаётся новый)
        bot: Объект бота для отправки сообщений
    """
    if not AIOGRAM_AVAILABLE:
        return
    
    if manager is None:
        manager = BookmarkManager()
    
    # ==================== СОЗДАНИЕ ЗАКЛАДКИ ====================
    @dp.message_handler(Text(startswith=['+Закладка', '+закладка'], ignore_case=True), content_types=['text'])
    async def create_bookmark_handler(message: types.Message):
        """Обработчик команды +Закладка название [enter] текст или в ответ на сообщение"""
        handler = BookmarkCommandHandler(manager)
        
        # Проверяем, является ли это ответом на сообщение
        if message.reply_to_message:
            # Создаём закладку в ответ на сообщение
            title, description = handler.parse_create_command(message.text)
            
            if not title:
                await message.answer(
                    "❌ <b>Ошибка формата!</b>\n\n"
                    "Правильный формат:\n"
                    "<code>+Закладка Название</code>",
                    parse_mode='html'
                )
                return
            
            # Используем текст или полное сообщение как описание
            if description:
                desc = description
            else:
                # Если описание не указано, используем текст оригинального сообщения
                if message.reply_to_message.text:
                    desc = message.reply_to_message.text[:200]
                elif message.reply_to_message.caption:
                    desc = message.reply_to_message.caption[:200]
                else:
                    desc = "[Вложение]"
            
            bookmark = manager.create_bookmark(
                title=title,
                author_id=message.from_user.id,
                author_name=message.from_user.first_name or message.from_user.username or "Unknown",
                description=desc,
                message_id=message.reply_to_message.message_id,
                chat_id=message.chat.id
            )
            
            # Создаём инлайн кнопку для перехода к сообщению
            link = manager.get_message_link(bookmark)
            keyboard = types.InlineKeyboardMarkup()
            if link:
                keyboard.add(types.InlineKeyboardButton(text="🔗 Перейти к сообщению", url=link))
            
            await message.answer(
                f"✅ <b>Закладка создана!</b>\n\n"
                f"{manager.format_bookmark(bookmark)}",
                parse_mode='html',
                reply_markup=keyboard
            )
        else:
            # Создаём закладку из текста команды
            title, description = handler.parse_create_command(message.text)
            
            if not title or not description:
                await message.answer(
                    "❌ <b>Ошибка формата!</b>\n\n"
                    "Правильный формат:\n"
                    "<code>+Закладка Название\n"
                    "Описание закладки</code>",
                    parse_mode='html'
                )
                return
            
            bookmark = manager.create_bookmark(
                title=title,
                author_id=message.from_user.id,
                author_name=message.from_user.first_name or message.from_user.username or "Unknown",
                description=description
            )
            
            await message.answer(
                f"✅ <b>Закладка создана!</b>\n\n"
                f"{manager.format_bookmark(bookmark)}",
                parse_mode='html'
            )
    
    # ==================== ПРОСМОТР ЗАКЛАДКИ ПО НОМЕРУ ====================
    @dp.message_handler(Text(startswith=['Закладка', 'закладка'], ignore_case=True), 
                        content_types=['text'])
    async def view_bookmark_handler(message: types.Message):
        """Обработчик команды Закладка {номер}"""
        # Пропускаем команды, которые начинаются с +, -, это отдельные команды
        if message.text.strip().startswith(('+', '-')):
            return
        
        handler = BookmarkCommandHandler(manager)
        bookmark_id = handler.parse_bookmark_number(message.text)
        
        if bookmark_id is None:
            await message.answer(
                "❌ Укажите номер закладки:\n"
                "<code>Закладка {номер}</code>",
                parse_mode='html'
            )
            return
        
        bookmark = manager.get_bookmark(bookmark_id)
        if not bookmark:
            await message.answer(f"❌ Закладка #{bookmark_id} не найдена")
            return
        
        # Создаём инлайн кнопку для перехода к сообщению если оно есть
        keyboard = types.InlineKeyboardMarkup()
        link = manager.get_message_link(bookmark)
        if link:
            keyboard.add(types.InlineKeyboardButton(text="🔗 Перейти к сообщению", url=link))
        
        await message.answer(
            manager.format_bookmark(bookmark),
            parse_mode='html',
            reply_markup=keyboard if keyboard.inline_keyboard else None
        )
    
    # ==================== ЧАТБУК (ВСЕ ОТКРЫТЫЕ ЗАКЛАДКИ) ====================
    @dp.message_handler(Text(startswith=['Чатбук', 'чатбук'], ignore_case=True), 
                        content_types=['text'])
    async def chatbook_handler(message: types.Message):
        """Обработчик команды Чатбук {номер страницы}"""
        handler = BookmarkCommandHandler(manager)
        page = handler.parse_page_number(message.text)
        
        bookmarks, total_pages = manager.get_public_bookmarks(page)
        
        if not bookmarks:
            await message.answer("📭 Нет открытых закладок")
            return
        
        text = "📖 <b>ЧАТБУК - Все закладки чата</b>\n\n"
        text += manager.format_bookmarks_list(bookmarks, page, total_pages)
        
        await message.answer(text, parse_mode='html')
    
    # ==================== МОИ ЗАКЛАДКИ ====================
    @dp.message_handler(Text(startswith=['Мои закладки', 'мои закладки'], ignore_case=True), 
                        content_types=['text'])
    async def my_bookmarks_handler(message: types.Message):
        """Обработчик команды Мои закладки {номер страницы}"""
        handler = BookmarkCommandHandler(manager)
        page = handler.parse_page_number(message.text)
        
        bookmarks, total_pages = manager.get_user_bookmarks(message.from_user.id, page)
        
        if not bookmarks:
            await message.answer("📭 У вас нет закладок")
            return
        
        text = f"📌 <b>Ваши закладки ({manager.get_user_bookmark_count(message.from_user.id)})</b>\n\n"
        text += manager.format_bookmarks_list(bookmarks, page, total_pages)
        
        await message.answer(text, parse_mode='html')
    
    # ==================== ЗАКЛАДКИ ПОЛЬЗОВАТЕЛЯ ====================
    @dp.message_handler(Text(startswith=['Закладки', 'закладки'], ignore_case=True), 
                        content_types=['text'])
    async def user_bookmarks_handler(message: types.Message):
        """Обработчик команды Закладки {ссылка} {номер страницы}"""
        # Пропускаем если это уже обработано другими команды
        if any(message.text.strip().lower().startswith(cmd) 
               for cmd in ['закладка', 'чатбук', 'мои закладки', '+закладка', '-закладка']):
            return
        
        # Попытка найти пользователя по @username или ID в тексте
        text_parts = message.text.split()
        
        if len(text_parts) < 2:
            await message.answer(
                "❌ Укажите пользователя:\n"
                "<code>Закладки @username {номер страницы}</code>",
                parse_mode='html'
            )
            return
        
        # Здесь можно добавить логику поиска пользователя по @username
        # Для простоты, отправляем уведомление
        await message.answer(
            "⚠️ Команда закладок пользователя требует дополнительной настройки "
            "для поиска пользователей по @username"
        )
    
    # ==================== УДАЛИТЬ ЗАКЛАДКУ ====================
    @dp.message_handler(Text(startswith=['Удалить закладку', 'удалить закладку', '-закладка'], 
                            ignore_case=True), content_types=['text'])
    async def delete_bookmark_handler(message: types.Message):
        """Обработчик команды Удалить закладку {номер} или -закладка {номер}"""
        handler = BookmarkCommandHandler(manager)
        bookmark_id = handler.parse_bookmark_number(message.text)
        
        if bookmark_id is None:
            await message.answer(
                "❌ Укажите номер закладки:\n"
                "<code>Удалить закладку {номер}</code>",
                parse_mode='html'
            )
            return
        
        # Проверяем права (модератор или автор)
        is_moderator = False  # Это должно быть проверено на основе прав пользователя
        success, msg = manager.delete_bookmark(bookmark_id, message.from_user.id, is_moderator)
        
        if success:
            await message.answer(f"✅ {msg}")
        else:
            await message.answer(f"❌ {msg}")
    
    # ==================== ИСКЛЮЧИТЬ ЗАКЛАДКУ ====================
    @dp.message_handler(Text(startswith=['Исключить закладку', 'исключить закладку', 
                            'убрать закладку'], ignore_case=True), content_types=['text'])
    async def exclude_bookmark_handler(message: types.Message):
        """Обработчик команды Исключить закладку {номер}"""
        handler = BookmarkCommandHandler(manager)
        bookmark_id = handler.parse_bookmark_number(message.text)
        
        if bookmark_id is None:
            await message.answer(
                "❌ Укажите номер закладки:\n"
                "<code>Исключить закладку {номер}</code>",
                parse_mode='html'
            )
            return
        
        is_moderator = False
        success, msg = manager.exclude_bookmark(bookmark_id, message.from_user.id, is_moderator)
        
        if success:
            await message.answer(f"✅ {msg}")
        else:
            await message.answer(f"❌ {msg}")
    
    # ==================== КЛАДМЕН (УПРАВЛЕНИЕ ВИДИМОСТЬЮ) ====================
    @dp.message_handler(Text(startswith=['+Кладмен', '+кладмен'], ignore_case=True), 
                        content_types=['text'])
    async def add_kladmen_handler(message: types.Message):
        """Обработчик команды +Кладмен {ссылка} - добавить закладки в чатбук"""
        count = manager.set_user_bookmarks_visibility(message.from_user.id, True)
        
        await message.answer(
            f"✅ Ваши {count} закладки добавлены в чатбук",
            parse_mode='html'
        )
    
    @dp.message_handler(Text(startswith=['-Кладмен', '-кладмен'], ignore_case=True), 
                        content_types=['text'])
    async def remove_kladmen_handler(message: types.Message):
        """Обработчик команды -Кладмен {ссылка} - исключить закладки из чатбука"""
        count = manager.set_user_bookmarks_visibility(message.from_user.id, False)
        
        await message.answer(
            f"✅ Ваши {count} закладок исключены из чатбука",
            parse_mode='html'
        )


# ==================== ЭКСПОРТ ====================
__all__ = ['Bookmark', 'BookmarkManager', 'BookmarkCommandHandler', 'register_bookmarks_handlers']
