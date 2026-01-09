from main.config import *
from datetime import datetime, timedelta
import sqlite3
from aiogram.types import ContentType

# Действия с очками и стоимостью
ACTIONS = {
    "подарить квартиру": {"points": 100000, "cost": 30000, "level": 10, "cooldown": 86400},
    "подарить круиз": {"points": 70000, "cost": 24500, "level": 10, "cooldown": 86400},
    "подарить машину": {"points": 30000, "cost": 12000, "level": 9, "cooldown": 43200},
    "подарить айфон": {"points": 5000, "cost": 2250, "level": 8, "cooldown": 21600},
    "подарить кулон": {"points": 3000, "cost": 1350, "level": 7, "cooldown": 14400},
    "сделать большой подарок": {"points": 3000, "cost": 1350, "level": 7, "cooldown": 14400},
    "признаться в чувствах": {"points": 2000, "cost": 950, "level": 6, "cooldown": 10800},
    "пригласить на свидание": {"points": 1000, "cost": 475, "level": 5, "cooldown": 7200},
    "пригласить в театр": {"points": 900, "cost": 428, "level": 5, "cooldown": 7200},
    "пригласить в кафе": {"points": 800, "cost": 380, "level": 5, "cooldown": 7200},
    "устроить сюрприз": {"points": 750, "cost": 356, "level": 5, "cooldown": 7200},
    "прогулки под луной": {"points": 500, "cost": 238, "level": 4, "cooldown": 3600},
    "пригласить в клуб": {"points": 500, "cost": 238, "level": 4, "cooldown": 3600},
    "пригласить в гости": {"points": 300, "cost": 150, "level": 3, "cooldown": 3600},
    "поговорить по душам": {"points": 300, "cost": 150, "level": 3, "cooldown": 3600},
    "поделиться секретом": {"points": 200, "cost": 100, "level": 3, "cooldown": 1800},
    "проводить домой": {"points": 200, "cost": 100, "level": 3, "cooldown": 1800},
    "ночные посиделки": {"points": 200, "cost": 100, "level": 3, "cooldown": 1800},
    "сходить в кино": {"points": 200, "cost": 100, "level": 3, "cooldown": 1800},
    "подарить игрушку": {"points": 170, "cost": 85, "level": 2, "cooldown": 1800},
    "проявить заботу": {"points": 150, "cost": 75, "level": 2, "cooldown": 1800},
    "подарить цветы": {"points": 150, "cost": 75, "level": 2, "cooldown": 1800},
    "гулять за ручки": {"points": 100, "cost": 50, "level": 2, "cooldown": 1800},
    "подарить конфеты": {"points": 100, "cost": 50, "level": 2, "cooldown": 1800},
    "сделать завтрак": {"points": 100, "cost": 50, "level": 2, "cooldown": 1800},
    "пригласить погулять": {"points": 70, "cost": 35, "level": 0, "cooldown": 900},
    "нежно обнять": {"points": 50, "cost": 25, "level": 0, "cooldown": 900},
    "подарить шоколадку": {"points": 50, "cost": 25, "level": 0, "cooldown": 900},
    "обнимать": {"points": 30, "cost": 15, "level": 0, "cooldown": 900},
    "поговорить": {"points": 30, "cost": 15, "level": 0, "cooldown": 900},
    "кинуть мем": {"points": 20, "cost": 10, "level": 0, "cooldown": 600},
    "поделиться едой": {"points": 20, "cost": 10, "level": 0, "cooldown": 600},
    "рассказать анекдот": {"points": 10, "cost": 5, "level": 0, "cooldown": 600},
    "сделать комплимент": {"points": 5, "cost": 3, "level": 0, "cooldown": 300},
    "прижать к себе": {"points": 300, "cost": 150, "level": 3, "cooldown": 3600},
    "целоваться": {"points": 400, "cost": 200, "level": 4, "cooldown": 3600},
    "романтический ужин": {"points": 1500, "cost": 713, "level": 5, "cooldown": 7200},
}

# Уровни отношений
LEVELS = [
    {"name": "Знакомые", "points": 0},
    {"name": "Приятели", "points": 500},
    {"name": "Друзья", "points": 2000},
    {"name": "Близкие друзья", "points": 5000},
    {"name": "Лучшие друзья", "points": 10000},
    {"name": "Неразлучные", "points": 20000},
    {"name": "Родственные души", "points": 40000},
    {"name": "Братья/Сестры", "points": 70000},
    {"name": "Семья", "points": 120000},
    {"name": "Единое целое", "points": 200000},
    {"name": "Легенда", "points": 350000},
]

def get_level_by_points(points):
    for i in range(len(LEVELS) - 1, -1, -1):
        if points >= LEVELS[i]["points"]:
            return i
    return 0

def init_db():
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS relationships (
        chat_id INTEGER,
        user1_id INTEGER,
        user2_id INTEGER,
        points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 0,
        status TEXT,
        date_start TEXT,
        interactions INTEGER DEFAULT 0,
        PRIMARY KEY (chat_id, user1_id, user2_id)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS relationship_cooldowns (
        chat_id INTEGER,
        user1_id INTEGER,
        user2_id INTEGER,
        action TEXT,
        last_used TEXT,
        PRIMARY KEY (chat_id, user1_id, user2_id, action)
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rel_temp_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        user1_id INTEGER,
        user2_id INTEGER,
        action TEXT,
        created TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS main_relationships (
        chat_id INTEGER,
        user_id INTEGER,
        partner_id INTEGER,
        PRIMARY KEY (chat_id, user_id)
    )''')
    conn.commit()
    conn.close()

init_db()

@dp.message_handler(Text(startswith=['+отн'], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def create_relationship(message):
    user_from = GetUserByMessage(message)
    if not user_from.user_id:
        await message.reply('📝 Укажите пользователя через @username или ответьте на сообщение')
        return
    
    try:
        status = message.text.split('\n')[1].strip()
    except:
        status = "Друзья"
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    user1_id = min(message.from_user.id, user_from.user_id)
    user2_id = max(message.from_user.id, user_from.user_id)
    
    if user1_id == user2_id:
        await message.reply('❌ Нельзя создать отношения с самим собой!')
        return
    
    existing = cursor.execute('SELECT * FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                             (message.chat.id, user1_id, user2_id)).fetchone()
    if existing:
        await message.reply('❌ Отношения уже существуют!')
        conn.close()
        return
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Принять", callback_data=f"rel_accept_{user1_id}_{user2_id}_{message.from_user.id}"),
        types.InlineKeyboardButton("❌ Отклонить", callback_data=f"rel_decline_{user1_id}_{user2_id}_{message.from_user.id}")
    )
    
    await message.reply(
        f'💕 <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> предлагает '
        f'<a href="tg://user?id={user_from.user_id}">{user_from.name}</a> отношения!\n'
        f'📝 Статус: {status}',
        reply_markup=keyboard,
        parse_mode='html'
    )
    
    cursor.execute('INSERT OR IGNORE INTO relationships VALUES (?,?,?,?,?,?,?,?)',
                  (message.chat.id, user1_id, user2_id, 0, 0, status, datetime.now().strftime('%d.%m.%Y'), 0))
    conn.commit()
    conn.close()

@dp.callback_query_handler(lambda c: c.data.startswith('rel_accept_'))
async def accept_relationship(call: types.CallbackQuery):
    _, _, user1_id, user2_id, initiator_id = call.data.split('_')
    user1_id, user2_id, initiator_id = int(user1_id), int(user2_id), int(initiator_id)
    
    target_id = user2_id if initiator_id == user1_id else user1_id
    if call.from_user.id != target_id:
        await bot.answer_callback_query(call.id, '❌ Эта кнопка не для тебя!', show_alert=True)
        return
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE relationships SET date_start=? WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (datetime.now().strftime('%d.%m.%Y'), call.message.chat.id, user1_id, user2_id))
    conn.commit()
    conn.close()
    
    await call.message.edit_text(
        f'✅ Отношения приняты!\n💕 Теперь вы вместе!',
        parse_mode='html'
    )

@dp.callback_query_handler(lambda c: c.data.startswith('rel_decline_'))
async def decline_relationship(call: types.CallbackQuery):
    _, _, user1_id, user2_id, initiator_id = call.data.split('_')
    user1_id, user2_id, initiator_id = int(user1_id), int(user2_id), int(initiator_id)
    
    target_id = user2_id if initiator_id == user1_id else user1_id
    if call.from_user.id != target_id:
        await bot.answer_callback_query(call.id, '❌ Эта кнопка не для тебя!', show_alert=True)
        return
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (call.message.chat.id, user1_id, user2_id))
    conn.commit()
    conn.close()
    
    await call.message.edit_text('❌ Отношения отклонены', parse_mode='html')

@dp.message_handler(Text(equals=['-отн', '! уйти'], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def delete_relationship(message):
    user_from = GetUserByMessage(message)
    if not user_from.user_id:
        await message.reply('📝 Укажите пользователя через @username или ответьте на сообщение')
        return
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    user1_id = min(message.from_user.id, user_from.user_id)
    user2_id = max(message.from_user.id, user_from.user_id)
    
    cursor.execute('DELETE FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (message.chat.id, user1_id, user2_id))
    cursor.execute('DELETE FROM relationship_cooldowns WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (message.chat.id, user1_id, user2_id))
    conn.commit()
    conn.close()
    
    await message.reply('💔 Отношения разорваны')

@dp.message_handler(Text(startswith=['отн основа'], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def set_main_relationship(message):
    user_from = GetUserByMessage(message)
    if not user_from.user_id:
        await message.reply('📝 Укажите пользователя через @username или ответьте на сообщение')
        return
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    user1_id = min(message.from_user.id, user_from.user_id)
    user2_id = max(message.from_user.id, user_from.user_id)
    
    rel = cursor.execute('SELECT * FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                        (message.chat.id, user1_id, user2_id)).fetchone()
    
    if not rel:
        await message.reply('❌ У вас нет отношений с этим пользователем!')
        conn.close()
        return
    
    cursor.execute('INSERT OR REPLACE INTO main_relationships VALUES (?,?,?)',
                  (message.chat.id, message.from_user.id, user_from.user_id))
    conn.commit()
    conn.close()
    
    await message.reply(f'✅ Основные отношения установлены с <a href="tg://user?id={user_from.user_id}">{user_from.name}</a>', parse_mode='html')

@dp.message_handler(Text(equals=['отн действия'], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def show_actions(message):
    user_from = GetUserByMessage(message)
    if not user_from.user_id:
        conn = sqlite3.connect(main_path, check_same_thread=False)
        cursor = conn.cursor()
        main_rel = cursor.execute('SELECT partner_id FROM main_relationships WHERE chat_id=? AND user_id=?',
                                 (message.chat.id, message.from_user.id)).fetchone()
        conn.close()
        
        if not main_rel:
            await message.reply('📝 Укажите пользователя через @username или ответьте на сообщение')
            return
        
        user_from.user_id = main_rel[0]
        user_from.name = GetUserByID(main_rel[0]).name
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    user1_id = min(message.from_user.id, user_from.user_id)
    user2_id = max(message.from_user.id, user_from.user_id)
    
    rel = cursor.execute('SELECT level FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                        (message.chat.id, user1_id, user2_id)).fetchone()
    
    if not rel:
        await message.reply('❌ У вас нет отношений с этим пользователем!')
        conn.close()
        return
    
    level = rel[0]
    text = f'💫 Доступные действия (уровень {level}):\n\n'
    
    for action, data in ACTIONS.items():
        if data['level'] <= level:
            text += f'🕔 «{action.capitalize()}» +{data["points"]}, {data["cost"]} i¢\n'
    
    conn.close()
    await message.reply(text)

@dp.message_handler(Text(startswith=['отн '], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def do_action(message):
    user_from = GetUserByMessage(message)
    if not user_from.user_id:
        conn = sqlite3.connect(main_path, check_same_thread=False)
        cursor = conn.cursor()
        main_rel = cursor.execute('SELECT partner_id FROM main_relationships WHERE chat_id=? AND user_id=?',
                                 (message.chat.id, message.from_user.id)).fetchone()
        conn.close()
        
        if not main_rel:
            await message.reply('📝 Укажите пользователя через @username или ответьте на сообщение')
            return
        
        user_from.user_id = main_rel[0]
        user_from.name = GetUserByID(main_rel[0]).name
    
    action_name = message.text.lower().replace('отн ', '').strip()
    
    if action_name not in ACTIONS:
        await message.reply('❌ Неизвестное действие!')
        return
    
    action = ACTIONS[action_name]
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    user1_id = min(message.from_user.id, user_from.user_id)
    user2_id = max(message.from_user.id, user_from.user_id)
    
    rel = cursor.execute('SELECT points, level, interactions FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                        (message.chat.id, user1_id, user2_id)).fetchone()
    
    if not rel:
        await message.reply('❌ У вас нет отношений с этим пользователем!')
        conn.close()
        return
    
    points, level, interactions = rel
    
    if action['level'] > level:
        await message.reply(f'❌ Действие доступно с уровня {action["level"]}!')
        conn.close()
        return
    
    cooldown = cursor.execute('SELECT last_used FROM relationship_cooldowns WHERE chat_id=? AND user1_id=? AND user2_id=? AND action=?',
                             (message.chat.id, user1_id, user2_id, action_name)).fetchone()
    
    if cooldown:
        last_used = datetime.strptime(cooldown[0], '%H:%M:%S %d.%m.%Y')
        if datetime.now() - last_used < timedelta(seconds=action['cooldown']):
            remaining = timedelta(seconds=action['cooldown']) - (datetime.now() - last_used)
            
            cursor.execute('INSERT INTO rel_temp_actions (chat_id, user1_id, user2_id, action, created) VALUES (?,?,?,?,?)',
                          (message.chat.id, user1_id, user2_id, action_name, datetime.now().strftime('%H:%M:%S %d.%m.%Y')))
            conn.commit()
            temp_id = cursor.lastrowid
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(f"💰 Использовать за {action['cost']} i¢", 
                                                    callback_data=f"rp_{temp_id}"))
            await message.reply(f'⏳ Действие на кулдауне! Осталось {remaining.seconds // 60} мин', reply_markup=keyboard)
            conn.close()
            return
    
    new_points = points + action['points']
    new_level = get_level_by_points(new_points)
    
    cursor.execute('UPDATE relationships SET points=?, level=?, interactions=interactions+1 WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (new_points, new_level, message.chat.id, user1_id, user2_id))
    cursor.execute('INSERT OR REPLACE INTO relationship_cooldowns VALUES (?,?,?,?,?)',
                  (message.chat.id, user1_id, user2_id, action_name, datetime.now().strftime('%H:%M:%S %d.%m.%Y')))
    
    conn.commit()
    conn.close()
    
    if new_level > level:
        user1 = GetUserByID(user1_id)
        user2 = GetUserByID(user2_id)
        await message.reply(
            f'🎉 Поздравляем!\n'
            f'💕 <a href="tg://user?id={user1_id}">{user1.name}</a> и '
            f'<a href="tg://user?id={user2_id}">{user2.name}</a> достигли нового уровня!\n'
            f'⭐ {LEVELS[new_level]["name"]} (уровень {new_level})\n'
            f'💫 Очки: {new_points}',
            parse_mode='html'
        )
    else:
        await message.reply(
            f'✅ Действие выполнено!\n'
            f'💕 +{action["points"]} очков'
        )

@dp.callback_query_handler(lambda c: c.data.startswith('rp_'))
async def pay_for_action(call: types.CallbackQuery):
    temp_id = int(call.data.split('_')[1])
    
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    temp_data = cursor.execute('SELECT chat_id, user1_id, user2_id, action FROM rel_temp_actions WHERE id=?', (temp_id,)).fetchone()
    if not temp_data:
        await bot.answer_callback_query(call.id, '❌ Действие устарело!', show_alert=True)
        conn.close()
        return
    
    chat_id, user1_id, user2_id, action_name = temp_data
    
    if call.from_user.id not in [user1_id, user2_id]:
        await bot.answer_callback_query(call.id, '❌ Эта кнопка не для тебя!', show_alert=True)
        conn.close()
        return
    
    action = ACTIONS[action_name]
    
    try:
        meshok = cursor.execute('SELECT meshok FROM farma WHERE user_id=?', (call.from_user.id,)).fetchone()[0]
    except:
        meshok = 0
    
    if meshok < action['cost']:
        await bot.answer_callback_query(call.id, f'❌ Недостаточно средств! Нужно {action["cost"]} i¢', show_alert=True)
        conn.close()
        return
    
    rel = cursor.execute('SELECT points, level FROM relationships WHERE chat_id=? AND user1_id=? AND user2_id=?',
                        (chat_id, user1_id, user2_id)).fetchone()
    
    if not rel:
        await bot.answer_callback_query(call.id, '❌ Отношения не найдены!', show_alert=True)
        conn.close()
        return
    
    points, level = rel
    new_points = points + action['points']
    new_level = get_level_by_points(new_points)
    
    cursor.execute('UPDATE relationships SET points=?, level=?, interactions=interactions+1 WHERE chat_id=? AND user1_id=? AND user2_id=?',
                  (new_points, new_level, chat_id, user1_id, user2_id))
    cursor.execute('UPDATE farma SET meshok=meshok-? WHERE user_id=?', (action['cost'], call.from_user.id))
    cursor.execute('INSERT OR REPLACE INTO relationship_cooldowns VALUES (?,?,?,?,?)',
                  (chat_id, user1_id, user2_id, action_name, datetime.now().strftime('%H:%M:%S %d.%m.%Y')))
    cursor.execute('DELETE FROM rel_temp_actions WHERE id=?', (temp_id,))
    
    conn.commit()
    conn.close()
    
    await call.message.edit_text(
        f'✅ Действие выполнено за монетки!\n'
        f'💕 +{action["points"]} очков\n'
        f'💰 -{action["cost"]} i¢'
    )
    await bot.answer_callback_query(call.id)
    
    if new_level > level:
        user1 = GetUserByID(user1_id)
        user2 = GetUserByID(user2_id)
        await bot.send_message(
            chat_id,
            f'🎉 Поздравляем!\n'
            f'💕 <a href="tg://user?id={user1_id}">{user1.name}</a> и '
            f'<a href="tg://user?id={user2_id}">{user2.name}</a> достигли нового уровня!\n'
            f'⭐ {LEVELS[new_level]["name"]} (уровень {new_level})\n'
            f'💫 Очки: {new_points}',
            parse_mode='html'
        )

@dp.message_handler(Text(equals=['отны'], ignore_case=True), content_types=ContentType.TEXT, is_forwarded=False)
async def show_relationships(message):
    conn = sqlite3.connect(main_path, check_same_thread=False)
    cursor = conn.cursor()
    
    rels = cursor.execute('SELECT user1_id, user2_id, points, level, status, date_start, interactions FROM relationships WHERE chat_id=?',
                         (message.chat.id,)).fetchall()
    
    if not rels:
        await message.reply('📝 В этом чате нет отношений')
        conn.close()
        return
    
    text = '💕 Отношения в чате:\n\n'
    
    for rel in rels:
        user1_id, user2_id, points, level, status, date_start, interactions = rel
        user1 = GetUserByID(user1_id)
        user2 = GetUserByID(user2_id)
        
        level_name = LEVELS[level]['name']
        
        text += (f'👥 <a href="tg://user?id={user1_id}">{user1.name}</a> ❤️ '
                f'<a href="tg://user?id={user2_id}">{user2.name}</a>\n'
                f'📊 Уровень: {level} ({level_name})\n'
                f'💫 Очки: {points}\n'
                f'📝 Статус: {status}\n'
                f'📅 С: {date_start}\n'
                f'🔄 Взаимодействий: {interactions}\n\n')
    
    conn.close()
    await message.reply(text, parse_mode='html')
