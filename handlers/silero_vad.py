import torch
import numpy as np

class VoiceActivityDetector:
    def __init__(self, model_path='silero_vad.jit', threshold=0.5, min_speech_duration_ms=250):
        self.model = torch.jit.load(model_path)
        self.model.eval()
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.sample_rate = 16000

    def get_speech_timestamps(self, audio):
        if isinstance(audio, np.ndarray):
            audio = torch.from_numpy(audio).float()
        if len(audio.shape) == 2:
            audio = audio.mean(dim=0)
        audio = audio / torch.max(torch.abs(audio))

        window_size_samples = int(self.sample_rate * self.min_speech_duration_ms / 1000)
        speech = []
        triggered = False
        current_start = 0

        probs = []
        for i in range(0, len(audio), window_size_samples):
            chunk = audio[i:i + window_size_samples]
            if len(chunk) < window_size_samples:
                break
            with torch.no_grad():
                prob = self.model(chunk.unsqueeze(0), self.sample_rate).item()
            probs.append(prob)

            if prob >= self.threshold and not triggered:
                current_start = i
                triggered = True
            elif prob < self.threshold and triggered:
                speech.append({'start': current_start, 'end': i})
                triggered = False

        if triggered:
            speech.append({'start': current_start, 'end': len(audio)})

        return speech
