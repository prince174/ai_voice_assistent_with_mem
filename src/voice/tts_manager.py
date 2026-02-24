import edge_tts
import hashlib
from pathlib import Path
import tempfile
from typing import Dict, Optional

class EdgeTTSManager:
    def __init__(self, temp_dir: Path = None):
        self.temp_dir = temp_dir or Path(tempfile.gettempdir())
        self.available_voices = {
            "ru-RU-DmitryNeural": "Male",
            "ru-RU-SvetlanaNeural": "Female",
            "ru-RU-CatherineNeural": "Female",
            "ru-RU-MarinaNeural": "Female",
            "ru-RU-MikhailNeural": "Male",
            "ru-RU-AndreyNeural": "Male",
        }
        self.default_voice = "ru-RU-SvetlanaNeural"
        self.voice_preferences: Dict[int, str] = {}
    
    async def get_available_voices(self, locale: str = "ru-RU"):
        try:
            voices = await edge_tts.list_voices()
            russian_voices = [v for v in voices if locale in v['Locale']]
            for v in russian_voices:
                self.available_voices[v['ShortName']] = v['Gender']
            return russian_voices
        except Exception as e:
            print(f"⚠️ Error getting voices: {e}")
            return []
    
    async def text_to_speech(self, text: str, user_id: int, voice: str = None) -> Optional[Path]:
        if not text or not text.strip():
            return None
        
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        mp3_path = self.temp_dir / f"tts_{user_id}_{text_hash}.mp3"
        
        if mp3_path.exists():
            mp3_path.unlink()
        
        voices_to_try = self._get_voice_priority(user_id, voice)
        
        for attempt_voice in voices_to_try:
            try:
                communicate = edge_tts.Communicate(
                    text[:1000],
                    attempt_voice,
                    rate="+0%",
                    volume="+0%",
                    pitch="+0Hz"
                )
                await communicate.save(str(mp3_path))
                
                if mp3_path.exists() and mp3_path.stat().st_size > 1000:
                    if voice != attempt_voice and user_id not in self.voice_preferences:
                        self.voice_preferences[user_id] = attempt_voice
                    return mp3_path
            except Exception:
                continue
        
        return None
    
    def _get_voice_priority(self, user_id: int, voice: Optional[str]) -> list:
        preferred = voice or self.voice_preferences.get(user_id)
        priority = [
            preferred,
            "ru-RU-SvetlanaNeural",
            "ru-RU-DmitryNeural",
            "ru-RU-CatherineNeural",
            "ru-RU-MarinaNeural",
            "ru-RU-MikhailNeural",
            "ru-RU-AndreyNeural",
        ]
        return [v for v in priority if v and v in self.available_voices]