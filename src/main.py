import asyncio
import logging
import signal
import sys
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters
)

from src.config.settings import BOT_TOKEN, WHISPER_MODEL
from src.database.repository import Database
from src.voice.tts_manager import EdgeTTSManager
from src.voice.stt_processor import STTProcessor
from src.bot.handlers import BotHandlers
from src.utils.logger import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Глобальные переменные
db = Database()
tts_manager = EdgeTTSManager()
stt_processor = STTProcessor(model_size=WHISPER_MODEL)
handlers = BotHandlers(db, tts_manager, stt_processor)

async def post_init(application):
    """Инициализация после старта"""
    await db.init()
    logger.info("✅ База данных подключена")
    logger.info(f"✅ Whisper модель: {WHISPER_MODEL}")

async def shutdown(application):
    """Корректное завершение работы"""
    logger.info("🛑 Завершение работы бота...")
    
    # Останавливаем приложение Telegram
    if application:
        await application.stop()
    
    # Закрываем соединение с БД
    if db:
        await db.close()
        logger.info("✅ Соединение с БД закрыто")
    
    logger.info("👋 Бот остановлен")

def handle_exit(application):
    """Обработчик сигналов завершения"""
    def signal_handler(sig, frame):
        logger.info(f"Получен сигнал {sig}, завершаем работу...")
        asyncio.create_task(shutdown(application))
        # Даем время на завершение
        asyncio.get_event_loop().call_later(3, lambda: sys.exit(0))
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
def main():
    app = ApplicationBuilder()\
        .token(BOT_TOKEN)\
        .post_init(post_init)\
        .build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("voice_on", handlers.voice_on))
    app.add_handler(CommandHandler("voice_off", handlers.voice_off))
    app.add_handler(CommandHandler("test_edge_tts", handlers.test_edge_tts))
    app.add_handler(CommandHandler("set_voice", handlers.set_voice))
    app.add_handler(CommandHandler("reset", handlers.reset))
    app.add_handler(CommandHandler("stats", handlers.stats))
    
    app.add_handler(MessageHandler(filters.VOICE, handlers.handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text))
    
    logger.info("🚀 Бот запускается...")
    logger.info(f"🎤 Whisper: {WHISPER_MODEL}")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Получен сигнал KeyboardInterrupt")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        asyncio.run(shutdown(app))

if __name__ == "__main__":
    main()