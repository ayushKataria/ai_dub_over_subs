import subprocess
import sys
import os

def remove_vocals(file_name: str, device: str):
    python_path = sys.executable
    inference_path = os.path.join("vocal-remover", "inference.py")

    commands = [python_path, inference_path, "--input", file_name, "--output_dir", r"."]
    if device == "cuda":
        commands += ["--gpu", "0"]
    subprocess.call(commands)

if __name__ == "__main__":
    remove_vocals("Making a smart closet with ML.mp4", device="cuda")
    

