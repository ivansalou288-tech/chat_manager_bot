# Интеграция с Telegram Mini App

## Шаг 1: Запуск API сервера

```bash
python api_server.py
```

## Шаг 2: Публикация API через ngrok

Для работы Telegram Mini App нужен публичный HTTPS URL.

### Установка ngrok:
1. Скачайте с https://ngrok.com/download
2. Зарегистрируйтесь и получите authtoken

### Запуск ngrok:
```bash
ngrok http 8080
```

Вы получите URL вида: `https://xxxx-xx-xx-xx-xx.ngrok-free.app`

## Шаг 3: Настройка index.html

Откройте `index.html` и измените `API_BASE_URL`:

```javascript
const API_BASE_URL = 'https://your-ngrok-url.ngrok-free.app/api';
```

## Шаг 4: Размещение index.html

### Вариант A: GitHub Pages (рекомендуется)
1. Создайте репозиторий на GitHub
2. Загрузите `index.html`
3. Включите GitHub Pages в настройках
4. Получите URL: `https://username.github.io/repo-name/index.html`

### Вариант B: Netlify/Vercel
1. Перетащите `index.html` на https://app.netlify.com/drop
2. Получите URL

### Вариант C: Тот же ngrok
```bash
# В папке с index.html
python -m http.server 8081

# В другом терминале
ngrok http 8081
```

## Шаг 5: Создание Mini App в BotFather

1. Откройте @BotFather в Telegram
2. Отправьте `/newapp`
3. Выберите вашего бота
4. Введите название: `Admin Panel`
5. Введите описание: `Админ панель для управления`
6. Загрузите иконку 640x360 (опционально)
7. Отправьте GIF/фото (опционально)
8. **Введите Web App URL**: `https://your-github-pages-url/index.html`
9. Введите короткое имя: `admin`

## Шаг 6: Тестирование

Откройте вашего бота в Telegram и нажмите кнопку меню → выберите ваше Mini App

## Важные замечания

1. **HTTPS обязателен** - Telegram Mini Apps работают только через HTTPS
2. **CORS настроен** - API сервер уже настроен для работы с любыми доменами
3. **User ID** - приложение автоматически получает ID пользователя из Telegram
4. **Доступ** - только пользователи из списка `ADMIN_USERS` в `api_server.py` имеют доступ

## Production развертывание

Для production используйте:
- VPS (DigitalOcean, AWS, etc.) для API сервера
- Nginx с SSL сертификатом (Let's Encrypt)
- GitHub Pages/Netlify для frontend

### Пример nginx конфигурации:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        add_header Access-Control-Allow-Origin *;
    }
}
```
