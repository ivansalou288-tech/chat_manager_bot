from admin_config import *

@dp.callback_query_handler(text="new_chat_link_check")
async def new_link_check(call: types.CallbackQuery):
    if call.from_user.id in can_new_link_users:
        await new_link(call)
        return
    else:
        await bot.answer_callback_query(call.id, text='⚠️Тебе не доступна эта функция')
        return

@dp.callback_query_handler(text="new_chat_link")
async def new_link(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1 состав", callback_data="1sost"),
        types.InlineKeyboardButton(text="2 состав", callback_data="2sost")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await call.message.answer("Создание новой ссылки", reply_markup=keyboard)

@dp.callback_query_handler(text="1sost")
async def first_sost(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1", callback_data="one1pep"),
        types.InlineKeyboardButton(text="2", callback_data="one2pep"),
        types.InlineKeyboardButton(text="3", callback_data="one3pep")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await call.message.answer('На сколько человек расчитана ссылка', reply_markup=keyboard)


@dp.callback_query_handler(text="2sost")
async def two_sost(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1", callback_data="two1pep"),
        types.InlineKeyboardButton(text="2", callback_data="two2pep"),
        types.InlineKeyboardButton(text="3", callback_data="two3pep")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await call.message.answer('На сколько человек расчитана ссылка', reply_markup=keyboard)

@dp.callback_query_handler(text="one1pep")
async def one1pep(call: types.CallbackQuery):
    activate_count = 1
    sost = 1
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)', (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}', parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()

@dp.callback_query_handler(text="one2pep")
async def one2pep(call: types.CallbackQuery):
    activate_count = 2
    sost = 1
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


@dp.callback_query_handler(text="one3pep")
async def one3pep(call: types.CallbackQuery):
    activate_count = 3
    sost = 1
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


@dp.callback_query_handler(text="two1pep")
async def two1pep(call: types.CallbackQuery):
    activate_count = 1
    sost = 2
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


@dp.callback_query_handler(text="two2pep")
async def two2pep(call: types.CallbackQuery):
    activate_count = 2
    sost = 2
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


@dp.callback_query_handler(text="two3pep")
async def two3pep(call: types.CallbackQuery):
    activate_count = 3
    sost = 2
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    pwo = PasswordGenerator()
    link = f"WERTY-{pwo.shuffle_password('ASDFGHJKL12345678', 8)}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()

