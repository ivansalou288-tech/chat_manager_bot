import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
from os.path import curdir
from traceback import print_tb

from aiogram.types import ContentType, ParseMode
from password_generator import PasswordGenerator

from main.config import *

@dp.message_handler(Text(startswith=['+турнир'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def create_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    moder_id = message.from_user.id

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    if await is_successful_moder(moder_id, message.chat.id, 'tur') == False:
        await message.reply('📝Ранг модератора не достаточен для использования этой команды')
        return
    elif await is_successful_moder(moder_id, message.chat.id, 'tur') == 'Need reg':
        await message.reply(
            '📝Для использования бота нужно зарегистрироваться\n\n💬<i>Для регистрации напиши @zzoobank, он все объяснит</i>',
            parse_mode='html')
        return
    txt = message.text

    pwo = PasswordGenerator()
    user = message.from_user
    id = pwo.shuffle_password('ASDFGHJKL12345678', 8)
    org_id = user.id
    org_name = user.first_name
    try:
        tur_name = txt.split('Название:')[1].split('Дата:')[0]
        mem_count = txt.split('Участников:')[1].split('Правила:')[0]
        mem_count_reg = 1
        date = txt.split('Дата:')[1].split('Участников:')[0]
        pravils = txt.split('Правила:')[1].split('Комментарии:')[0]
        comments = txt.split('Комментарии:')[1]
        if tur_name == '\n' or mem_count == '\n' or mem_count_reg == '\n' or date == '\n' or pravils == '\n':
            await message.answer(
                '📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>+Турнир\n\nНазвание:\nДата:\nУчастников:\nПравила:\nКомментарии:\n</code>',
                parse_mode='HTML')
            return
        mem_count = int(mem_count)
    except IndexError:
        await message.answer('📝Неверное использование команды \n\n💬Правильное использование этой команды:\n\n<code>+Турнир\n\nНазвание:\nДата:\nУчастников:\nПравила:\nКомментарии:\n</code>',parse_mode='HTML')
        return
    except ValueError:
        await message.answer('📝Неверное использование команды \n\n💬 <i>Кол-во участников должно быть целым числом от 1 до 60</i>',parse_mode='HTML')
        return

        return
    if tur_name == '':
        await message.answer('Название турнира не может быть пустым')

    date = date.split('\n')[0]
    try:
        print(date)
        lst = datetime.strptime(date, "%H:%M:%S %d.%m.%Y")
    except ValueError:
        try:
            print(date)
            lst = datetime.strptime(date, " %H:%M:%S %d.%m.%Y")
        except ValueError:
            await message.answer('Дата должна быть в формате «час:мин:сек день.месяц.год(в формате 2025)»')
            return

    try:
        cursor.execute(f'INSERT INTO information (id, org_id, org_name, tur_name, mem_count, mem_count_reg, date, pravils, comments, command) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (id, org_id,org_name, tur_name, mem_count, mem_count_reg, date, pravils, comments, 4))
        connection.commit()
        cursor.execute('INSERT INTO users (tur_id, user_id, user_status) VALUES (?, ?, ?)',
                       (id, message.from_user.id, 'организатор'))
        connection.commit()
        await message.answer(f'✅ Турнир с названием «{tur_name}» создан')
    except sqlite3.IntegrityError:
        await message.answer('📝У тебя уже есть зарегестрированный турнир!\n\n💬 <i>Сначала нужно провести или отменить уже зарегестрированный турнир</i>', parse_mode=ParseMode.HTML)


@dp.message_handler(Text(startswith=['-турнир'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def dell_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    id_tur = cursor.execute('SELECT id FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    name_tur = cursor.execute('SELECT tur_name FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    try:
        id_tur = id_tur[0][0]
        print(id_tur)
        buttons = [
            types.InlineKeyboardButton(text="Удалить", callback_data=f"yes_dell-{message.from_user.id}"),
            types.InlineKeyboardButton(text="Отменить", callback_data=f"otmena-{message.from_user.id}"),

        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        connection.commit()
        await message.answer(f'📝Хочешь удалить турнир с названием «{name_tur[0][0]}»?', reply_markup=keyboard)
    except IndexError:
        await message.answer('📝У тебя нет зарегестрированых турниров!\n\n💬 <i>Создать турнир можно по команде <code>+турнир\n{название турнира}</code></i>', parse_mode=ParseMode.HTML)
        return


@dp.message_handler(Text(startswith=['! турниры'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_turs(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    turnirs = cursor.execute('SELECT * FROM information').fetchall()
    id = []
    org_id = []
    org_name = []
    tur_name = []
    mem_count = []
    mem_count_reg = []
    date = []
    pravils = []
    comments = []
    com_type = []
    can_reg = []
    comands = []
    turnirs_count = 0
    itog = []

    for tur in turnirs:
        id.append(tur[0])
        org_id.append(tur[1])
        org_name.append(tur[2])
        tur_name.append(tur[3])
        mem_count.append(tur[4])
        mem_count_reg.append(tur[5])
        date.append(tur[6])
        pravils.append(tur[7])
        comments.append(tur[8])
        comands.append(tur[9])
        can_reg.append(tur[11])
        com_type.append(tur[10])
        turnirs_count += 1
    slov = {'yes': "открыта", 'no': 'закрыта', 'start': 'Турнир уже идет'}
    for i in range(turnirs_count):

        text = f'<b>{i+1}.</b> «{(tur_name[i])[1:(len(tur_name[i]))-1]}» | Организатор: <a href="tg://user?id={org_id[i]}">{org_name[i]}</a>\n<b>Регистрация:</b> {slov[can_reg[i]]}\n<b>Айди турнира: </b><code>{id[i]}</code>'
        itog.append(text)
    try:

        await message.answer(text='\n\n'.join(itog), parse_mode=ParseMode.HTML)

    except MessageTextIsEmpty:
        await message.answer('Активные туриниры чата отсутвуют')


@dp.message_handler(Text(startswith=['+тур'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def create_tur_dann(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        turnir_id = cursor.execute('SELECT id FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('У вас отсутвуют зарегестрированные турниры')
        return
    comments = message.text.split('\n')[1:]
    if message.text.split()[1] == "название":
        cursor.execute('UPDATE information SET tur_name = ? WHERE id = ?', ('\n'.join(comments), turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "участники":
        try:
            count = int(comments[0])
            if count > 60 or count < 1:
                await message.answer('Число участников должно быть целыми числом до 60 человек')
                return
        except ValueError:
            await message.answer('Число участников должно быть целыми числом до 60 человек')
            return
        cursor.execute('UPDATE information SET mem_count = ? WHERE id = ?', (count, turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "команды":
        try:
            count = int(comments[0])
            if count > 4 or count < 1:
                await message.answer('Число участников должно быть целыми числом до 60 человек')
                return
        except ValueError:
            await message.answer('Число человек в команде должно быть целым числом от 1 до 4')
            return
        cursor.execute('UPDATE information SET command = ? WHERE id = ?', (count, turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "регистрация":
        if comments[0] != 'сам' and comments[0] != 'авто':
            await message.answer('📝 Регистрация команд может быть только самостоятельной(<code>сам</code>) или автоматической(<code>авто</code>)', parse_mode='HTML')
            return
        slov = {'сам': 'self', 'авто': 'auto'}
        cursor.execute('UPDATE information SET com_type = ? WHERE id = ?', (slov[comments[0]], turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "дата":
        try:
            lst = datetime.strptime('\n'.join(comments), "%H:%M:%S %d.%m.%Y")
        except ValueError:
            await message.answer('Дата должна быть в формате «час:мин:сек день.месяц.год(в формате 2025)»')
            return
        cursor.execute('UPDATE information SET date = ? WHERE id = ?', ('\n'.join(comments), turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "правила":
        cursor.execute('UPDATE information SET pravils = ? WHERE id = ?', ('\n'.join(comments), turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

    if message.text.split()[1] == "комментарии":
        cursor.execute('UPDATE information SET comments = ? WHERE id = ?', ('\n'.join(comments), turnir_id,))
        connection.commit()
        await message.answer('✅ Обновлено')

@dp.message_handler(Text(startswith=['! анрег команду'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    print( message.text.split()[3])
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    otv = cursor.execute(f"SELECT username FROM [{-(klan)}] WHERE tg_id=?", (message.from_user.id,)).fetchall()[0][0]
    otv_nik = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE tg_id=?", (message.from_user.id,)).fetchall()[0][0]

    strk = f'{otv_nik} - @{otv} '
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        print(strk)
        otv = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, strk)).fetchall()[0][0]
    except IndexError:
        await message.answer(f'🗓 Ты не являешься ответсвеном в команде',parse_mode=ParseMode.HTML)
        return
    cursor.execute('DELETE FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, strk))
    connection.commit()
    await message.answer('Команда удалена')

@dp.message_handler(Text(startswith=['! турнир', '. турнир'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[2]
    except IndexError:
        return
    turnirs = cursor.execute('SELECT * FROM information WHERE id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return
    id = []
    org_id = []
    org_name = []
    tur_name = []
    mem_count = []
    mem_count_reg = []
    date = []
    pravils = []
    comments = []
    com_type = []
    can_reg = []
    comands = []
    turnirs_count = 0
    itog = []

    for tur in turnirs:
        id.append(tur[0])
        org_id.append(tur[1])
        org_name.append(tur[2])
        tur_name.append(tur[3])
        mem_count.append(tur[4])
        mem_count_reg.append(tur[5])
        date.append(tur[6])
        pravils.append(tur[7])
        comments.append(tur[8])
        comands.append(tur[9])
        can_reg.append(tur[11])
        com_type.append(tur[10])
        turnirs_count += 1

    slov = {'yes': "открыта", 'no': 'закрыта', 'start': 'Турнир уже идет'}
    slov_reg = {'self': "самостоятельная", 'auto': 'автоматическая'}
    for i in range(turnirs_count):
        text = f'<b>{i+1}.</b> «{tur_name[i]}» | Организатор: <a href="tg://user?id={org_id[i]}">{org_name[i]}</a>\n<b>🕰️ Дата проведения:</b> {date[i]}\n<b>👤 Максимальное количество участников:</b> {mem_count[i]}\n<b>👥 Максимальное количество игроков в команде:</b> {comands[i]}\n<b>👨‍✈️ Количество зарегестрированных участников:</b> {mem_count_reg[i]}\n\n📝 <b>Регистрация:</b> {slov[can_reg[i]]}\n🧾 <b>Регистрация команд:</b> {slov_reg[com_type[i]]}\n\n<b>📜 Правила турнира:</b>{pravils[i]}\n\n<b>💬 Коментарии от организатора турнира:</b>{comments[i]}\n\n<b>🆔 Айди турнира: </b><code>{id[i]}</code>'
        itog.append(text)

    await message.answer(text='\n\n'.join(itog), parse_mode=ParseMode.HTML)

@dp.message_handler(Text(startswith=['! рег команду', '! рег команды'], ignore_case=True), content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    print(message.text.split()[3])
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return
    turnirs = cursor.execute('SELECT * FROM information WHERE id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>', parse_mode='html')
        return
    comm = cursor.execute('SELECT com_type FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    if comm == 'auto':
        await message.answer('Регистрация команды невозможна в турнире с автоматическим распределением команд')
        return
    try:
        a = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, message.from_user.id)).fetchall()[0][0]
    except IndexError:
        await message.answer(f'🗓 Ты не зарегестрирован на этот турнир\n💬 <i>Зарегестрироваться на этот турнир можно по команде «<code>! рег {id_tur}</code>»</i>', parse_mode=ParseMode.HTML)
        return
    command_count = cursor.execute('SELECT command FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    print(command_count)

    text = message.text
    try:
        first = text.split('1) ')[1].split('\n')[0]
    except IndexError as e:
        print(e, 284)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков',parse_mode='html')
        return
    try:
        second = text.split('2) ')[1].split('\n')[0]
    except IndexError as e:
        print(e, 290)
        if command_count >= 2:
            await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков',parse_mode='html')
            return
    try:
        third = text.split('3) ')[1].split('\n')[0]
    except IndexError as e:
        print(e, 297)
        if command_count >= 3:
            await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков',parse_mode='html')
            return
    try:
        fore = text.split('4) ')[1]
    except IndexError as e:
        print(e, 304)
        if command_count >= 4:
            await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков',parse_mode='html')
            return
    num_otv = 0
    errors = 0
    otvs = 0
    try:
        otv = first.split('- отв')[1]
        otv = first.split('- отв')[0]
        num_otv = 1
        otvs+=1
    except IndexError:
        errors +=1
    except UnboundLocalError:
        errors += 1
    try:
        otv = second.split('- отв')[1]
        otv = second.split('- отв')[0]
        print(otv)
        num_otv = 2
        otvs += 1
    except IndexError:
        errors +=1
    except UnboundLocalError:
        errors += 1
    try:
        otv = third.split('- отв')[1]
        otv = third.split('- отв')[0]
        num_otv = 3
        otvs += 1
    except IndexError:
        errors +=1
    except UnboundLocalError:
        errors += 1
    try:
        otv = fore.split('- отв')[1]
        otv = fore.split('- отв')[0]
        num_otv = 4
        otvs += 1
    except IndexError:
        errors += 1
    except UnboundLocalError:
        errors += 1

    if errors == 4:
        print(350)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков', parse_mode='html')
        return
    if otvs > 1:
        await message.answer('🗓 Неверное использование команды\n💬 <i>Лидер команды может быть только один</i>', parse_mode='html')
        return

    #проверка на регистрацию на турнир
    try:
        first_us = first.split('@')[1].split()[0]
    except IndexError:
        print(360)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков', parse_mode='html')
        return
    except UnboundLocalError:
        pass
    try:
        second_us = second.split('@')[1].split()[0]
    except IndexError:
        print(368)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков', parse_mode='html')
        return
    except UnboundLocalError:
        pass
    try:
        third_us = third.split('@')[1].split()[0]
    except IndexError:
        print(376)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков', parse_mode='html')
        return
    except UnboundLocalError:
        pass
    try:
        fore_us = fore.split('@')[1].split()[0]
    except IndexError:
        print(384)
        await message.answer('🗓 Неверное использование команды\n💬 <i>Верное использование:\n\n</i><code>! рег команды {айди турнира}\n1) ник - @юзер - отв\n2) ник - @юзер\n3) ник - @юзер\n4) ник - @юзер</code> \n\n! если турнир расчитан на более маленькие команды просто писать меньше игроков', parse_mode='html')
        return
    except UnboundLocalError:
        pass
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    try:
        first_id = int(cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (first_us,)).fetchall()[0][0])
        second_id = int(cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (second_us,)).fetchall()[0][0])
        third_id = int(cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (third_us,)).fetchall()[0][0])
        fore_id = int(cursor.execute(f"SELECT tg_id FROM [{-(klan)}] WHERE username=?", (fore_us,)).fetchall()[0][0])
    except IndexError:
        await message.answer(f'🗓 Кто то из твоей команды не зарегестрирован на этот турнир\n💬 <i>Зарегестрироваться на этот турнир можно по команде «<code>! рег {id_tur}</code>»</i>', parse_mode=ParseMode.HTML)
        return
    except UnboundLocalError:
        pass
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        a = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, first_id)).fetchall()[0][0]
        b = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, second_id)).fetchall()[0][0]
        c = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, third_id)).fetchall()[0][0]
        d = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, fore_id)).fetchall()[0][0]
    except IndexError:
        await message.answer(f'🗓 Кто то из твоей команды не зарегестрирован на этот турнир\n💬 <i>Зарегестрироваться на этот турнир можно по команде «<code>! рег {id_tur}</code>»</i>', parse_mode=ParseMode.HTML)
        return
    except UnboundLocalError:
        pass

    #проверка на наличие игроков в других командах
    err = 0
    try:
        fir = cursor.execute('SELECT two_gamer FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, first)).fetchall()[0][0]
    except IndexError:
        err+=1
    except UnboundLocalError:
        pass
    try:
        sec = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND two_gamer = ?', (id_tur, second)).fetchall()[0][0]
    except IndexError:
        err+=1
    except UnboundLocalError:
        pass
    try:
        thir = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND two_gamer = ?', (id_tur, third)).fetchall()[0][0]
    except IndexError:
        err+=1
    except UnboundLocalError:
        pass
    try:
        fore = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND two_gamer = ?', (id_tur, fore)).fetchall()[0][0]
    except IndexError:
        err+=1
    except UnboundLocalError:
        pass





    print(err)
    if err == command_count:
        pass
    else:
        await message.answer(f'🗓 Кто то из твоей команды уже зарегестрирован в другой команде',
                             parse_mode=ParseMode.HTML)
        return



    if command_count == 1:
        second = ''
        third = ''
        fore = ''
    if command_count == 2:
        third = ''
        fore = ''
    if command_count == 3:
        fore = ''

    if num_otv == 1:
        cursor.execute('INSERT INTO comands (tur_id, otv, two_gamer, third_gamer, fore_gamer) VALUES (?, ?, ?, ?, ?)',(id_tur, otv, second, third, fore))
    if num_otv == 2:
        cursor.execute('INSERT INTO comands (tur_id, otv, two_gamer, third_gamer, fore_gamer) VALUES (?, ?, ?, ?, ?)',(id_tur, otv, first, third, fore))
    if num_otv == 3:
        cursor.execute('INSERT INTO comands (tur_id, otv, two_gamer, third_gamer, fore_gamer) VALUES (?, ?, ?, ?, ?)',(id_tur, otv, first, second, fore))
    if num_otv == 4:
        cursor.execute('INSERT INTO comands (tur_id, otv, two_gamer, third_gamer, fore_gamer) VALUES (?, ?, ?, ?, ?)',(id_tur, otv, first, second, third))
    connection.commit()

    await message.answer(text=f'✅ Команда зарегестрированна', parse_mode=ParseMode.HTML)

@dp.message_handler(Text(startswith=['! рег'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[2]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM information WHERE id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>', parse_mode=ParseMode.HTML)
        return
    comm = cursor.execute('SELECT com_type FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    if comm == 'no' or comm == 'start':
        await message.answer('Регистрация на турнир закрыта')
        return
    try:
        a = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, message.from_user.id)).fetchall()[0][0]
        await message.answer('🗓 Ты уже зарегестрирован на этот турнир')
        return
    except IndexError:
        pass

    cursor.execute('INSERT INTO users (tur_id, user_id, user_status) VALUES (?, ?, ?)', (id_tur, message.from_user.id, 'участник'))
    connection.commit()
    cursor.execute('UPDATE information SET mem_count_reg = mem_count_reg+1 WHERE id = ?', (id_tur,))
    connection.commit()
    a = cursor.execute('SELECT mem_count FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    b = cursor.execute('SELECT mem_count_reg FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    if a == b:
        cursor.execute('UPDATE information SET can_reg = ? WHERE id = ?', ('no', id_tur,))
        connection.commit()
    await message.answer('✅ Ты зарегестрирован')

@dp.message_handler(Text(startswith=['! открыть рег'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM users WHERE tur_id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer(
            '📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return
    try:
        org = cursor.execute('SELECT user_id FROM users WHERE tur_id = ? AND user_status = ?',(id_tur, 'организатор')).fetchall()[0][0]
    except IndexError:
        await message.answer('📝 Ты не являешься организатором этого турнира', parse_mode=ParseMode.HTML)
        return
    if org != message.from_user.id:
        await message.answer('📝 Ты не являешься организатором этого турнира', parse_mode=ParseMode.HTML)
        return

    cursor.execute('UPDATE information SET can_reg = ? WHERE id = ?', ('yes', id_tur))
    connection.commit()

@dp.message_handler(Text(startswith=['! закрыть рег'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM users WHERE tur_id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer(
            '📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return
    try:
        org = cursor.execute('SELECT user_id FROM users WHERE tur_id = ? AND user_status = ?',(id_tur, 'организатор')).fetchall()[0][0]
    except IndexError:
        await message.answer('📝 Ты не являешься организатором этого турнира', parse_mode=ParseMode.HTML)
        return
    if org != message.from_user.id:
        await message.answer('📝 Ты не являешься организатором этого турнира', parse_mode=ParseMode.HTML)
        return

    cursor.execute('UPDATE information SET can_reg = ? WHERE id = ?', ('no', id_tur))
    connection.commit()


@dp.message_handler(Text(startswith=['! анрег'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[2]
    except IndexError:
        return
    turnirs = cursor.execute('SELECT * FROM information WHERE id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return
    try:
        a = cursor.execute('SELECT user_status FROM users WHERE tur_id = ? AND user_id = ?', (id_tur, message.from_user.id)).fetchall()[0][0]
        cursor.execute('DELETE FROM users WHERE tur_id = ? AND user_id = ?',(id_tur, message.from_user.id))
        connection.commit()
        cursor.execute('UPDATE information SET mem_count_reg = mem_count_reg-1 WHERE id = ?', (id_tur,))
        connection.commit()
        cursor.execute('DELETE FROM comands WHERE tur_id = ? AND user_id = ?',(id_tur, message.from_user.id))
        connection.commit()
        await message.answer('✅ Ты вышел из турнира\n\n💬 <i>Если ты состоял в команде, твоему лидеру стоит перерегать команду</i>')
        return
    except IndexError:
        await message.answer('🗓 Ты не зарегестрирован на этот турнир')
        return

@dp.message_handler(Text(startswith=['! тур участники'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM users WHERE tur_id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return


    user_id = []
    user_status = []

    mem_count_reg = 0
    itog = []
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    for tur in turnirs:
        user_id.append(tur[2])
        user_status.append(tur[1])

        mem_count_reg += 1

    for i in range(mem_count_reg):
        user_name = cursor.execute(f'SELECT nik FROM [{-(klan)}] WHERE tg_id = ?', (user_id[i],)).fetchall()[0][0]
        text = f'<b>{i+1}.</b> <a href="tg://user?id={user_id[i]}">{user_name}</a> | Статус: {user_status[i]}'
        itog.append(text)
    a ='\n\n'.join(itog)
    await message.answer(text=f'🗓 <b>Участники турнира</b>\n\n{a}', parse_mode=ParseMode.HTML)

@dp.message_handler(Text(startswith=['! тур команды'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def check_tur_cmd(message: types.Message):

    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM comands WHERE tur_id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return


    otv = []
    first = []
    second = []
    third = []
    commands_count = 0
    itog = []
    for command in turnirs:
        otv.append(command[1])
        first.append(command[2])
        second.append(command[3])
        third.append(command[4])
        commands_count += 1


    for i in range(commands_count):
        text = f'<b>{i+1}. Команда</b>\nОтв: {otv[i]}\n1) {first[i]}\n2) {second[i]}\n3) {third[i]}'
        itog.append(text)

    itog_txt = '\n\n'.join(itog)
    await message.answer(text=itog_txt, parse_mode=ParseMode.HTML)

@dp.message_handler(Text(startswith=['! вины'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def start_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[2]
    except IndexError:
        print(1)
        return
    turnirs = cursor.execute('SELECT * FROM wins WHERE tur = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return

    otv = []
    count = []
    wins_count = 0
    itof = []
    for row in turnirs:
        otv.append(row[1])
        count.append(row[2])
        wins_count += 1


    for i in range(wins_count):
        txt = f'<b>{i+1}.</b> Команда\n<b>Отв:</b> {otv[i]}\nВины: {count[i]}'
        itof.append(txt)

    await message.answer('\n\n'.join(itof), parse_mode='html')


@dp.message_handler(Text(startswith=['! распределить команды'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def respredel_tur_cmd(message: types.Message):

    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    try:
        id_tur = message.text.split()[3]
    except IndexError:
        return

    turnirs = cursor.execute('SELECT * FROM users WHERE tur_id = ?', (id_tur,)).fetchall()
    if turnirs == []:
        await message.answer('📜 Такого турнира не существует\n💬 <i>Посмотреть активные турниры можно по команде «<code>! турниры</code>»</i>')
        return
    try:
        org = cursor.execute('SELECT user_id FROM users WHERE tur_id = ? AND user_status = ?', (id_tur, 'организатор')).fetchall()[0][0]
    except IndexError:
        await message.answer('📝 Ты не являешься организатором этого турнира',parse_mode=ParseMode.HTML)
        return
    if org != message.from_user.id:
        await message.answer('📝 Ты не являешься организатором этого турнира',parse_mode=ParseMode.HTML)
        return
    command_count = cursor.execute('SELECT command FROM information WHERE id = ?', (id_tur,)).fetchall()[0][0]
    cursor.execute('DELETE FROM comands WHERE tur_id = ?', (id_tur,))
    connection.commit()
    user_id = []
    user_status = []

    mem_count_reg = 0
    itog = []

    for tur in turnirs:
        user_id.append(tur[2])
        user_status.append(tur[1])
        mem_count_reg += 1

    random.shuffle(user_id)
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    commandd = []
    for i in range(mem_count_reg):
        connection = sqlite3.connect(main_path)
        cursor = connection.cursor()
        username = cursor.execute(f"SELECT username FROM [{-(klan)}] WHERE tg_id=?", (int(user_id[i]),)).fetchall()[0][0]
        nik = cursor.execute(f"SELECT nik_pubg FROM [{-(klan)}] WHERE tg_id=?", (int(user_id[i]),)).fetchall()[0][0]
        strk = f'{nik} - @{username} '
        commandd.append(strk)

        if (i+1) % command_count == 0 or i == mem_count_reg - 1:
            otv = commandd[0]
            first = commandd[1]
            try:
                second = commandd[2]
            except IndexError:
                second = ''
            try:
                third = commandd[3]
            except IndexError:
                third = ''
            if command_count == 1:
                second = ''
                third = ''
                fore = ''
            if command_count == 2:
                third = ''
                fore = ''
            if command_count == 3:
                fore = ''
            connection = sqlite3.connect(tur_path)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO comands (tur_id, otv, two_gamer, third_gamer, fore_gamer) VALUES (?, ?, ?, ?, ?)',(id_tur, otv, first, second, third))
            connection.commit()
            commandd = []



    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()

    await message.answer(f'📝 Команды перераспределены рандомно \n\n💬<i> Посмотреть список команд мэтого турнира можно по команде</i> «<code>! тур команды {id_tur}</code>»', parse_mode=ParseMode.HTML)

@dp.callback_query_handler(Text(startswith=['yes_dell', 'otmena'], ignore_case=True))
async def successful_recom(call: types.CallbackQuery):
    if call.data.split('-')[0] == 'yes_dell':
        if int(call.from_user.id) != int(call.data.split('-')[1]):
            return
        connection = sqlite3.connect(tur_path)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM information WHERE org_id = ?', (call.from_user.id,))
        connection.commit()
        await call.message.edit_text('✅Удалено')
    if call.data.split('-')[0] == 'otmena':
        if int(call.from_user.id) != int(call.data.split('-')[1]):
            return
        await call.message.edit_text('❌Отменено')

@dp.message_handler(Text(startswith=['! начать турнир'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def start_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    id_tur = cursor.execute('SELECT id FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    name_tur = cursor.execute('SELECT tur_name FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    try:
        id_tur = id_tur[0][0]
        cursor.execute('UPDATE information SET can_reg = ? WHERE id = ?', ('start', id_tur))
        connection.commit()
        cursor.execute('UPDATE information SET com_type = ? WHERE id = ?', ('auto', id_tur))
        connection.commit()
        comments = '\n'.join(message.text.split('\n')[1:])
        cursor.execute('UPDATE starts SET comments = ? WHERE id = ?', (comments, id_tur))
        connection.commit()

        try:
            cursor.execute(f'SELECT user_id FROM users WHERE tur_id = ?', (id_tur,))
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

        if comments == "":
            await message.reply(f'📢{name1} Созывает всех участников турнира! Начинается турнир!', parse_mode='html')
        else:
            await message.reply(f'📢{name1} Созывает всех участников турнира! Начинается турнир!\n\n💬 Коментарии:\n{comments}', parse_mode='html')
        a = ''
        for r in range(users_count):
            a += mentions[r]
            print(a)
            print(r)
            if (r + 1) % 5 == 0 or r == users_count - 1:
                await message.reply(f'<b>⬆️Общи{a}й сбор ({(r // 6) + 1})</b>', parse_mode='html')
                a = ''

    except IndexError:
        await message.answer('📝У тебя нет зарегестрированых турниров!\n\n💬 <i>Создать турнир можно по команде <code>+турнир\n{название турнира}</code></i>', parse_mode=ParseMode.HTML)
        return

@dp.message_handler(Text(startswith=['! вин'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def start_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    id_tur = cursor.execute('SELECT id FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    name_tur = cursor.execute('SELECT tur_name FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    try:
        id_tur = id_tur[0][0]
    except IndexError:
        await message.answer('📝У тебя нет зарегестрированых турниров!\n\n💬 <i>Создать турнир можно по команде <code>+турнир\n{название турнира}</code></i>', parse_mode=ParseMode.HTML)
        return
    try:
        num = int(message.text.split(' ')[2])
    except ValueError:
        return

    user_id = await get_user_id(message)
    if user_id == False:
        await message.reply('📝Невозможно найти информацию о пользователе\n\n💬Введите корректный юзернейм(<code>@</code><i>юзер</i>), тг айди (<code>@</code><i>айди</i>) или ответь на сообщение',parse_mode='html')
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    username = (message.text.split('@')[1]).split()[0]
    nik = cursor.execute(f"SELECT nik FROM [{-(klan)}] WHERE username=?", (username,)).fetchall()[0][0]
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    otvs = cursor.execute('SELECT otv FROM comands WHERE tur_id = ?', (id_tur,)).fetchall()
    print(otvs)
    txt = f'{nik} - @{username} '
    print(txt)
    try:
        otv = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, txt)).fetchall()[0][0]
    except IndexError:
        txt = f' {nik} - @{username} '
        try:
            otv = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, txt)).fetchall()[0][0]
        except IndexError:
            txt = f'{nik} - @{username}'
            try:
                otv = cursor.execute('SELECT otv FROM comands WHERE tur_id = ? AND otv = ?', (id_tur, txt)).fetchall()[0][0]
            except IndexError:
                await message.answer('Такого отва не существует')
                return

    try:
        print(cursor.execute('SELECT count FROM wins WHERE tur = ? AND otv = ?', (id_tur, otv)).fetchall()[0][0])
        cursor.execute('UPDATE wins SET count = count+1 WHERE tur = ? AND otv = ?', (id_tur, otv))
        connection.commit()
    except IndexError:
        cursor.execute('INSERT INTO wins (tur, otv, count, is_winer) VALUES (?, ?, ?, ?)', (id_tur, otv, 1, 'False'))
        connection.commit()

@dp.message_handler(Text(startswith=['! закончить турнир'], ignore_case=True),content_types=ContentType.TEXT,is_forwarded=False)
async def start_tur(message: types.Message):
    connection = sqlite3.connect(tur_path)
    cursor = connection.cursor()
    id_tur = cursor.execute('SELECT id FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    name_tur = cursor.execute('SELECT tur_name FROM information WHERE org_id = ?', (message.from_user.id,)).fetchall()
    try:
        id_tur = id_tur[0][0]
    except IndexError:
        await message.answer('📝У тебя нет зарегестрированых турниров!\n\n💬 <i>Создать турнир можно по команде <code>+турнир\n{название турнира}</code></i>', parse_mode=ParseMode.HTML)
        return

    win_otv = cursor.execute('SELECT otv FROM wins WHERE count=(select max(count) from wins) AND tur = ?', (id_tur,)).fetchall()[0][0]
    win_count = cursor.execute('SELECT count FROM wins WHERE count=(select max(count) from wins) AND tur = ?', (id_tur,)).fetchall()[0][0]
    await message.answer(f'🥇 Поздравляем команду с отвом {win_otv}\nКоличество их побед: {win_count}\nПоздравляем!', parse_mode=ParseMode.HTML)
    cursor.execute('DELETE FROM wins WHERE tur = ?', (id_tur,))
    connection.commit()
    cursor.execute('DELETE FROM USERS WHERE tur_id = ?', (id_tur,))
    connection.commit()
    cursor.execute('DELETE FROM starts WHERE id = ?', (id_tur,))
    connection.commit()
    cursor.execute('DELETE FROM information WHERE id = ?', (id_tur,))
    connection.commit()
    cursor.execute('DELETE FROM comands WHERE tur_id = ?', (id_tur,))
    connection.commit()
if __name__ == "__main__":
    executor.start_polling(dp)