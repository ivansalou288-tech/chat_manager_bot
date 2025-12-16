from admin_config import *
@dp.callback_query_handler(text="recommend_check")
async def recommend_check(call: types.CallbackQuery):
    if call.from_user.id in can_recommend_users:
        await recommend(call)
        return
    else:
        await bot.answer_callback_query(call.id, text='⚠️Тебе не доступна эта функция')
        return


@dp.callback_query_handler(text="recommend")
async def recommend(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    await call.message.delete()
    await bot.send_message(call.message.chat.id, 'Напиши юзернейм или айди в пабге того кого хочешь рекомендовать')
    try:
        cursor.execute('INSERT INTO dinamic_admn_recommend (user_id, is_do) VALUES (?, ?)', (call.from_user.id, True))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE dinamic_admn_recommend SET is_do = ? WHERE user_id = ?", (True, call.from_user.id,))
    connection.commit()


@dp.callback_query_handler(text="not_successful_user")
async def not_successful_user(call: types.CallbackQuery):
    try:
        await bot.delete_message(call.message.chat.id, (call.message.message_id)-1)
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        pass
    await recommend(call)


@dp.callback_query_handler(text="successful_user")
async def successful_user(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    try:
        cursor.execute('INSERT INTO dinamic_admn_recommend (user_id, is_do) VALUES (?, ?)', (call.from_user.id, True))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE dinamic_admn_recommend SET is_do = ? WHERE user_id = ?", (True, call.from_user.id,))
    connection.commit()
    await call.message.delete()
    await bot.delete_message(call.message.chat.id, (call.message.message_id) - 1)
    await call.message.answer('Напиши чем отличился данный игрок в формате: \n\n<code>Причина:</code> убил 35 паков в соло', parse_mode='html')

@dp.message_handler(Text(startswith="Причина:", ignore_case=True))
async def comments_recom(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        is_do = cursor.execute(f"SELECT is_do FROM dinamic_admn_recommend WHERE user_id=?", (message.from_user.id,)).fetchall()[0][0]
    except IndexError:
        return
    if is_do != True:
        return
    date = datetime.now().strftime('%d.%m.%Y')
    comments = message.text.split('Причина:')[1]
    moder = message.from_user.id
    cursor.execute(f"UPDATE din_admn_user_data SET comments = ? WHERE moder = ?", (comments, moder))
    connection.commit()
    print('------------------')
    print(comments)
    print(message.text.split('Причина:'))
    await bot.delete_message(message.chat.id, (message.message_id) - 1)
    await bot.delete_message(message.chat.id, message.message_id)
    await message.answer('Принято! Теперь напиши на кого ты его рекомендуешь в формате: \n\n<code>Рекомендую на:</code> тест отв', parse_mode='html')

@dp.message_handler(Text(startswith="Рекомендую на:", ignore_case=True))
async def rang_recom(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        is_do = cursor.execute(f"SELECT is_do FROM dinamic_admn_recommend WHERE user_id=?", (message.from_user.id,)).fetchall()[0][0]
    except IndexError:
        return
    if is_do != True:
        return
    cursor.execute(f"UPDATE dinamic_admn_recommend SET is_do = ? WHERE user_id = ?", (False, message.from_user.id,))
    connection.commit()
    comments = message.text.split('Рекомендую на:')[1]
    moder = message.from_user.id
    cursor.execute(f"UPDATE din_admn_user_data SET rang = ? WHERE moder = ?", (comments, moder))
    connection.commit()
    await bot.delete_message(message.chat.id, (message.message_id) - 1)
    await bot.delete_message(message.chat.id, message.message_id)
    all = cursor.execute('SELECT * FROM din_admn_user_data WHERE moder = ?', (moder,)).fetchall()[0]
    user_id = all[0]
    pubg_id = all[1]
    moder = all[2]
    comments = all[3]
    rang = all[4]
    date = all[5]


    buttons = [
        types.InlineKeyboardButton(text="Верно", callback_data="successful_recom"),
        types.InlineKeyboardButton(text="Не правильно", callback_data="not_successful_user"),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    connection.commit()

    await message.answer(
        f'Рекомендация <a href="tg://user?id={user_id}">Пользователя</a>:\n\n🟢 <b>1</b>. От {moder}:\n<b>&#8195Чем отличился:</b> {comments}\n<b>&#8195Рекомендован на:</b> {rang}',
        parse_mode='html', reply_markup=keyboard)

@dp.message_handler()
async def user_get(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    date = datetime.now().strftime('%d.%m.%Y')
    try:
        is_do = cursor.execute(f"SELECT is_do FROM dinamic_admn_recommend WHERE user_id=?", (message.from_user.id,)).fetchall()[0][0]
        print(is_do)
    except IndexError:
        return
    if is_do != 1:
        if is_do != 11:
            return
    await bot.delete_message(message.chat.id, (message.message_id) - 1)
    cursor.execute(f"UPDATE dinamic_admn_recommend SET is_do = ? WHERE user_id = ?", (0, message.from_user.id,))
    connection.commit()
    try:
        pubg_id = int(message.text)
        user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        nik_pubg = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        username = cursor.execute(f"SELECT username FROM [{-(klan)}] WHERE id_pubg=?", (pubg_id,)).fetchall()[0][0]
        if username == None:
            username = 'отсутвует'
    except ValueError:

        try:
            username = (message.text.split('@')[1]).split()[0]
            user_id = cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
            nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
            nik_pubg = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
            pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
        except IndexError:
                await message.reply(
                    '📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>) или напиши игровой айди пользователя',
                    parse_mode='html')
                return

    if is_do == 1:
            await recom_user_check(message=message, user_id=user_id, pubg_id=pubg_id, date=date, nik_pubg=nik_pubg, nik=nik, username=username)
    if is_do == 11:
            await recommend_snat_2_step(message, user_id)

@dp.callback_query_handler(text="successful_recom")
async def successful_recom(call: types.CallbackQuery):
    await call.message.edit_text('✅Рекомендация заполнена')
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    moder = call.from_user.id
    all = cursor.execute('SELECT * FROM din_admn_user_data WHERE moder = ?', (moder,)).fetchall()[0]


    user_id = all[0]
    pubg_id = all[1]
    moder = all[2]
    comments = all[3]
    rang = all[4]
    date = all[5]
    pwo = PasswordGenerator()
    id_recom = pwo.shuffle_password('ASDFGHJKL12345678', 8)
    moder = call.from_user.id
    cursor.execute(
        'INSERT INTO recommendation (user_id, pubg_id, moder, comments, rang, date, recom_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (user_id, pubg_id, moder, comments, rang, date, id_recom))



    connection.commit()

    cursor.execute('DELETE FROM din_admn_user_data WHERE moder = ?', (moder,))
    connection.commit()

async def recom_user_check(message, user_id, pubg_id, date, nik_pubg, nik, username):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    if user_id == message.from_user.id:
        await message.reply('📝Жулик, не рекомендуй!\n\n💬<i>Нельзя рекомендовать самого себя</i>', parse_mode='html')
        return
    moder_men = message.from_user.id
    users_idss = cursor.execute(f"SELECT user_id FROM recommendation WHERE moder=?", (moder_men,)).fetchall()
    print(users_idss)
    for user_ids in users_idss:
        print(user_ids[0], user_id)

        if user_ids[0] == user_id:
            await message.reply('📝Жулик, не рекомендуй!\n\n💬<i>Нельзя рекомендовать одного человека больше одного раза</i>', parse_mode='html')
            return
    cursor.execute('INSERT INTO din_admn_user_data (user_id, pubg_id, moder, comments, rang, date) VALUES (?, ?, ?, ?, ?, ?)', (user_id, pubg_id, moder_men, '', '', date))
    buttons = [
        types.InlineKeyboardButton(text="Верно", callback_data="successful_user"),
        types.InlineKeyboardButton(text="Не правильно", callback_data="not_successful_user"),

    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer(f'Данные этого юзера:\n\nПабг-айди: {pubg_id}\nНик в пабге: {nik_pubg}\nНик в клане: {nik}\nЮзернейм: @{username}\n<a href="https://t.me/{username}">Ссылка на пользователя</a>',
                         reply_markup=keyboard, parse_mode='html', disable_web_page_preview=True)
    connection.commit()



@dp.callback_query_handler(text="recommend_check_snat")
async def recommend_check_snat(call: types.CallbackQuery):
    if call.from_user.id in can_recommend_users:
        await recommend_snat_1_step(call)
        return
    else:
        await bot.answer_callback_query(call.id, text='⚠️Тебе не доступна эта функция')
        return


@dp.callback_query_handler(text="recommend_snat_1_step")
async def recommend_snat_1_step(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    await call.message.delete()
    await bot.send_message(call.message.chat.id,
                           'Напиши юзернейм или айди в пабге того у кого хочешь снять свою реокмендацию')
    try:
        cursor.execute('INSERT INTO dinamic_admn_recommend (user_id, is_do) VALUES (?, ?)', (call.from_user.id, 11))
    except sqlite3.IntegrityError:
        cursor.execute(f"UPDATE dinamic_admn_recommend SET is_do = ? WHERE user_id = ?", (11, call.from_user.id,))
    connection.commit()

@dp.callback_query_handler(text="recommend_snat_2_step")
async def recommend_snat_2_step(message, user_id):
    moder = message.from_user.id
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    alll = cursor.execute('SELECT moder FROM recommendation WHERE user_id = ?', (user_id,)).fetchall()
    if alll == []:
        await bot.send_message(message.chat.id, '📝Рекомендации пользователя отсутвуют')
        return
    mod_count = 0
    idss=[]
    for i in alll:
        mod_count +=1
    is_this_moder = False
    for t in range(mod_count):
        num = t
        b = (alll[num][0])
        idss.append(b)
    for y in range(mod_count):
        print(idss[y], moder)

        if int(idss[y]) == moder:
            is_this_moder = True

    if is_this_moder == False:
        await bot.send_message(message.chat.id, '📝Ты не рекомендовал этого пользователя')
        return
    recom_id=cursor.execute('SELECT recom_id FROM recommendation WHERE user_id = ? AND moder = ?', (user_id, moder,)).fetchall()[0][0]
    print(recom_id)
    cursor.execute('DELETE FROM recommendation WHERE recom_id = ?', (recom_id,))
    await bot.send_message(message.chat.id, '✅Рекомендация удалена')
    connection.commit()