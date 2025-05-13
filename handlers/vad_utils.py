import torch
import torchaudio
from silero_vad import get_speech_timestamps, read_audio, save_audio
import os

# Загружаем модель напрямую через torch
model = torch.jit.load("silero_vad.jit")

def extract_voice_segments(input_path, output_path, chat_id=None, send_message=None):
    try:
        if send_message:
            send_message(chat_id, "🧠 Отбираю только голос с помощью VAD...")

        print(f"[VAD] Загружаю аудио: {input_path}")
        wav = read_audio(input_path, sampling_rate=16000)

        print("[VAD] Ищу голосовые фрагменты...")
        model.reset_states()
        speech_timestamps = get_speech_timestamps(wav, model='silero_vad', sampling_rate=16000)

        if not speech_timestamps:
            err = "❌ Речь не найдена — попробуй другое видео"
            if send_message:
                send_message(chat_id, err)
            raise ValueError(err)

        print(f"[VAD] Найдено {len(speech_timestamps)} фрагментов речи")

        chunks = []
        for t in speech_timestamps:
            start = int(t['start'] * 16)
            end = int(t['end'] * 16)
            segment = wav[start:end]
        
            # Применим fade-in и fade-out (длительность по 50 мс = 800 сэмплов при 16к)
            fade_duration = min(800, segment.shape[1] // 4)  # не больше 25% длины
            segment = torchaudio.functional.fade(
                waveform=segment,
                fade_in_len=fade_duration,
                fade_out_len=fade_duration,
                fade_shape='linear'
            )
        
            chunks.append(segment)


        speech = torch.cat(chunks)

        print(f"[VAD] Сохраняю результат: {output_path}")
        torchaudio.save(output_path, speech.unsqueeze(0), 16000)

        # Проверим, что файл не пустой
        if speech.shape[1] == 0:
            os.remove(output_path)
            err = "❌ Ошибка: Silero не нашёл ни одного голосового фрагмента"
            print(f"[VAD] {err}")
            if send_message:
                send_message(chat_id, err)
            return None


        if send_message:
            send_message(chat_id, "✅ Речь успешно выделена")

        return output_path

    except Exception as e:
        error_msg = f"❌ Ошибка фильтрации речи: {str(e)}"
        print(f"[VAD] {error_msg}")
        if send_message:
            send_message(chat_id, error_msg)
        raise
