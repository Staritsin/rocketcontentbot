import torch
import torchaudio
from silero_vad import get_speech_timestamps, read_audio, save_audio

def extract_voice_segments(input_path, output_path):
    wav = read_audio(input_path, sampling_rate=16000)
    speech_timestamps = get_speech_timestamps(wav, model='silero_vad', sampling_rate=16000)

    if not speech_timestamps:
        raise ValueError("❌ Речь не найдена — попробуй другое видео")

    save_audio(output_path, wav, speech_timestamps, sampling_rate=16000)
