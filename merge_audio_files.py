import subprocess
import json
from moviepy.editor import *
from tts import update_wav_speed

def merge(file_name: str, target_language: str = ""):
    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)
    
    with open("concat_file.txt", "w") as file:
        file.write("file silence.wav\n")
        for subtitle in subtitles:
            file.write(f"outpoint {int(subtitle['end'])}\n")
            file.write(f"file {subtitle['file_name']}\n")
            # file.write("file silence.wav\n")
    
    subprocess.call(['ffmpeg', "-loglevel", "error", '-f', 'concat', '-safe', '0', '-i', 'concat_file.txt', '-c', 'copy', 'output.wav'])

    subprocess.call(["ffmpeg", "-loglevel", "error", "-i", "output.wav", "-f", "wav", "-bitexact", "-acodec", "pcm_s16le", "output_new.wav"])

    # new_file = update_wav_speed("output_new.wav", 300, "./")

    videoclip = VideoFileClip(file_name)
    new_clip = videoclip.without_audio()
    audioclip = AudioFileClip("output_new.wav")
    audioclip_instrumental = AudioFileClip(file_name.replace(".mp4", "_Instruments.wav"))
    audioclip_combined = CompositeAudioClip([audioclip, audioclip_instrumental])

    new_clip_with_audio = new_clip.set_audio(audioclip_combined) 
    new_clip_with_audio.write_videofile(f"{file_name}_{target_language}.mp4")


if __name__ == "__main__":
    merge()