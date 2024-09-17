import subprocess

def remove_vocals(file_name: str, device: str):
    commands = [r"./.venv/Scripts/python.exe", "vocal-remover\inference.py", "--input", file_name, "--output_dir", r"./"]
    if device == "cuda":
        commands += ["--gpu", "0"]
    subprocess.call(commands)

if __name__ == "__main__":
    remove_vocals("Making a smart closet with ML.mp4")
    

