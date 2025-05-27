import subprocess
import os

def remove_silence(input_path, output_path):
    try:
        # Удаление тишины через ffmpeg без перекодировки видео
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-af", "silenceremove=start_periods=1:start_duration=0.3:start_threshold=-40dB:detection=peak",
            "-c:v", "copy",
            output_path
        ], check=True)

        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при удалении тишины: {e}")
        return None
