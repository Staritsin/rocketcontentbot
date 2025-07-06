import subprocess
import os
import ffmpeg
from handlers.utils import send_message
import librosa
import torch
import torchaudio

# ✅ Импорт из silero_vad + автоматическая загрузка модели
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from silero_vad.utils_vad import collect_chunks, save_audio

# ✅ Загружаем модель Silero VAD одной строкой
model = load_silero_vad()
model.eval()

# ✅ Утилиты
utils = {
    'get_speech_timestamps': get_speech_timestamps,
    'collect_chunks': collect_chunks,
    'save_audio': save_audio,
    'read_audio': read_audio
}

# ✅ Распаковываем tuple, который возвращает silero_vad()
get_speech_timestamps = utils['get_speech_timestamps']
collect_chunks = utils['collect_chunks']
save_audio = utils['save_audio']
read_audio = utils['read_audio']


def remove_silence(chat_id, input_path, output_path):
    try:
        normalized_path = input_path  # по умолчанию, если не нужно перекодировать

        send_message(chat_id, f"[1] 🛠️ Начинаю обработку файла: {os.path.basename(input_path)}")
        print(f"[1] Получен файл: {input_path} → будет сохранён как: {output_path}")

        try:
            probe = ffmpeg.probe(input_path)
            video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            if not video_streams:
                send_message(chat_id, "❌ В файле нет видеопотока. Пропускаем.")
                return
            if not audio_streams:
                send_message(chat_id, "❌ В файле нет звука. Обработка невозможна.")
                return

            if input_path.endswith((".mov", ".webm", ".mkv")):
                send_message(chat_id, "🧰 Конвертирую видео в стабильный формат перед вырезкой тишины...")
                normalized_path = input_path.replace(".mov", "_normalized.mp4").replace(".webm", "_normalized.mp4").replace(".mkv", "_normalized.mp4")

                convert_cmd = [
                    "ffmpeg", "-y", "-i", input_path,
                    "-vf", "fps=30,scale=720:1280",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
                    "-c:a", "aac", "-b:a", "128k",
                    normalized_path
                ]

                result = subprocess.run(convert_cmd, capture_output=True, text=True)
                print(f"[🪵] FFmpeg нормализация stdout:\n{result.stdout}")
                print(f"[🪵] FFmpeg нормализация stderr:\n{result.stderr}")

                if result.returncode != 0 or not os.path.exists(normalized_path):
                    send_message(chat_id, "❌ Ошибка при нормализации видео. Прерываю обработку.")
                    return

                input_path = normalized_path

            command = [
                "auto-editor",
                input_path,
                "--edit", "audio:threshold=2%",
                "--frame_margin", "2",
                "--video_speed", "1",
                "--export", "default",
                "--output-file", output_path,
                "--video_codec", "libx264",
                "--audio_codec", "aac",
                "--no-open"
            ]

            print(f"[DEBUG] Auto-editor input: {input_path}")
            print(f"[DEBUG] Auto-editor output: {output_path}")
            print(f"[DEBUG] Auto-editor CMD: {' '.join(command)}")
            print(f"[2] Команда auto-editor:\n{' '.join(command)}")

        except Exception as e:
            send_message(chat_id, f"⚠️ ffprobe вызвал ошибку: {str(e)}")
            return

        send_message(chat_id, "[2] 🔇 Запускаю auto-editor...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            send_message(chat_id, "❌ Итоговый файл пустой или не записан. Проверь output_path.")
            print(f"[ОШИБКА] Пустой или повреждённый файл: {output_path}")
            return

        print(f"[3] Auto-editor stdout:\n{result.stdout}")
        print(f"[3] Auto-editor stderr:\n{result.stderr}")

        probe = subprocess.run([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height",
            "-of", "default=noprint_wrappers=1:nokey=1",
            output_path
        ], capture_output=True, text=True)

        print(f"[4] ffprobe:\n{probe.stdout}")

        if not probe.stdout.strip():
            send_message(chat_id, "⚠️ ffprobe не вернул данных. Видео может быть повреждено.")
            print(f"[ОШИБКА] ffprobe не дал результата по файлу: {output_path}")

        if not os.path.exists(output_path):
            send_message(chat_id, f"⚠️ Обработка завершилась, но файл не найден: {output_path}")
            print(f"[ОШИБКА] Файл не найден: {output_path}")
            return None

        send_message(chat_id, "✅ Тишина удалена. Видео готово.")
        print(f"[4] ✅ Готово! Файл сохранён: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        send_message(chat_id, f"❌ Ошибка при выполнении auto-editor: {e}")
        print(f"[ОШИБКА] subprocess error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return None

    except Exception as e:
        send_message(chat_id, f"❌ Общая ошибка: {str(e)}")
        print(f"[ОШИБКА] remove_silence(): {str(e)}")
        return None


def remove_silence_vad(chat_id, input_path, output_path):
    try:
        send_message(chat_id, "🧠 Запускаю точную вырезку по голосу (Silero VAD)...")
        print(f"[VAD] Начинаю анализ: {input_path}")

        wav_path = input_path.replace(".mp4", "_audio.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path
        ], capture_output=True)

        # ✅ Новый способ загрузки WAV — безопасный и точный
        audio = read_audio(wav_path, sampling_rate=16000)

        # ✅ Получение меток речи с return_seconds=True
        speech_timestamps = get_speech_timestamps(audio, model, return_seconds=True)

        if not speech_timestamps:
            send_message(chat_id, "⚠️ Голос не обнаружен. Видео не обработано.")
            return None

        segments = []
        for ts in speech_timestamps:
            start = ts['start']
            end = ts['end']
            segments.append(f"between(t,{start:.2f},{end:.2f})")

        vf_expr = "+".join(segments)

        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"select='{vf_expr}',setpts=N/FRAME_RATE/TB",
            "-af", f"aselect='{vf_expr}',asetpts=N/SR/TB",
            "-c:v", "libx264", "-c:a", "aac",
            output_path
        ], capture_output=True)

        if not os.path.exists(output_path):
            send_message(chat_id, "❌ Не удалось сохранить файл после VAD-обработки.")
            return None

        send_message(chat_id, "✅ Вырезка по голосу завершена. Видео готово.")
        return output_path

    except Exception as e:
        send_message(chat_id, f"❌ VAD ошибка: {str(e)}")
        print(f"[VAD-ERROR]: {e}")
        return None
