from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database paths
current_path = Path(__file__).parent.parent.parent
main_path = current_path / 'databases' / 'Base_bot.db'

# Chat IDs mapping
CHAT_IDS = {
    'klan': None,
    'sost-1': None,
    'sost-2': None
}

# Admin users who can access the panel
ADMIN_USERS = [8015726709, 1401086794, 1240656726]

def init_chat_ids():
    """Initialize chat IDs from database"""
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    CHAT_IDS['klan'] = -int(cursor.execute("SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchone()[0])
    CHAT_IDS['sost-1'] = -int(cursor.execute("SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchone()[0])
    CHAT_IDS['sost-2'] = -int(cursor.execute("SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchone()[0])
    connection.close()

@app.route('/api/check-access', methods=['POST', 'OPTIONS'])
def check_access():
    """Check if user has access to admin panel"""
    if request.method == 'OPTIONS':
        return '', 204
    data = request.json
    user_id = data.get('user_id', 0)
    return jsonify({'has_access': user_id in ADMIN_USERS})

@app.route('/api/users/<chat_key>', methods=['GET', 'OPTIONS'])
def get_users(chat_key):
    """Get users list for specific chat"""
    if request.method == 'OPTIONS':
        return '', 204
    if chat_key not in CHAT_IDS:
        return jsonify({'error': 'Invalid chat key'}), 400
    
    chat_id = CHAT_IDS[chat_key]
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        users_count_reg = cursor.execute(f'SELECT COUNT(*) FROM [{-chat_id}]').fetchone()[0] - 1
        users_count = cursor.execute('SELECT count FROM count_users WHERE chat_id = ?', (chat_id,)).fetchone()[0]
        cursor.execute(f'SELECT * FROM [{-chat_id}]')
        users_data = cursor.fetchall()
        
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 
                      'Заместитель', 'Менеджер', 'Владелец')
        
        users = []
        for idx, user in enumerate(users_data):
            if user[1] != 'all':
                users.append({
                    'number': idx + 1,
                    'tg_id': user[0],
                    'username': user[1],
                    'name': user[2],
                    'age': user[3],
                    'pubg_nick': user[4],
                    'pubg_id': user[5],
                    'nik': user[6],
                    'rang': user[7],
                    'rang_name': rangs_name[user[7]] if user[7] < len(rangs_name) else 'Неизвестно',
                    'last_date': user[8],
                    'date_vhod': user[9],
                    'mess_count': user[10]
                })
        
        return jsonify({
            'users_count_reg': users_count_reg,
            'users_count': users_count,
            'users': users
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/api/permissions/<chat_key>', methods=['GET', 'OPTIONS'])
def get_permissions(chat_key):
    """Get command permissions for specific chat"""
    if request.method == 'OPTIONS':
        return '', 204
    if chat_key not in ['klan', 'sost-1']:
        return jsonify({'error': 'Invalid chat key'}), 400
    
    table_name = 'klan' if chat_key == 'klan' else 'sostav'
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    
    try:
        cursor.execute(f'SELECT * FROM [{table_name}]')
        dks = cursor.fetchall()
        
        command_names = {
            'ban': 'Блокировка пользователей',
            'mut': 'Ограничение пользователей',
            'warn': 'Предупреждение пользователей',
            'all': 'Созыв пользователей',
            'rang': 'Изменение ранга пользователей',
            'dk': 'Изменение доступа вызова команд',
            'change_pravils': 'Изменение правил чата',
            'close_chat': 'Изменение ограничений чата',
            'change_priv': 'Изменение приветствия чата',
            'obavlenie': 'Создание объявления',
            'tur': 'Создание турниров',
            'dell': 'Удаление сообщений'
        }
        
        permissions = []
        for command in dks:
            permissions.append({
                'command': command[0],
                'command_name': command_names.get(command[0], command[0]),
                'access': command[1]
            })
        
        return jsonify({'permissions': permissions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    init_chat_ids()
    print('✓ API сервер запускается...')
    print('✓ Доступен на http://0.0.0.0:8080')
    print('✓ Для Telegram Mini App используйте ngrok или публичный сервер')
    app.run(host='0.0.0.0', port=8080, debug=True)
