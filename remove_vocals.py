import subprocess

def remove_vocals(file_name: str):
    subprocess.call([r"./.venv/Scripts/python.exe", "vocal-remover\inference.py", "--input", file_name, "--output_dir", r"./"])

if __name__ == "__main__":
    remove_vocals("Making a smart closet with ML.mp4")
    

