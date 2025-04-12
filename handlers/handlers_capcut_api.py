
import requests
import os

CAPCUT_API_KEY = os.environ.get("CAPCUT_API_KEY")
CAPCUT_TEMPLATE_ID = "your-template-id"  # TODO: заменить на ID шаблона CapCut

def create_reels_from_template(chat_id, video_clips, text):
    try:
        # 1. Подготовка данных
        video_urls = [clip['video_url'] for clip in video_clips]

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

        # 2. Отправка запроса на создание видео
        response = requests.post("https://api.capcut.com/v1/render", json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result.get("video_url", "")

    except Exception as e:
        raise RuntimeError(f"Ошибка создания видео в CapCut: {e}")
