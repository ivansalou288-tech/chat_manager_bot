"""
Интеграция API сервера с админ-ботом
Запускает REST API для Mini App одновременно с ботом
"""

from admin_api import create_app
from aiohttp import web
import asyncio
import threading
import logging

logger = logging.getLogger(__name__)


class APIServer:
    """Управление API сервером"""
    
    def __init__(self, user_id=None, host='0.0.0.0', port=8080):
        """
        Args:
            user_id: ID администратора для проверки доступа
            host: Адрес для запуска сервера
            port: Порт для запуска сервера
        """
        self.user_id = user_id
        self.host = host
        self.port = port
        self.app = None
        self.runner = None
        self.loop = None
        self.thread = None
    
    async def _run_async(self):
        """Асинхронный запуск сервера"""
        self.app = create_app()
        if self.user_id:
            self.app['user_id'] = self.user_id
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        
        logger.info(f'API сервер запущен на http://{self.host}:{self.port}')
        logger.info(f'Endpoints:')
        logger.info(f'  - GET  /api/users/{{chat}}  (klan, sost-1, sost-2)')
        logger.info(f'  - GET  /api/permissions/{{chat}}')
        logger.info(f'  - POST /api/check-access')
        
        # Ждем бесконечно
        await asyncio.Event().wait()
    
    def _run_in_thread(self):
        """Запуск цикла событий в отдельном потоке"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._run_async())
        except asyncio.CancelledError:
            logger.info('API сервер остановлен')
        except Exception as e:
            logger.error(f'Ошибка API сервера: {e}')
        finally:
            self.loop.close()
    
    def start(self):
        """Запуск сервера в отдельном потоке"""
        self.thread = threading.Thread(target=self._run_in_thread, daemon=True)
        self.thread.start()
        logger.info(f'API сервер запускается на {self.host}:{self.port}...')
    
    async def stop(self):
        """Остановка сервера"""
        if self.runner:
            await self.runner.cleanup()
            logger.info('API сервер остановлен')


def start_api_server(user_id=None, host='0.0.0.0', port=8080):
    """
    Удобная функция для запуска API сервера
    
    Использование в admin_bot.py:
        from admin_integration import start_api_server
        
        # Запускаем API
        start_api_server(user_id=1240656726)
        
        # Запускаем бота как обычно
        if __name__ == "__main__":
            executor.start_polling(dp)
    
    Args:
        user_id: ID администратора (из can_admin_panel)
        host: Хост для запуска
        port: Порт для запуска
    """
    server = APIServer(user_id=user_id, host=host, port=port)
    server.start()
    return server


# Пример использования в admin_bot.py
if __name__ == '__main__':
    # Демонстрация
    from admin_config import can_admin_panel
    
    # Получаем ID первого админа
    admin_id = can_admin_panel[0] if can_admin_panel else None
    
    # Запускаем API
    print(f"Запуск API для пользователя {admin_id}")
    api_server = start_api_server(user_id=admin_id)
    
    # Ваш основной код здесь
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Завершение работы...")
