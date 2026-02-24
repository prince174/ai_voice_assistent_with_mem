#!/usr/bin/env python3
"""
Скрипт для тестирования всех доступных голосов Edge TTS
Запуск: python scripts/test_voices.py
"""

import asyncio
import edge_tts
from pathlib import Path
import sys
from typing import List, Dict

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_voice(voice: str, text: str, output_dir: Path) -> bool:
    """Тестирует один голос"""
    try:
        output_path = output_dir / f"test_{voice}.mp3"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
        
        if output_path.exists() and output_path.stat().st_size > 1000:
            print(f"✅ {voice}: работает")
            return True
        else:
            print(f"⚠️ {voice}: файл слишком мал")
            return False
    except Exception as e:
        print(f"❌ {voice}: ошибка - {e}")
        return False

async def main():
    """Основная функция"""
    print("🔊 Тестирование Edge TTS голосов\n")
    
    # Создаем папку для тестов
    test_dir = Path("test_audio")
    test_dir.mkdir(exist_ok=True)
    
    # Получаем список всех голосов
    print("📋 Получение списка голосов...")
    voices = await edge_tts.list_voices()
    
    # Фильтруем русские голоса
    russian_voices = [v for v in voices if 'ru-RU' in v['Locale']]
    
    print(f"\n🇷🇺 Найдено русских голосов: {len(russian_voices)}")
    
    # Тестовый текст
    test_text = "Привет! Это тест голоса. Раз, два, три, проверка."
    
    # Тестируем каждый голос
    working_voices = []
    for i, voice in enumerate(russian_voices, 1):
        voice_name = voice['ShortName']
        print(f"\n[{i}/{len(russian_voices)}] Тестирую {voice_name}...")
        
        if await test_voice(voice_name, test_text, test_dir):
            working_voices.append(voice_name)
    
    # Выводим результаты
    print("\n" + "="*50)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"\n✅ Рабочие голоса ({len(working_voices)}):")
    for voice in working_voices:
        print(f"  - {voice}")
    
    # Обновляем список для tts_manager.py
    print(f"\n📝 Обновите список в tts_manager.py:")
    print("self.available_voices = {")
    for voice in working_voices:
        gender = "Male" if "Male" in voice else "Female"  # Приблизительно
        print(f'    "{voice}": "{gender}",')
    print("}")

if __name__ == "__main__":
    asyncio.run(main())