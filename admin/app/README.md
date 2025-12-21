# Admin Web App - API Server

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

1. Запустите API сервер:
```bash
python api_server.py
```

Сервер будет доступен на `http://localhost:8080`

2. Откройте `index.html` в браузере или разместите на веб-сервере

## API Endpoints

### POST /api/check-access
Проверка доступа пользователя к админ-панели
```json
Request: {"user_id": 123456789}
Response: {"has_access": true}
```

### GET /api/users/{chat_key}
Получение списка пользователей чата
- chat_key: `klan`, `sost-1`, `sost-2`
```json
Response: {
  "users_count_reg": 10,
  "users_count": 15,
  "users": [...]
}
```

### GET /api/permissions/{chat_key}
Получение разрешений команд для чата
- chat_key: `klan`, `sost-1`
```json
Response: {
  "permissions": [
    {"command": "ban", "command_name": "Блокировка пользователей", "access": "Есть"}
  ]
}
```

## Конфигурация

В `index.html` измените `API_BASE_URL` на адрес вашего API сервера:
```javascript
const API_BASE_URL = 'http://localhost:8080/api';
```

Для production используйте:
```javascript
const API_BASE_URL = 'https://your-domain.com/api';
```
