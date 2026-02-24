from pathlib import Path
import tempfile
import os
from pydub import AudioSegment
from telegram.ext import ContextTypes

async def download_voice(file_id: str, context: ContextTypes.DEFAULT_TYPE) -> Path:
    file = await context.bot.get_file(file_id)
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"voice_{file_id}.ogg"
    await file.download_to_drive(temp_path)
    return temp_path

def convert_to_wav(ogg_path: Path, sample_rate: int = 16000) -> Path:
    wav_path = ogg_path.with_suffix('.wav')
    audio = AudioSegment.from_file(ogg_path, format="ogg")
    audio = audio.set_frame_rate(sample_rate).set_channels(1)
    audio.export(wav_path, format="wav")
    return wav_path

def safe_unlink(path: Path):
    try:
        if path and path.exists():
            os.unlink(path)
    except Exception:
        pass