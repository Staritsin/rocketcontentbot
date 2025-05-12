import os
import uuid
import subprocess
import requests
from handlers.utils import send_message, download_telegram_file

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "stories"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handle_stories_pipeline(chat_id, file_id):
    try:
        uid = str(uuid.uuid4())

        # 1. Скачиваем .mov файл
        mov_path = os.path.join(UPLOAD_DIR, f"{uid}.mov")
        download_telegram_file(file_id, mov_path)

        # 2. Конвертируем в .mp4
        mp4_path = os.path.join(UPLOAD_DIR, f"{uid}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", mov_path,
            "-vcodec", "libx264", "-acodec", "aac",
            mp4_path
        ], check=True)

        # 3. Удаление тишины и ускорение
        voice_path = os.path.join(UPLOAD_DIR, f"{uid}_voice.mp4")
        insert_percent = user_states[chat_id] = {'mode': 'stories_processing', 'inserts_percent': 30}
        subprocess.run([
            "auto-editor", mp4_path,
            "--silent", "remove",
            "--frame_margin", "25",
            "--video_speed", "1.2",
            "--silent_threshold", "3.0",
            "--cut_percent", str(insert_percent),
            "--export_to", voice_only_path,
            "--no_open"
        ], check=True)


        # 4. Ресайз под вертикальный формат
        vertical_path = os.path.join(OUTPUT_DIR, f"{uid}_vertical.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", voice_path,
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy", vertical_path
        ], check=True)

        # 5. Нарезка на куски по 40 секунд
        segment_pattern = os.path.join(OUTPUT_DIR, f"{uid}_part_%03d.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", vertical_path,
            "-c", "copy", "-map", "0",
            "-segment_time", "40", "-f", "segment", segment_pattern
        ], check=True)

        # 6. Отправка первого куска
        first_part = segment_pattern.replace("%03d", "000")
        if os.path.exists(first_part):
            with open(first_part, "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendVideo",
                    data={"chat_id": chat_id},
                    files={"video": f}
                )
            send_message(chat_id, "✅ Сторис готов! 🔥")
        else:
            send_message(chat_id, "⚠️ Ошибка: видео слишком короткое или не сгенерировалось.")

    except Exception as e:
        send_message(chat_id, f"❌ Ошибка обработки: {e}")

    finally:
        for path in [mov_path, mp4_path, voice_path, vertical_path]:
            if os.path.exists(path):
                os.remove(path)
