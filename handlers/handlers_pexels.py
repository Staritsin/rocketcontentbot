import requests
import os

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/videos/search"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

def get_pexels_clips(keywords, per_page=3):
    """
    Получает короткие видеоклипы по ключевым словам с Pexels.
    Возвращает список словарей с ключами: video_url, width, height.
    """
    if not PEXELS_API_KEY:
        raise ValueError("PEXELS_API_KEY не установлен в переменных окружения.")

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    result_clips = []

    for keyword in keywords:
        url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={per_page}&orientation=portrait"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for video in data.get("videos", []):
                video_url = video["video_files"][0]["link"]
                width = video["width"]
                height = video["height"]

                result_clips.append({
                    "video_url": video_url,
                    "width": width,
                    "height": height,
                    "source": "pexels",
                    "keyword": keyword
                })

        except Exception as e:
            print(f"⚠️ Ошибка загрузки видео для ключа '{keyword}': {e}")

    return result_clips
