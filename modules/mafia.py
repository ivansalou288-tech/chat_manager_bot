import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import types
from main.config import about_user_sdk, klan, dp, bot
from aiogram.types import ChatPermissions, ParseMode
from aiogram import executor, Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
import random
#from config import *
import sqlite3
from aiogram.utils.exceptions import *
from password_generator import PasswordGenerator

curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'
kasik_path = curent_path / 'databases' / 'kasik.db'
mafia_path = curent_path / 'databases' / 'mafia.db'



QUANTITY_OF_ROLES = {4: '2 1 0 0 1 0', 5: '0 1 2 1 1 0', 
                     6: '3 1 0 1 1 0', 7: '4 1 0 1 1 0', 8: '4 1 1 1 1 0',
                     9: '4 1 1 1 1 1', 10: '4 1 2 1 1 1'}


ROLES_ABOUT = {
    "mirny": "👥 Мирный - Обычный мирный житель, не обладает особыми способностями. Побеждает с горожанами, если все злые роли устранены.",
    "don_mafia": "🕴 Дон - Глава мафии. Ночью выбирает жертву вместе с мафией и осуществляет убийство.",
    "mafia": "💀 Мафия - Член мафиозной семьи. Ночью выбирают жертву вместе с Доном. Может занять роль Дона, если тот погибнет.",
    "police": "🕵️‍♂️ Комиссар - Полиция/следователь. Ночью может либо узнать роль одного игрока, либо убить его.",
    # "👮♂️ Сержант": "Помощник Комиссара. Знает о проверках Комиссара и может стать новым Комиссаром, если тот умрёт.",
    "doctor": "🏥 Доктор - Ночной защитник. Может спасти одного игрока от убийства. Один раз за игру может спасти себя.",
    "maniak": "🔪 Маньяк - Нейтральная убийственная роль. Каждую ночь убивает игрока. Цель — остаться последним выжившим."
}

token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
api_id =21842840
api_hash ="1db0b6e807c90e6364287ad8af7fa655"
bot = Bot(token=token)
dp = Dispatcher(bot)

class Person:
    def __init__(self, user_id, card):
        self.user_id = user_id
        self.card = card


@dp.message_handler(commands=["мафия", " мафия"], commands_prefix=["!", '.', '/'])
async def get_ref(message: types.Message):
    if message.from_user.id == message.from_user.id and message.from_user.id != 1240656726:
        await message.answer("В разработке")
        return
    
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    pwo = PasswordGenerator()
    code = pwo.shuffle_password('abhtsyufjkx12345678', 8)
    link = f'https://t.me/for_klan_tests_bot?start={code}'
    button = types.InlineKeyboardButton(text="Присоединиться", url=link)
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(button)
    try:
        cursor.execute("INSERT INTO messages (chat_id, message, game, text) VALUES (?, ?, ?, ?)", (message.chat.id, 0000, code, "Новая игра создана\n\nЗарегестрированны:"))
    except sqlite3.IntegrityError:
        await message.answer('Игра в этом чате уже идет')
        connection.commit()
        return
    mess_id = (await message.answer("Новая игра создана\n\nЗарегестрированны:", reply_markup=keyboard)).message_id
    cursor.execute('UPDATE messages SET message = ? WHERE game = ?', (mess_id, code,))
    connection.commit()



# хендлер для расшифровки ссылки
@dp.message_handler(commands=["start"])
async def handler(message: types.Message):
    args = message.get_args()
    if args == '':
        await start(message)
        return
    
    user_id = message.from_user.id
    username = message.from_user.username
    user_name = message.from_user.full_name

    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO players (game, player_id, player_username, player_name, player_card) VALUES (?, ?, ?, ?, ?)", (args, user_id, username, user_name, None))
    except sqlite3.IntegrityError:
        await message.answer('Ты уже зарегестрирован')
        connection.commit()
        return
    connection.commit()

    cursor.execute('SELECT message FROM messages WHERE game = ?', (args,))
    mess = cursor.fetchall()[0][0]
    cursor.execute('SELECT chat_id FROM messages WHERE game = ?', (args,))
    chat_id = cursor.fetchall()[0][0]
    cursor.execute('SELECT text FROM messages WHERE game = ?', (args,))
    text = cursor.fetchall()[0][0]



    link = f'https://t.me/for_klan_tests_bot?start={args}'
    button = types.InlineKeyboardButton(text="Присоединиться", url=link)
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(button)
    new_text = f'{text}\n<a href="https://t.me/{username}">{user_name}</a>'
    await bot.edit_message_text(chat_id=chat_id, message_id=int(mess), text = new_text,parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard)
    cursor.execute('UPDATE messages SET text = ? WHERE game = ?', (new_text, args))
    connection.commit()
    await message.answer(f"Вы зарегестрированны")



@dp.message_handler(commands=["star"], commands_prefix=["!", '.', '/'])
async def give_roles(message: types.Message):
    global ROLES_ABOUT
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    chat_id = message.chat.id
    try:
        cursor.execute('SELECT game FROM messages WHERE chat_id = ?', (chat_id,))
        game = cursor.fetchall()[0][0]
    except IndexError:
        await message.answer('В этом чате нет активных игр')
        return
    
    # * раздача ролей


    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS game_{game} (
        player INTEGER,
        player_card TEXT,
        liveness TEXT
        )
        ''')
    connection.commit()

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS night_{game} (
        user INTEGER,
        doctor INTEGER DEFAULT (0),
        mafia INTEGER DEFAULT (0),
        maniak INTEGER DEFAULT (0)
        )
        ''')
    connection.commit()

    cursor.execute('SELECT message FROM messages WHERE game = ?', (game,))
    mess = cursor.fetchall()[0][0]
    try:
        await bot.delete_message(chat_id, mess)
    except Exception:
        pass
    players = cursor.execute('SELECT player_id FROM players WHERE game = ?', (game,)).fetchall()
    players_id = []
    count = 0
    for player in players:
        players_id.append(player[0])
        count +=1
    print(players_id)
    random.shuffle(players_id)
    print(players_id)
    count_card_txt = QUANTITY_OF_ROLES[count]

    mirny = int(count_card_txt.split()[0])
    don_mafia = int(count_card_txt.split()[1])
    mafia = int(count_card_txt.split()[2])
    police = int(count_card_txt.split()[3])
    doctor = int(count_card_txt.split()[4])
    maniak = int(count_card_txt.split()[5])


    for id in players_id:
        cursor.execute(f'INSERT INTO night_{game} (user, doctor, mafia, maniak) VALUES (?, ?, ?, ?)', (id, 0, 0, 0))
        connection.commit()
        if mirny > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('mirny', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'mirni', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["mirny"]}')
            mirny -= 1
        elif don_mafia > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('don_mafia', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'don_mafia', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["don_mafia"]}')
            don_mafia -= 1
        elif mafia > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('mafia', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'mafia', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["mafia"]}')
            mafia -= 1
        elif police > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('police', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'police', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["police"]}')
            police -= 1
        elif doctor > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('doctor', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'doctor', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["doctor"]}')
            doctor -= 1
        elif maniak > 0:
            cursor.execute('UPDATE players SET player_card = ? WHERE game = ? AND player_id = ?', ('maniak', game, id,))
            connection.commit()
            cursor.execute(f"INSERT INTO game_{game} (player, player_card, liveness) VALUES (?, ?, ?)", (id, 'maniak', 'True', ))
            connection.commit()
            await bot.send_message(id, f'Твоя роль:\n{ROLES_ABOUT["maniak"]}')
            maniak -= 1
        else:
            break
        
    # * начало игры

    await start_game(message, game)
    # cursor.execute('DELETE FROM players')
    # connection.commit()

    # cursor.execute('DELETE FROM messages')
    # connection.commit()


async def start_game(message, game):
    await start_night(message, game)

async def start_night(message,game):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    await message.answer("Ночь началась, проверьте ЛС бота")
    try:
        doctor = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('doctor','True')).fetchall()[0][0]
    except IndexError:
        doctor = False
    try:
        police = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('police','True')).fetchall()[0][0]
    except IndexError:
        police = False
    try:
        maniak = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('maniak','True')).fetchall()[0][0]
    except IndexError:
        maniak = False

    try:
        don_mafia = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('don_mafia','True')).fetchall()[0][0]
    except IndexError:
        don_mafia = False

    mafias = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('mafia','True')).fetchall()
    mafia = []
    for maf in mafias:
        mafia.append(maf[0])
    

    # if mafia == []:
    #     # TODO: стоп игра 
    #     return
    if doctor:
        await doctor_funk(message, game, doctor)
    if police:
        await police_funk(message, game, police)
    for id in mafia:
        await mafia_funk(message,game, id)

async def doctor_funk(message, game, doctor):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'lek_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1


    await bot.send_message(chat_id=doctor, text='Кого ты хочешь вылечить?', reply_markup=keyboard)


async def police_funk(message, game, police):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'check_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1
    await bot.send_message(chat_id=police, text='Кого ты хочешь проверить?', reply_markup=keyboard)


async def mafia_funk(message, game, mafia):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'maf_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1
    await bot.send_message(chat_id=mafia, text='Кого ты хочешь предложить дону?', reply_markup=keyboard)



@dp.callback_query_handler(Text(startswith='lek_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('lek_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE night_{game} SET doctor = ? WHERE user = ?', (1, id))
    connection.commit()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    await call.message.edit_text(f"Ты выбрал {name}, он не умрет")

    
@dp.callback_query_handler(Text(startswith='check_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('check_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    username = cursor.execute('SELECT player_username FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    card = cursor.execute('SELECT player_card FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    if card != 'mafia' and card != 'don_mafia':
        await call.message.edit_text(f'Игрок <a href="https://t.me/{username}">{name}</a> не является мафией(любая другая роль)',parse_mode='html', disable_web_page_preview=True)
        return
    else:
        await call.message.edit_text(f'Игрок <a href="https://t.me/{username}">{name}</a> находится в рядах мафиози', parse_mode='html', disable_web_page_preview=True)
        return

@dp.callback_query_handler(Text(startswith='maf_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('maf_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    username = cursor.execute('SELECT player_username FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    try:
        don_mafia = cursor.execute(f'SELECT player FROM game_{game} WHERE player_card = ? AND liveness = ?', ('don_mafia','True')).fetchall()[0][0]
    except IndexError:
        await call.message.answer('Ошибка')
        return
    await bot.send_message(chat_id=don_mafia, text=f'Одна из мафий предлагает убить <a href="https://t.me/{username}">{name}</a>', parse_mode='html', disable_web_page_preview=True)
    await call.message.edit_text(text='Дон мафия получил ваше предложение')
    
    

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
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    text = cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('commands',)).fetchall()[0][0]
    await bot.send_message(call.from_user.id, f'🗓<b>Список команд чата:</b>\n\n{text}', parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await bot.answer_callback_query(call.id, text='')


@dp.message_handler(commands=["test"], commands_prefix=["!", '.', '/'])
async def get_ref(message: types.Message):
    pass
    

if __name__ == "__main__":
    executor.start_polling(dp)