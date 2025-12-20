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
import asyncio
import time
import re
#?from config import *
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



QUANTITY_OF_ROLES = {4: '2 1 0 0 1 0', 5: '2 1 0 1 1 0',
                     6: '3 1 0 1 1 0', 7: '4 1 0 1 1 0', 8: '4 1 1 1 1 0',
                     9: '4 1 1 1 1 1', 10: '4 1 2 1 1 1'}


ROLES_ABOUT = {
    "mirny": "👥 Мирный - Обычный мирный житель, не обладает особыми способностями. Побеждает с горожанами, если все злые роли устранены.",
    "don_mafia": "🕴 Дон - Глава мафии. Ночью выбирает жертву вместе с мафией и осуществляет убийство.",
    "mafia": "💀 Мафия - Член мафиозной семьи. Ночью выбирают жертву вместе с Доном. Может занять роль Дона, если тот погибнет.",
    "police": "🕵️‍♂️ Комиссар - Полиция/следователь. Ночью может либо узнать роль одного игрока, либо убить его.",
    #* "👮♂️ Сержант": "Помощник Комиссара. Знает о проверках Комиссара и может стать новым Комиссаром, если тот умрёт.",
    "doctor": "🏥 Доктор - Ночной защитник. Может спасти одного игрока от убийства. Один раз за игру может спасти себя.",
    "maniak": "🔪 Маньяк - Нейтральная убийственная роль. Каждую ночь убивает игрока. Цель — остаться последним выжившим."
}

#? token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
#? api_id =21842840
#? api_hash ="1db0b6e807c90e6364287ad8af7fa655"
#? bot = Bot(token=token)
#? dp = Dispatcher(bot)

#* Класс для хранения данных игрока (ID и роль)
class Person:
    def __init__(self, user_id, card):
        self.user_id = user_id
        self.card = card


#? -------------------------
#? Between-nights voting flow
#? -------------------------
_VOTE_EVENTS = {}  #? game -> asyncio.Event

#? -------------------------
#? Night auto-finish flow
#? -------------------------
_NIGHT_LOCKS = {}  #? game -> asyncio.Lock


# * Получает блокировку для конкретной игры (предотвращает одновременное завершение ночи)
def _get_night_lock(game: str) -> asyncio.Lock:
    lock = _NIGHT_LOCKS.get(game)
    if lock is None:
        lock = asyncio.Lock()
        _NIGHT_LOCKS[game] = lock
    return lock


# * Создает таблицы для отслеживания состояния ночи и действий игроков
def _ensure_night_state_tables(cursor, game: str):
    game = _safe_game_id(game)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS night_meta (
            game TEXT PRIMARY KEY,
            night_no INTEGER NOT NULL,
            status TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS night_actions_{game} (
            night_no INTEGER NOT NULL,
            actor INTEGER NOT NULL,
            role TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (night_no, actor)
        )
        """
    )


# * Начинает новую ночь и регистрирует всех активных игроков с ролями
def _begin_new_night(cursor, game: str, actors):
    """
    Starts a new night round for this game and registers required actors.
    actors: list[tuple[int, str]] -> (actor_id, role_name)
    Returns night_no
    """
    game = _safe_game_id(game)
    row = cursor.execute("SELECT night_no FROM night_meta WHERE game = ?", (game,)).fetchone()
    night_no = 1 if row is None else int(row[0]) + 1

    cursor.execute(
        """
        INSERT INTO night_meta (game, night_no, status)
        VALUES (?, ?, ?)
        ON CONFLICT(game) DO UPDATE SET
            night_no=excluded.night_no,
            status=excluded.status
        """,
        (game, night_no, "open"),
    )

    #? Keep the actions table small (remove older nights)
    cursor.execute(f"DELETE FROM night_actions_{game} WHERE night_no < ?", (night_no - 2,))

    #? Register required actors for this night
    for actor_id, role in actors:
        cursor.execute(
            f"""
            INSERT INTO night_actions_{game} (night_no, actor, role, done)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(night_no, actor) DO UPDATE SET
                role=excluded.role,
                done=excluded.done
            """,
            (night_no, int(actor_id), str(role)),
        )

    return night_no


# * Отмечает что игрок завершил свое ночное действие
def _mark_night_done(cursor, game: str, actor_id: int):
    game = _safe_game_id(game)
    row = cursor.execute("SELECT night_no, status FROM night_meta WHERE game = ?", (game,)).fetchone()
    if not row:
        return
    night_no, status = int(row[0]), str(row[1])
    if status != "open":
        return
    cursor.execute(
        f"UPDATE night_actions_{game} SET done = 1 WHERE night_no = ? AND actor = ?",
        (night_no, int(actor_id)),
    )


# * Проверяет завершили ли все игроки свои действия и автоматически заканчивает ночь
async def _maybe_finish_night(trigger_message, game: str):
    """
    If all required actors acted for the current night -> calls end_night().
    Uses DB state to avoid double-finishing.
    """
    game = _safe_game_id(game)
    lock = _get_night_lock(game)

    should_finish = False
    async with lock:
        connection = sqlite3.connect(mafia_path, check_same_thread=False)
        cursor = connection.cursor()
        _ensure_night_state_tables(cursor, game)

        row = cursor.execute("SELECT night_no, status FROM night_meta WHERE game = ?", (game,)).fetchone()
        if not row:
            return

        night_no, status = int(row[0]), str(row[1])
        if status != "open":
            return

        total = cursor.execute(
            f"SELECT COUNT(*) FROM night_actions_{game} WHERE night_no = ?",
            (night_no,),
        ).fetchone()[0]
        done = cursor.execute(
            f"SELECT COUNT(*) FROM night_actions_{game} WHERE night_no = ? AND done = 1",
            (night_no,),
        ).fetchone()[0]

        if total and done >= total:
            # * mark as closing to avoid double-trigger from concurrent callbacks
            cursor.execute("UPDATE night_meta SET status = ? WHERE game = ?", ("closing", game))
            connection.commit()
            should_finish = True

    if should_finish:
        await end_night(trigger_message, game)


# * Проверяет безопасность ID игры для использования в SQL запросах
def _safe_game_id(game: str) -> str:
    # ? game comes from generated start-code; still keep it safe for dynamic table names
    if not isinstance(game, str) or not re.fullmatch(r"[A-Za-z0-9_]+", game):
        raise ValueError("Invalid game id")
    return game


#* Создает таблицы для системы голосования между ночами
def _ensure_vote_tables(cursor, game: str):
    game = _safe_game_id(game)
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS votes_{game} (
            round INTEGER NOT NULL,
            voter INTEGER NOT NULL,
            target INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            PRIMARY KEY (round, voter)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vote_state (
            game TEXT PRIMARY KEY,
            round INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            message_id INTEGER,
            candidates TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )


# * Преобразует список кандидатов в строку для хранения в БД
def _candidates_to_text(candidates):
    #? store as comma-separated ints
    return ",".join(str(int(x)) for x in candidates)


# * Преобразует строку кандидатов обратно в список
def _text_to_candidates(text: str):
    if not text:
        return []
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out


# * Получает список всех живых игроков в игре
async def _get_alive_players(cursor, game: str):
    game = _safe_game_id(game)
    rows = cursor.execute(
        f"SELECT player FROM game_{game} WHERE liveness = ?",
        ("True",),
    ).fetchall()
    return [r[0] for r in rows]


# * Получает имя игрока по его ID
async def _get_player_name(cursor, game: str, player_id: int) -> str:
    row = cursor.execute(
        "SELECT player_name FROM players WHERE game = ? AND player_id = ?",
        (game, player_id),
    ).fetchall()
    return row[0][0] if row else str(player_id)


# * Создает сообщение с кнопками для голосования в групповом чате
async def _start_vote_round(chat_id: int, game: str, round_no: int, candidates):
    """
    Posts a single vote message in the group chat with inline buttons for candidates.
    Votes are collected via callback handler dv_...
    """
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    _ensure_vote_tables(cursor, game)

    candidates = [int(x) for x in candidates]
    candidates_text = _candidates_to_text(candidates)

    #? Clear any stale votes for this round (if the bot restarts mid-game)
    cursor.execute(f"DELETE FROM votes_{game} WHERE round = ?", (round_no,))
    connection.commit()

    #? Save state (message_id will be updated after send)
    cursor.execute(
        """
        INSERT INTO vote_state (game, round, chat_id, message_id, candidates, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(game) DO UPDATE SET
            round=excluded.round,
            chat_id=excluded.chat_id,
            message_id=excluded.message_id,
            candidates=excluded.candidates,
            status=excluded.status
        """,
        (game, round_no, chat_id, None, candidates_text, "open"),
    )
    connection.commit()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for pid in candidates:
        name = await _get_player_name(cursor, game, pid)
        keyboard.insert(
            types.InlineKeyboardButton(
                text=name,
                callback_data=f"dv_{round_no}_{pid}in{game}",
            )
        )

    alive = await _get_alive_players(cursor, game)
    if round_no == 1:
        text = (
            "🗳 Голосование между ночами!\n\n"
            "Каждый живой игрок должен выбрать, кого исключить.\n"
            f"Проголосовало: 0/{len(alive)}"
        )
    else:
        text = (
            "🗳 Переголосование!\n\n"
            "Равенство голосов. Голосуем только среди кандидатов ниже.\n"
            f"Проголосовало: 0/{len(alive)}"
        )

    sent = await bot.send_message(chat_id, text, reply_markup=keyboard)
    cursor.execute(
        "UPDATE vote_state SET message_id = ? WHERE game = ?",
        (sent.message_id, game),
    )
    connection.commit()

    #? prepare event for this round
    ev = _VOTE_EVENTS.get(game)
    if ev is None or ev.is_set():
        ev = asyncio.Event()
        _VOTE_EVENTS[game] = ev
    else:
        ev.clear()

    return sent.message_id


# * Обрабатывает голоса в дневном голосовании между ночами
@dp.callback_query_handler(Text(startswith='dv_', ignore_case=True))
async def between_nights_vote_callback(call: types.CallbackQuery):
    """
    Callback format: dv_{round}_{target}in{game}
    Stores vote in votes_{game} and signals the waiting coroutine when all alive voted.
    """
    try:
        payload = call.data.split("dv_")[1]
        round_str = payload.split("_")[0]
        rest = payload.split("_", 1)[1]
        target_str = rest.split("in")[0]
        game = rest.split("in")[1].split()[0]
        round_no = int(round_str)
        target_id = int(target_str)
        game = _safe_game_id(game)
    except Exception:
        await call.answer("Ошибка голоса", show_alert=False)
        return

    voter_id = call.from_user.id

    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    _ensure_vote_tables(cursor, game)
    connection.commit()

    #? Check state is open and round matches
    state_rows = cursor.execute(
        "SELECT round, chat_id, message_id, candidates, status FROM vote_state WHERE game = ?",
        (game,),
    ).fetchall()
    if not state_rows:
        await call.answer("Голосование не активно", show_alert=False)
        return

    active_round, chat_id, message_id, candidates_text, status = state_rows[0]
    candidates = _text_to_candidates(candidates_text)

    if status != "open" or int(active_round) != int(round_no):
        await call.answer("Этот раунд уже закрыт", show_alert=False)
        return

    #? only in correct chat message
    if call.message and (call.message.chat.id != int(chat_id) or call.message.message_id != int(message_id)):
        await call.answer("Неактуальное сообщение", show_alert=False)
        return

    #? voter must be alive
    alive_check = cursor.execute(f"SELECT liveness FROM game_{game} WHERE player = ?",(voter_id,),).fetchall()
    if not alive_check or alive_check[0][0] != "True":
        await call.answer("Ты не можешь голосовать", show_alert=True)
        return

    #? target must be allowed and alive
    if int(target_id) not in set(candidates):
        await call.answer("Нельзя голосовать за этого игрока", show_alert=True)
        return

    target_alive = cursor.execute(
        f"SELECT liveness FROM game_{game} WHERE player = ?",
        (int(target_id),),
    ).fetchall()
    if not target_alive or target_alive[0][0] != "True":
        await call.answer("Этот игрок уже выбыл", show_alert=True)
        return

    #? Upsert vote (one vote per alive voter per round)
    now_ts = int(time.time())
    cursor.execute(
        f"""
        INSERT INTO votes_{game} (round, voter, target, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(round, voter) DO UPDATE SET
            target=excluded.target,
            created_at=excluded.created_at
        """,
        (round_no, voter_id, int(target_id), now_ts),
    )
    connection.commit()

    #? Update progress in the vote message
    alive_players = await _get_alive_players(cursor, game)
    voted_count = cursor.execute(
        f"SELECT COUNT(*) FROM votes_{game} WHERE round = ?",
        (round_no,),
    ).fetchall()[0][0]

    try:
        if round_no == 1:
            new_text = (
                "🗳 Голосование между ночами!\n\n"
                "Каждый живой игрок должен выбрать, кого исключить.\n"
                f"Проголосовало: {voted_count}/{len(alive_players)}"
            )
        else:
            new_text = (
                "🗳 Переголосование!\n\n"
                "Равенство голосов. Голосуем только среди кандидатов ниже.\n"
                f"Проголосовало: {voted_count}/{len(alive_players)}"
            )
        await call.message.edit_text(new_text, reply_markup=call.message.reply_markup)
    except Exception:
        pass

    await call.answer("Голос учтён", show_alert=False)

    #? Finish round when all alive voted
    if voted_count >= len(alive_players):
        cursor.execute("UPDATE vote_state SET status = ? WHERE game = ?", ("closed", game))
        connection.commit()
        ev = _VOTE_EVENTS.get(game)
        if ev is None:
            ev = asyncio.Event()
            _VOTE_EVENTS[game] = ev
        ev.set()


# * Подсчитывает голоса и возвращает результаты голосования
def _tally_votes(votes_rows, allowed_targets):
    allowed_set = set(int(x) for x in allowed_targets)
    tally = {int(x): 0 for x in allowed_set}
    for (_round, _voter, target, _created_at) in votes_rows:
        target = int(target)
        if target in allowed_set:
            tally[target] = tally.get(target, 0) + 1
    return tally


# * Завершает раунд голосования и определяет победителя или лидеров при ничьей
async def _finalize_vote_round(cursor, game: str, round_no: int, candidates):
    """
    Returns (winner_id, leaders_list, tally_dict)
    winner_id is non-None only if a single leader exists.
    """
    game = _safe_game_id(game)
    votes = cursor.execute(
        f"SELECT round, voter, target, created_at FROM votes_{game} WHERE round = ?",
        (round_no,),
    ).fetchall()
    tally = _tally_votes(votes, candidates)
    if not tally:
        return None, [], {}
    max_votes = max(tally.values())
    leaders = [pid for pid, cnt in tally.items() if cnt == max_votes]
    if len(leaders) == 1:
        return leaders[0], leaders, tally
    return None, leaders, tally


# * Проводит полное голосование между ночами с возможными переголосованиями и исключает игрока
async def between_nights_vote_and_kill(message: types.Message, game: str) -> bool:
    """
    Runs the between-nights voting in the group chat.
    - Round 1: vote among all alive players
    - If tie for first place: revote among tied players only
    - If still tie: pick random among tied

    Returns True if game ended after vote-kill, else False.
    """
    game = _safe_game_id(game)
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    _ensure_vote_tables(cursor, game)
    connection.commit()

    #? Find chat_id reliably
    try:
        chat_id = cursor.execute("SELECT chat_id FROM messages WHERE game = ?", (game,)).fetchall()[0][0]
    except Exception:
        chat_id = message.chat.id

    alive = await _get_alive_players(cursor, game)
    if len(alive) < 2:
        return await check_game_end(message, game)

    #? Round 1
    round_no = 1
    await _start_vote_round(chat_id, game, round_no, alive)

    ev = _VOTE_EVENTS.get(game)
    try:
        await asyncio.wait_for(ev.wait(), timeout=300)  #? 5 minutes
    except asyncio.TimeoutError:
        #? proceed with what we have
        pass

    winner, leaders, _tally = await _finalize_vote_round(cursor, game, round_no, alive)

    #? Tie -> revote among leaders only
    if winner is None and len(leaders) >= 2:
        round_no = 2
        await _start_vote_round(chat_id, game, round_no, leaders)
        ev = _VOTE_EVENTS.get(game)
        try:
            await asyncio.wait_for(ev.wait(), timeout=180)  #? 3 minutes
        except asyncio.TimeoutError:
            pass

        winner2, leaders2, _tally2 = await _finalize_vote_round(cursor, game, round_no, leaders)
        if winner2 is None and len(leaders2) >= 2:
            winner = random.choice(leaders2)
        else:
            winner = winner2 if winner2 is not None else random.choice(leaders)

    if winner is None:
        winner = random.choice(alive)

    #? Kill voted player
    cursor.execute(f"UPDATE game_{game} SET liveness = ? WHERE player = ?", ("False", int(winner)))
    connection.commit()

    dead_name = await _get_player_name(cursor, game, int(winner))
    await bot.send_message(chat_id, f"⚖️ По итогам голосования исключён: {dead_name}")

    #? Check end after vote kill
    if await check_game_end(message, game):
        return True
    return False


#? EN: Creates a new Mafia game in the current chat and posts a join link for players to register.
#* RU: Создаёт новую игру «Мафия» в текущем чате и отправляет ссылку, по которой игроки могут зарегистрироваться.
@dp.message_handler(commands=["мафия", " мафия"], commands_prefix=["!", '.', '/'])
async def get_ref(message: types.Message):
    if message.from_user.id == message.chat.id:
        await message.answer("В разработке")
        return
    
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    pwo = PasswordGenerator()
    code = pwo.shuffle_password('abhtsyufjkx12345678', 8)
    link = f'https://t.me/werty_chat_manager_bot?start={code}'
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



#? EN: Handles /start with a game code, registers the user as a Mafia player and updates the lobby message.
#* RU: Обрабатывает /start с кодом игры, регистрирует пользователя в мафии и обновляет сообщение‑лобби.
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



    link = f'https://t.me/werty_chat_manager_bot?start={args}'
    button = types.InlineKeyboardButton(text="Присоединиться", url=link)
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(button)
    new_text = f'{text}\n<a href="https://t.me/{username}">{user_name}</a>'
    await bot.edit_message_text(chat_id=chat_id, message_id=int(mess), text = new_text,parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=keyboard)
    cursor.execute('UPDATE messages SET text = ? WHERE game = ?', (new_text, args))
    connection.commit()
    await message.answer(f"Вы зарегестрированны")



#? EN: Distributes Mafia roles randomly among registered players in this chat and starts the game.
#* RU: Случайным образом раздаёт роли в мафии среди зарегистрированных игроков этого чата и запускает игру.
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
    
    #* раздача ролей


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
        
    #* начало игры

    await start_game(message, game)
    #* cursor.execute('DELETE FROM players')
    #* connection.commit()

    #* cursor.execute('DELETE FROM messages')
    #* connection.commit()


#? EN: Helper to start the Mafia game – simply switches to the first night phase.
#* RU: Вспомогательная функция запуска игры в мафию – переводит игру к первой ночи.
async def start_game(message, game):
    await start_night(message, game)


#? EN: Starts the night phase: announces night, prepares state and sends night tasks to all active roles.
#* RU: Запускает ночную фазу: объявляет ночь, подготавливает состояние и рассылает задания всем активным ролям.
async def start_night(message,game):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    #? Always announce night start in the group chat
    try:
        chat_id = cursor.execute('SELECT chat_id FROM messages WHERE game = ?', (game,)).fetchall()[0][0]
    except Exception:
        chat_id = message.chat.id
    try:
        await bot.send_message(chat_id, "🌙 Ночь началась, проверьте ЛС бота")
    except Exception:
        #? don't fail the night if we can't post to chat
        pass
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

    #? Register required night actors for auto-finish
    try:
        _ensure_night_state_tables(cursor, game)
        actors = []
        if doctor:
            actors.append((int(doctor), "doctor"))
        if police:
            actors.append((int(police), "police"))
        if don_mafia:
            actors.append((int(don_mafia), "don_mafia"))
        for mid in mafia:
            actors.append((int(mid), "mafia"))
        if maniak:
            actors.append((int(maniak), "maniak"))
        _begin_new_night(cursor, game, actors)
        connection.commit()
    except Exception:
        #? If state init fails, keep game playable (manual /test can still end night)
        pass
    

    #* if mafia == []
    #*     #* TODO: стоп игра 
    #*     return
    if doctor:
        await doctor_funk(message, game, doctor)
    if police:
        await police_funk(message, game, police)
    if don_mafia:
        await don_mafia_funk(message, game, don_mafia)
    for id in mafia:
        await mafia_funk(message,game, id, don_mafia)
    if maniak:
        await maniak_funk(message, game, maniak)

#? EN: Sends the doctor a list of players to heal during the night phase.
#* RU: Отправляет доктору список игроков для лечения в ночной фазе.
async def doctor_funk(message, game, doctor):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        if player[0] == doctor:
            continue
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'lek_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1


    await bot.send_message(chat_id=doctor, text='Кого ты хочешь вылечить?', reply_markup=keyboard)


#? EN: Sends the police/commissioner a list of players to investigate during the night.
#* RU: Отправляет комиссару список игроков для проверки в ночной фазе.
async def police_funk(message, game, police):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        if player[0] == police:
            continue
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'check_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1
    await bot.send_message(chat_id=police, text='Кого ты хочешь проверить?', reply_markup=keyboard)


#? EN: Sends the mafia don a list of players to kill during the night phase.
#* RU: Отправляет дону мафии список игроков для убийства в ночной фазе.
async def don_mafia_funk(message, game, don_mafia):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        if player[0] == don_mafia:
            continue
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        btn = types.InlineKeyboardButton(text=name, callback_data=f'don_{player[0]}in{game}')
        keyboard.add(btn)
    await bot.send_message(chat_id=don_mafia, text='Кого ты хочешь убить?', reply_markup=keyboard)


#? EN: Sends mafia members a list of players to suggest to the don for killing.
#* RU: Отправляет мафии список игроков для предложения дону на убийство.
async def mafia_funk(message, game, mafia, don_mafia):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    players_id = []
    count = 0
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        if player[0] == mafia or player[0] == don_mafia:
            continue
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        players_id.append(player[0])
        btn = types.InlineKeyboardButton(text=name, callback_data=f'maf_{player[0]}in{game}')
        keyboard.add(btn)
        count +=1
    await bot.send_message(chat_id=mafia, text='Кого ты хочешь предложить дону?', reply_markup=keyboard)


#? EN: Sends the maniac a list of players to kill during the night phase.
#* RU: Отправляет маньяку список игроков для убийства в ночной фазе.
async def maniak_funk(message, game, maniak):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    players = cursor.execute(f'SELECT player FROM game_{game} WHERE liveness = ?', ('True', )).fetchall()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for player in players:
        if player[0] == maniak:
            continue
        name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, player[0])).fetchall()[0][0]
        btn = types.InlineKeyboardButton(text=name, callback_data=f'man_{player[0]}in{game}')
        keyboard.add(btn)
    await bot.send_message(chat_id=maniak, text='Кого ты хочешь убить?', reply_markup=keyboard)


# * Завершает ночь, обрабатывает все действия и объявляет результаты
async def end_night(message, game):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    #? mark night closed (prevents double end from concurrent callbacks)
    try:
        _ensure_night_state_tables(cursor, game)
        cursor.execute("UPDATE night_meta SET status = ? WHERE game = ?", ("closed", game))
        connection.commit()
    except Exception:
        pass

    #? Resolve chat_id for posting results and next phases
    try:
        chat_id = cursor.execute('SELECT chat_id FROM messages WHERE game = ?', (game,)).fetchall()[0][0]
    except Exception:
        chat_id = message.chat.id
    
    #* Получаем всех игроков и их статусы ночи
    night_data = cursor.execute(f'SELECT user, doctor, mafia, maniak FROM night_{game}').fetchall()
    
    dead_players = []
    saved_players = []
    
    for player_data in night_data:
        user_id, doctor, mafia, maniak = player_data
        
        #* Если игрока лечил доктор - он 100% жив
        if doctor == 1:
            name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, user_id)).fetchall()[0][0]
            saved_players.append(name)
            continue
            
        #* Если игрока убивали мафия или маньяк - он мертв
        if mafia == 1 or maniak == 1:
            name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, user_id)).fetchall()[0][0]
            dead_players.append(name)
            #* Обновляем статус жизни игрока
            cursor.execute(f'UPDATE game_{game} SET liveness = ? WHERE player = ?', ('False', user_id))
    
    connection.commit()
    
    #* Формируем сообщение о результатах ночи
    result_text = "🌅 Наступило утро!\n\n"
    
    if dead_players:
        result_text += f"💀 Этой ночью погибли: {', '.join(dead_players)}\n"
    else:
        result_text += "✅ Этой ночью никто не погиб\n"
        
    if saved_players:
        result_text += f"🏥 Доктор спас: {', '.join(saved_players)}\n"
    
    try:
        await bot.send_message(chat_id, result_text)
    except Exception:
        await message.answer(result_text)

    #* Проверяем конец игры (и, если нужно, завершаем)
    if await check_game_end(message, game):
        return

    #* Между ночами — голосование, затем снова ночь
    ended = await between_nights_vote_and_kill(message, game)
    if ended:
        return

    #* Готовим таблицу ночи для следующего раунда (пересоздаём список живых)
    cursor.execute(f'DELETE FROM night_{game}')
    alive_players = cursor.execute(f"SELECT player FROM game_{game} WHERE liveness = ?", ('True',)).fetchall()
    for (player_id,) in alive_players:
        cursor.execute(
            f'INSERT INTO night_{game} (user, doctor, mafia, maniak) VALUES (?, ?, ?, ?)',
            (player_id, 0, 0, 0),
        )
    connection.commit()

    #* Запускаем новую ночь с живыми игроками
    await start_night(message, game)


# * Проверяет условия окончания игры (победа мирных/мафии)
async def check_game_end(message, game) -> bool:
    """
    True  -> игра завершена (победитель объявлен, данные по игре очищены)
    False -> игра продолжается

    Условия:
    - Если все мафия + дон мафия мертвы -> победа мирных.
    - Если все мирные (все роли кроме мафии/дона) мертвы -> победа мафии.
    """
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    mafia_alive = cursor.execute(
        f"SELECT COUNT(*) FROM game_{game} "
        f"WHERE liveness = ? AND player_card IN ('mafia', 'don_mafia')",
        ('True',),
    ).fetchall()[0][0]

    peaceful_alive = cursor.execute(
        f"SELECT COUNT(*) FROM game_{game} "
        f"WHERE liveness = ? AND player_card NOT IN ('mafia', 'don_mafia')",
        ('True',),
    ).fetchall()[0][0]

    if mafia_alive == 0 and peaceful_alive == 0:
        await end_game(message, game, winner="draw")
        return True

    if mafia_alive == 0:
        await end_game(message, game, winner="peaceful")
        return True

    # * Mafia wins when they control/parity the peaceful side
    if mafia_alive > 0 and mafia_alive >= peaceful_alive:
        await end_game(message, game, winner="mafia")
        return True

    return False


# * Завершает игру, объявляет победителя и очищает данные
async def end_game(message, game, winner: str):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()

    #* Пытаемся получить chat_id из таблицы messages (на случай, если message не из нужного чата)
    try:
        chat_id = cursor.execute('SELECT chat_id FROM messages WHERE game = ?', (game,)).fetchall()[0][0]
    except IndexError:
        chat_id = message.chat.id

    if winner == "peaceful":
        text = "🏆 Игра окончена!\n\nПобеда мирных: вся мафия устранена."
    elif winner == "mafia":
        text = "💀 Игра окончена!\n\nПобеда мафии: все мирные устранены."
    else:
        text = "🤝 Игра окончена!\n\nНичья: в живых не осталось игроков."

    try:
        await bot.send_message(chat_id, text)
    except Exception:
        #* если не получилось — хотя бы не падаем
        await message.answer(text)

    #* Чистим данные игры, чтобы можно было создать новую в этом чате
    cursor.execute(f'DROP TABLE IF EXISTS night_{game}')
    cursor.execute(f'DROP TABLE IF EXISTS game_{game}')
    cursor.execute('DELETE FROM players WHERE game = ?', (game,))
    cursor.execute('DELETE FROM messages WHERE game = ?', (game,))
    connection.commit()


# * Обрабатывает выбор доктора (кого лечить)
@dp.callback_query_handler(Text(startswith='lek_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('lek_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE night_{game} SET doctor = ? WHERE user = ?', (1, id))
    #? mark doctor acted
    try:
        _mark_night_done(cursor, game, call.from_user.id)
    except Exception:
        pass
    connection.commit()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    await call.message.edit_text(f"Ты выбрал {name}, он не умрет")
    await _maybe_finish_night(call.message, game)

    
# * Обрабатывает проверку комиссара (узнает роль игрока)
@dp.callback_query_handler(Text(startswith='check_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('check_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    username = cursor.execute('SELECT player_username FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    card = cursor.execute('SELECT player_card FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    #? mark police acted (even if result differs)
    try:
        _mark_night_done(cursor, game, call.from_user.id)
        connection.commit()
    except Exception:
        pass
    if card != 'mafia' and card != 'don_mafia':
        await call.message.edit_text(f'Игрок <a href="https://t.me/{username}">{name}</a> не является мафией(любая другая роль)',parse_mode='html', disable_web_page_preview=True)
        await _maybe_finish_night(call.message, game)
        return
    else:
        await call.message.edit_text(f'Игрок <a href="https://t.me/{username}">{name}</a> находится в рядах мафиози', parse_mode='html', disable_web_page_preview=True)
        await _maybe_finish_night(call.message, game)
        return

# * Обрабатывает предложение мафии дону (кого убить)
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
    #? mark mafia member acted
    try:
        _mark_night_done(cursor, game, call.from_user.id)
        connection.commit()
    except Exception:
        pass
    await _maybe_finish_night(call.message, game)


# * Обрабатывает выбор дона мафии (кого убить)
@dp.callback_query_handler(Text(startswith='don_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('don_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE night_{game} SET mafia = 1 WHERE user = ?', (id,))
    #? mark don acted
    try:
        _mark_night_done(cursor, game, call.from_user.id)
    except Exception:
        pass
    connection.commit()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    await call.message.edit_text(f"Ты выбрал убить {name}")
    await _maybe_finish_night(call.message, game)


# * Обрабатывает выбор маньяка (кого убить)
@dp.callback_query_handler(Text(startswith='man_', ignore_case=True))
async def successful_recom1(call: types.CallbackQuery):
    id = int((call.data.split('man_')[1]).split('in')[0])
    game = (call.data.split('in')[1]).split()[0]
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f'UPDATE night_{game} SET maniak = 1 WHERE user = ?', (id,))
    #? mark maniak acted
    try:
        _mark_night_done(cursor, game, call.from_user.id)
    except Exception:
        pass
    connection.commit()
    name = cursor.execute('SELECT player_name FROM players WHERE game = ? AND player_id = ?', (game, id)).fetchall()[0][0]
    await call.message.edit_text(f"Ты выбрал убить {name}")
    await _maybe_finish_night(call.message, game)
    

#? EN: Shows the bot's main menu with clan information and available commands.
#* RU: Показывает главное меню бота с информацией о клане и доступными командами.
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

    ]

    commands = types.InlineKeyboardButton(text='⚒️ Команды', url='https://ivansalou288-tech.github.io/chat_manager_bot/html/USER_GUIDE.html')
    web = types.InlineKeyboardButton(text='👨‍💻 Наш сайт', url='https://ivansalou288-tech.github.io/chat_manager_bot/html/index.html')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons).add(commands).add(web)

    await bot.send_photo(message.chat.id,photo=open(f'{curent_path}/photos/klan_ava.jpg', 'rb'), caption=f'Приветсвуем тебя в <b>WERTY | Чат-менеджер</b>\n\n{is_in_klan}\n\nЧто ты хочешь сделать?', parse_mode='html',reply_markup=keyboard)

#? EN: Terminates the game via 'stop' command and cleans up all related database tables.
#* RU: Завершает игру по команде 'stop' и очищает все связанные таблицы базы данных.
@dp.message_handler(commands=["stop"], commands_prefix=["!", '.', '/'])
async def stop_game(message: types.Message):
    if message.from_user.id != 1240656726:
        await message.answer('нет иди нахуй')
        return
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT game FROM messages WHERE chat_id = ?', (message.chat.id,))
        game = cursor.fetchall()[0][0]
        game = _safe_game_id(game)
    except IndexError:
        await message.answer('В этом чате нет активных игр')
        return
    
    # * Очищаем основные таблицы
    cursor.execute('DELETE FROM players WHERE game = ?', (game,))
    cursor.execute('DELETE FROM messages WHERE game = ?', (game,))
    
    # * Удаляем динамические таблицы созданные в процессе игры
    cursor.execute(f'DROP TABLE IF EXISTS game_{game}')
    cursor.execute(f'DROP TABLE IF EXISTS night_{game}')
    cursor.execute(f'DROP TABLE IF EXISTS night_actions_{game}')
    cursor.execute(f'DROP TABLE IF EXISTS votes_{game}')
    
    # * Очищаем метаданные (только если таблицы существуют)
    try:
        cursor.execute('DELETE FROM night_meta WHERE game = ?', (game,))
    except sqlite3.OperationalError:
        pass  # Таблица не существует
    try:
        cursor.execute('DELETE FROM vote_state WHERE game = ?', (game,))
    except sqlite3.OperationalError:
        pass  # Таблица не существует
    
    connection.commit()
    
    # * Очищаем события из памяти
    if game in _VOTE_EVENTS:
        del _VOTE_EVENTS[game]
    if game in _NIGHT_LOCKS:
        del _NIGHT_LOCKS[game]
    
    await message.answer('🛑 Игра завершена и все данные очищены')


#? EN: Test command to forcefully end the night phase (admin only).
#* RU: Тестовая команда для принудительного завершения ночи (только для админа).
@dp.message_handler(commands=["test"], commands_prefix=["!", '.', '/'])
async def get_ref(message: types.Message):
    connection = sqlite3.connect(mafia_path, check_same_thread=False)
    cursor = connection.cursor()
    if message.from_user.id != 1240656726:
        await message.answer('нет иди нахуй')
        return
    try:
        cursor.execute('SELECT game FROM messages WHERE chat_id = ?', (message.chat.id,))
        game = cursor.fetchall()[0][0]
        await end_night(message, game)
    except IndexError:
        await message.answer('В этом чате нет активных игр')
    

#? if __name__ == "__main__":
#?     executor.start_polling(dp)





    