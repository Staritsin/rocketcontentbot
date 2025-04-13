import requests
import os
from handlers.state import user_states
from handlers.handlers_voice import handle_voice_transcription
from handlers.handlers_rewrite import handle_rewrite_transcript as handle_rewrite_text
from handlers.handlers_gpt_keywords import extract_keywords_from_text
from handlers.handlers_pexels import get_pexels_clips
from handlers.handlers_capcut_api import create_reels_from_template
from handlers.handlers_subtitles import generate_subtitles
from handlers.handlers_publish import publish_reels
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

BOT_TOKEN = os.environ.get('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
RUNWAY_API_KEY = os.environ.get("RUNWAY_API_KEY")
RUNWAY_API_URL = "https://api.runwayml.com/v1/"
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

headers = {
    "Authorization": f"Bearer {RUNWAY_API_KEY}",
    "Content-Type": "application/json"
}

def test_runway_generation(chat_id):
    prompt = "A futuristic cyberpunk city at night, flying cars, neon lights"
    payload = {
        "prompt": prompt,
        "num_frames": 24,
        "width": 512,
        "height": 512,
        "seed": 42
    }
    try:
        response = requests.post(RUNWAY_API_URL + "videos", headers=headers, json=payload)
        result = response.json()
        if response.status_code == 200:
            video_url = result.get("video_url", "⚠️ Видео не найдено")
            send_message(chat_id, f"🎬 Готово! Вот видео:\n{video_url}")
        else:
            send_message(chat_id, f"❌ Ошибка RunwayML: {result}")
    except Exception as e:
        send_message(chat_id, f"❌ Ошибка при подключении к RunwayML: {e}")

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={
        "chat_id": chat_id,
        "text": text
    })

def handle_capcut(chat_id):
    text = (
        "🎬 Отправь видео, ссылку на Reels конкурента или YouTube-ссылку.\n\n"
        "Я сделаю всё сам: транскрибация → рерайт → ключевые слова → видео из Pexels → шаблон CapCut → субтитры → публикация 🔥"
    )
    requests.post(TELEGRAM_API_URL, json={
        'chat_id': chat_id,
        'text': text
    })
    user_states[chat_id] = {'mode': 'capcut_generation'}

def process_capcut_pipeline(chat_id, input_data):
    try:
        video_path = download_video(input_data)
        transcript = transcribe_video(video_path, chat_id)
        rewritten_text = handle_rewrite_text(chat_id, transcript)
        keywords = extract_keywords_from_text(rewritten_text)
        pexels_clips = get_pexels_clips(keywords)
        final_video_url = create_reels_from_template(chat_id, pexels_clips, rewritten_text)
        generate_subtitles(chat_id, rewritten_text, final_video_url)
        publish_reels(chat_id, final_video_url)

        keyboard = [
            [InlineKeyboardButton("🌟 Всё получилось", callback_data='success')],
            [InlineKeyboardButton("🔙 В меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard).to_dict()

        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"🎉 Готово! Твой Reels собран и готов к публикации!",
            'reply_markup': reply_markup
        })

    except Exception as e:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': chat_id,
            'text': f"❌ Ошибка во время генерации Reels: {e}"
        })

def download_video(input_data):
    file_id = input_data.get('video', {}).get('file_id') or input_data.get('document', {}).get('file_id')
    if not file_id:
        raise ValueError("Нет file_id для загрузки видео")

    file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
    file_path = file_info['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    local_path = "/tmp/video.mp4"
    with open(local_path, "wb") as f:
        f.write(requests.get(file_url).content)
    return local_path


def transcribe_video(video_path, chat_id):
    try:
        with open(video_path, "rb") as f:
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files={"file": f},
                data={"model": "whisper-1"}
            )
        result = response.json()
        return result.get("text", "❌ Не удалось распознать речь.")
    except Exception as e:
        send_message(chat_id, f"❌ Ошибка транскрибации: {e}")
        raise

