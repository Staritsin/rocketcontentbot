import torch
import numpy as np
import torchaudio
from silero_vad import get_speech_timestamps, read_audio, save_audio

# Загружаем модель и утилиты один раз
vad_model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)

(get_speech_timestamps, _, read_audio, _, _) = utils

def extract_voice_segments(input_path, output_path):
    wav = read_audio(input_path, sampling_rate=16000)

    # ← исправлено: передаём модель, а не строку
    speech_timestamps = get_speech_timestamps(wav, vad_model, sampling_rate=16000)

    if not speech_timestamps:
        raise ValueError("❌ Речь не найдена — попробуй другое видео")

    # Сохраняем файл с вырезанными фрагментами речи
    save_audio(output_path, wav, speech_timestamps, sampling_rate=16000)
