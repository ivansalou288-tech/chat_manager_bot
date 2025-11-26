import aiogram
import telebot
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
import sqlite3
from aiogram.utils.exceptions import UserIsAnAdministratorOfTheChat

token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"


bot = Bot(token=token)
dp = Dispatcher(bot)


@dp.message_handler(Text(startswith=["преды", 'варны'], ignore_case=True))
async def warns_check(message: types.Message):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    if message.reply_to_message:
        tg = message.reply_to_message.from_user
        tg_id = tg.id
    else:
        tg =message.from_user
        tg_id = tg.id
    cursor.execute("SELECT * FROM warns WHERE tg_id=?", (tg_id,))
    try:
        warns = cursor.fetchall()[0]
        warns_count = warns[1]
        first_warn = warns[2]
        second_warn = warns[3]
        therd_warn = warns[4]
        print(warns_count, first_warn, second_warn, therd_warn, end='\n')
        if warns_count == 0:
            await message.reply(f'<b>Предупредения <a href="tg://user?id={tg_id}">{tg.first_name}</a> отсутвуют! Поздравляем!</b>', parse_mode='html')
        if warns_count == 1:
             await  message.reply(f'<b>Предупреждения <a href="tg://user?id={tg_id}">{tg.first_name}</a>:</b>\n<b>| Количество предупреждений: 1</b>\n\n<b>| Причина первого предупреждения:</b> {first_warn}', parse_mode='html')
        if warns_count == 2:
             await  message.reply(f'<b>Предупреждения <a href="tg://user?id={tg_id}">{tg.first_name}</a>:</b>\n<b>Количество предупреждений: 2</b>\n\n<b>| Причина первого предупреждения:</b> {first_warn}\n\n| <b>Причина второго предупреждения:</b> {second_warn}', parse_mode='html')
        if warns_count == 3:
             await  message.reply(f'<b>Предупреждения <a href="tg://user?id={tg_id}">{tg.first_name}</a>:</b>\n<b>Количество предупреждений: 3</b>\n\n<b>| Причина первого предупреждения:</b> {first_warn}\n\n| <b>Причина второго предупреждения:</b> {second_warn}\n\n| <b>Причина второго предупреждения:</b> {therd_warn}', parse_mode='html')
    except IndexError:
        await message.reply(
            f'<b>Предупредения <a href="tg://user?id={tg_id}">{tg.first_name}</a> отсутвуют! Поздравляем!</b>',
            parse_mode='html')


@dp.message_handler(Text(startswith=['пред','варн'], ignore_case=True), is_chat_admin=True)
async def warnUser(message: types.Message):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    try:
        comments = "".join(message.text.split("\n")[1])
    except IndexError:
        comments=" "
    if message.chat.type in ['group', 'supergroup']:
        if message.reply_to_message:
            tg_id = message.reply_to_message.from_user.id
            cursor.execute('SELECT warns_count FROM warns WHERE tg_id=?', (tg_id,))
            try:
                warns_count = cursor.fetchall()[0][0]
            except IndexError:
                pass

            def firstSeen(tg_id):
                connection = sqlite3.connect('warn_list.db', check_same_thread=False)
                cursor = connection.cursor()
                cursor.execute("SELECT tg_id FROM warns WHERE tg_id=?", (tg_id,))
                rez = cursor.fetchall()
                if not rez:

                    return True
                else:

                    return False

            if not firstSeen(tg_id):
                warn_count_new = int(warns_count) + 1
                if comments == "" or comments == " ":
                    cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                    await message.reply(
                          f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое {warn_count_new}-е предупреждение! Будь акуратнее!',
                          parse_mode='html')
                    connection.commit()
                else:
                    if warn_count_new == 1:
                        cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                        cursor.execute('UPDATE warns SET first_warn = ? WHERE tg_id = ?',
                                       (comments, tg_id))
                        connection.commit()
                        await message.reply(
                            f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое {warn_count_new}-е предупреждение!\n<b>| Причина: {comments}</b>\nБудь акуратнее!',
                            parse_mode='html')
                    elif warn_count_new == 2:
                        cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                        cursor.execute('UPDATE warns SET second_warn = ? WHERE tg_id = ?',
                                       (comments, tg_id))
                        connection.commit()
                        await message.reply(
                            f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое {warn_count_new}-е предупреждение!\n<b>| Причина: {comments}</b>\nБудь акуратнее!',
                            parse_mode='html')
                    elif warn_count_new == 3:
                        cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                        cursor.execute('UPDATE warns SET therd_warn = ? WHERE tg_id = ?',
                                       (comments, tg_id))
                        connection.commit()
                        await message.reply(
                            f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое {warn_count_new}-е предупреждение!\n<b>| Причина: {comments}</b>\nБудь акуратнее!',
                            parse_mode='html')


            else:
                if comments == "" or comments == " ":
                    cursor.execute('INSERT INTO warns (tg_id, warns_count, first_warn, second_warn, therd_warn) VALUES (?, ?, ?, ?, ?)',
                                   (tg_id, 1, '', '', ''))
                    await message.reply(
                          f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое первое предупреждение! Будь акуратнее!',
                          parse_mode='html')
                    connection.commit()
                else:
                    cursor.execute(
                        'INSERT INTO warns (tg_id, warns_count, first_warn, second_warn, therd_warn) VALUES (?, ?, ?, ?, ?)',
                        (tg_id, 1, comments, '', ''))
                    await message.reply(
                        f'| <b>Нарушитель: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Получает свое первое предупреждение!\n<b>| Причина: {comments}</b>\nБудь акуратнее!',
                        parse_mode='html')
                    connection.commit()

            if warn_count_new == 3:
                await message.reply(f'Достигнут лимит предпреждений!', parse_mode = 'html')

                await warns_check(message)


        else:
             await message.reply("эта команда должна быть ответом на сообщение")
    else:
        await message.answer('Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')



@dp.message_handler(Text(startswith=['снять пред','снять варн', '-пред','-варн'], ignore_case=True), is_chat_admin=True)
async def warnUser(message: types.Message):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.type in ['group', 'supergroup']:
        if message.reply_to_message:
            tg_id = message.reply_to_message.from_user.id
            cursor.execute('SELECT warns_count FROM warns WHERE tg_id=?', (tg_id,))
            connection.commit()
            try:
                warns_count = cursor.fetchall()[0][0]
                if warns_count == 0:
                    await message.reply(
                        f'<b>У <a href="tg://user?id={message.reply_to_message.from_user.id}">Пользователя</a></b>\nОтсутвуют предупреждения! Мы рады для тебя!',
                        parse_mode='html')
                else:
                    warn_count_new = int(warns_count) - 1
                    if warn_count_new == 0:
                        cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                        cursor.execute('UPDATE warns SET first_warn = ? WHERE tg_id = ?', (None, tg_id))
                        connection.commit()
                    if warn_count_new == 1:
                        cursor.execute('UPDATE warns SET warns_count = ? WHERE tg_id = ?', (warn_count_new, tg_id))
                        cursor.execute('UPDATE warns SET second_warn = ? WHERE tg_id = ?', (None, tg_id))
                        connection.commit()
                    await message.reply(
                            f'| <b>Пользователь: <a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a></b>\n| Свободен от одного своего предупреждения! Поздравляю!\n<b>| Количество предупреждений <a href="tg://user?id={message.reply_to_message.from_user.id}">Пользователя</a>:</b> {warn_count_new}',
                            parse_mode='html')

            except IndexError:
                await message.reply(
                    f'<b>У <a href="tg://user?id={message.reply_to_message.from_user.id}">Пользователя</a></b>\nОтсутвуют предупреждения! Мы рады для тебя!',
                    parse_mode='html')



        else:
             await message.reply("эта команда должна быть ответом на сообщение")
    else:
        await message.answer('Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')








if __name__ == "__main__":
    executor.start_polling(dp)