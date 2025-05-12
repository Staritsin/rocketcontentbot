import os
import uuid
import requests
import subprocess
from handlers.utils import send_message, download_telegram_file

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "stories"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handle_stories_pipeline(chat_id, file_id):
    try:
        uid = str(uuid.uuid4())

        send_message(chat_id, "⏳ Скачиваю видео...")
        mov_path = os.path.join(UPLOAD_DIR, f"{uid}.mov")
        download_telegram_file(file_id, mov_path)

        send_message(chat_id, "🎥 Конвертирую в .mp4...")
        mp4_path = os.path.join(UPLOAD_DIR, f"{uid}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", mov_path,
            "-vcodec", "libx264", "-acodec", "aac",
            mp4_path
        ], check=True)

        send_message(chat_id, "🔇 Удаляю тишину и ускоряю...")
        voice_only_path = os.path.join(UPLOAD_DIR, f"{uid}_voice.mp4")
        insert_percent = user_states.get(chat_id, {}).get('inserts_percent', 30)
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

        send_message(chat_id, "📱 Ресайз под формат 9:16...")
        vertical_path = os.path.join(OUTPUT_DIR, f"{uid}_vertical.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", voice_only_path,
            "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy", vertical_path
        ], check=True)

        send_message(chat_id, "✂️ Нарезаю на куски по 40 сек...")
        segment_output = os.path.join(OUTPUT_DIR, f"{uid}_part_%03d.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", vertical_path,
            "-c", "copy", "-map", "0",
            "-segment_time", "40", "-f", "segment",
            segment_output
        ], check=True)

        send_message(chat_id, "📤 Отправляю готовое видео...")
        first_part = segment_output.replace("%03d", "000")
        if os.path.exists(first_part):
            with open(first_part, "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendVideo",
                    data={"chat_id": chat_id},
                    files={"video": f}
                )
            send_message(chat_id, "✅ Сторис готов! 🔥")
        else:
            send_message(chat_id, "⚠️ Видео получилось пустым или слишком коротким.")

    except Exception as e:
        send_message(chat_id, f"❌ Ошибка обработки: {e}")
    finally:
        for f in [mov_path, mp4_path, voice_only_path, vertical_path]:
            if os.path.exists(f):
                os.remove(f)
