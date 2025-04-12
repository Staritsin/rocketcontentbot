import requests
import os
from handlers.state import user_states
from handlers.handlers_voice import handle_voice_transcription
from handlers.handlers_rewrite import handle_rewrite_text
from handlers.handlers_gpt_keywords import extract_keywords_from_text
from handlers.handlers_pexels import get_pexels_clips
from handlers.handlers_capcut_api import create_reels_from_template
from handlers.handlers_subtitles import generate_subtitles
from handlers.handlers_publish import publish_reels
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'


def handle_capcut(chat_id):
    text = (
        "🎬 Отправь видео, ссылку на Reels конкурента или YouTube-ссылку.\n\n"
        "Я сделаю всё сам: транскрибация → рерайт → ключевые слова → видео из Pexels → шаблон CapCut → субтитры → публикация 🔥"
    )
    requests.post(f"{TELEGRAM_API_URL}", json={
        'chat_id': chat_id,
        'text': text
    })
    user_states[chat_id] = {'mode': 'capcut_generation'}


def process_capcut_pipeline(chat_id, input_data):
    try:
        # 1. Получение видео
        video_path = download_video(input_data)

        # 2. Транскрибация
        transcript = transcribe_video(video_path, chat_id)

        # 3. Рерайт
        rewritten_text = handle_rewrite_text(chat_id, transcript)

        # 4. Извлечение ключевых слов
        keywords = extract_keywords_from_text(rewritten_text)

        # 5. Поиск видеофутажей
        pexels_clips = get_pexels_clips(keywords)

        # 6. Генерация видео через CapCut
        final_video_url = create_reels_from_template(chat_id, pexels_clips, rewritten_text)

        # 7. Субтитры
        generate_subtitles(chat_id, rewritten_text, final_video_url)

        # 8. Публикация
        publish_reels(chat_id, final_video_url)

        # Успешный финал
        keyboard = [
            [InlineKeyboardButton("🌟 Всё получилось", callback_data='success')],
            [InlineKeyboardButton("🔙 В меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard).to_dict()

        requests.post(f"{TELEGRAM_API_URL}", json={
            'chat_id': chat_id,
            'text': f"🎉 Готово! Твой Reels собран и готов к публикации!",
            'reply_markup': reply_markup
        })

    except Exception as e:
        requests.post(f"{TELEGRAM_API_URL}", json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка во время генерации Reels: {e}"
        })


# === TO DO: функция скачивания видео по ссылке/файлу ===
def download_video(input_data):
    # Здесь будет логика для скачивания видео с Telegram, YouTube или Instagram
    # Например, через yt_dlp или скачивание из message['video']
    return "/tmp/video.mp4"  # заглушка
