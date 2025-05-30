import os
import tempfile
import subprocess
from handlers.vad_utils import remove_silence

def merge_videos(chat_id, video_paths, final_output_path):
    processed_paths = []

    # 🔁 Просто проверяем и собираем пути
    for path in video_paths:
        if os.path.exists(path):
            processed_paths.append(path)

    if not processed_paths:
        return None

    # 📄 Создаём список файлов для ffmpeg
    list_file = os.path.join(tempfile.gettempdir(), "videos_to_merge.txt")
    with open(list_file, "w") as f:
        for path in processed_paths:
            f.write(f"file '{path}'\n")

    # 🧪 Промежуточный путь склеенного видео
    merged_temp_path = os.path.join(tempfile.gettempdir(), "merged_output.mp4")

    try:
        subprocess.run([
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-vf", "format=yuv420p",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            merged_temp_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка склейки видео: {e}")
        return None

    # 🧼 Удаляем тишину уже после склейки
        cleaned_path = remove_silence(chat_id, merged_temp_path, final_output_path)
        
        if not os.path.exists(final_output_path):
            print(f"[ERROR] merge_videos: файл не создан: {final_output_path}")
            return None
        
        return final_output_path

    
   



        

