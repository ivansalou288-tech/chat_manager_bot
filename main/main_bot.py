import datetime
import aiogram
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram.utils.exceptions import CantInitiateConversation, MessageNotModified 
from aiogram.types import ContentType
from telebot.types import CopyTextButton
from password_generator import PasswordGenerator

#Тестовое изменение
from config import *
from modules.farm import *
from modules.kasik import *
from modules.turnaments import *
from modules.mafia import *
from modules.cubes import *
from modules.message_top import *
from modules.obvinenie import *
from modules.rus_rulet import *
from modules.golden_rulet import *

@dp.callback_query_handler(text="successful_recom1")
async def successful_recom1(call: types.CallbackQuery):
    if call.from_user.id not in can_recommend_users:
        await bot.answer_callback_query(call.id, text='⚠️Тебе не доступна эта функция')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    all = cursor.execute('SELECT * FROM din_admn_user_data WHERE moder = ?', (call.from_user.id,)).fetchall()[0]

    user_id = all[0]
    pubg_id = all[1]
    moder = all[2]
    comments = all[3]
    recom = all[4]
    date = all[5]
    pwo = PasswordGenerator()
    id_recom = pwo.shuffle_password('ASDFGHJKL12345678', 8)
    cursor.execute(
        'INSERT INTO recommendation (user_id, pubg_id, moder, comments, rang, date, recom_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, pubg_id, moder, comments, recom, date, id_recom))
    await call.message.edit_text('✅Рекомендация заполнена')
    connection.commit()
    cursor.execute('DELETE FROM din_admn_user_data WHERE moder = ?', (moder,))
    connection.commit()


@dp.callback_query_handler(text="not_successful_user1")
async def successful_recom1(call: types.CallbackQuery):
    if call.from_user.id not in can_recommend_users:
        await bot.answer_callback_query(call.id, text='⚠️Тебе не доступна эта функция')
        return
    await call.message.edit_text('❌Отменено')

@dp.message_handler(commands=['start', 'help'])
async def start(message):
    if message.chat.id != message.from_user.id:
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    about = await about_user_sdk(message.from_user.id, klan)
    if about == '' or about == None:
        is_in_klan = '❌ Ты не участник клана'
    else:
        is_in_klan = f'✅ Ты участник клана\n\n<b>Твое описание</b>\n{about}'
    buttons = [
        types.InlineKeyboardButton(text="☎️  Менеджер", url='https://t.me/werty_pub'),
        types.InlineKeyboardButton(text="📝  Регистрация", url="https://t.me/werty_clan_helper_bot"),
        types.InlineKeyboardButton(text="Канал WERTY", url="https://t.me/Werty_Metro"),
        types.InlineKeyboardButton(text="👨‍💻Нашел баг!(админ бота)", url="https://t.me/zzoobank")

    ]

    commands = types.InlineKeyboardButton(text='⚒️ Команды', callback_data='commands')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons).add(commands)

    await bot.send_photo(message.chat.id,photo=open(f'{curent_path}/photos/klan_ava.jpg', 'rb'), caption=f'Приветсвуем тебя в <b>WERTY | Чат-менеджер</b>\n\n{is_in_klan}\n\nЧто ты хочешь сделать?', parse_mode='html',reply_markup=keyboard)

@dp.callback_query_handler(text="commands")
async def successful_recom1(call: types.CallbackQuery):
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('commands',)).fetchall()[0][0]
    await bot.send_message(call.from_user.id, f'🗓<b>Список команд чата:</b>\n\n{text}', parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await bot.answer_callback_query(call.id, text='')

@dp.message_handler(Text(startswith=["муты"], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Функция размута
async def mutes_check(message):
    if len(message.text.split()[0]) != 4:
        return
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return

    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM muts WHERE chat_id = ?", (message.chat.id,))
    all = cursor.fetchall()

    moders_mens = []
    dates = []
    rang_mut = []
    comments = []
    users_ids = []
    mutes_count = 0
    itog = []
    for users in all:
        mutes_count += 1
    for i in range(mutes_count):
        users_ids.append(all[i][0])
    for i in range(mutes_count):
        rang_mut.append(all[i][1])
    for i in range(mutes_count):
        moders_mens.append(all[i][3])
    for i in range(mutes_count):
        dates.append(all[i][4])
    for i in range(mutes_count):
        comments.append(all[i][5])
    for i in range(mutes_count):
        print(users_ids[i])
        try:
            name_user = cursor.execute(f'SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?', (users_ids[i],)).fetchall()[0][0]
        except IndexError:
            name_user = 'Пользователь'
        print(name_user)
        textt = f'<b>{i + 1}</b>. <a href="tg://user?id={users_ids[i]}">{name_user}</a> [{rang_mut[i]}]\n⏱️ До {dates[i]}\n👮‍Заглушил: {moders_mens[i]}\n💬Причина: {comments[i]}'
        itog.append(textt)
    itog_text = '\n\n'.join(itog)
    if itog_text == '':
        itog_text = '💬 Список пока пуст'
    await message.answer(f'⚪️ <b>Список пользователей, которым запрещено писать:</b>\n\n{itog_text}',
                         parse_mode=ParseMode.HTML)


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


@dp.message_handler(Text(startswith=['анмут', "размут"], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * Функция размута
async def unmute(message):
    if len(message.text.split()[0]) > 6:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        try:
            if message.text.split('@')[1] != "":
                pass
            else:
                return
        except IndexError:
            return
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
    # * ----------------------------------------------------------------------------------------------------

    a = await unmute_user(user_id, message.chat.id, message)
    if a == True:
        await message.reply(
            f'🔊<a href="tg://user?id={user_id}">{name_user}</a> можешь говорить, но будь аккуратнее впредь\n\n❗️Правила чата можно посмотреть по команде «<code>правила</code>»',
            parse_mode='html')
    else:
        await message.reply(a)

    connection.commit()


@dp.message_handler(Text(startswith='бан', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Функция бана
async def ban(message):
    if len(message.text.split()[0]) != 3:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[1:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '' and len(a) > 1:
            return
        elif comm == a:
            pass
        else:
            print('text', comm)

            print((' '.join(a.split(comm))).strip())
            try:
                a = ' '.join(a.split(comm)).strip()
                username = a.split('@')[1]
            except IndexError:
                return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    try:
        comments = "".join(message.text.split("\n")[1:])
    except IndexError:
        comments = ""
    user_id = await get_user_id(message)

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik


    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return

    user_men = f'<a href="tg://user?id={user_id}">{name_user}</a>'
    moder_men = moder_link
    message_id = message.message_id
    # * ----------------------------------------------------------------------------------------------
    if await ban_user(user_id, message.chat.id, user_men, moder_men, comments, message_id, message) == True:
        await message.reply(
            f'<b>❗️Внимание❗️</b>\n🔴Злостный нарушитель <a href="tg://user?id={user_id}">{name_user}</a> получает бан и покидает нас\n👮‍♂️Выгнал его: {moder_link}\n💬Выгнали его за: {comments}',
            parse_mode='html')


@dp.message_handler(Text(startswith='причина бана', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Функция бана
async def prich_ban(message):
    if len(message.text.split()[1]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = await get_user_id(message)

 
    try:
        all = cursor.execute(f"SELECT * FROM [{-(message.chat.id)}bans] WHERE tg_id=?", (user_id,)).fetchall()[0]
    except:
        await message.reply('📝Пользователь не забанен')
        return
    pubg_id = all[1]
    message_id = all[2]
    comments = all[3]
    date = all[4]
    user_men = all[5]
    moder_men = all[6]
    chat_idd = int(str(message.chat.id).split('100')[1])
    message_link = f'https://t.me/c/{chat_idd}/{message_id}'
    await message.reply(
        f'🚨Нарушитель {user_men} был забанен навсегда\n💬Причина: {comments}\n👮‍♂️Забанил: {moder_men}\n⏰Когда: {date}\n📝Айди в пабге: {pubg_id}\n📨<a href="{message_link}">Прейти к сообщению</a>',
        parse_mode='html')


@dp.message_handler(Text(startswith='разбан', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Функция разбана
async def unban(message):
    if len(message.text.split()[0]) != 6:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
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
    # * ----------------------------------------------------------------------------------------------
    await unban_user(message.chat.id, user_id)
    await message.reply(
        f' ✅ Пользователь <a href="tg://user?id={user_id}">{name_user}</a> разбанен\n👮‍♂️Помиловал его: {moder_link}\n\n💬<a href="tg://user?id={user_id}">{name_user}</a>, мы ждем твоего возвращения!',
        parse_mode='html')


@dp.message_handler(Text(startswith='вернуть', ignore_case=True), content_types=ContentType.TEXT,
                    is_forwarded=False)  # * Функция вернуть
async def returner(message):
    if len(message.text.split()[0]) != 7:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
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
    # * ----------------------------------------------------------------------------------------------
    await unban_user(message.chat.id, user_id)
    try:
        link_chat = await bot.export_chat_invite_link(message.chat.id)
        await bot.send_message(chat_id=user_id, text=f'🗓 Вы были разбанены в чате <b>{message.chat.title}</b> вступить можно по ссылке: {link_chat}', parse_mode='html', disable_web_page_preview=True)
    except CantInitiateConversation:
        await message.answer(f' ✅ Пользователь <a href="tg://user?id={user_id}">{name_user}</a> разбанен\n👮‍♂️Помиловал его: {moder_link}\n\n💬<a href="tg://user?id={user_id}">{name_user}</a>, но не получил сообщение о приглашение!', parse_mode='html')
        return
    await message.reply( f' ✅ Пользователь <a href="tg://user?id={user_id}">{name_user}</a> разбанен\n👮‍♂️Помиловал его: {moder_link}\n\n💬<a href="tg://user?id={user_id}">{name_user}</a>, и получил сообщение о приглашение!', parse_mode='html')


@dp.message_handler(Text(startswith='кик', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Функция кика
async def kick(message):
    if len(message.text.split()[0]) != 3:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'ban') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'ban') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik


    try:
        comments = "".join(message.text.split("\n")[1:])
    except IndexError:
        comments = ""

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    # * ----------------------------------------------------------------------------------------------

    if await kick_user(user_id, message.chat.id) == True:
        await message.reply(
            f'❎ <a href="tg://user?id={user_id}">{name_user}</a> покидает нас с возможностью возвращения\n👮‍♂️Выгнал его: {moder_link}\n💬Причина изгнания: {comments}',
            parse_mode='html')


@dp.message_handler(commands=["id"], content_types=ContentType.TEXT,is_forwarded=False)  # * Функция узнавания айди чата
async def id_chat(message):
    await message.reply(f'айди чата "<code>{message.chat.id}</code>"', parse_mode='html')


@dp.message_handler(Text(startswith="пинг", ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * проверка работоспособности бота
async def ping(message):
    try:
        text = message.text.split(' ')[1]
    except IndexError:
        if len(message.text) > 4:
            return
        await message.reply("ПОНГ")


@dp.message_handler(Text(startswith="бот", ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * проверка работоспособности бота
async def bot_check(message):
    try:
        text = message.text.split(' ')[1]
    except IndexError:
        if len(message.text) > 3:
            return
        await message.reply("✅Бот на месте")


@dp.message_handler(Text(startswith=['моя статья'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def vagn_abavlenie(message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    a = random.randint(0, len(states))
    men = message.from_user.get_mention(as_html=True)
    text = states[a]
    try: 
        cursor.execute(f'INSERT INTO states (user_id, text) VALUES (?,?)', (message.from_user.id, text))
        connection.commit()
        await message.reply(f'🤷‍♂️ Сегодня {men} приговаривается к статье {text}', parse_mode = 'html')
    except sqlite3.IntegrityError:
        text = cursor.execute('SELECT text FROM states WHERE user_id = ?', (message.from_user.id,)).fetchall()[0][0]
        connection.commit()
        await message.reply(f'🤷‍♂️ Сегодня {men} уже приговаривался к статье {text}', parse_mode = 'html')
    connection.commit()
@dp.message_handler(Text(startswith='Постинг', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * Постинг напоминание в группу "замы"
async def check_posting(message):
    global posting
    if posting == True:
        await message.reply(text="🔴Постинг уже актививрован")
    else:
        posting = True
        await message.reply(text="Автопостинг напоминаний активирован")
        await shedul_posting(message)

@dp.message_handler(Text(startswith=['созвать админов', 'созвать отв'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def admn_sbor(message):
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang > 0')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    name1 = message.from_user.get_mention(as_html=True)

    comments = " ".join(message.text.split("\n")[1:])
    if comments == "":
        await message.reply(f'📢{name1} объявляет созыв админов', parse_mode='html')
    else:
        await message.reply(f'📢{name1} объявляет созыв админов\n\n💬 Объявление:\n{comments}', parse_mode='html')
    a = ''
    for r in range(users_count):
        a += mentions[r]
        print(a)
        print(r)
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await message.reply(f'<b>⬆️Созват{a}ь Админов ({(r // 6) + 1})</b>', parse_mode='html')
            a = ''

@dp.message_handler(Text(startswith=['созыв', 'созвать', 'общий сбор'], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * Общий сбор
async def all_sbor(message):
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    #
    try:
        if len(message.text.split()[1]) > 4:
            return
    except IndexError:
        pass
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[2:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '' and len(a) > 1:
            return
        elif comm == a:
            pass
        else:
            print('text', comm)

            print((' '.join(a.split(comm))).strip())
            return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'all') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'all') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'all') == 'chat error':
        await message.reply('📝Непредвиденная ошибка!\n💬<i>Для решения обратитесь к админу этого бота: @zzoobank</i>')
        return
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    try:
        cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}]')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    name1 = message.from_user.get_mention(as_html=True)

    comments = "\n".join(message.text.split("\n")[1:])
    if comments == "":
        await message.reply(f'📢{name1} объявляет общий сбор', parse_mode='html')
    else:
        await message.reply(f'📢{name1} объявляет общий сбор\n\n💬 Объявление:\n{comments}', parse_mode='html')
    a = ''
    for r in range(users_count):
        a += mentions[r]
        print(a)
        print(r)
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await message.reply(f'<b>⬆️Общи{a}й сбор ({(r // 6) + 1})</b>', parse_mode='html')
            a = ''


@dp.message_handler(Text(startswith=["преды", 'варны'], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * Просмотр варнов своих и другово пользователя
async def warns_check(message: types.Message):
    if len(message.text.split()[0]) != 5:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if len(message.text.split()[1:]) > 0 and '\n'.join(message.text.split('\n')[1:]) != ' '.join(message.text.split()[1:]):
        try:
            message.text.split('@')[1]
        except IndexError:
            return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    user_id = await get_user_id_self(message)
    name_user = GetUserByID(user_id).nik

    text = await warn_check_sdk(user_id, message.chat.id, name_user)
    await message.reply(text, parse_mode='html')


@dp.message_handler(Text(startswith=['пред', 'варн'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * Выдача преда
async def warnUser(message: types.Message):
    if len(message.text.split()[0]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if len(message.text) > 0:
        a = ' '.join(message.text.split()[1:])
        print('text1', a)
        comm = ' '.join(message.text.split('\n')[1:])
        comm = ' '.join(comm.split())
        if comm == '' and len(a) > 1:
            return
        elif comm == a:
            pass
        else:
            print('text', comm)

            print((' '.join(a.split(comm))).strip())
            try:
                a = ' '.join(a.split(comm)).strip()
                username = a.split('@')[1]
            except IndexError:
                return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'warn') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'warn') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    try:
        comments = "".join(message.text.split("\n")[1:])
    except IndexError:
        comments = ""
    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik


    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    # * ------------------------------------------------------------------------------------------------
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()

    if not firstSeen(user_id, message):
        cursor.execute(f'SELECT warns_count FROM [{-(message.chat.id)}] WHERE tg_id=?', (user_id,))
        warns_count = cursor.fetchall()[0][0]
        warn_count_new = int(warns_count) + 1
        is_first = False
    else:
        warn_count_new = 1
        is_first = True

    await give_warn(message=message, comments=comments, warn_count_new=warn_count_new, user_id=user_id,
                    is_first=is_first)
    await message.reply(
        f'🛑 Нарушитель <a href="tg://user?id={user_id}">{name_user}</a> нарушил правила и получает предупреждение <b>({warn_count_new}/3)</b>\n<b>👮‍♂️Поймал его:</b> {moder_link}\n<b>💬Нарушение:</b> {comments}\n\n<a href="tg://user?id={user_id}">{name_user}</a>, больше так не делай, соблюдай правила!',
        parse_mode='html')
    if warn_count_new == 3:
        warns = await warns_check(message)
        print(warns)
        await limit_warns(message)


@dp.message_handler(Text(startswith=['снять пред', 'снять варн'], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * Снятие преда
async def snat_warnUser(message: types.Message):
    global klan
    if len(message.text.split()[1]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    a = 0
    if len(message.text.split()[2:]) > 0 and '\n'.join(message.text.split('\n')[2:]) != ' '.join(message.text.split()[2:]):
        try:
            message.text.split('@')[1]
            int(message.text.split(' ')[2])
        except IndexError:
            a += 1
        except ValueError:
             a += 1
    if a == 2:
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'warn') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'warn') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik

    if message.chat.id == message.from_user.id:
        await message.answer('Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'SELECT warns_count FROM [{-(message.chat.id)}] WHERE tg_id=?', (user_id,))
    try:
        warns_count = int(cursor.fetchall()[0][0])
    except IndexError:
        warns_count = 0
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    if warns_count == 0:
        warn_count_new = warns_count
    else:
        warn_count_new = warns_count - 1
    if warns_count == 0:
        await message.reply(f'❕Предупреждения <a href="tg://user?id={user_id}">{name_user}</a> отсутствуют',
                            parse_mode='html')
        return

    try:
        warn_count_dell = int(message.text.split()[2])
    except ValueError:
        warn_count_dell = warns_count
    except IndexError:
        warn_count_dell = warns_count

    moder_link = message.from_user.get_mention(as_html=True)

    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя снять предупреждение выданное более старшим модером')
        return
    # * ------------------------------------------------------------------------------------------------

    if int(warn_count_dell) not in range(1, 4):
        await message.reply('Номер предупреждения должен быть целым числом в диапозоне от 1 до 3')
        return
    if warn_count_dell > warns_count:
        await message.reply(
            '❕Предупреждение с таким номером отсутвует!\n\n💬<i>Предупреждения пользователя можно узнать по команде</i>«<code>преды @</code><i>юзер</i>»',
            parse_mode='html')
        return
    await snat_warn(user_id=user_id, number_warn=warn_count_dell, warn_count_new=warn_count_new, message=message)
    await message.reply(
        f'✅<a href="tg://user?id={user_id}">{name_user}</a>, с тебя сняли одно предупреждение\n👮‍♂️Добрый модер: {moder_link}\n💬Количество твоих предупреждений: {warn_count_new} из 3\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
        parse_mode='html')

    connection.commit()
    connection.close()


@dp.message_handler(Text(startswith=['снятые преды', 'снятые варны'], ignore_case=True))  # * Снятые преды
async def snatie_warnUser(message: types.Message):
    global page, mes_id, itog, page_c
    if len(message.text.split()[1]) != 5:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    can_chech_snat_pred = [8015726709, 1401086794, 1240656726]
    moder = message.from_user.id
    if moder in can_chech_snat_pred:
        pass
    else:
        await message.reply('📝Тебе не доступна эта функция', parse_mode='HTML')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik
    tg_id = user_id
    page = 0
    mes_id = 0
    itog = []
    page_c = 0
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{-(message.chat.id)}snat] WHERE user_id=?", (tg_id,))

    all = cursor.fetchall()

    texts = []
    moder_gives = []
    moder_snat = []
    itog = []
    warns_count = 0
    for users in all:
        warns_count += 1
    for i in range(warns_count):
        texts.append(all[i][1])

    for i in range(warns_count):
        moder_gives.append(all[i][2])

    for i in range(warns_count):
        moder_snat.append(all[i][3])
    ar = []
    for i in range(warns_count):
        textt = (
            f'🔸{i + 1}. От {moder_gives[i]} | Снял: {moder_snat[i]}\n&#8195&#8194Причина предупреждения: {texts[i]}')
        ar.append(textt)
        if (i + 1) % 15 == 0 or i == warns_count - 1:
            itog.append('\n\n'.join(ar))
            ar.clear()

    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="back"),
        types.InlineKeyboardButton(text="▶️", callback_data="next")

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    for i in itog:
        page_c += 1
    try:
        await bot.send_message(message.from_user.id,
                            f'🗓<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}',
                            parse_mode='html',
                            reply_markup=keyboard)
    except IndexError:
        await message.reply('Снятых предупреждений нет')
        return
    await message.answer(
        '🗓Список снятых предупреждений пользователя отправлен в <a href="https://t.me/werty_chat_manager_bot">лс</a>',
        parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.callback_query_handler(text="back")
async def successful_recom(call: types.CallbackQuery):
    global page, page_c
    global itog
    # * print(call.data, page, itog)
    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="back"),
        types.InlineKeyboardButton(text="▶️", callback_data="next")

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    try:
        page -= 1
        if page < 0:
            await bot.answer_callback_query(call.id, text='⚠️это первая страница')
            return
        await call.message.edit_text(
            f'🗓<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}', parse_mode='html',
            reply_markup=keyboard)
        # * print(page)
    except IndexError:
        page += 1
        await bot.answer_callback_query(call.id, text='⚠️это первая страница')
        return
    except MessageNotModified:
        return


@dp.callback_query_handler(text="next")
async def successful_recom(call: types.CallbackQuery):
    global page, page_c
    global itog
    print(call.data, page, itog)

    buttons = [
        types.InlineKeyboardButton(text="◀️", callback_data="back"),
        types.InlineKeyboardButton(text="▶️", callback_data="next")

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    try:
        page += 1
        if page < 0:
            await bot.answer_callback_query(call.id, text='⚠️это последняя страница')
            return
        await call.message.edit_text(
            f'🗓<b>Снятые предупреждения этого пользователя(страниц: {page_c}):</b>\n\n{itog[page]}', parse_mode='html',
            reply_markup=keyboard)

    except IndexError:
        page -= 1
        await bot.answer_callback_query(call.id, text='⚠️это последняя страница')
    except MessageNotModified:
        pass


@dp.message_handler(Text(startswith="повысить", ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * повысить пользователя
async def rang_up(message: types.Message):
    if len(message.text.split()[0]) != 8:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return

    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik

    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    # * Повышаем
    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу повысить самого себя")
        return
    try:
        rang_delta = int(message.text.split()[1])

        new_rang_user = rang_delta
    except ValueError:
        rang_delta = 1
        new_rang_user = first_rang_user + rang_delta
    except IndexError:
        rang_delta = 1
        new_rang_user = first_rang_user + rang_delta

    if new_rang_user > rang_moder:
        await message.reply("Нельзя повысить на более старший ранг чем ты")
        return
    if new_rang_user < first_rang_user:
        await message.reply("Пользователь уже на этой должности или выше")
        return
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET rang = ? WHERE tg_id = ?',
                   (new_rang_user, user_id))
    connection.commit()
    new = cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    await message.reply(
        f'✅Ранг <a href="tg://user?id={user_id}">{name_user}</a> назначен(а): {rangs_name[new]}[{new}]',
        parse_mode="html")
    connection.commit()
    connection.close()


@dp.message_handler(Text(startswith=["понизить", "занизить"], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * понизить пользователя
async def rang_down(message: types.Message):
    if len(message.text.split()[0]) != 8:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik

    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return

    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу понизить самого себя")
        return
    if await is_more_moder(user_id, moder_id, message.chat.id) == False:
        await message.reply('Нельзя использовать эту команду по отношению к старшему или равному модеру')
        return
    try:
        rang_delta = int(message.text.split()[1])

        new_rang_user = rang_delta
    except ValueError:
        rang_delta = 1
        new_rang_user = first_rang_user - rang_delta
    except IndexError:
        rang_delta = 1
        new_rang_user = first_rang_user - rang_delta
    if new_rang_user > 6 or new_rang_user < 0:
        await message.reply("Такого ранга не существует")
        return
    if new_rang_user > rang_moder:
        await message.reply("Пользователь уже на этой должности или выше")
        return
    if new_rang_user > first_rang_user:
        await message.reply("Пользователь уже на этой должности или выше")
        return
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET rang = ? WHERE tg_id = ?',
                   (new_rang_user, user_id))
    connection.commit()
    new = cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    await message.reply(
        f'✅Модератору <a href="tg://user?id={user_id}">{name_user}</a> понижен ранг до {rangs_name[new]}[{new}]',
        parse_mode="html")
    connection.commit()
    connection.close()


@dp.message_handler(Text(startswith=["снять", "разжаловать"], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * снять пользователя с поста модератора
async def rang_snat(message: types.Message):
    if len(message.text.split()[0]) > 11:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return

    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'rang') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'rang') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik


    try:
        rang_moder = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    try:
        first_rang_user = \
        cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply("Не могу понизить самого себя")
        return
    if first_rang_user >= rang_moder:
        await message.reply("Нельзя понизить старшего или равного по званию")
        return
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET rang = ? WHERE tg_id = ?',
                   (0, user_id))

    connection.commit()
    new = cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    await message.reply(
        f'❎ Модератор <a href="tg://user?id={user_id}">{name_user}</a> разжалован(а)',
        parse_mode="html")
    connection.commit()
    connection.close()


@dp.message_handler(Text(startswith="описание", ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * просмтр описания пользователя
async def about_user(message: types.Message):
    if len(message.text.split()[0]) != 8:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    user_id = await get_user_id_self(message)
    name_user = GetUserByID(user_id).nik

    try:
        tg_id = user_id
        print(tg_id)

        cursor.execute(f"SELECT * FROM [{-(message.chat.id)}] WHERE tg_id=?", (tg_id,))
        users = cursor.fetchall()
        print(users)
        for user in users:
            user_about = {
                'tg_id': user[0],
                'usename': user[1],
                'name': user[2],
                'age': user[3],
                'nik_pubg': user[4],
                'id_pubg': user[5],
                'nik': user[6],
                'rang': user[7]
            }

        # * Выводим в нормальном формате описание

        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                      'Менеджер',
                      'Владелец')
        print(rangs_name[4])
        sm = "🎄"
        stars = ""
        for i in range(int(user_about['rang'])):
            stars += sm
        text = await about_user_sdk(user_id, message.chat.id)
        itog_text = f'📝Описание пользователя:\n\n{text}'
        cursor.execute(f"SELECT id_pubg FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,))
        id_pubg = cursor.fetchall()[0][0]

        # * Создаём текст для копирования
        id_copy = CopyTextButton(text=str(id_pubg))

        id_btn = types.InlineKeyboardButton(text="📋Скопировать айди",
                                            copy_text=id_copy)  # * Внедряем текст для копирования в инлайн-кнопки

        keyboard = types.InlineKeyboardMarkup().add(id_btn)
        await message.reply(text=text, reply_markup=keyboard, parse_mode="html")

    except UnboundLocalError:
        await message.reply(f'Описание <a href="tg://user?id={user_id}">Пользователя</a> не заполнено',
                            parse_mode="html")


@dp.message_handler(Text(startswith="-чат", ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * закрыть чат
async def minus_chat(message):
    if len(message.text.split()[0]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'close_chat') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'close_chat') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    await bot.set_chat_permissions(message.chat.id, ChatPermissions(can_send_messages=False))
    buttons = [
        types.InlineKeyboardButton(text="Открыть чат", callback_data="open_chat"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.reply(
        f'🤐 <b>Чат закрыт для общения</b>\nТеперь писать в чат могут только администраторы\n\n💬<i> Чат можно открыть по команде «</i><code>+чат</code><i>»</i> или нажав на кнопку снизу',
        reply_markup=keyboard, parse_mode="HTML")


@dp.message_handler(Text(startswith="-смс", ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * закрыть чат
async def minus_chat(message):
    if len(message.text.split()[0]) != 4:
        return
    
    if not message.reply_to_message:
        return
    
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'dell') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'dell') == 'Need reg':
        await message.reply('📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    try:
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        await bot.delete_message(message.chat.id, message.message_id)
    except MessageCantBeDeleted:
        await message.answer('Не могу удалить сообщение т.к у меня нет таких прав')


@dp.message_handler(Text(startswith="+чат", ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * открыть чат
async def open_chat(message):
    moder_id = message.from_user.id
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if await is_successful_moder(moder_id, message.chat.id, 'close_chat') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'close_chat') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>')
        return
    await bot.set_chat_permissions(message.chat.id,
                                   ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                   can_send_photos=True, can_send_videos=True,
                                                   can_send_audios=True, can_send_documents=True,
                                                   can_send_other_messages=True,
                                                   can_send_video_notes=True, can_send_voice_notes=True,
                                                   can_pin_messages=True,
                                                   can_add_web_page_previews=True, can_send_polls=True))
    await message.reply(f'✅ Чат открыт для общения\n<i>Теперь у всех есть разрешение на отправку сообщений</i>',
                        parse_mode="HTML")


@dp.callback_query_handler(text='open_chat')  # * * обработчик открытия чата
async def open_chat_button(call):
    moder_id = call.from_user.id
    if await is_successful_moder(moder_id, call.message.chat.id, 'close_chat') == False:
        await bot.answer_callback_query(call.id, text='📝Ранг модератора не достаточен для использования этой команды',
                                        show_alert=True)
        return
    elif await is_successful_moder(moder_id, call.message.chat.id, 'close_chat') == 'Need reg':
        await bot.answer_callback_query(call.id,
                                        text='📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
                                        show_alert=True)
        return
    await bot.set_chat_permissions(call.message.chat.id,
                                   ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                   can_send_photos=True, can_send_videos=True,
                                                   can_send_audios=True, can_send_documents=True,
                                                   can_send_other_messages=True,
                                                   can_send_video_notes=True, can_send_voice_notes=True,
                                                   can_pin_messages=True,
                                                   can_add_web_page_previews=True, can_send_polls=True))
    await bot.send_message(call.message.chat.id,
                           '✅ Чат открыт для общения\n<i>Теперь у всех есть разрешение на отправку сообщений</i>',
                           parse_mode="HTML")


@dp.message_handler(Text(startswith='кто админ', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * просмотр админов чата
async def kto_admin(message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    try:
        cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (6,))
    except IndexError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    shars = ['🎱', '🌍', '⚾', '🔮', '️🎾', '🥎', '🏐']
    users_6rang = cursor.fetchall()
    rang_6 = []
    for user in users_6rang:
        rang_6.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')

    cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (5,))
    users_5rang = cursor.fetchall()
    rang_5 = []
    for user in users_5rang:
        rang_5.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')

    cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (4,))
    users_4rang = cursor.fetchall()
    rang_4 = []
    for user in users_4rang:
        rang_4.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')

    cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (3,))
    users_3rang = cursor.fetchall()
    rang_3 = []
    for user in users_3rang:
        rang_3.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')

    cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (2,))
    users_2rang = cursor.fetchall()
    rang_2 = []
    for user in users_2rang:
        rang_2.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')

    cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}] WHERE rang = ?', (1,))
    users_1rang = cursor.fetchall()
    rang_1 = []
    for user in users_1rang:
        rang_1.append(
            f'{shars[random.randint(0, 6)]} <a href="tg://user?id={user[0]}">{cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?", (user[0],)).fetchall()[0][0]}</a>')
    r6 = "\n".join(rang_6)
    r5 = "\n".join(rang_5)
    r4 = "\n".join(rang_4)
    r3 = "\n".join(rang_3)
    r2 = "\n".join(rang_2)
    r1 = "\n".join(rang_1)
    ri6 = 6
    ri5 = 5
    ri4 = 4
    ri3 = 3
    ri2 = 2
    ri1 = 1
    rs6 = "🎄🎄🎄🎄🎄🎄"
    rs5 = "🎄🎄🎄🎄🎄"
    rs4 = "🎄🎄🎄🎄"
    rs3 = "🎄🎄🎄"
    rs2 = "🎄🎄"
    rs1 = "🎄"
    rang6 = ""
    rang5 = ""
    rang4 = ""
    rang3 = ""
    rang2 = ""
    rang1 = ""
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')

    if r6 != "":
        rang6 = f'{rs6}\n{rangs_name[ri6]}:\n{r6}\n\n'
    if r5 != "":
        rang5 = f'{rs5}\n{rangs_name[ri5]}:\n{r5}\n\n'
    if r4 != "":
        rang4 = f'{rs4}\n{rangs_name[ri4]}:\n{r4}\n\n'
    if r3 != "":
        rang3 = f'{rs3}\n{rangs_name[ri3]}:\n{r3}\n\n'
    if r2 != "":
        rang2 = f'{rs2}\n{rangs_name[ri2]}:\n{r2}\n\n'
    if r1 != "":
        rang1 = f'{rs1}\n{rangs_name[ri1]}:\n{r1}\n\n'

    try:
        await message.reply(text=f'{rang6}{rang5}{rang4}{rang3}{rang2}{rang1}', parse_mode='html')
    except aiogram.utils.exceptions.MessageTextIsEmpty:
        await message.reply('Админов в этом чате нет')


@dp.message_handler(Text(startswith='ник', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * просмотр ника
async def nik(message):
    if len(message.text.split()[0]) != 3:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        if len(message.text.split()[1]) > 0:
            try:
                message.text.split('@')[1]
            except IndexError:
                return
    except IndexError:
        pass
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = await get_user_id_self(message)
    name_user = GetUserByID(user_id).nik

    tg_id = user_id
    try:
        nik = cursor.execute(f'SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id = ?', (tg_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(f'<a href="tg://user?id={user_id}">Пользователь</a> не заполнил ник', parse_mode="html")
        return
    if nik == '':
        await message.reply(f'<a href="tg://user?id={user_id}">Пользователь</a> не заполнил ник', parse_mode="html")
    else:
        await message.reply(f'🗓Ник <a href="tg://user?id={user_id}">пользователя</a>: «{nik}»', parse_mode="html")


@dp.message_handler(Text(startswith='+ник', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * изменение ника
async def plus_nik(message):
    if len(message.text.split()[0]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    tg_id = message.from_user.id
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = " ".join(message.text.split(" ")[1:])

    if comments == '' or comments == " ":
        await message.reply('Ник не должен быть пустым')
        return
    if len(comments) > 20:
        await message.reply('Ник не должен быть длиннее 50 символов')
        return
    await message.reply(f'✅ Ник {message.from_user.get_mention(as_html=True)} изменён на «{comments}»',
                        parse_mode="html")
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET nik = ? WHERE tg_id = ?',
                   (comments, tg_id))
    connection.commit()


@dp.message_handler(Text(startswith='+игровой ник', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * изменение ника
async def plus_nik(message):
    if len(message.text.split()[1]) != 3:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    tg_id = message.from_user.id
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = " ".join(message.text.split(" ")[2:])

    if comments == '' or comments == " ":
        await message.reply('Ник не должен быть пустым')
        return
    if len(comments) > 12:
        await message.reply('Не верный ник')
        return
    await message.reply(f'✅ Игровой ник {message.from_user.get_mention(as_html=True)} изменён на «{comments}»',
                        parse_mode="html")
    cursor.execute(f'UPDATE [{-(klan)}] SET nik_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    cursor.execute(f'UPDATE [{-(sost_1)}] SET nik_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    cursor.execute(f'UPDATE [{-(sost_2)}] SET nik_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    connection.commit()


@dp.message_handler(Text(startswith='+игровой айди', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * изменение ника
async def plus_nik(message):
    if len(message.text.split()[1]) != 4:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    tg_id = message.from_user.id
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        comments = int(message.text.split(" ")[2])
    except ValueError:
        await message.answer('📝Некоректное айди')
        return

    def split_number(number):
        num = []
        while number > 0:
            digit = number % 10
            num.append(digit)
            number = number // 10
        return num[::-1]

    id_p = split_number(comments)
    if id_p[0] != 5 or len(str(comments)) < 9 or len(str(comments)) > 12:
        await message.answer('📝Некоректное айди')
        return

    await message.reply(f'✅ Айди {message.from_user.get_mention(as_html=True)} изменён на «{comments}»',
                        parse_mode="html")
    cursor.execute(f'UPDATE [{-(klan)}] SET id_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    cursor.execute(f'UPDATE [{-(sost_1)}] SET id_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    cursor.execute(f'UPDATE [{-(sost_2)}] SET id_pubg = ? WHERE tg_id = ?',
                   (comments, tg_id))
    connection.commit()


@dp.message_handler(Text(startswith='дк', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * изменение мигимального рангда команд
async def dk(message):
    if len(message.text.split()[0]) != 2:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if message.chat.id == klan:
        rang_up_dk = int(cursor.execute("SELECT dk FROM klan WHERE comand=?", ("dk",)).fetchall()[0][0])  # * Ранг с которого можно повышать
    else:
        rang_up_dk = int(cursor.execute("SELECT dk FROM sostav WHERE comand=?", ("dk",)).fetchall()[0][0])
    rang_moder = cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (message.from_user.id,)).fetchall()[0][0]

    print(rang_moder)
    if rang_moder < rang_up_dk:
        await message.reply("Ранг модератора не достаточен для использования этой команды")
        return

    try:
        command = message.text.split(' ')[1]
        rang_dk = int(message.text.split(' ')[2])
    except IndexError:
        await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
        return
    except ValueError:
        print("2222222")
        try:
            command = message.text.split(' ')[1] + ' ' + message.text.split(' ')[2]
            print(command)
            rang_dk = int(message.text.split(' ')[3])
        except IndexError:
            await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
            return
        except ValueError:
            await message.reply(f'Неверное использование команды дк\nПример: дк мут 3')
            return

    if command == 'мут' or command == 'анмут' or command == 'размут':
        command_en = 'mut'
    elif command == 'бан' or command == 'разбан' or command == 'анбан':
        command_en = 'ban'
    elif command == 'пред' or command == 'варн' or command == 'снять пред' or command == 'снять варн':
        command_en = 'warn'
    elif command == 'общий сбор' or command == 'созвать' or command == 'созыв':
        command_en = 'all'
    elif command == 'повысить' or command == 'понизить' or command == "снять":
        command_en = 'rang'
    elif command == 'дк':
        command_en = 'dk'
    elif command == 'изменение правил' or command == '+правила':
        command_en = 'change_pravils'
    elif command == '-чат' or command == 'закрыть чат':
        command_en = 'close_chat'
    elif command == 'изменение приветствия' or command == '+приветствие':
        command_en = 'change_priv'
    elif command == 'создание объявления' or command == '+объявление':
        command_en = 'obavlenie'
    elif command == 'турниры' or command == 'турнир':
        command_en = 'tur'
    elif command == '-смс' or command == 'удаление сообщения':
        command_en = 'dell'
    else:
        await message.reply('Настройки для этой команды нет')
        return
    num = ['0', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    if rang_dk > 6 or rang_dk < 0:
        await message.reply('📝Такого ранга не существует')
        return
    if message.chat.id == klan:
        cursor.execute(f"UPDATE klan SET dk = ? WHERE comand = ?", (rang_dk, command_en,))
        connection.commit()
    else:
        cursor.execute(f"UPDATE sostav SET dk = ? WHERE comand = ?", (rang_dk, command_en,))
        connection.commit()
    if rang_dk > 0 and rang_dk <= 6:
        await message.reply(
            f"{num[rang_dk]} Команда «{command}» теперь доступна с ранга модератора {rangs_name[rang_dk]} ({rang_dk})")
    if rang_dk == 0:
        await message.reply(f'✅Команда «{command}» теперь доступна всем')


@dp.message_handler(Text(startswith='правила', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)  # * просмотр правил
async def pravila(message):
    if len(message.text) != 7:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = f"🗓<b>Правила чата</b>\n\n{cursor.execute(f'SELECT text FROM pravils WHERE chat_id=?', (message.chat.id,)).fetchall()[0][0]}"
    await message.reply(text, parse_mode='HTML')
    return text


@dp.message_handler(Text(startswith='+правила', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * изменение правил чата
async def plus_pravila(message):

    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return

    moder_id = message.from_user.id
    if await is_successful_moder(moder_id, message.chat.id, 'change_pravils') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'change_pravils') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='HTML')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = '\n'.join(message.text.split("\n")[1:])
    if comments == '':
        await message.reply('📝 Правила не заданы')
        return
    cursor.execute(f'SELECT text FROM pravils WHERE chat_id=?', (message.chat.id,))
    if cursor.fetchall() == []:
        cursor.execute(f'INSERT INTO pravils (chat_id, text) VALUES (?, ?)', (message.chat.id, comments))
    else:
        cursor.execute(f'UPDATE pravils SET text = ? WHERE chat_id = ?', (comments, message.chat.id))
    connection.commit()
    await message.answer('✅ Правила чата обновлены')


@dp.message_handler(Text(startswith="кто я", ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def all_about_self_user(message: types.Message):
    if len(message.text) != 5:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    user_id = message.from_user.id
    try:
        clan_nik_user = cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            f'Полное описание <a href="tg://user?id={message.from_user.id}">Пользователя</a> не заполнено',
            parse_mode="html")
        return
    status = (await bot.get_chat_member(message.chat.id, message.from_user.id))['status']
    print(status, clan_nik_user)
    if status == 'administrator':
        chat_status = '<i>👨🏻‍🔧 Телеграм-админ этого чата</i>'
    elif status == 'creator':
        chat_status = '<i>👨🏻‍🔧 Создатель этого чата</i>'
    elif status == 'member' or status == 'restricted':
        chat_status = '💚 Состоит в чате'
    else:
        chat_status = 'Неизвестно'

    about_user = await about_user_sdk(user_id, message.chat.id)
    try:
        rang = about_user.split('\n<b>👤Имя')[0]
    except AttributeError:
        return
    about_user = '\n<b>👤Имя' + about_user.split('\n<b>👤Имя')[1]
    # * await message.reply(about_user, parse_mode="html")
    warns = await warn_check_sdk(user_id, message.chat.id, clan_nik_user)
    profile_pictures = await dp.bot.get_user_profile_photos(user_id)

    recom = await recom_check_sdk(user_id, clan_nik_user)

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,))
    users = cursor.fetchall()

    for user in users:
        user_about_list = {
            'last_date': user[8],
            'date_vhod': user[9]
        }
    if user_about_list['last_date'] == '' or user_about_list['last_date'] == None:
        lst_date = 'Неизвестно'
    else:
        last_date = user_about_list['last_date']
        lst = datetime.strptime(user_about_list['last_date'], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst

        days = delta.days * 24
        sec = int(str(delta.total_seconds()).split('.')[0])

        hours = sec // 3600 - days
        minutes = (sec % 3600) // 60
        days = delta.days

        if days == 0:
            days_text = ''
        else:
            days_text = f'{days} дн '
        if hours == 0:
            hours_text = ''
        else:
            hours_text = f'{hours} ч '
        if minutes == 0:
            minutes_text = ''
        else:
            minutes_text = f'{minutes} мин '

        lst_date = f'{days_text}{hours_text}{minutes_text}'

        if lst_date == '' or lst_date == None:
            lst_date = 'только что'

    if user_about_list['date_vhod'] == 'Неизвестно':
        date_vh = ''
    else:

        lst = datetime.strptime(user_about_list['date_vhod'], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst

        days = delta.days * 24
        sec = int(str(delta.total_seconds()).split('.')[0])

        hours = sec // 3600 - days
        minutes = (sec % 3600) // 60
        days = delta.days
        mouth = days // 30
        days = days % 30

        if mouth == 0:
            mouth_text = ''
        else:
            mouth_text = f'{mouth} мес '
        if days == 0:
            days_text = ''
        else:
            days_text = f'{days} дн '
        if hours == 0:
            hours_text = ''
        else:
            hours_text = f'{hours} ч '
        if minutes == 0:
            minutes_text = ''
        else:
            minutes_text = f'{minutes} мин '

        date_vh = f'({mouth_text}{days_text}{hours_text}{minutes_text})'
    itog_text = f'🎅Это пользователь <a href="tg://user?id={user_id}">{clan_nik_user}</a>\n{chat_status}\n\n{rang}\n\n<b>🧾Описание пользователя:</b>{about_user}\n<b>🕑Последнее сообщение:</b> {lst_date}\n🕰️<b>В клане c:</b> {user_about_list["date_vhod"]} {date_vh}\n\n📨Клановый ник: {clan_nik_user}\n\n{warns}\n\n{recom}'
    try:
        await bot.send_photo(chat_id=message.chat.id, photo=dict((profile_pictures.photos[0][0])).get("file_id"),
                             caption=itog_text, parse_mode=ParseMode.HTML)
    except IndexError:
        await message.reply(itog_text, parse_mode=ParseMode.HTML)


@dp.message_handler(Text(startswith="кто ты", ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def all_about_user(message: types.Message):
    print(len(message.text))
    if len(message.text.split()[1]) != 2:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik
    # * text = await warn_check_sdk(user_id, message.chat.id, name_user)
    # * await message.reply(text, parse_mode='html')

    try:
        clan_nik_user = \
        cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            f'Полное описание <a href="tg://user?id={user_id}">Пользователя</a> не заполнено',
            parse_mode="html")
        return
    status = (await bot.get_chat_member(message.chat.id, user_id))['status']
    print(status)
    if status == 'administrator':
        chat_status = '<i>👨🏻‍🔧 Телеграм-админ этого чата</i>'
    elif status == 'creator':
        chat_status = '<i>👨🏻‍🔧 Создатель этого чата</i>'
    elif status == 'member' or status == 'restricted':
        chat_status = '💚 Состоит в чате'
    else:
        chat_status = '💔 Не состоит вы чате'

    about_user = await about_user_sdk(user_id, message.chat.id)
    rang = about_user.split('\n<b>👤Имя')[0]
    about_user = '\n<b>👤Имя' + about_user.split('\n<b>👤Имя')[1]
    # * await message.reply(about_user, parse_mode="html")
    warns = await warn_check_sdk(user_id, message.chat.id, clan_nik_user)
    profile_pictures = await dp.bot.get_user_profile_photos(user_id)
    print(profile_pictures)
    recom = await recom_check_sdk(user_id, name_user)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,))
    users = cursor.fetchall()

    for user in users:
        user_about_list = {
            'last_date': user[8],
            'date_vhod': user[9]
        }
    if user_about_list['last_date'] == '' or user_about_list['last_date'] == None:
        lst_date = 'Неизвестно'
    else:
        last_date = user_about_list['last_date']
        lst = datetime.strptime(user_about_list['last_date'], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst

        days = delta.days * 24
        sec = int(str(delta.total_seconds()).split('.')[0])

        hours = sec // 3600 - days
        minutes = (sec % 3600) // 60
        days = delta.days

        if days == 0:
            days_text = ''
        else:
            days_text = f'{days} дн '
        if hours == 0:
            hours_text = ''
        else:
            hours_text = f'{hours} ч '
        if minutes == 0:
            minutes_text = ''
        else:
            minutes_text = f'{minutes} мин '

        lst_date = f'{days_text}{hours_text}{minutes_text}'

        if lst_date == '' or lst_date == None:
            lst_date = 'только что'
    print(user_about_list['date_vhod'])
    if user_about_list['date_vhod'] == 'Неизвестно':
        date_vh = ''
    else:

        lst = datetime.strptime(user_about_list['date_vhod'], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst

        days = delta.days * 24
        sec = int(str(delta.total_seconds()).split('.')[0])

        hours = sec // 3600 - days
        minutes = (sec % 3600) // 60
        days = delta.days
        mouth = days // 30
        days = days % 30

        if mouth == 0:
            mouth_text = ''
        else:
            mouth_text = f'{mouth} мес '
        if days == 0:
            days_text = ''
        else:
            days_text = f'{days} дн '
        if hours == 0:
            hours_text = ''
        else:
            hours_text = f'{hours} ч '
        if minutes == 0:
            minutes_text = ''
        else:
            minutes_text = f'{minutes} мин '

        date_vh = f'({mouth_text}{days_text}{hours_text}{minutes_text})'
    itog_text = f'🎅Это пользователь <a href="tg://user?id={user_id}">{clan_nik_user}</a>\n{chat_status}\n\n{rang}\n\n<b>🧾Описание пользователя:</b>{about_user}\n<b>🕑Последнее сообщение:</b> {lst_date}\n🕰️<b>В клане c:</b> {user_about_list["date_vhod"]} {date_vh}\n\n📨Клановый ник: {clan_nik_user}\n\n{warns}\n\n{recom}'

    try:
        await bot.send_photo(chat_id=message.chat.id, photo=dict((profile_pictures.photos[0][0])).get("file_id"),
                             caption=itog_text, parse_mode=ParseMode.HTML)
    except IndexError:
        await message.reply(itog_text, parse_mode=ParseMode.HTML)


@dp.message_handler(content_types=ContentType.NEW_CHAT_MEMBERS)  # * приветсвие нового участника
async def new_chat_mem(message):
    new = message.new_chat_members[0]
    username = new.username
    user_id = new.id
    user = new.get_mention(as_html=True)
    print(user_id, username)
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        cursor.execute(f'UPDATE [{-(klan)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(f'UPDATE [{-(sost_1)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(f'UPDATE [{-(sost_2)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute(f'SELECT text FROM privets WHERE chat_id=?', (message.chat.id,)).fetchall()[0][0]
    await bot.send_message(message.chat.id, f'🗓 Приветствие: {user}\n{text}', parse_mode='html')
    text = await pravila_sdk(message)
    await bot.send_message(message.chat.id, text, parse_mode='HTML')


@dp.message_handler(Text(startswith='+приветствие', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def add_privetstvie(message):
    moder_id = message.from_user.id
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if await is_successful_moder(moder_id, message.chat.id, 'change_priv') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'change_priv') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = '\n'.join(message.text.split("\n")[1:])
    if comments == '':
        await message.reply('📝 Приветствие не задано')
        return
    cursor.execute(f'SELECT text FROM privets WHERE chat_id=?', (message.chat.id,))
    if cursor.fetchall() == []:
        cursor.execute(f'INSERT INTO privets (chat_id, text) VALUES (?, ?)', (message.chat.id, comments))
    else:
        cursor.execute(f'UPDATE privets SET text = ? WHERE chat_id = ?', (comments, message.chat.id))
    connection.commit()
    await message.answer('✅ Приветствие новых пользователей обновлено')


@dp.message_handler(Text(startswith='приветствие', ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)  # * просмотр приветсвия
async def privetstvie(message):
    if len(message.text) != 11:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        a = cursor.execute(f'SELECT text FROM privets WHERE chat_id=?', (message.chat.id,)).fetchall()[0][0]
    except:
        a = 'Приветствуем тебя в чате'
    await message.reply(
        f"🗓<b>Приветствие новых пользователей</b>\n\n{a}",
        parse_mode='HTML')


@dp.message_handler(Text(startswith='!Настройка', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def set_new_chat(message):
    if message.chat.id == message.from_user.id:
        return
    if message.from_user.id != 1240656726:
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    # * try:
    # *     cursor.execute(f"SELECT rang FROM [{-(message.chat.id)}] WHERE tg_id=?", (message.from_user.id,))
    # *     await message.reply('Чат уже готов к работе')
    # *     return
    # * except sqlite3.OperationalError:

    table_creation_query = f"""
                    CREATE TABLE [{-(message.chat.id)}] (
                        tg_id    INTEGER UNIQUE
                                         NOT NULL,
                        username TEXT,
                        name     TEXT    NOT NULL,
                        age      INTEGER NOT NULL,
                        nik_pubg TEXT    NOT NULL,
                        id_pubg  INTEGER NOT NULL
                                         UNIQUE,
                        nik      TEXT,
                        rang     INTEGER NOT NULL
                                         DEFAULT (0)
                    );
                """
    try:
        cursor.execute(table_creation_query)
    except sqlite3.OperationalError:
        pass
    connection.commit()
    table_creation_query = f"""
                            CREATE TABLE [{-(message.chat.id)}bans]  (
                                tg_id      INTEGER UNIQUE
                                                   NOT NULL,
                                id_pubg    INTEGER NOT NULL
                                                   UNIQUE,
                                message_id,
                                prichina,
                                date,
                                user_men,
                                moder_men
                            );

                        """
    try:
        cursor.execute(table_creation_query)
    except sqlite3.OperationalError:
        pass
    connection.commit()
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    table_creation_query = f"""
                            CREATE TABLE [{-(message.chat.id)}]  (
                                tg_id        INTEGER PRIMARY KEY
                                                     UNIQUE
                                                     NOT NULL,
                                warns_count  INTEGER,
                                first_warn   TEXT,
                                second_warn  TEXT,
                                therd_warn   TEXT,
                                first_moder,
                                second_moder,
                                therd_moder
                            );
                        """
    try:
        cursor.execute(table_creation_query)
    except sqlite3.OperationalError:
        pass
    connection.commit()
    table_creation_query = f"""
                            CREATE TABLE [{-(message.chat.id)}snat]  (
                                user_id,
                                warn_text,
                                moder_give,
                                moder_snat
                            );

                        """
    try:
        cursor.execute(table_creation_query)
    except sqlite3.OperationalError:
        pass
    connection.commit()
    await message.reply('Чат готов к работе')


@dp.message_handler(Text(startswith='!изменить правила входа', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def set_new_pravil_vhod(message):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id in [8015726709, 1401086794, 1240656726]:
        pass
    else:
        return

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = '\n'.join(message.text.split("\n")[1:])
    if comments == '':
        await message.reply('📝Правила не заданы')
        return
    cursor.execute(f'UPDATE texts SET text = ? WHERE text_name = ?', (comments, 'pravils'))
    connection.commit()
    await message.answer('✅ Правила для новых пользователей обновлено')


@dp.message_handler(Text(startswith='!правила входа', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def set_new_pravil_vhod(message):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id in [8015726709, 1401086794, 1240656726]:
        pass
    else:
        return

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('pravils',)).fetchall()[0][0]
    await message.answer(text, parse_mode='html')


@dp.message_handler(Text(startswith='!изменение чатов', ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def set_new_chat(message):
    if message.chat.id != message.from_user.id or message.from_user.id != 1240656726:
        return
    text = message.text
    try:
        klan_id = text.split('Клан:')[1].split()[0]
    except IndexError:
        try:
            klan_id = text.split('клан:')[1].split()[0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>!изменение чатов\nклан:\nсостав 1:\nсостав 2:\nлоги:</code>',
                parse_mode='HTML')
            return
    try:
        sost_1_id = text.split('Состав 1:')[1].split()[0]
    except IndexError:
        try:
            sost_1_id = text.split('состав 1:')[1].split()[0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>!изменение чатов\nклан:\nсостав 1:\nсостав 2:\nлоги:</code>',
                parse_mode='HTML')
            return

    try:
        sost_2_id = text.split('Состав 2:')[1].split()[0]
    except IndexError:
        try:
            sost_2_id = text.split('состав 2:')[1].split()[0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>!изменение чатов\nклан:\nсостав 1:\nсостав 2:\nлоги:</code>',
                parse_mode='HTML')
            return
    try:
        logs = text.split('Логи:')[1].split()[0]
    except IndexError:
        try:
            logs = text.split('логи:')[1].split()[0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>!изменение чатов\nклан:\nсостав 1:\nсостав 2:\nлоги:</code>',
                parse_mode='HTML')
            return

    if logs == '' or klan_id == '' or sost_1_id == '' or sost_2_id == '':
        await message.reply(
            '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>!изменение чатов\nклан:\nсостав 1:\nсостав 2:\nлоги:</code>',
            parse_mode='HTML')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE chat_ids SET chat_id = ? WHERE chat_name = ?', (klan_id, 'klan'))
    cursor.execute(f'UPDATE chat_ids SET chat_id = ? WHERE chat_name = ?', (logs, 'logs_gr'))
    cursor.execute(f'UPDATE chat_ids SET chat_id = ? WHERE chat_name = ?', (sost_1_id, 'sost_1'))
    cursor.execute(f'UPDATE chat_ids SET chat_id = ? WHERE chat_name = ?', (sost_2_id, 'sost_2'))
    connection.commit()
    await message.reply('Обновлено')


@dp.message_handler(Text(startswith="Рекомендации", ignore_case=True))
async def recom_check(message):
    if len(message.text.split()[0]) != 12:
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    user_id = GetUserByMessage(message).user_id
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
        return

    name_user = GetUserByID(user_id).nik
    tg_id=user_id
    text = await recom_check_sdk(tg_id, name_user)
    if text == '':
        await message.reply(f'📝Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют',
                            parse_mode='html')
        return
    await message.reply(f'{text}', parse_mode='html')


@dp.message_handler(Text(startswith=['+рекомендация', 'рекомендовать'], ignore_case=True),
                    content_types=ContentType.TEXT,is_forwarded=False)
async def add_recom(message):
    moder = message.from_user.id
    if moder in can_recommend_users:
        pass
    else:
        await message.reply('📝Тебе не доступна эта функция')
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = message.text
    try:
        us = text.split()[1]
        print(us)
    except IndexError:
        await message.reply(
            '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>+рекомендация {юзер или пабг айди}\nПричина: \nРекомендую на: </code>',
            parse_mode='HTML')
        return
    try:
        pubg_id = int(us)
        user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        nik_pubg = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        username = cursor.execute(f"SELECT username FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
    except ValueError:
        try:
            username = us.split('@')[1]
            print(username)

            user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
            nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
            nik_pubg = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][
                0]
            pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди пользователя',
                parse_mode='html')
            return
    if user_id == message.from_user.id:
        await message.reply('📝Жулик, не рекомендуй!\n\n💬<i>Нельзя рекомендовать самого себя</i>', parse_mode='html')
        return
    moder_men = message.from_user.id
    users_idss = cursor.execute(f"SELECT user_id FROM recommendation WHERE moder=?", (moder_men,)).fetchall()
    print(users_idss)
    for user_ids in users_idss:
        print(user_ids[0], user_id)

        if user_ids[0] == user_id:
            await message.reply(
                '📝Жулик, не рекомендуй!\n\n💬<i>Нельзя рекомендовать одного человека больше одного раза</i>',
                parse_mode='html')
            return
    try:
        comments = (text.split('Причина:')[1:])[0].split('\n')[0]

    except IndexError:
        try:
            comments = (text.split('причина:')[1:])[0].split('\n')[0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>+рекомендация {юзер или пабг айди}\nПричина: \nРекомендую на: </code>',
                parse_mode='HTML')
            return
    try:
        recom = text.split('Рекомендую на:')[1:][0]
    except IndexError:
        try:
            recom = text.split('Рекомендую на:')[1:][0]
        except IndexError:
            await message.reply(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>+рекомендация {юзер или пабг айди}\nПричина: \nРекомендую на: </code>',
                parse_mode='HTML')
            return
    pwo = PasswordGenerator()
    id_recom = pwo.shuffle_password('ASDFGHJKL12345678', 8)
    moder = message.from_user.id
    date = datetime.now().strftime('%d.%m.%Y')
    buttons = [
        types.InlineKeyboardButton(text="Верно", callback_data="successful_recom1"),
        types.InlineKeyboardButton(text="Не правильно", callback_data="not_successful_user1"),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    connection.commit()
    cursor.execute(
        'INSERT INTO din_admn_user_data (user_id, pubg_id, moder, comments, rang, date) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, pubg_id, moder, comments, recom, date))
    connection.commit()
    await message.answer(
        f'Рекомендация <a href="tg://user?id={user_id}">Пользователя</a>:\n\n🟢 <b>1</b>. От <a href="tg://user?id={moder}">{message.from_user.first_name}</a>:\n<b>&#8195Чем отличился:</b> {comments}\n<b>&#8195Рекомендован на:</b> {recom}',
        parse_mode='html', reply_markup=keyboard)



@dp.message_handler(Text(startswith=['-рекомендация'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def dell_recom(message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        us = message.text.split()[1]
        print(us)
    except IndexError:
        await message.reply(
            '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n«<code>-рекомендация {юзер или пабг айди} от {юзер или пабг айди}</code>»',
            parse_mode='HTML')
        return
    moder = message.from_user.id
    if moder in can_snat_recommend_users:
        pass
    else:
        await message.reply('📝Тебе не доступна эта функция\n\n💬<i>Снять свою рекомендацию можно в админ боте</i>',
                            parse_mode='HTML')
        return

    try:
        pubg_id = int(us)
        user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
    except ValueError:
        try:
            username = us.split('@')[1]
            user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
        except IndexError:
            await message.reply(
                '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди пользователя',
                parse_mode='html')
            return

    try:
        moder_t = message.text.split('от ')[1].split()[0]
        try:
            pubg_id = int(moder_t)
            moder_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        except ValueError:
            try:
                username = moder_t.split('@')[1]
                moder_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][
                    0]
            except IndexError:
                await message.reply(
                    '📝Невозможно найти информацию о модераторе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди модератора',
                    parse_mode='html')
                return
    except IndexError:
        moder_id = message.from_user.id

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    alll = cursor.execute('SELECT moder FROM recommendation WHERE user_id = ?', (user_id,)).fetchall()
    if alll == []:
        await bot.send_message(message.chat.id, '📝Рекомендации пользователя отсутвуют')
        return
    mod_count = 0
    idss = []
    for i in alll:
        mod_count += 1
    is_this_moder = False
    for t in range(mod_count):
        num = t
        b = (alll[num][0])
        idss.append(b)
    for y in range(mod_count):
        print(idss[y], moder_id)

        if int(idss[y]) == moder_id:
            is_this_moder = True

    if is_this_moder == False:
        await bot.send_message(message.chat.id, '📝Этот пользователь не рекомендовал этого пользователя')
        return
    recom_id = cursor.execute('SELECT recom_id FROM recommendation WHERE user_id = ? AND moder = ?',
                              (user_id, moder_id,)).fetchall()[0][0]
    print(recom_id)
    cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (recom_id,))
    await bot.send_message(message.chat.id, '✅Рекомендация удалена')
    connection.commit()


@dp.message_handler(commands=['ид'], commands_prefix=['!', '.'])
async def id_user_check(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    try:
        username = (message.text.split('@')[1]).split()[0]
        tg_id = cursor.execute(f"SELECT tg_id FROM [{-(message.chat.id)}] WHERE username=?", (username,)).fetchall()[0][
            0]
        name_user = (await bot.get_chat_member(message.chat.id, tg_id))['user']['first_name']
    except IndexError:
        if message.reply_to_message:
            tg = message.reply_to_message.from_user
            tg_id = tg.id
            name_user = tg.first_name
            username = tg.username
        else:
            tg = message.from_user
            tg_id = tg.id
            name_user = tg.first_name
            username = tg.username

    await message.answer(
        f'👤 Пользователь <a href="https://t.me/{username}">{name_user}</a>\n🆔 равен @<code>{tg_id}</code>',
        parse_mode='html', disable_web_page_preview=True)


@dp.message_handler(Text(startswith='!изменить список команд', ignore_case=True))
async def id_user_check(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    comments = '\n'.join(message.text.split('\n')[1:])
    if message.from_user.id != 1240656726:
        return
    cursor.execute('UPDATE texts SET text = ? WHERE text_name = ?', (comments, 'commands',))
    await message.answer('✅Изменено')
    connection.commit()


@dp.message_handler(Text(startswith='!список команд_admin', ignore_case=True))
async def id_user_check(message: types.Message):
    if message.from_user.id != 1240656726:
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('commands',)).fetchall()[0][0]
    await bot.send_message(message.from_user.id, f'{text}',
                           disable_web_page_preview=True)
    await message.answer('🗓Список команд отправлен в <a href="https://t.me/for_klan_tests_bot">лс</a>',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.message_handler(Text(startswith=['!команды', '! команды'], ignore_case=True))
async def id_user_check(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('commands',)).fetchall()[0][0]
    try:
        await bot.send_message(message.from_user.id, f'🗓<b>Список команд чата:</b>\n\n{text}', parse_mode=ParseMode.HTML,
                           disable_web_page_preview=True)
    except CantInitiateConversation:
        await message.answer('🗓 Диалог с ботом не найден')
        return
    await message.answer('🗓Список команд отправлен в <a href="https://t.me/for_klan_tests_bot">лс</a>',
                         parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.message_handler(commands=['квест'], commands_prefix='!')
async def quest_change(message: types.Message):
    if message.from_user.id in [1803851598, 1240656726]:
        pass
    else:
        await message.answer('Тебе не доступна эта команда')
        return
    try:
        comments = '\n'.join(message.text.split('\n')[1:])
        num = int(message.text.split()[1])
        print(num, comments)
    except IndexError:
        return
    except ValueError:
        return
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    names = ['', 'first', 'second', 'third']
    cursor.execute(f'UPDATE quests SET text = ? WHERE quest = ?', (comments, names[num]))
    connection.commit()
    await message.answer("✅ Изменено")


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


async def quests_funk(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    global is_quests
    is_quests = True
    while True:
        a = cursor.execute('SELECT text FROM quests').fetchall()

        quests = [a[0][0], a[1][0], a[2][0]]
        now_time = datetime.now().strftime("%H:%M:%S")
        await asyncio.sleep(1)
        if now_time == "10:00:00":
            if datetime.today().weekday() == 0:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[0]}', parse_mode='html')
            if datetime.today().weekday() == 1:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста',
                                       parse_mode='html')
            if datetime.today().weekday() == 2:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[1]}', parse_mode='html')
            if datetime.today().weekday() == 3:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста',
                                       parse_mode='html')
            if datetime.today().weekday() == 4:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[2]}', parse_mode='html')
            if datetime.today().weekday() == 5:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста',
                                       parse_mode='html')


@dp.message_handler(Text(startswith=['+объявление'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def abavlenie(message):
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'chat error':
        await message.reply('📝Непредвиденная ошибка!\n💬<i>Для решения обратитесь к админу этого бота: @zzoobank</i>')
        return

    comments = "\n".join(message.text.split("\n")[1:])

    message_id = (await bot.send_message(message.chat.id, f'❗️️<b>ОБЪЯВЛЕНИЕ</b> ❗️️\n\n{comments}\n\n▫️Объявил {moder_link}', parse_mode='html')).message_id
    print(message_id)
    await bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)

@dp.message_handler(Text(startswith=['+важное объявление'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def vagn_abavlenie(message):
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    moder_id = message.from_user.id
    moder_link = message.from_user.get_mention(as_html=True)
    if await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'obavlenie') == 'chat error':
        await message.reply('📝Непредвиденная ошибка!\n💬<i>Для решения обратитесь к админу этого бота: @zzoobank</i>')
        return

    comments = "\n".join(message.text.split("\n")[1:])

    message_id = (await bot.send_message(message.chat.id, f'❗️️<b>ВАЖНОЕ ОБЪЯВЛЕНИЕ</b> ❗️️\n\n{comments}\n\n▫️Объявил {moder_link}', parse_mode='html')).message_id
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    try:
        cursor.execute(f'SELECT tg_id FROM [{-(message.chat.id)}]')
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        await message.reply('Непредвиденная ошибка! обратитесь к админу этого бота: @zzoobank')
        return

    users_count = 0
    mentions = []
    for user in users:
        users_count += 1
        mentions.append(f'<a href="tg://user?id={user[0]}">&#x200b</a>')

    a = ''
    for r in range(users_count):
        a += mentions[r]
        print(a)
        print(r)
        if (r + 1) % 5 == 0 or r == users_count - 1:
            await bot.send_message(chat_id=message.chat.id, text=f'<b>⬆️Общи{a}й сбор ({(r // 6) + 1})</b>', parse_mode='html', reply_to_message_id=message_id)
            a = ''

    await bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)

@dp.message_handler(Text(startswith=['! ссылка клан'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def vagn_abavlenie(message):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id != 1240656726:
        return
    try:
        link = await bot.export_chat_invite_link(chat_id=klan)
        await message.answer(link)
    except aiogram.utils.exceptions.BadRequest:
        await message.answer('Нет прав')

@dp.message_handler(Text(startswith=['! ссылка состав 1'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def vagn_abavlenie(message):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id != 1240656726:
        return
    try:
        link = await bot.export_chat_invite_link(chat_id=sost_1)
        await message.answer(link)
    except aiogram.utils.exceptions.BadRequest:
        await message.answer('Нет прав')

@dp.message_handler(Text(startswith=['! ссылка состав 2'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def vagn_abavlenie(message):
    if message.chat.id != message.from_user.id:
        return
    if message.from_user.id != 1240656726:
        return
    try:
        link = await bot.export_chat_invite_link(chat_id=sost_2)
        await message.answer(link)
    except aiogram.utils.exceptions.BadRequest:
        await message.answer('Нет прав')

@dp.message_handler(Text(startswith=['! очс'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def dell_st(message):
    if message.from_user.id != 1240656726:
        return
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM states")
    connection.commit()
    await message.answer('Очищено')


@dp.message_handler()
async def get_username(message: types.Message):
    global is_auto_unmute
    global is_quests
    username = message.from_user.username
    user_id = int(message.from_user.id)
    # print(user_id, username, message.text)
    if message.chat.id not in chats:
        await message.answer('кыш')
        await bot.send_message(chat_id=1240656726,text= f'{message.from_user.username} | {message.text} | {message.chat.title}')
        return
    try:
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute(f'UPDATE [{-(sost_1)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        cursor.execute(f'UPDATE [{-(klan)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        cursor.execute(f'UPDATE [{-(sost_2)}] SET username = ? WHERE tg_id = ?', (username, user_id))
        cursor.execute(f'UPDATE [{1003101400599}] SET username = ? WHERE tg_id = ?', (username, user_id))
        now = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        cursor.execute(f'UPDATE [{-(message.chat.id)}] SET last_date = ? WHERE tg_id = ?', (now, user_id))
        cursor.execute(f'UPDATE [{-(message.chat.id)}] SET mess_count = mess_count+1 WHERE tg_id = ?', (user_id,))
        connection.commit()
        chat_mem = await bot.get_chat_members_count(chat_id=message.chat.id)
        try:
            cursor.execute(f'INSERT INTO count_users (chat_id, count) VALUES (?, ?)', (message.chat.id,chat_mem, ))
        except sqlite3.IntegrityError:
            cursor.execute(f'UPDATE count_users SET count = ? WHERE chat_id = ?', (message.chat.id,chat_mem))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute(f'INSERT INTO all_users (user_id, username) VALUES (?, ?)', (user_id, username))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.commit()
        cursor.execute(f'UPDATE all_users SET username = ? WHERE user_id = ?', (username, user_id))
        connection.commit()
    connection.commit()
    if is_auto_unmute == False:
        print('auto_unmute')
        await auto_unmute(message)
    if is_quests == False:
        print('quests')
        await quests_funk(message)
    if posting == False:
        print('posting')
        await shedul_posting(message)
    return username


async def shedul_posting(message):
    global posting
    posting = True
    while True:
        now_time = datetime.now().strftime("%H:%M:%S")
        await asyncio.sleep(1)
        if now_time == "00:00:00":
            connection = sqlite3.connect(main_path)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM states")
            connection.commit()
            global week_count
            if datetime.today().weekday() == 1:
                await bot.send_message(chat_id=-1003101400599, text=tuesday)
            if datetime.today().weekday() == 2:
                await bot.send_message(chat_id=-1003101400599, text=wednesday)
            if datetime.today().weekday() == 3:
                await bot.send_message(chat_id=-1003101400599, text=thursday)
            if datetime.today().weekday() == 4:
                await bot.send_message(chat_id=-1003101400599, text=friday)
            if datetime.today().weekday() == 5:
                await bot.send_message(chat_id=-1003101400599, text=saturday)
            if datetime.today().weekday() == 6:
                await bot.send_message(chat_id=-1003101400599, text=sunday)
            if datetime.today().weekday() == 0 and week_count == 1:
                await bot.send_photo(chat_id=-1003212045301, photo=open('photos/first_week.jpg', 'rb'), caption=first_monday)
                week_count += 1
            elif datetime.today().weekday() == 0 and week_count == 2:
                await bot.send_photo(chat_id=-1003101400599, photo=open('photos/second_week.jpg', 'rb'), caption=second_monday)
                week_count += 1
            elif datetime.today().weekday() == 0 and week_count == 3:
                await bot.send_photo(chat_id=-1003101400599, photo=open('photos/third_week.jpg', 'rb'), caption=third_monday)
                week_count += 1
            if week_count == 4:
                week_count = 1


if __name__ == "__main__":
    executor.start_polling(dp)