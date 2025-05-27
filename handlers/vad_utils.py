import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Преобразование в mp4 если нужно
        if not input_path.endswith(".mp4"):
            converted = input_path.replace(".mov", "_converted.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vf", "fps=30",
                "-vcodec", "libx264", "-acodec", "aac",
                converted
            ], check=True)
            input_path = converted

        # Удаление тишины с повторным кодированием
        subprocess.run([
            "auto-editor", input_path,
            "--edit", "audio:threshold=4%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "video",
            "--output-file", output_path,
            "--video-codec", "libx264",
            "--audio-codec", "aac"
        ], check=True)

        print("[DEBUG] Удаление тишины прошло успешно:", output_path)
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка auto-editor: {e}")
        return None
