import subprocess
import os
import uuid

def remove_silence(input_path, output_path):
    try:
        subprocess.run([
            "auto-editor",
            input_path,
            "--silent-threshold", "0.03",
            "--frame-margin", "2",
            "--add-fade", "0.1",
            "--video-speed", "1",
            "--export", "video",
            "--output", output_path
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка удаления тишины: {e}")
        return None
