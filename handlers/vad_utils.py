import torch
import torchaudio
from silero_vad import get_speech_timestamps, read_audio

def extract_voice_segments(input_path, output_path):
    wav = read_audio(input_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, model='silero_vad', sampling_rate=16000)

    if not speech_timestamps or len(speech_timestamps) == 0:
        raise ValueError("❌ Речь не найдена — попробуй другое видео")

    chunks = []
    for t in speech_timestamps:
        start = int(t['start'] * 16)
        end = int(t['end'] * 16)
        chunks.append(wav[start:end])

    if not chunks:
        raise ValueError("❌ Не удалось извлечь голосовые фрагменты")

    speech = torch.cat(chunks)
    torchaudio.save(output_path, speech.unsqueeze(0), 16000)
