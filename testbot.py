import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import main_token as token
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
#?from config import *
import sqlite3
from aiogram.utils.exceptions import *
from main.utils import CopyTextButton
from path import Path
from aiogram.utils.exceptions import CantInitiateConversation, MessageNotModified 
from aiogram.types import ContentType
from telebot.types import CopyTextButton
from password_generator import PasswordGenerator
from main.config import *
token = '8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q'
bot = Bot(token=token)
dp = Dispatcher(bot)


#? EN: Starts a background loop that automatically unmutes users when their mute time expires.
#* RU: Запускает фоновый цикл, автоматически размутивющий пользователей по истечении времени мута.
@dp.message_handler(commands=['auto_unmute'])
async def auto_unmute(message: types.Message):
    global is_auto_unmute
    is_auto_unmute = True

    while True:
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        try:

            dates = cursor.execute(f"SELECT date FROM muts").fetchall()
            dates_muts = []
            for date in dates:
                dates_muts.append(date[0])
            now_time = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
            await asyncio.sleep(1)
            # * print(dates_muts, now_time)
            connection.commit()
            if now_time in dates_muts:

                now_time = (datetime.now() - timedelta(seconds=1)).strftime('%H:%M:%S %d.%m.%Y')
                # * print(now_time)
                # * print('размут')

                user_id = cursor.execute(f"SELECT user_id FROM muts WHERE date = ?",
                                         (now_time,)).fetchall()[0][0]
                chat_id = cursor.execute(f"SELECT chat_id FROM muts WHERE date = ?",
                                         (now_time,)).fetchall()[0][0]
                name_user = await bot.get_chat_member(chat_id=chat_id, user_id=int(user_id))
                name_user = name_user['user']['first_name']
                try:
                    cursor.execute(f'DELETE FROM muts WHERE date = ?', (now_time,))
                    connection.commit()
                    connection.close()
                except sqlite3.OperationalError:
                    print('error')
                    return
                await bot.send_message(chat_id,
                                       f'🔊<a href="tg://user?id={user_id}">{name_user}</a> твой срок молчания подошел к концу, можешь говорить, но будь аккуратнее впредь\n\n❗️Правила чата можно посмотреть по команде «<code>правила</code>»',
                                       parse_mode='html')

        except IndexError:
            connection.commit()
            connection.close()


#? EN: Mutes a user in the chat for a specified time with a reason; works only for allowed moderators.
#* RU: Замьючивает пользователя в чате на заданное время с указанием причины; доступно только разрешённым модераторам.
@dp.message_handler(Text(startswith='мут', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Мут
async def mute(message):
    global klan, is_auto_unmute
    if len(message.text.split()[0]) != 3:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return

    try:
        comments = "\n".join(message.text.split("\n")[1:])
    except IndexError:
        comments = ""
    try:
        mutetype = message.text.split()[2]
    except IndexError:
        mutetype = "час"
    try:
        muteint = int(message.text.split()[1])

    except ValueError:
        try:
            muteint = 1
            mutetype = message.text.split()[1]
        except IndexError:
            mutetype = "час"
    except IndexError:
        muteint = 1

    try:
        print(mutetype.split('@')[1])
        mutetype = 'час'
    except:
        pass
    if int(muteint) > 100:
        await message.reply('Слишком большое число! \n Делай меньше!')
        return
    if muteint <= 0:
        await message.reply('Неверное значение времени мута')
        return

    # * if len(message.text.split()[1:]) > 0 and message.text.split()[1] != mutetype and message.text.split()[1] != str(muteint):
    # *     try:
    # *         if message.text.split()[2] == mutetype:
    # *             pass
    # *         else:
    # *             try:
    # *                 print('True')
    # *                 print(' '.join(message.text.split()[0:]))
    # *                 if ' '.join(message.text.split()[0:]) != message.text.split('\n')[0]:
    # *                     print('..........')
    # *             except IndexError:
    # *                 pass
    # *             print("---------------------")
    # *     except IndexError:
    # *         pass
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[1:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '':
            pass
        elif comm == a:
            pass
        else:
            print('text', comm)

            print((' '.join(a.split(comm))).strip())








    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'mut') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'mut') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return


    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    # * ------------------------------------------------------------------------------------------------

    a = await mute_user(user_id, message.chat.id, muteint, mutetype, message, comments)
    if a == True:
        try:
            if mutetype == comments.split()[0]:
                mutetype = 'час'
        except IndexError:
            mutetype = 'час'
        await message.reply(
            f'🔇<b>Нарушитель:</b> <a href="tg://user?id={user_id}">{name_user}</a> лишается права слова\n⏰<b>Срок наказания:</b> {muteint} {mutetype}\n<b>👿Наказал его:</b> {moder_link}\n💬<b>Нарушение: {comments}</b>',
            parse_mode='html')
        if is_auto_unmute == False:
            await auto_unmute(message)
        return

    elif a == False:
        if is_auto_unmute == False:
            await auto_unmute(message)
        return

    else:
        await message.reply(a)
        if is_auto_unmute == False:
            await auto_unmute(message)
        return


if __name__ == "__main__":
    executor.start_polling(dp)