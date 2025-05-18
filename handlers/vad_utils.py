import subprocess
import os


def remove_silence(input_path, output_path):
    try:
        subprocess.run([
            "auto-editor",
            input_path,
            "--edit", "audio:threshold=3%",
            "--frame_margin", "2",
            "--video-speed", "1",
            "--export", "video",
            "--output", output_path
        ], check=True)


        return output_path  # ✅ должен быть на этом уровне, не глубже

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка удаления тишины: {e}")
        return None
