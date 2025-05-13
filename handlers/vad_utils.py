import torch
import torchaudio
from silero_vad import get_speech_timestamps, read_audio, save_audio, collect_chunks, vad_model

# Инициализация модели
model = vad_model()

def extract_voice_segments(input_path, output_path):
    # Чтение WAV с частотой дискретизации 16кГц
    wav = read_audio(input_path, sampling_rate=16000)

    # Сброс состояний VAD перед началом обработки
    model.reset_states()

    # Получаем временные метки речи
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

    if not speech_timestamps:
        raise ValueError("❌ Речь не найдена — попробуй другое видео")

    # Вырезаем участки с речью и сохраняем
    speech = collect_chunks(wav, speech_timestamps)
    torchaudio.save(output_path, speech.unsqueeze(0), 16000)
