import subprocess
import os

def remove_silence(input_path, output_path):
    subprocess.run([
        "auto-editor",
        input_path,
        "--silent-threshold", "0.03",  # ← это чувствительность тишины
        "--frame-margin", "2",         # ← сколько кадров оставить до/после
        "--add-fade", "0.1",           # ← сглаживание в переходах
        "--video-speed", "1",          # ← ускорение/замедление
        "--export", "video",
        "--output", output_path
    ], check=True)


        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка удаления тишины: {e}")
        return None
