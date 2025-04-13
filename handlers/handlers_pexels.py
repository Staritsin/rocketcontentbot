import requests
import os

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/videos/search"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

def get_pexels_clips(keywords, max_results=3):
    """
    Ищет видео по ключевым словам на Pexels и возвращает список ссылок на mp4.
    """
    result_videos = []

    for keyword in keywords:
        response = requests.get(PEXELS_API_URL, headers=HEADERS, params={
            "query": keyword,
            "per_page": max_results
        })
        if response.status_code != 200:
            continue

        data = response.json()
        for video in data.get("videos", []):
            # Возьмем самое маленькое по размеру видео для быстрого Reels
            video_url = sorted(video["video_files"], key=lambda v: v["width"])[0]["link"]
            result_videos.append({
                "keyword": keyword,
                "video_url": video_url
            })

    return result_videos
