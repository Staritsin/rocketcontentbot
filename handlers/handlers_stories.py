import os
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

import uuid
import requests
import subprocess
import ffmpeg  # добавлен
from handlers.utils import send_message, download_telegram_file, send_video
from handlers.handlers_rewrite import handle_rewrite_transcript as handle_rewrite_text
from handlers.handlers_gpt_keywords import extract_keywords_from_text
from handlers.handlers_pexels import get_pexels_clips
from handlers.handlers_capcut_api import create_reels_from_template
from handlers.handlers_subtitles import generate_subtitles
from handlers.handlers_publish import publish_reels
from handlers.state import user_states
from handlers.vad_utils import remove_silence
from handlers.video_merge import merge_videos  # 👈 вставь это


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "stories"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def handle_stories_pipeline(chat_id, file_id):
    # Проверяем, если уже идёт обработка — не запускаем повторно
    if user_states.get(chat_id, {}).get("processing"):
        send_message(chat_id, "⏳ Видео уже обрабатывается. Подожди завершения.")
        return
        
    # Устанавливаем флаг обработки
    user_states[chat_id] = {"processing": True}
    
    mov_path = None
    mp4_path = None
    voice_only_path = None
    processed_path = None
    vertical_path = None
    
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

        # 🔽 Вставить вот это:
        video_paths = [mp4_path] if isinstance(mp4_path, str) else mp4_path

        send_message(chat_id, "🧩 Объединяю видео...")
        
        merged_temp_path = os.path.join(OUTPUT_DIR, f"{file_id}_merged_raw.mp4")
        merged_path = os.path.join(OUTPUT_DIR, f"{file_id}_merged.mp4")
        
        merged_ok = merge_videos(chat_id, video_paths, merged_temp_path)
        
        if not merged_ok or not os.path.exists(merged_temp_path):
            send_message(chat_id, "❌ Ошибка: merge_videos не создал промежуточный файл.")
            user_states[chat_id] = {}
            return
        
        send_message(chat_id, "🧹 Удаляю тишину после склейки...")
        cleaned_path = remove_silence(chat_id, merged_temp_path, merged_path)
        
        if not cleaned_path or not os.path.exists(cleaned_path):
            send_message(chat_id, "❌ Ошибка при удалении тишины после склейки.")
            user_states[chat_id] = {}
            return

        
        send_message(chat_id, "✅ Видео готово. Что делаем дальше?", buttons=[
            ["1️⃣ Опубликовать", "2️⃣ Субтитры", "3️⃣ Вставки"],
            ["4️⃣ Всё сразу"]
        ])
        send_video(chat_id, cleaned_path)


        
        send_message(chat_id, "✅ Видео обработано и склеено. Что делаем дальше?", buttons=[
            ["📤 Опубликовать", "🎬 Наложить субтитры"]
        ])
        send_video(chat_id, merged_path)
        
        user_states[chat_id] = {}


        send_message(chat_id, "🔈 Очищаю звук от шума и дыхания...")
        denoised_path = os.path.join(UPLOAD_DIR, f"{uid}_denoised.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", mp4_path,
            "-af", "highpass=f=150, lowpass=f=3000, afftdn=nf=-25",  # фильтры шумов и частот
            "-c:v", "copy",
            denoised_path
        ], check=True)

        print(f"[DEBUG] denoised_path до remove_silence: {denoised_path}")

        send_message(chat_id, "🔇 Удаляю тишину и ускоряю...")
        voice_only_path = os.path.join(UPLOAD_DIR, f"{uid}_voice.mp4")
        voice_only_path = remove_silence(chat_id, denoised_path, voice_only_path)
        print(f"[DEBUG] voice_only_path из remove_silence: {voice_only_path}")

        if voice_only_path is None:
            send_message(chat_id, "❌ Ошибка при удалении тишины.")
            return

        processed_path = voice_only_path  # <=== ВОТ ЭТА СТРОКА

        send_message(chat_id, "📱 Ресайз под формат 9:16...")
        vertical_path = os.path.join(OUTPUT_DIR, f"{uid}_vertical.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", processed_path,
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

        send_message(chat_id, "📤 Отправляю готовое видео...")

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
                        from handlers.handlers_rewrite import send_video_action_buttons
                        send_video_action_buttons(chat_id)
                        
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
        for f in [mov_path, mp4_path, voice_only_path, processed_path, vertical_path]:
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



import requests
from moviepy.editor import concatenate_videoclips, VideoFileClip
from handlers.handlers_rewrite import send_video_action_buttons

def process_stories_multiple(chat_id, video_ids):
    local_paths = []
    for i, file_id in enumerate(video_ids):
        # Получаем ссылку на файл
        file_info = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        # Скачиваем файл
        local_file = f"uploads/video_{chat_id}_{i}.mp4"
        with open(local_file, "wb") as f:
            f.write(requests.get(file_url).content)
        local_paths.append(local_file)

    # Склеиваем видео
    try:
        # Проверка файлов перед склейкой
        if not local_paths:
            send_message(chat_id, "❌ Не удалось загрузить видео для склейки.")
            return
        
        for path in local_paths:
            if not os.path.exists(path):
                send_message(chat_id, f"❌ Файл не найден: {path}")
                return
        
        try:
            clips = [VideoFileClip(p, audio=True) for p in local_paths]
        except Exception as e:
            send_message(chat_id, f"❌ Ошибка чтения видео: {e}")
            return


        final_clip = concatenate_videoclips(clips)
        output_path = f"stories/final_{chat_id}.mp4"
        
        if not os.path.exists(output_path):
            send_message(chat_id, f"❌ Итоговое видео не создано: {output_path}")
            return

        try:
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        except Exception as e:
            send_message(chat_id, f"❌ Ошибка при сохранении видео: {e}")
            return



        # Отправляем пользователю
        with open(output_path, "rb") as video:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                data={"chat_id": chat_id},
                files={"video": video}
            )
    
        # Удаляем временные файлы
        for path in local_paths:
            os.remove(path)
        if os.path.exists(output_path):
            os.remove(output_path)

        # Кнопки
        send_video_action_buttons(chat_id)

    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка склейки: {e}"
        })

