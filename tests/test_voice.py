import pytest
import asyncio
from pathlib import Path
import tempfile
from src.voice.tts_manager import EdgeTTSManager
from src.voice.audio_utils import safe_unlink

@pytest.fixture
def tts_manager():
    """Фикстура для TTS менеджера"""
    return EdgeTTSManager(temp_dir=Path(tempfile.gettempdir()))

@pytest.mark.asyncio
async def test_tts_initialization(tts_manager):
    """Тест инициализации TTS менеджера"""
    assert tts_manager.default_voice == "ru-RU-SvetlanaNeural"
    assert isinstance(tts_manager.available_voices, dict)
    assert len(tts_manager.available_voices) > 0

@pytest.mark.asyncio
async def test_text_to_speech(tts_manager):
    """Тест генерации речи"""
    test_text = "Привет, это тест"
    user_id = 12345
    
    audio_path = await tts_manager.text_to_speech(test_text, user_id)
    
    assert audio_path is not None
    assert audio_path.exists()
    assert audio_path.stat().st_size > 1000
    
    # Чистим
    safe_unlink(audio_path)

@pytest.mark.asyncio
async def test_empty_text(tts_manager):
    """Тест с пустым текстом"""
    audio_path = await tts_manager.text_to_speech("", 12345)
    assert audio_path is None

@pytest.mark.asyncio
async def test_get_available_voices(tts_manager):
    """Тест получения списка голосов"""
    voices = await tts_manager.get_available_voices()
    assert isinstance(voices, list)
    
    # Проверяем структуру голосов
    if voices:
        voice = voices[0]
        assert "ShortName" in voice
        assert "Gender" in voice
        assert "Locale" in voice