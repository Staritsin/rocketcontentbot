import requests
import os

# Получаем API ключ и ID шаблона из переменных окружения
CAPCUT_API_KEY = os.environ.get("CAPCUT_API_KEY")
CAPCUT_TEMPLATE_ID = os.environ.get("CAPCUT_TEMPLATE_ID")  # ❗️Укажи в .env или окружении

CAPCUT_API_URL = "https://api.capcut.com/v1/render"

def create_reels_from_template(chat_id, video_clips, text):
    """
    Основная функция генерации видео через CapCut API.
    """
    try:
        if not CAPCUT_API_KEY or not CAPCUT_TEMPLATE_ID:
            raise ValueError("❌ Нет API ключа или ID шаблона CapCut.")

        # 1. Собираем список ссылок на футажи
        video_urls = [clip['video_url'] for clip in video_clips]

        # 2. Формируем JSON-запрос
        payload = {
            "template_id": CAPCUT_TEMPLATE_ID,
            "clips": video_urls,
            "text_overlay": text,
            "output_format": "reels",
            "audio_track": "default"
        }

        headers = {
            "Authorization": f"Bearer {CAPCUT_API_KEY}",
            "Content-Type": "application/json"
        }

        # 3. Запрос к CapCut API
        response = requests.post(CAPCUT_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result.get("video_url", "")

    except Exception as e:
        raise RuntimeError(f"❌ Ошибка CapCut API: {e}")
