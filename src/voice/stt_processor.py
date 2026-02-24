from faster_whisper import WhisperModel
from pathlib import Path
from typing import Optional

class STTProcessor:
    def __init__(self, model_size: str = "base", device: str = "cpu"):
        self.model = WhisperModel(model_size, device=device, compute_type="int8")
    
    def transcribe(self, audio_path: Path, language: str = "ru") -> str:
        segments, _ = self.model.transcribe(str(audio_path), language=language)
        return " ".join(segment.text for segment in segments).strip()