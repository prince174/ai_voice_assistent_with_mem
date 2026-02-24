from telegram import Update
from telegram.ext import ContextTypes
import logging
import ollama
from pathlib import Path

from src.config.settings import MODEL_NAME, VOICE_ENABLED
from src.config.constants import SYSTEM_PROMPT
from src.database.repository import Database
from src.voice.tts_manager import EdgeTTSManager
from src.voice.stt_processor import STTProcessor
from src.voice.audio_utils import download_voice, convert_to_wav, safe_unlink
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Глобальная переменная для управления голосом
voice_enabled = VOICE_ENABLED

class BotHandlers:
    def __init__(self, db: Database, tts: EdgeTTSManager, stt: STTProcessor):
        self.db = db
        self.tts = tts
        self.stt = stt
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /start"""
        user = update.effective_user
        await self.db.ensure_user(
            user.id, user.username, user.first_name, user.last_name
        )
        
        voice_status = "включены 🎤" if voice_enabled else "отключены 🔇"
        
        await update.message.reply_text(
            f"🤖 Привет, {user.first_name}!\n"
            f"Я Telegram-бот с голосовыми функциями!\n\n"
            f"🎙️ Отправь голосовое — я распознаю и отвечу голосом\n"
            f"💬 Могу и просто текстом\n\n"
            f"Голосовые ответы: {voice_status}\n\n"
            f"*Команды:*\n"  # Звездочки для жирного текста в Markdown
            f"/set\_voice — выбрать голос\n"  # Экранируем underscore
            f"/test\_edge\_tts — тест голоса\n"
            f"/voice\_on — включить голос\n"
            f"/voice\_off — выключить голос\n"
            f"/reset — очистить историю 🧹\n"
            f"/stats — статистика 📊",
            parse_mode='Markdown'  # Оставляем Markdown
        )
        
    async def voice_on(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Включить голосовые ответы"""
        global voice_enabled
        voice_enabled = True
        await update.message.reply_text("🔊 Голосовые ответы включены!")
    
    async def voice_off(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выключить голосовые ответы"""
        global voice_enabled
        voice_enabled = False
        await update.message.reply_text("🔇 Голосовые ответы отключены")
    
    async def test_edge_tts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тестирует Edge TTS с диагностикой"""
        await update.message.reply_text("🔊 Тестирую Microsoft Neural Voices...")
        
        try:
            # Получаем актуальный список голосов
            voices = await self.tts.get_available_voices()
            
            if voices:
                voice_list = "\n".join([f"- {v['ShortName']}: {v['Gender']}" for v in voices[:10]])
                await update.message.reply_text(f"✅ Найдены голоса:\n{voice_list}")
            else:
                await update.message.reply_text("⚠️ Использую стандартные голоса")
                voices = [
                    {"ShortName": "ru-RU-SvetlanaNeural", "Gender": "Female"},
                    {"ShortName": "ru-RU-DmitryNeural", "Gender": "Male"},
                ]
            
            # Тестируем первые 3 голоса
            success = False
            for voice_info in voices[:3]:
                voice_name = voice_info['ShortName']
                await update.message.reply_text(f"🔄 Пробую голос: {voice_name}...")
                
                audio_path = await self.tts.text_to_speech(
                    f"Привет! Это тестовое сообщение голосом {voice_name}.", 
                    update.effective_user.id,
                    voice=voice_name
                )
                
                if audio_path and audio_path.exists():
                    with open(audio_path, 'rb') as f:
                        await update.message.reply_voice(voice=f)
                    
                    safe_unlink(audio_path)
                    await update.message.reply_text(f"✅ Голос {voice_name} работает!")
                    success = True
                    break
                else:
                    await update.message.reply_text(f"❌ Голос {voice_name} не сработал")
            
            if not success:
                await update.message.reply_text("❌ Ни один голос не сработал. Проверьте подключение к интернету.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}\n\nПроверьте подключение к интернету и попробуйте снова.")
    
    async def set_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установить предпочитаемый голос"""
        user_id = update.effective_user.id
        
        if not context.args:
            voices = await self.tts.get_available_voices()
            voice_list = "\n".join([f"{i+1}. {v['ShortName']} ({v['Gender']})" 
                                   for i, v in enumerate(voices[:10])])
            await update.message.reply_text(
                f"Доступные голоса:\n{voice_list}\n\n"
                f"Используйте: /set_voice <название_голоса>\n"
                f"Например: /set_voice ru-RU-MikhailNeural"
            )
            return
        
        selected_voice = context.args[0]
        self.tts.voice_preferences[user_id] = selected_voice
        await update.message.reply_text(f"✅ Голос изменен на: {selected_voice}")

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить историю диалога для пользователя"""
        user_id = update.effective_user.id

        try:
            # Используем метод класса Database
            await self.db.delete_user_history(user_id)

            await update.message.reply_text(
                "🧹 История диалога очищена!\n"
                "Можем начать общение заново."
            )
            logger.info(f"🧹 Пользователь {user_id} очистил историю")

        except Exception as e:
            logger.error(f"Ошибка при очистке истории: {e}")
            await update.message.reply_text("❌ Не удалось очистить историю")

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать статистику использования"""
        user_id = update.effective_user.id

        try:
            # Получаем статистику через метод класса Database
            stats = await self.db.get_user_stats(user_id)

            # Форматируем даты
            first_date = stats['first_msg'].strftime("%d.%m.%Y %H:%M") if stats['first_msg'] else "нет данных"
            last_date = stats['last_msg'].strftime("%d.%m.%Y %H:%M") if stats['last_msg'] else "нет данных"

            # Используем HTML для форматирования
            stats_text = (
                f"<b>📊 Ваша статистика</b>\n\n"
                f"💬 Всего сообщений: {stats['total']}\n"
                f"👤 Ваших сообщений: {stats['user_msgs']}\n"
                f"🤖 Ответов бота: {stats['bot_msgs']}\n"
                f"📅 Первое сообщение: {first_date}\n"
                f"🕐 Последнее сообщение: {last_date}\n"
            )

            if stats['total'] > 0:
                user_percent = (stats['user_msgs'] / stats['total']) * 100
                bot_percent = (stats['bot_msgs'] / stats['total']) * 100
                stats_text += f"\n<b>📈 Соотношение:</b>\n"
                stats_text += f"   👤 {user_percent:.1f}% / 🤖 {bot_percent:.1f}%"

            await update.message.reply_text(stats_text, parse_mode='HTML')
            logger.info(f"📊 Пользователь {user_id} запросил статистику")

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text("❌ Не удалось получить статистику")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик голосовых сообщений"""
        user = update.effective_user
        voice = update.message.voice
        
        logger.info(f"🎤 [{user.id}] Получено голосовое, длительность: {voice.duration}с")
        
        # Показываем статус
        await update.message.chat.send_action(action="typing")
        await update.message.reply_text("🎧 Распознаю речь...")
        
        ogg_path = None
        wav_path = None
        audio_path = None
        
        try:
            # 1. Скачиваем голосовое
            ogg_path = await download_voice(voice.file_id, context)
            
            # 2. Конвертируем в WAV
            wav_path = convert_to_wav(ogg_path)
            
            # 3. Распознаём речь
            user_text = self.stt.transcribe(wav_path)
            logger.info(f"📝 Распознано: {user_text}")
            
            # 4. Показываем пользователю, что услышали
            await update.message.reply_text(f"📝 Вы сказали: {user_text}")
            
            # 5. Сохраняем в БД
            await self.db.ensure_user(user.id, user.username, user.first_name, user.last_name)
            await self.db.save_message(user.id, 'user', user_text)
            await self.db.trim_history(user.id)
            
            # 6. Получаем историю и генерируем ответ
            history = await self.db.get_history(user.id)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history)
            
            response = ollama.chat(model=MODEL_NAME, messages=messages)
            answer = response.get("message", {}).get("content", "")
            
            if not answer.strip():
                await update.message.reply_text("⚠️ Модель вернула пустой ответ.")
                return
            
            # 7. Сохраняем ответ
            await self.db.save_message(user.id, "assistant", answer, MODEL_NAME)
            await self.db.trim_history(user.id)
            
            # 8. Отправляем ответ (с голосом или без)
            if voice_enabled and answer.strip():
                await update.message.reply_text("🔊 Генерирую голосовой ответ...")
                audio_path = await self.tts.text_to_speech(answer, user.id)
                
                if audio_path and audio_path.exists():
                    with open(audio_path, 'rb') as audio_file:
                        await update.message.reply_voice(
                            voice=audio_file,
                            caption="🎤 Голосовой ответ"
                        )
                else:
                    await update.message.reply_text(answer)
                    logger.warning("⚠️ Голос не сгенерировался, отправлен только текст")
            else:
                await update.message.reply_text(answer)
            
        except Exception as e:
            error_msg = f"❌ Ошибка при обработке голоса: {e}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
        finally:
            # Чистим временные файлы
            safe_unlink(ogg_path)
            safe_unlink(wav_path)
            safe_unlink(audio_path)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user = update.effective_user
        user_text = update.message.text
        audio_path = None
        
        await self.db.ensure_user(user.id, user.username, user.first_name, user.last_name)
        await self.db.save_message(user.id, 'user', user_text)
        await self.db.trim_history(user.id)
        
        logger.info(f"📨 [{user.id}] Текст: {user_text[:50]}...")
        
        await update.message.chat.send_action(action="typing")
        
        try:
            history = await self.db.get_history(user.id)
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages.extend(history)
            
            response = ollama.chat(model=MODEL_NAME, messages=messages)
            answer = response.get("message", {}).get("content", "")
            
            if not answer.strip():
                await update.message.reply_text("⚠️ Модель вернула пустой ответ.")
                return
            
            await self.db.save_message(user.id, "assistant", answer, MODEL_NAME)
            await self.db.trim_history(user.id)
            
            if voice_enabled:
                audio_path = await self.tts.text_to_speech(answer, user.id)
                if audio_path and audio_path.exists():
                    with open(audio_path, 'rb') as audio_file:
                        await update.message.reply_voice(voice=audio_file)
                else:
                    await update.message.reply_text(answer)
            else:
                await update.message.reply_text(answer)
                
        except Exception as e:
            error_msg = f"❌ Ошибка: {e}"
            logger.error(error_msg)
            await update.message.reply_text(error_msg)
        finally:
            safe_unlink(audio_path)