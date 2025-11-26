import aiogram
import random
import telebot
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
#from config import *
import sqlite3
from aiogram.utils.exceptions import *
from utils import CopyTextButton

all_users = "@EzhikNaZame @TurboSonicc @prostiname @admnpg @werty_pub"


token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
api_id =21842840
api_hash ="1db0b6e807c90e6364287ad8af7fa655"
connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
cursor = connection.cursor()
logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])
klan_chat_id = klan
first_monday = "Доброе утром замы! \n Сегодня первая неделя цикла, а значит у Нейма(@prostiname) 3 проверки на недели"
second_monday = "Доброе утром замы! \n Сегодня вторая неделя цикла, а значит у Соника(@TurboSonicc) 3 проверки на недели"
third_monday ="Доброе утром замы! \n Сегодня вторая неделя цикла, а значит у Ежика(@EzhikNaZAME) 3 проверки на недели"
tuesday="Всем замам, Доброе утро! \nСегодня вторник, проверку делает Ежик(@EzhikNaZAME)"
wednesday="Всем замам, Доброе утро! \nСегодня среда, проверку делает Нейм(@prostiname), на подстраховке Ежик(@EzhikNaZAME)"
thursday="Всем замам, Доброе утро! \nСегодня четверг, проверку делает Ежик(@EzhikNaZAME)"
friday="Всем замам, Доброе утро! \nСегодня пятница, проверку делает Соник(@TurboSonicc), на подстраховке Ежик(@EzhikNaZAME)"
saturday="Всем замам, Доброе утро! \nСегодня суббота, проверку делает Нейм(@prostiname), на подстраховке Соник(@TurboSonicc) и Ежик(@EzhikNaZAME)"
sunday="Всем замам, Доброе утро! \nСегодня воскресенье, проверку делает Соник(@TurboSonicc), на подстраховке Ежик(@EzhikNaZAME) и Нейм(@prostiname)"

can_recommend_users = [8015726709, 1401086794, 1240656726, 5714854312, 1803851598]
can_snat_recommend_users = [8015726709, 1401086794, 1240656726]
week_count = 1
posting = False
bot = Bot(token=token)
dp = Dispatcher(bot)
is_auto_unmute = False
is_quests = False
page = 0
mes_id = 0
itog = []
page_c = 0
async def recom_check_sdk(tg_id, name_user):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    moder_gives = []
    moder_rang = []
    comments = []
    rang = []
    date = []
    itog = []
    all = cursor.execute('SELECT * FROM recommendation WHERE user_id = ?', (tg_id,)).fetchall()
    print(all)
    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    recommendation_count = 0
    for i in all:
        recommendation_count += 1


    for i in range(recommendation_count):
        moder_gives.append(all[i][2])

    for i in range(recommendation_count):
        comments.append(all[i][3])

    for i in range(recommendation_count):
        rang.append(all[i][4])

    for i in range(recommendation_count):
        date.append(all[i][5])

    for moder in moder_gives:
        id = int(moder)
        rang_m = cursor.execute(f"SELECT rang FROM [{-(sost_1)}] WHERE tg_id=?", (id,)).fetchall()[0][0]
        moder_rang.append(rangs_name[rang_m])

    for i in range(recommendation_count):
        name_mod = cursor.execute(f"SELECT nik FROM [{-(sost_1)}] WHERE tg_id=?", (int(moder_gives[i]),)).fetchall()[0][0]

        textt = f'🟢 <b>{i+1}</b>. От <a href="tg://user?id={moder_gives[i]}">{name_mod}</a> | Должность: {moder_rang[i]}\n<b>&#8195Чем отличился:</b> {comments[i]}\n<b>&#8195Рекомендован на:</b> {rang[i]}\n<b>&#8195Дата рекомендации: {date[i]}</b>'
        itog.append(textt)
    text = '\n\n'.join(itog)
    if text == '':
        text = f'📝Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют'
    else:
        text = f'📝Рекомендации <a href="tg://user?id={tg_id}">{name_user}</a>:\n\n{text}'
    return text


async def quests_funk(message: types.Message):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
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
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')
            if datetime.today().weekday() == 2:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[1]}', parse_mode='html')
            if datetime.today().weekday() == 3:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')
            if datetime.today().weekday() == 4:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ДНЯ</b>❗️\n\n{quests[2]}', parse_mode='html')
            if datetime.today().weekday() == 5:
                await bot.send_message(klan, f'❗️<b>КВЕСТ ПРОШЛОГО ДНЯ ЗАКОНЧЕН</b>❗️\n\n💬Ждите следующего квеста', parse_mode='html')

async def warn_check_sdk(tg_id, chat_id, name_user):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{-(chat_id)}] WHERE tg_id=?", (tg_id,))
    try:
        warns = cursor.fetchall()[0]
        warns_count = warns[1]
        first_warn = warns[2]
        second_warn = warns[3]
        therd_warn = warns[4]
        first_mod = warns[5]
        second_mod = warns[6]
        therd_mod = warns[7]
        if first_warn == None or first_warn == 'None':
            first_warn = ''
        if second_warn == None or second_warn == 'None':
            second_warn = ''
        if therd_warn == None or therd_warn == 'None':
            therd_warn = ''
        print(warns_count, first_warn, second_warn, therd_warn, end='\n')

        if warns_count == 0:
            text = f'<b>❕Предупреждения</b> <a href="tg://user?id={tg_id}">{name_user}</a> отсутсвуют! Поздравляем!'

            return text
        if warns_count == 1:
            print(2222)
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} из 3 предупреждения\n\n🔺 1. От {first_mod}:\n&#8195&#8194Причина: {first_warn}'

            return text
        if warns_count == 2:
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} из 3 предупреждения\n\n🔺 1. От {first_mod}:\n&#8195&#8194Причина: {first_warn}\n\n🔺 2. От {second_mod}:\n&#8195&#8194Причина: {second_warn}'

            return text
        if warns_count == 3:
            text = f'❕Пользователь <a href="tg://user?id={tg_id}">{name_user}</a> имеет {warns_count} из 3 предупреждений\n\n🔺 1. От {first_mod}:\n&#8195&#8194Причина: {first_warn}\n\n🔺 2. От {second_mod}:\n&#8195&#8194Причина: {second_warn}\n\n🔺 3. От {therd_mod}:\n&#8195&#8194Причина: {therd_warn}'

            return text
    except IndexError:
        text = f'<b>❕Предупреждения <a href="tg://user?id={tg_id}">{name_user}</a> отсутвуют! Поздравляем!</b>'
        return text

async def about_user_sdk(user_id, chat_id):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{-(chat_id)}] WHERE tg_id=?", (user_id,))
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

    # Выводим в нормальном формате описание

    rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                  'Владелец')
    print(rangs_name[4])
    sm = "⭐️"
    stars = ""
    for i in range(int(user_about['rang'])):
        stars += sm
    text = f"{stars} [{user_about['rang']}] Ранг: <b>{rangs_name[user_about['rang']]}</b>\n<b>Имя: </b>{user_about['name']}\n<b>Возраст:</b> {user_about['age']}\n<b>Игровой Ник:</b> {user_about['nik_pubg']}\n<b>Игровой айди:</b> <code>{user_about['id_pubg']}</code>"
    return text

async def pravila_sdk(message):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    text = f"🗓<b>Правила чата</b>\n\n{cursor.execute(f'SELECT text FROM pravils WHERE chat_id=?', (message.chat.id,)).fetchall()[0][0]}"
    return text

async def shedul_posting(message):
    global posting
    posting = True
    while True:
        now_time = datetime.now().strftime("%H:%M:%S")
        await asyncio.sleep(1)
        if now_time == "00:00:00":
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

async def snat_warn(user_id, number_warn, warn_count_new, message):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    num_list = ['nul', 'first', 'second', 'therd']
    number_warn_dell = f'{num_list[number_warn]}_warn'
    number_moder = f'{num_list[number_warn]}_moder'
    try:
        text = cursor.execute(f'SELECT {number_warn_dell} FROM [{-(message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    except IndexError:
        return
    moder = cursor.execute(f'SELECT {number_moder} FROM [{-(message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET warns_count = ? WHERE tg_id = ?',
                   (warn_count_new, user_id))
    connection.commit()
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET {number_warn_dell} = ? WHERE tg_id = ?',
                   (None, user_id))
    connection.commit()
    cursor.execute(f"SELECT * FROM [{-(message.chat.id)}] WHERE tg_id=?", (user_id,))
    connection.commit()
    warns = cursor.fetchall()[0]

    first_warn = warns[2]
    second_warn = warns[3]
    therd_warn = warns[4]
    first_mod = warns[5]
    second_mod = warns[6]
    therd_mod = warns[7]

    if number_warn == 1:
        first_warn = second_warn
        second_warn = therd_warn
        therd_warn = None
        first_mod = second_mod
        second_mod = therd_mod
        therd_mod = None
    if number_warn == 2:
        second_warn = therd_warn
        therd_warn = None
        second_mod = therd_mod
        therd_mod = None
    number_warn_dell = f'{num_list[number_warn]}_warn'
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET first_warn = ? WHERE tg_id = ?',
                   (first_warn, user_id))
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET second_warn = ? WHERE tg_id = ?',
                   (second_warn, user_id))
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET therd_warn = ? WHERE tg_id = ?',(therd_warn, user_id))
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET first_moder = ? WHERE tg_id = ?',
                   (first_mod, user_id))
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET second_moder = ? WHERE tg_id = ?',
                   (second_mod, user_id))
    cursor.execute(f'UPDATE [{-(message.chat.id)}] SET therd_moder = ? WHERE tg_id = ?',
                   (therd_mod, user_id))
    connection.commit()

    cursor.execute(f'INSERT INTO [{-(message.chat.id)}snat] (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)', (user_id, text, moder, message.from_user.get_mention(as_html=True)))
    connection.commit()

async def is_successful_moder(moder_id, chat_id, command):
    global klan_chat_id
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    try:
        rang_moder = cursor.execute(f"SELECT rang FROM [{-(chat_id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    except IndexError:
        return 'Need reg'
    except sqlite3.OperationalError:
        return 'chat error'
    if chat_id == klan_chat_id:
        command_dk = int(cursor.execute("SELECT dk FROM klan WHERE comand=?", (command,)).fetchall()[0][0])
    else:
        command_dk = int(cursor.execute("SELECT dk FROM sostav WHERE comand=?", (command,)).fetchall()[0][0])
    if rang_moder < command_dk:
        return False
    else:
        return True

async def is_more_moder(user_id, moder_id, chat_id):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    rang_moder = cursor.execute(f"SELECT rang FROM [{-(chat_id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    try:
        first_rang_user = cursor.execute(f"SELECT rang FROM [{-(chat_id)}] WHERE tg_id=?",(user_id,)).fetchall()[0][0]
    except IndexError:
        if user_id == 8451829699:
            return False
        else:
            first_rang_user = 0

    if first_rang_user >= rang_moder:
        return False
    else:
        return True

async def give_warn(message, comments, warn_count_new, user_id, is_first):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    num_list = ['nul', 'first', 'second', 'therd']
    number_warn = f'{num_list[warn_count_new]}_warn'
    number_moder = f'{num_list[warn_count_new]}_moder'
    if is_first == False:
        cursor.execute(f'UPDATE [{-(message.chat.id)}] SET warns_count = ? WHERE tg_id = ?', (warn_count_new, user_id))
        cursor.execute(f'UPDATE [{-(message.chat.id)}] SET {number_warn} = ? WHERE tg_id = ?', (comments, user_id))
        cursor.execute(f'UPDATE [{-(message.chat.id)}] SET {number_moder} = ? WHERE tg_id = ?', (message.from_user.get_mention(as_html=True), user_id))
    else:
        cursor.execute(f'INSERT INTO [{-message.chat.id}] VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user_id,warn_count_new, comments, '', '', message.from_user.get_mention(as_html=True), '', ''))


    connection.commit()

async def limit_warns(message):
    buttons = [
        types.InlineKeyboardButton(text="Бан", callback_data="banFromPred"),
        types.InlineKeyboardButton(text="Снять пред", callback_data="snat_pred")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.reply(f'❗Достигнут лимит предупреждений\n\nЧто делать с пользователем?', reply_markup=keyboard)

@dp.callback_query_handler(text = 'banFromPred')
async def ban_from_pred(call: types.CallbackQuery):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    user_id = cursor.execute(f'SELECT tg_id FROM [{-(call.message.chat.id)}] WHERE warns_count = ?', (3,)).fetchall()[0][0]
    moder_pred_id = cursor.execute(f'SELECT therd_moder FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    a = moder_pred_id.split('<a href="tg://user?id=')[1].split('">')[0]
    print(a)
    print(call.from_user.id)
    if int(call.from_user.id) == int(a):
        connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
        cursor = connection.cursor()
        name_narush = cursor.execute(f"SELECT nik FROM [{-(call.message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        # await bot.answer_callback_query(call.id,text='Бан', show_alert=True)
        user_men = f'<a href="tg://user?id={user_id}">{name_narush}</a>'
        moder_men = call.message.from_user.get_mention(as_html=True)
        message_id = (call.message.message_id) + 1

        comments = 'Достигнут лимит предупреждений'
        await ban_user(user_id, call.message.chat.id, user_men, moder_men, comments, message_id, call.message)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.send_message(call.message.chat.id,
            f'<b>❗️Внимание❗️</b>\n🔴Злостный нарушитель <a href="tg://user?id={user_id}">{name_narush}</a> Получил достиг лимита предупреждений, получает бан и покидает нас\n👮‍♂Решение принял: {call.from_user.get_mention(as_html=True)}',
            parse_mode='html')
        connection = sqlite3.connect('warn_list.db', check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,))
        connection.commit()
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)
        return

@dp.callback_query_handler(text = "snat_pred")
async def snat_pred(call: types.CallbackQuery):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    user_id = \
    cursor.execute(f'SELECT tg_id FROM [{-(call.message.chat.id)}] WHERE warns_count = ?', (3,)).fetchall()[0][0]
    moder_pred_id = \
    cursor.execute(f'SELECT therd_moder FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    a = moder_pred_id.split('<a href="tg://user?id=')[1].split('">')[0]
    print(a)
    print(call.from_user.id)
    if int(call.from_user.id) == int(a):
        # await bot.answer_callback_query(call.id,text='Снять пред', show_alert=True)
        buttons = [
            types.InlineKeyboardButton(text="1", callback_data="1warn"),
            types.InlineKeyboardButton(text="2", callback_data="2warn"),
            types.InlineKeyboardButton(text="3", callback_data="3warn")
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(*buttons)
        await bot.send_message(call.message.chat.id, 'Номер предупреждения который нужно снять:', reply_markup=keyboard)
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)
        return
@dp.callback_query_handler(text = "1warn")
async def warn_1(call: types.CallbackQuery):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    user_id = cursor.execute(f'SELECT tg_id FROM [{-(call.message.chat.id)}] WHERE warns_count = ?', (3,)).fetchall()[0][0]
    moder_pred_id = cursor.execute(f'SELECT therd_moder FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    a = moder_pred_id.split('<a href="tg://user?id=')[1].split('">')[0]

    if int(call.from_user.id) == int(a):
        connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
        cursor = connection.cursor()
        name_narush = cursor.execute(f"SELECT nik FROM [{-(call.message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=1, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id, f'✅<a href="tg://user?id={user_id}">{name_narush}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {call.from_user.get_mention(as_html=True)}\n💬Сняли тебе первое предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»', parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)

@dp.callback_query_handler(text = "2warn")
async def warn_2(call: types.CallbackQuery):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    user_id = \
    cursor.execute(f'SELECT tg_id FROM [{-(call.message.chat.id)}] WHERE warns_count = ?', (3,)).fetchall()[0][0]
    moder_pred_id = \
    cursor.execute(f'SELECT therd_moder FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    a = moder_pred_id.split('<a href="tg://user?id=')[1].split('">')[0]

    if int(call.from_user.id) == int(a):
        connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
        cursor = connection.cursor()
        name_narush = \
        cursor.execute(f"SELECT nik FROM [{-(call.message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=2, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id,
                               f'✅<a href="tg://user?id={user_id}">{name_narush}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {call.from_user.get_mention(as_html=True)}\n💬Сняли тебе первое предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
                               parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)

@dp.callback_query_handler(text = "3warn")
async def warn_3(call: types.CallbackQuery):
    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    user_id = \
    cursor.execute(f'SELECT tg_id FROM [{-(call.message.chat.id)}] WHERE warns_count = ?', (3,)).fetchall()[0][0]
    moder_pred_id = \
    cursor.execute(f'SELECT therd_moder FROM [{-(call.message.chat.id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    a = moder_pred_id.split('<a href="tg://user?id=')[1].split('">')[0]

    if int(call.from_user.id) == int(a):
        connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
        cursor = connection.cursor()
        name_narush = \
        cursor.execute(f"SELECT nik FROM [{-(call.message.chat.id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await snat_warn(user_id=user_id, number_warn=3, warn_count_new=2, message=call.message)
        await bot.send_message(call.message.chat.id,
                               f'✅<a href="tg://user?id={user_id}">{name_narush}</a>, тебя помиловали, теперь количество твоих предупреждений: 2 из 3\n👮‍♂️Помиловал: {call.from_user.get_mention(as_html=True)}\n💬Сняли тебе первое предупреждение\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»',
                               parse_mode='html')
    else:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали', show_alert=True)

def firstSeen(tg_id, message):

    connection = sqlite3.connect('warn_list.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT tg_id FROM [{-(message.chat.id)}] WHERE tg_id=?", (tg_id,))
    rez = cursor.fetchall()
    if not rez:
        return True
    else:
        return False

async def insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    try:
        pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(chat_id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        pubg_id = 'неизвестен'
    date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    try:
        cursor.execute(f'INSERT INTO [{-(chat_id)}bans] (tg_id, id_pubg, message_id, prichina, date, user_men, moder_men) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, pubg_id, message_id, comments, date, user_men, moder_men))
    except sqlite3.IntegrityError:
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET id_pubg = ? WHERE tg_id = ?', (pubg_id, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET message_id = ? WHERE tg_id = ?', (message_id, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET prichina = ? WHERE tg_id = ?', (comments, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET date = ? WHERE tg_id = ?', (date, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET user_men = ? WHERE tg_id = ?', (user_men, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET moder_men = ? WHERE tg_id = ?', (moder_men, user_id))
    connection.commit()

async def mute_user(user_id, chat_id, muteint, mutetype, message, comments):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    if mutetype == "ч" or mutetype == "часов" or mutetype == "час" or mutetype == "часа":
        dt = datetime.now() + timedelta(hours=int(muteint))
        timestamp = dt.timestamp()
    elif mutetype == "м" or mutetype == "минут" or mutetype == "минуты" or mutetype == "минута":
        dt = datetime.now() + timedelta(minutes=int(muteint))
        timestamp = dt.timestamp()
    elif mutetype == "д" or mutetype == "дней" or mutetype == "день" or mutetype == "дня":
        dt = datetime.now() + timedelta(days=int(muteint))
        timestamp = dt.timestamp()
    elif mutetype == comments:
        dt = datetime.now() + timedelta(hours=int(muteint))
        timestamp = dt.timestamp()
    date = dt.strftime('%H:%M:%S %d.%m.%Y')
    try:
        await bot.restrict_chat_member(chat_id, user_id,
                                       permissions=ChatPermissions(can_send_messages=False),
                                       until_date=timestamp)
        moder_id = message.from_user.id
        moder_men = message.from_user.get_mention(as_html=True)
        rang_moder = cursor.execute(f"SELECT rang FROM [{-(chat_id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
        try:

            rang_f_moder = cursor.execute(f'SELECT rang_moder FROM muts WHERE user_id=? AND chat_id = ?', (user_id, chat_id,)).fetchall()[0][0]
            if rang_f_moder > rang_moder:
                rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                              'Менеджер',
                              'Владелец')
                text = f'📝 Ранг модератора не достаточен для перевыдачи мута. Обратитесь к модератору рангом от {rang_f_moder}+ ({rangs_name[rang_f_moder]})'
                return text
            cursor.execute(f'UPDATE muts SET rang_moder = ? WHERE user_id = ? AND chat_id = ?',
                           (rang_moder, user_id, chat_id))
            cursor.execute(f'UPDATE muts SET moder_id = ? WHERE user_id = ? AND chat_id = ?', (moder_id, user_id, chat_id))
            cursor.execute(f'UPDATE muts SET moder_men = ? WHERE user_id = ? AND chat_id = ?',
                           (moder_men, user_id, chat_id))
            cursor.execute(f'UPDATE muts SET date = ? WHERE user_id = ? AND chat_id = ?', (date, user_id, chat_id))
            cursor.execute(f'UPDATE muts SET comments = ? WHERE user_id = ? AND chat_id = ?', (comments, user_id, chat_id))
        except IndexError:
            cursor.execute(
                f'INSERT INTO muts (chat_id, user_id, rang_moder, moder_id, moder_men, date, comments) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (chat_id, user_id, rang_moder, moder_id, moder_men, date, comments))

        connection.commit()
        return True
    except UserIsAnAdministratorOfTheChat:
        await message.reply(
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата',
            parse_mode='html')
        return False
    except CantRestrictChatOwner:
        await message.reply(
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Владельцем этого чата',
            parse_mode='html')
        return False

async def unmute_user(user_id, chat_id, message):
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    try:
        rang_f_moder = cursor.execute(f'SELECT rang_moder FROM muts WHERE user_id = ? AND chat_id = ?', (user_id, chat_id)).fetchall()[0][0]
    except IndexError:
        text = '🗓 Пользователь не лишён свободы слова'
        return text
    moder_id = message.from_user.id
    rang_moder = cursor.execute(f"SELECT rang FROM [{-(chat_id)}] WHERE tg_id=?", (moder_id,)).fetchall()[0][0]
    if rang_f_moder > rang_moder:
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель',
                      'Менеджер',
                      'Владелец')
        text = f'📝 Ранг модератора не достаточен для размута. Обратитесь к модератору рангом от {rang_f_moder}+ ({rangs_name[rang_f_moder]})'
        return text
    await bot.restrict_chat_member(chat_id, user_id,
                                   permissions=ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                                               can_send_photos=True, can_send_videos=True,
                                                               can_send_audios=True, can_send_documents=True,
                                                               can_send_other_messages=True,
                                                               can_send_video_notes=True, can_send_voice_notes=True,
                                                               can_pin_messages=True,
                                                               can_add_web_page_previews=True, can_send_polls=True))
    cursor.execute(f'DELETE FROM muts WHERE user_id = ? AND chat_id = ?', (user_id, chat_id, ))
    connection.commit()
    return True


async def ban_user(user_id, chat_id, user_men, moder_men, comments, message_id, message):
    try:
        await bot.ban_chat_member(chat_id, user_id)
        # connection = sqlite3.connect('warn_list.db', check_same_thread=False)
        # cursor = connection.cursor()
        # cursor.execute(f'DELETE FROM [{-(chat_id)}] WHERE tg_id = ?', (user_id,))
        # connection.commit()
        await snat_warn(user_id, 3, 2, message)
        await snat_warn(user_id, 2, 1, message)
        await snat_warn(user_id, 1, 0, message)
        await insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id)
        return True
    except UserIsAnAdministratorOfTheChat:
        await bot.send_message(chat_id,
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата',
            parse_mode='html')
        return False
    except CantRestrictChatOwner:
        await bot.send_message(chat_id,
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Владельцем этого чата',
            parse_mode='html')
        return False


async def unban_user(chat_id,user_id):
    await bot.unban_chat_member(chat_id, user_id)
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'DELETE FROM [{-(chat_id)}bans] WHERE tg_id = ?', (user_id,))
    connection.commit()
async def kick_user(user_id, chat_id):
    try:
        await bot.kick_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)
        return True
    except UserIsAnAdministratorOfTheChat:
        await bot.send_message(chat_id,
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Телеграм-админом этого чата',
            parse_mode='html')
    except CantRestrictChatOwner:
        await bot.send_message(chat_id,
            f'👨🏻‍🔧 <a href="tg://user?id={user_id}">Пользователь</a> является Владельцем этого чата',
            parse_mode='html')
