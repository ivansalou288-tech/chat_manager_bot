import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from password_generator import PasswordGenerator
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import asyncio
#from config import *
import sqlite3
from aiogram.utils.exceptions import *
from pyexpat.errors import messages
from telebot.apihelper import answer_web_app_query

from main.config import *
from path import Path

curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'
kasik_path = curent_path / 'databases' / 'kasik.db'



#? EN: Opens the casino (slot/dice) interface, letting user choose a bet from their farm bag with cooldown.
#* RU: Открывает интерфейс казика (слоты/кости), позволяя выбрать ставку из мешка фармы с кулдауном.
@dp.message_handler(Text(startswith=['! казик', '!казик'], ignore_case=True))  # Снятие преда
async def kasik(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])


    #  if message.from_user.id != 1240656726:
    #     return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    
    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = message.from_user.id
    try:
        cursor.execute(f"SELECT last_date FROM stavki WHERE user_id = ?", (user_id,))
        lst = datetime.strptime(cursor.fetchall()[0][0], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        print(now, lst)
        delta = now - lst
        print(delta, timedelta(minutes = 15))
        if delta > timedelta(minutes = 15):
            pass
        else:
            delta = timedelta(minutes = 15) - delta
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
            await message.answer(f'❌Можно играть в казик только раз в 15 минут. Следующий деп через {lst_date}', parse_mode=ParseMode.HTML)
            return
    except IndexError:
        pass

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = message.from_user.id
    try:
        meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('Твой мешок пустой! Иди работай а потом депай')
        return
    if int(meshok)<100:
        await message.answer('Твой мешок пустой! Иди работай а потом депай')
        return
    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    stavka = 100
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    message_id = (await bot.send_photo(message.chat.id,photo=open(f'{curent_path}/photos/dep.jpg', 'rb'), caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka}', parse_mode='html', reply_markup=keyboard)).message_id
    try:
        cursor.execute('INSERT INTO stavki (user_id, mess_id, stavka, last_date) VALUES (?, ?, ?, ?)', (user_id, message_id, 100,  datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
        connection.commit()
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE stavki SET stavka = ? WHERE user_id = ?', (100, user_id))
        connection.commit()
        cursor.execute('UPDATE stavki SET mess_id = ? WHERE user_id = ?', (message_id, user_id))
        connection.commit()
        cursor.execute('UPDATE stavki SET last_date = ? WHERE user_id = ?', (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), user_id))
        connection.commit()
    connection.commit()


#? EN: Increases the casino bet by 1000 eZ¢ (if user has enough coins).
#* RU: Увеличивает ставку в казике на 1000 eZ¢ (если у пользователя хватает монет).
@dp.callback_query_handler(text = 'plus1')
async def plus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+1000) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+1000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+1000}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 1000 eZ¢ but not below the minimum (100).
#* RU: Уменьшает ставку в казике на 1000 eZ¢, но не ниже минимальной (100).
@dp.callback_query_handler(text = 'minus1')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-1000) < 100:
        await bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-1000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-1000}', parse_mode='html', reply_markup=keyboard)

#? EN: Increases the casino bet by 10 000 eZ¢ (big step).
#* RU: Увеличивает ставку в казике на 10 000 eZ¢ (крупный шаг).
@dp.callback_query_handler(text = 'plus5')
async def plus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+10000) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+10000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+10000}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 10 000 eZ¢ but not below 100.
#* RU: Уменьшает ставку в казике на 10 000 eZ¢, но не ниже 100.
@dp.callback_query_handler(text = 'minus5')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-10000) < 100:
        await bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-10000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-10000}', parse_mode='html', reply_markup=keyboard)



#? EN: Increases the casino bet by 100 eZ¢ (small step).
#* RU: Увеличивает ставку в казике на 100 eZ¢ (малый шаг).
@dp.callback_query_handler(text = 'plus')
async def plus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+100) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+100 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+100}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 100 eZ¢ but not below 100.
#* RU: Уменьшает ставку в казике на 100 eZ¢, но не ниже 100.
@dp.callback_query_handler(text = 'minus')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-100) < 100:
        await bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-100 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-100}', parse_mode='html', reply_markup=keyboard)

#? EN: Sets the casino bet to the user’s entire bag balance (All-In).
#* RU: Устанавливает ставку в казике равной всему балансу мешка пользователя (All-In).
@dp.callback_query_handler(text = 'all_in')
async def all_in(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return

    cursor.execute('UPDATE stavki SET stavka = ? WHERE user_id = ?', (meshok, call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)
    try:
        await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {meshok}', parse_mode='html', reply_markup=keyboard)
    except MessageNotModified:
        return


#? EN: Rolls Telegram dice, resolves the casino game and updates user’s bag based on win/lose result.
#* RU: Бросает телеграм‑кубик, определяет исход игры в казике и обновляет мешок пользователя по результату.
@dp.callback_query_handler(text = 'dep')
async def dep(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?',(call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return

    res = (await bot.send_dice(call.message.chat.id))['dice']['value']
    await call.message.delete()
    if res <=4:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)-int(stavka), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await bot.send_photo(call.message.chat.id, photo=open(f'{curent_path}/photos/proig.jpg', 'rb'),caption=f'Ты проиграл! повезет в следущий раз! \n\n💰 В твоем мешке теперь: 🍊 {int(meshok)-int(stavka)}  eZ¢\nТвоя ставка: {stavka}', parse_mode='html')
        return
    if res == 5:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)+int(stavka), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await bot.send_photo(call.message.chat.id, photo=open(f'{curent_path}/photos/win.jpg', 'rb'),caption=f'🎉Ты выиграл! И получил Х2 к своей ставке\n💰 В твоем мешке теперь: 🍊 {int(meshok)+int(stavka)}  eZ¢\n🎄Твоя ставка: {stavka}', parse_mode='html')
        return

    if res == 6:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)+(2 * int(stavka)), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await bot.send_photo(call.message.chat.id, photo=open(f'{curent_path}/photos/win.jpg', 'rb'),caption=f'🎉Ты выиграл! И получил Х3 к своей ставке\n💰 В твоем мешке теперь: 🍊 {int(meshok)+2*(int(stavka))}  eZ¢\n🎄Твоя ставка: {stavka}', parse_mode='html')
        return

if __name__ == "__main__":
    executor.start_polling(dp)