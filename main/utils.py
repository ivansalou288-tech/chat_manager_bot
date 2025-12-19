from typing import TYPE_CHECKING, Any

from aiogram.types.base import TelegramObject


#? EN: Custom Telegram object for creating copy text buttons in inline keyboards
#* RU: Пользовательский Telegram объект для создания кнопок копирования текста в инлайн-клавиатурах
class CopyTextButton(TelegramObject):
    text: str

    if TYPE_CHECKING:

        def __init__(__pydantic__self__, *, text: str, **__pydantic_kwargs: Any) -> None:

            super().__init__(text=text, **__pydantic_kwargs)