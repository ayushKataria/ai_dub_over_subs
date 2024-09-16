import subprocess
import json
from moviepy.editor import *
from tts import update_wav_speed

def merge(folder_name: str = ".\tts_files"):
    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)
    
    with open("concat_file.txt", "w") as file:
        file.write("file silence.wav\n")
        for subtitle in subtitles:
            file.write(f"outpoint {round(subtitle['start'], 0)}\n")
            file.write(f"file {subtitle['file_name']}\n")
            file.write("file silence.wav\n")
    
    subprocess.call(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'concat_file.txt', '-c', 'copy', 'output.wav'])

    subprocess.call(["ffmpeg", "-i", "output.wav", "-f", "wav", "-bitexact", "-acodec", "pcm_s16le", "output_new.wav"])

    # new_file = update_wav_speed("output_new.wav", 300, "./")

    videoclip = VideoFileClip("Making a smart closet with ML.mp4")
    new_clip = videoclip.without_audio()
    audioclip = AudioFileClip("output_new.wav")

    new_clip_with_audio = new_clip.set_audio(audioclip) 
    new_clip_with_audio.write_videofile("output.mp4")


if __name__ == "__main__":
    merge()