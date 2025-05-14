import os
import uuid
import requests
import subprocess
import ffmpeg  # добавлен
from handlers.utils import send_message, download_telegram_file
from handlers.handlers_rewrite import handle_rewrite_transcript as handle_rewrite_text
from handlers.handlers_gpt_keywords import extract_keywords_from_text
from handlers.handlers_pexels import get_pexels_clips
from handlers.handlers_capcut_api import create_reels_from_template
from handlers.handlers_subtitles import generate_subtitles
from handlers.handlers_publish import publish_reels
from handlers.state import user_states
from handlers.vad_utils import remove_silence

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "stories"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handle_stories_pipeline(chat_id, file_id):
    vertical_path = None  # Чтобы не было ошибки в finally


    if user_states.get(chat_id, {}).get("processing") == True:
        send_message(chat_id, "⏳ Видео уже обрабатывается. Подожди завершения.")
        return
    user_states[chat_id] = {"processing": True}
    voice_only_path = None
    
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


        send_message(chat_id, "🔈 Очищаю звук от шума и дыхания...")
        denoised_path = os.path.join(UPLOAD_DIR, f"{uid}_denoised.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", mp4_path,
            "-af", "highpass=f=150, lowpass=f=3000, afftdn=nf=-25",  # фильтры шумов и частот
            "-c:v", "copy",
            denoised_path
        ], check=True)

        send_message(chat_id, "🔇 Удаляю тишину и ускоряю...")
        voice_only_path = os.path.join(UPLOAD_DIR, f"{uid}_voice.mp4")
        
        denoised_path = remove_silence(denoised_path, voice_only_path)
        
        if denoised_path is None:
            send_message(chat_id, "❌ Ошибка при удалении тишины.")
            return

        send_message(chat_id, "📱 Ресайз под формат 9:16...")
        vertical_path = os.path.join(OUTPUT_DIR, f"{uid}_vertical.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", voice_only_path,
            "-vf", "scale='if(gt(a,9/16),720,-2)':'if(gt(a,9/16),-2,1280)',pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy", vertical_path
        ], check=True)

        # Добавлена проверка длины видео
        probe = ffmpeg.probe(vertical_path)
        duration = float(probe['format']['duration'])

        if duration < 40:
            send_message(chat_id, "🎯 Видео короче 40 сек — отправляю как есть.")
            first_part = vertical_path  # Просто используем его без нарезки
        else:
            send_message(chat_id, "✂️ Нарезаю на куски по 40 сек...")
            segment_output = os.path.join(OUTPUT_DIR, f"{uid}_part_%03d.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", vertical_path,
                "-c", "copy", "-map", "0",
                "-segment_time", "40", "-f", "segment",
                segment_output
            ], check=True)
            first_part = segment_output.replace("%03d", "000")


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
            file_size_mb = os.path.getsize(first_part) / (1024 * 1024)
            print(f"📦 Размер файла: {file_size_mb:.2f} MB")

            with open(first_part, "rb") as f:
                try:
                    if file_size_mb < 49:
                        response = requests.post(
                            f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendVideo",
                            data={"chat_id": chat_id},
                            files={"video": f}
                        )
                    else:
                        print("⚠️ Видео слишком большое, отправляю как документ")
                        response = requests.post(
                            f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendDocument",
                            data={"chat_id": chat_id},
                            files={"document": f}
                        )
            
                    result = response.json()
                    print("✅ Ответ Telegram:", result)
            
                    if response.status_code == 200 and result.get("ok"):
                        send_message(chat_id, "✅ Сторис готов! 🔥")
                    else:
                        send_message(chat_id, f"⚠️ Ошибка Telegram: {result.get('description') or 'без описания'}")
            
                except Exception as e:
                    print("❌ Ошибка отправки в Telegram:", e)
                    send_message(chat_id, f"❌ Ошибка при отправке: {str(e)}")


        else:
            send_message(chat_id, "⚠️ Видео получилось пустым или слишком коротким.")

    except Exception as e:
        send_message(chat_id, f"❌ Ошибка обработки: {e}")
    finally:
        for f in [mov_path, mp4_path, voice_only_path, vertical_path]:
            if f and os.path.exists(f):  # ✅ Проверка на None
                os.remove(f)
    
        if chat_id in user_states:
            del user_states[chat_id]



def process_capcut_pipeline(chat_id, input_data):
    try:
        send_message(chat_id, "⏳ Скачиваю видео...")
        video_path = download_telegram_file(input_data, f"/tmp/{uuid.uuid4()}.mp4")

        send_message(chat_id, "🧠 Транскрибирую видео...")
        transcript = transcribe_video(video_path, chat_id)

        send_message(chat_id, "✍️ Делаю рерайт текста...")
        rewritten_text = handle_rewrite_text(chat_id, transcript)

        send_message(chat_id, "🗝 Извлекаю ключевые слова...")
        keywords = extract_keywords_from_text(rewritten_text)

        send_message(chat_id, "🎞 Ищу видео по ключевым словам...")
        pexels_clips = get_pexels_clips(keywords)

        send_message(chat_id, "🎬 Собираю видео в CapCut шаблоне...")
        final_video_url = create_reels_from_template(chat_id, pexels_clips, rewritten_text)

        send_message(chat_id, "🔤 Генерирую субтитры...")
        generate_subtitles(chat_id, rewritten_text, final_video_url)

        send_message(chat_id, "📤 Публикую Reels...")
        publish_reels(chat_id, final_video_url)

    except Exception as e:
        send_message(chat_id, f"❌ Ошибка генерации Reels: {e}")
