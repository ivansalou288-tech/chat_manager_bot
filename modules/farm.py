import random

from aiogram.types import ContentType, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from main.config import *

@dp.message_handler(Text(startswith=['фарма', 'ферма', 'раб раб работать'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def farm(message):
    user_id = message.from_user.id
    delta_bust = random.randint(3, 150)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        meshok_old = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        meshok_old = 0
    try:
        cursor.execute(f"SELECT last_date FROM farma WHERE user_id = ?", (user_id,))
        lst = datetime.strptime(cursor.fetchall()[0][0], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst
        print(delta)
        if delta > timedelta(hours=4):
            meshok_new = meshok_old + delta_bust
            cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_new, user_id))
            cursor.execute('UPDATE farma SET last_date = ? WHERE user_id = ?', (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), user_id))
            await message.answer(f'✅ <b>ЗАЧЁТ!</b> 🍊 +{delta_bust} eZ¢', parse_mode=ParseMode.HTML)
            connection.commit()
        else:
            delta = timedelta(hours=4) - delta
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
            await message.answer(f'❌<b>НЕЗАЧЕТ!</b> Фармить можно раз в 4 часа.\nСледующая добыча через {lst_date}', parse_mode=ParseMode.HTML)
    except IndexError:
        meshok_new = meshok_old + delta_bust
        cursor.execute('INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)', (user_id, meshok_new, datetime.now().strftime("%H:%M:%S %d.%m.%Y")))

        await message.answer(f'✅ <b>ЗАЧЁТ!</b> 🍊 +{delta_bust} eZ¢', parse_mode=ParseMode.HTML)
        connection.commit()


@dp.message_handler(Text(startswith=['мешок'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def mesh(message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        username = (message.text.split('@')[1]).split()[0]

    except IndexError:
        if not message.reply_to_message:
            user_id = message.from_user.id
            name_user = message.from_user.first_name
            username = message.from_user.username
        else:
            user_id = message.reply_to_message.from_user.id
            name_user = message.reply_to_message.from_user.first_name
            username = message.reply_to_message.from_user.username
    try:
        user_id = \
            cursor.execute(f"SELECT tg_id FROM [{-(message.chat.id)}] WHERE username=?", (username,)).fetchall()[0][0]
        name_user = \
            cursor.execute(f"SELECT nik FROM [{-(message.chat.id)}] WHERE username=?", (username,)).fetchall()[0][0]
    except IndexError:
        await message.reply(
            '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>) или ответь на сообщение нужного пользователя',
            parse_mode='html')
        return
    except UnboundLocalError:
        pass
    except sqlite3.OperationalError:
        return
    try:
        meshok_old = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        meshok_old = 0
    await message.answer(f'💰 В мешке <a href="https://t.me/{username}">{name_user}</a>: 🍊 {meshok_old}  eZ¢', parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@dp.message_handler(Text(startswith=['! перевести'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def mesh(message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    
    # if message.from_user.id == 1240656726:
    #     await message.answer('Я знаю тебя заставляют, по этому тебе не доступна эта функция')
    #     return

    user_id = await get_user_id(message)
    if user_id == False:
        await message.reply(
            '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',
            parse_mode='html')
        return
    self_id = message.from_user.id
    try:
        meshok_self = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (self_id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('Твой мешок пустой! Иди работай а потом переводи')
        return
    if meshok_self <100:
        await message.answer('Твой мешок пустой! Иди работай а потом переводи')
        return
    meshok_user = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]

    perev = 100

    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)
    message_id = (await bot.send_message(message.chat.id, text=f'💰 В твоем мешке: 🍊 {meshok_self}  eZ¢\nТвой перевод: {perev}',parse_mode='html', reply_markup=keyboard)).message_id
    try:
        cursor.execute('INSERT INTO perevod (self_id, user_id, mess_id, stavka) VALUES (?, ?, ?, ?)', (self_id,user_id, message_id, 100))
        connection.commit()
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE perevod SET stavka = ? WHERE self_id = ?', (100,self_id))
        connection.commit()
        cursor.execute('UPDATE perevod SET mess_id = ? WHERE self_id = ?', (message_id, self_id))
        connection.commit()
        cursor.execute('UPDATE perevod SET user_id = ? WHERE self_id = ?', (user_id, self_id))
        connection.commit()
    connection.commit()



@dp.callback_query_handler(text = 'pls_1000')
async def plus(call: types.CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+1000) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka+1000 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka+1000}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'min_1000')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-1000) < 100:
        await bot.answer_callback_query(call.id, text='перевод не может быть меньше 100')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka-1000 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)
    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka-1000}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'pls_50')
async def plus(call: types.CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+50000) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka+50000 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka+50000}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'min_50')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-50000) < 100:
        await bot.answer_callback_query(call.id, text='перевод не может быть меньше 100')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka-50000 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka-50000}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'pls_100')
async def plus(call: types.CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+100) > int(meshok):
        await bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka+100 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka+100}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'min_100')
async def minus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-100) < 100:
        await bot.answer_callback_query(call.id, text='перевод не может быть меньше 100')
        return
    cursor.execute('UPDATE perevod SET stavka = stavka-100 WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {stavka-100}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')

@dp.callback_query_handler(text = 'all_p')
async def plus(call: types.CallbackQuery):
    print(call.data)
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return

    cursor.execute('UPDATE perevod SET stavka = ? WHERE self_id = ?', (meshok, call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="pls_100")
    b = InlineKeyboardButton(text="-100", callback_data="min_100")
    f = InlineKeyboardButton(text="+1000", callback_data="pls_1000")
    g = InlineKeyboardButton(text="-1000", callback_data="min_1000")
    t = InlineKeyboardButton(text="+50k", callback_data="pls_50")
    y = InlineKeyboardButton(text="-50k", callback_data="min_50")
    c = InlineKeyboardButton(text="Перевести", callback_data="perev")
    d = InlineKeyboardButton(text="Все", callback_data="all_p")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(a, b).add(f, g).add(t, y).row(d).row(c)

    await call.message.edit_text(text=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвой перевод: {meshok}',parse_mode='html', reply_markup=keyboard)
    await bot.answer_callback_query(call.id, text='')


@dp.callback_query_handler(text = 'perev')
async def plus(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    user_id = cursor.execute('SELECT user_id FROM perevod WHERE self_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    self_id = call.from_user.id
    try:
        meshok_self = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (self_id,)).fetchall()[0][0]
    except IndexError:
        await call.message.answer('Твой мешок пустой! Иди работай а потом переводи')
        return
    meshok_user = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]

    perev = cursor.execute('SELECT stavka FROM perevod WHERE self_id = ? AND mess_id = ?',(call.from_user.id, call.message.message_id)).fetchall()[0][0]


    cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_user+perev, user_id))
    connection.commit()
    cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (meshok_self-perev, self_id))
    connection.commit()
    cursor.execute('DELETE FROM perevod WHERE self_id = ?', (call.from_user.id,))
    connection.commit()
    await call.message.delete()
    await bot.send_message(call.message.chat.id,text=f'Успешно',parse_mode='html')


