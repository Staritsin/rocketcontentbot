import os
import requests

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
PEXELS_API_URL = "https://api.pexels.com/videos/search"

HEADERS = {
    "Authorization": PEXELS_API_KEY
}

def get_pexels_clips(keywords, max_results=3):
    clips = []
    for keyword in keywords:
        try:
            response = requests.get(
                PEXELS_API_URL,
                headers=HEADERS,
                params={"query": keyword, "per_page": 1}
            )
            data = response.json()
            videos = data.get("videos", [])
            if videos:
                video_url = videos[0]["video_files"][0]["link"]
                clips.append(video_url)
        except Exception as e:
            print(f"❌ Ошибка при поиске футажа по '{keyword}': {e}")
    return clips
