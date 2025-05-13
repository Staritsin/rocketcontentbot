import torch
import numpy as np
import torchaudio
from silero_vad import VoiceActivityDetector

model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    trust_repo=True
)

(get_speech_timestamps, _, read_audio, _, _) = utils

def extract_voice_segments(input_path: str, output_path: str):
    wav = read_audio(input_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=16000)

    if not speech_timestamps:
        raise RuntimeError("⛔ Речь не найдена.")

    # Обрезаем по временным меткам
    chunks = []
    for i, t in enumerate(speech_timestamps):
        start = int(t['start'] * 16)  # 16kHz
        end = int(t['end'] * 16)
        chunks.append(wav[start:end])

    speech = torch.cat(chunks)
    torchaudio.save(output_path, speech.unsqueeze(0), 16000)
