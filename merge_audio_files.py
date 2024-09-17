import subprocess
import json
from moviepy.editor import *

def merge(file_name: str, target_language: str = ""):
    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)
    
    # Create updated silence file larger than the video
    duration = subtitles[-1]['end'] + 100               # Fetched the end of last subtitle and added 100 just for safety
    generate_silent_wav("silence.wav", duration)
    
    with open("concat_file.txt", "w") as file:
        end = 0
        for subtitle in subtitles:
            update_audio_file(subtitle['file_name'])
            silence_length = round((subtitle['start'] - end), 2)
            file.write("file silence.wav\n")
            file.write(f"outpoint {silence_length}\n")
            file.write(f"file {subtitle['file_name']}\n")
            end = subtitle['end']
    
    subprocess.call(['ffmpeg', "-loglevel", "error", "-y", '-safe', '0', '-f', 'concat', '-i', 'concat_file.txt', 'output.wav'])

    subprocess.call(["ffmpeg", "-loglevel", "error", "-y", "-i", "output.wav", "-f", "wav", "-bitexact", "-acodec", "pcm_s16le", "output_new.wav"])

    # new_file = update_wav_speed("output_new.wav", 300, "./")

    videoclip = VideoFileClip(file_name)
    new_clip = videoclip.without_audio()
    audioclip = AudioFileClip("output_new.wav")
    audioclip_instrumental = AudioFileClip(file_name.replace(".mp4", "_Instruments.wav"))
    audioclip_combined = CompositeAudioClip([audioclip, audioclip_instrumental])

    new_clip_with_audio = new_clip.set_audio(audioclip_combined) 
    new_clip_with_audio.write_videofile(file_name.replace(".mp4", f"_{target_language}.mp4"))

def generate_silent_wav(output_file, duration):
    # ffmpeg command to generate a silent WAV file
    command = [
        'ffmpeg', '-y',  # Overwrite output file if exists
        "-loglevel", "error", # Change loglevel
        '-f', 'lavfi',  # Use lavfi filter
        '-i', f'anullsrc=r=24000:cl=mono',  # Generate silence with sample rate 24000 and mono channel
        '-t', str(duration),  # Duration of the silent audio
        '-acodec', 'pcm_s16le',  # Audio codec PCM signed 16-bit little-endian
        output_file  # Output file
    ]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        print(f"Silent WAV file of {duration} seconds saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error while generating the silent WAV file: {e}")

def update_audio_file(file_path):
    # Define a temporary output file name
    temp_file = file_path + ".temp.wav"

    # ffmpeg command to update the audio file
    command = [
        'ffmpeg', '-y',  # Overwrite the temp file without confirmation
        "-loglevel", "error", # Change loglevel
        '-i', file_path,  # Input audio file
        '-ar', '24000',  # Set the sample rate to 24000 Hz
        '-acodec', 'pcm_s16le',  # Set the codec to PCM signed 16-bit little-endian
        '-b:a', '384k',  # Set the bitrate to 384 kbps
        temp_file  # Temporary output file
    ]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        # print(f"Audio file {file_path} has been processed and saved? to {temp_file}")

        # Replace the original file with the updated file
        os.replace(temp_file, file_path)
        # print(f"Original file {file_path} has been overwritten.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error while updating the audio file: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    merge(file_name="Making a smart closet with ML.mp4", target_language="hi")