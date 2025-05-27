import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Преобразование MOV → MP4, если нужно
        if input_path.lower().endswith('.mov'):
            mp4_path = input_path.replace('.mov', '_converted.mp4')
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vcodec", "libx264", "-acodec", "aac",
                mp4_path
            ], check=True)
            input_path = mp4_path

        # Удаление тишины
        subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=3%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "video",
            "--output-file", output_path,
            "--video-codec", "libx264"
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при удалении тишины: {e}")
        return None
