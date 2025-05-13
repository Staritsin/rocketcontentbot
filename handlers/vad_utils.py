import torch
import torchaudio
from silero_vad import get_speech_timestamps, read_audio, collect_chunks

# Загрузка модели через torch.hub
model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)

def extract_voice_segments(input_path, output_path):
    wav = read_audio(input_path, sampling_rate=16000)
    model.reset_states()  # Обязательно: сброс перед каждой обработкой
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

    if not speech_timestamps:
        raise ValueError("❌ Речь не найдена — попробуй другое видео")

    speech = collect_chunks(wav, speech_timestamps)
    torchaudio.save(output_path, speech.unsqueeze(0), 16000)
