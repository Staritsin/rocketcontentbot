import os
import tempfile
import subprocess
from handlers.vad_utils import remove_silence

def merge_videos(chat_id, video_paths, final_output_path):
    processed_paths = []

    for i, path in enumerate(video_paths):
        temp_output = os.path.join(tempfile.gettempdir(), f"processed_{i}.mp4")
        cleaned_path = remove_silence(chat_id, path, temp_output)

        if cleaned_path:
            processed_paths.append(cleaned_path)

    if not processed_paths:
        return None

    list_file = os.path.join(tempfile.gettempdir(), "videos_to_merge.txt")
    with open(list_file, "w") as f:
        for path in processed_paths:
            f.write(f"file '{path}'\n")

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
            final_output_path
        ], check=True)
        return final_output_path


    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка склейки видео: {e}")
        return None
