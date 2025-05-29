import subprocess
import os
import ffmpeg
from handlers.utils import send_message



def remove_silence(chat_id, input_path, output_path):
    try:
        normalized_path = input_path  # по умолчанию, если не нужно перекодировать
        
        # Этап 1: Уведомляем пользователя
        send_message(chat_id, f"[1] 🛠️ Начинаю обработку файла: {os.path.basename(input_path)}")
        print(f"[1] Получен файл: {input_path} → будет сохранён как: {output_path}")

        # Этап 2: Составляем команду

        # 🧠 Проверка наличия аудио и видео дорожек
       
        
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
                
            # 🎞️ Шаг доп. Подготовка: нормализуем нестабильные форматы (mov/webm/mkv)
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
                
                input_path = normalized_path  # заменяем путь на новый

            
        # 👇 Команда
            command = [
                "auto-editor",
                normalized_path,
                "--edit", "audio:threshold=2%",
                "--frame_margin", "2",
                "--video_speed", "1",
                "--export", "video",
                "--output-file", output_path,
                "--video_codec", "libx264",
                "--audio_codec", "aac",
                "--overwrite",
                "--no-open"
            ]


            print(f"[2] Команда auto-editor:\n{' '.join(command)}")
        
        except Exception as e:
            send_message(chat_id, f"⚠️ ffprobe вызвал ошибку: {str(e)}")
            return


        # Этап 3: Запускаем auto-editor
        send_message(chat_id, "[2] 🔇 Запускаю auto-editor...")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # 💡 Проверка: файл существует и не пустой
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            send_message(chat_id, "❌ Итоговый файл пустой или не записан. Проверь output_path.")
            print(f"[ОШИБКА] Пустой или повреждённый файл: {output_path}")
            return
        
        # 🖨️ Логи stdout/stderr для отладки
        print(f"[3] Auto-editor stdout:\n{result.stdout}")
        print(f"[3] Auto-editor stderr:\n{result.stderr}")
                

        # ⬇️ Проверка кодека через ffprobe (добавь сразу после запуска auto-editor)
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
                

        print(f"[3] Auto-editor stdout:\n{result.stdout}")
        print(f"[3] Auto-editor stderr:\n{result.stderr}")

        # Этап 4: Проверка существования выходного файла
        if not os.path.exists(output_path):
            send_message(chat_id, f"⚠️ Обработка завершилась, но файл не найден: {output_path}")
            print(f"[ОШИБКА] Файл не найден: {output_path}")
            return None

        # Этап 5: Успех
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
