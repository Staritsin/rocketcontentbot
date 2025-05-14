import subprocess
import os

def remove_silence(input_path, output_path, threshold="0.03", margin="2", fade="0.1", speed="1"):
    try:
        subprocess.run([
            "auto-editor",
            input_path,
            "--silent-threshold", threshold,
            "--frame-margin", margin,
            "--add-fade", fade,
            "--video-speed", speed,
            "--export", "video",
            "--output", output_path
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка удаления тишины: {e}")
        return None
