import types
from unittest.mock import call

import aiogram
import sqlite3
from aiogram import executor, Bot, Dispatcher
token="8310916743:AAHqODYdviyxXhPZcsNhN4tpXeIlLm-FAJ8"

bot1 = Bot(token=token)
dp = Dispatcher(bot1)


connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
cursor = connection.cursor()

import telebot

logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])
print(logs_gr, sost_1, sost_2, klan)
bot = telebot.TeleBot(token)

is_in_clan = False
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != message.from_user.id:
        return
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    buttons = [
        telebot.types.InlineKeyboardButton(text="Вступить в клан", callback_data="new_member"),
        telebot.types.InlineKeyboardButton(text="Уже в клане", callback_data="not_new"),
        telebot.types.InlineKeyboardButton(text='Посмотреть канал Werty', url="https://t.me/Werty_Metro")


    ]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    bot.send_photo(chat_id=message.chat.id, photo=open('photos/klan_ava.jpg', 'rb'), reply_markup=keyboard, caption='Приветствуем тебя в нашем боте!\nЧто ты хочешь сделать?')


@bot.callback_query_handler(func=lambda call: True)
def new_member(call):
    if call.data == "not_new":
        # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text='Ты уже в клане! тебе не нужно не куда входить, иди сопровождения делай)')
    if call.data == "new_member":
        # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text = 'Напишите ваш код вступления')
        global is_in_clan
        is_in_clan = True






@bot.message_handler()

def get_text_messages(message):

    if message.chat.id != message.from_user.id:
        return


    global is_in_clan
    if is_in_clan == False:
        return
    connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute("SELECT activate_count, sost FROM links_for_sosts WHERE link_text = ?", (message.text,))
    link_data = cursor.fetchall()

    if link_data == []:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.send_message(chat_id=message.chat.id, text='Неверный код вступления, за новым обратитесь к @werty_pub')
        return
    activate_count, sostav = link_data[0]
    activate_count_new = activate_count - 1
    if activate_count_new == 0:
        cursor.execute('DELETE FROM links_for_sosts WHERE link_text = ?', (message.text,))
        connection.commit()
    else:
        cursor.execute('UPDATE links_for_sosts SET activate_count = ? WHERE link_text = ?', (activate_count_new, message.text))
        connection.commit()



    global name, age, nik_pubg, id_pubg
    def firstSeen(get_id):
        connection = sqlite3.connect('Base_bot.db', check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute(f"SELECT tg_id FROM [{-klan}] WHERE tg_id=?", (get_id,))
        rez = cursor.fetchall()
        if not rez:
            print("add")
            # addUser(get_id)

            return True
        else:
            print('Уже в базе')
            # cursor.execute('UPDATE users SET name, age, nik_pubg, id_pubg = ?, ?, ?, ? WHERE tg_id = ?', (name, age, id_pubg, nik_pubg, get_id))
            return False

    if not firstSeen(message.chat.id):
        bot.send_message(message.chat.id, 'Вы уже участник клана!')
    else:
        print(f'{message.from_user.id} входит в клан')


        def name(message):

            global name, age, nik_pubg, id_pubg
            name = message.text
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши свой возраст:')
            bot.register_next_step_handler(msg, aget)

        def aget(message):
            global name, age, nik_pubg, id_pubg

            try:
                age = int(message.text)
            except ValueError:
                msg = bot.send_message(chat_id=message.chat.id, text='Возраст должен быть одним числом\nНапиши свой возраст:')
                bot.register_next_step_handler(msg, aget)
                return
            if age < 7 or age > 50:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Напиши свой реальный возраст!\nНапиши свой возраст:')
                bot.register_next_step_handler(msg, aget)
                return
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши свой игровой айди:')
            bot.register_next_step_handler(msg, id_pubgt)

        def id_pubgt(message):
            global name, age, nik_pubg, id_pubg
            try:
                id_pubg = int(message.text)
            except ValueError:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Айди должно быть одним числом\nНапиши свое айди:')
                bot.register_next_step_handler(msg, id_pubgt)
                return

            def split_number(number):
                num = []
                while number > 0:
                    digit = number % 10
                    num.append(digit)
                    number = number // 10
                return num[::-1]


            id_p = split_number(id_pubg)
            if id_p[0] != 5 or len(str(id_pubg)) < 9 or len(str(id_pubg)) > 12:
                msg = bot.send_message(chat_id=message.chat.id, text = 'Айди некореткное!\nВведите коректное игровое айди:')
                bot.register_next_step_handler(msg, id_pubgt)
                return
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши игровой ник:')
            bot.register_next_step_handler(msg, nik_pubg)

        def nik_pubg(message):
            global name, age, nik_pubg, id_pubg
            nik_pubg = message.text
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            #функция кидания ссылок на клан, состав, и правил
            addUser(message.from_user.id, message.from_user.username)

        def addUser(tg_id, username):
            global name, age, nik_pubg, id_pubg

            cursor.execute(f'INSERT INTO [{-klan}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (tg_id, username, name, age, nik_pubg, id_pubg, nik_pubg, 0))
            cursor.execute(
                f'INSERT INTO [{-sost_1}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (tg_id, username, name, age, nik_pubg, id_pubg, nik_pubg, 0))
            cursor.execute(
                f'INSERT INTO [{-sost_2}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (tg_id, username, name, age, nik_pubg, id_pubg, nik_pubg, 0))
            connection.commit()
            klan_link = bot.export_chat_invite_link(klan)
            if sostav == 1:
                sostav_link =  bot.export_chat_invite_link(sost_1)
            else:
                sostav_link = bot.export_chat_invite_link(sost_2)
            bot.send_message(message.chat.id,
                             f'Добро пожаловать в клан Werty!\n\nТвое описание:\nИмя: {name}\nВозраст: {age}\nАйди: {id_pubg}\nНик: {nik_pubg}\n\n Твои ссылки на состав и клан:')
            bot.send_message(message.chat.id, klan_link)
            bot.send_message(message.chat.id, sostav_link)
            bot.send_message(logs_gr, f' <a href="tg://user?id={message.chat.id}">Пользователь</a> вошел в клан и {sostav} состав\n\nЕго описание: \nИмя: {name}\nВозраст: {age}\nАйди: {id_pubg}\nНик: {nik_pubg}', parse_mode='html')




        msg = bot.send_message(message.chat.id, 'напиши свое имя:')
        bot.register_next_step_handler(msg, name)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)



