import random
from aiogram import types
from aiogram.dispatcher import Dispatcher

# Dictionary to store the target number for each chat
chat_targets = {}

def register_hot_cold_handlers(dp: Dispatcher):
    dp.register_message_handler(start_hot_cold, commands=['хг'], commands_prefix='!/.')
    dp.register_message_handler(guess_number, lambda message: message.chat.id in chat_targets)
    dp.register_message_handler(cancel_hot_cold, commands=['стоп-хг'], commands_prefix='!/.')

async def start_hot_cold(message: types.Message):
    """Start the Hot-Cold game by generating a random number."""
    chat_id = message.chat.id
    target_number = random.randint(1, 100)  # Bot picks a number between 1 and 100
    chat_targets[chat_id] = target_number

    await message.reply(
        "Игра 'Горячо-Холодно' началась! Я загадал число от 1 до 100. Попробуйте угадать!"
    )

async def guess_number(message: types.Message):
    """Handle a player's guess and provide feedback."""
    chat_id = message.chat.id

    try:
        guess = int(message.text)
    except ValueError:
        await message.reply("Пожалуйста, введите число.")
        return

    target_number = chat_targets[chat_id]
    difference = abs(target_number - guess)

    if guess == target_number:
        await message.reply("Поздравляю! Вы угадали число!")
        del chat_targets[chat_id]  # End the game for this chat
    elif difference <= 5:
        await message.reply("Горячо!")
    elif difference <= 15:
        await message.reply("Тепло.")
    else:
        await message.reply("Холодно.")

async def cancel_hot_cold(message: types.Message):
    """Cancel the Hot-Cold game for the chat."""
    chat_id = message.chat.id

    if chat_id in chat_targets:
        del chat_targets[chat_id]
        await message.reply("Игра 'Горячо-Холодно' завершена.")
    else:
        await message.reply("Игра не была начата.")