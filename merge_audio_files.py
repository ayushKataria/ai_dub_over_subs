import subprocess
import json
import math
from moviepy.editor import *

slow_langs = ["hi"]

def merge(file_name: str, target_language: str = "", device: str = "cpu"):
    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)
    
    # Create updated silence file larger than the video
    duration = subtitles[-1]['end'] + 100               # Fetched the end of last subtitle and added 100 just for safety
    generate_silent_wav("silence.wav", duration, device)
    
    lossless_output = None

    with open("concat_file.txt", "w") as file:
        end = 0
        silence_debt = 0
        added_seconds = 0
        index = 0
        is_first = True
        for subtitle in subtitles:
            update_audio_file(subtitle['file_name'], device)

            silence_length = math.floor((subtitle['start'] - end))
            silence_debt += ((subtitle['start'] - end)) - float(silence_length)

            if silence_debt >= 1.5 and target_language not in slow_langs:
                silence_length += 1
                silence_debt -= 1.5

            file.write("file silence.wav\n")
            file.write(f"outpoint {silence_length}\n")
            file.write(f"file {subtitle['file_name']}\n")
            
            end = subtitle['end']

            if subtitle['video_slow_down'] != 1:
                if is_first:
                    is_first = False
                    lossless_output = slow_down_video(file_name, subtitle['start'] + added_seconds, subtitle['end'] + added_seconds, subtitle['video_slow_down'])
                else:
                    lossless_output = slow_down_video(lossless_output, subtitle['start'] + added_seconds, subtitle['end'] + added_seconds, subtitle['video_slow_down'], True)
                    index += 1
                added_seconds += (subtitle['end'] - subtitle['start']) * (subtitle['video_slow_down'] - 1)

    if lossless_output != None:
        output_video = final_encode_lossless_to_final(lossless_output, "temp_output.mp4")
    else:
        output_video = file_name
    
    command = ['ffmpeg', "-loglevel", "error", "-y", '-safe', '0', '-f', 'concat', '-i', 'concat_file.txt', 'output.wav']
    if device == "cuda":
        command += ["-hwaccel", "cuda"]
    subprocess.call(command)

    command = ["ffmpeg", "-loglevel", "error", "-y", "-i", "output.wav", "-f", "wav", "-bitexact", "-acodec", "pcm_s16le", "output_new.wav"]
    if device == "cuda":
        command += ["-hwaccel", "cuda"]
    subprocess.call(command)

    # new_file = update_wav_speed("output_new.wav", 300, "./")

    videoclip = VideoFileClip(output_video)
    new_clip = videoclip.without_audio()

    audioclip = AudioFileClip("output_new.wav")
    audioclip_instrumental = AudioFileClip(file_name.replace(".mp4", "_Instruments.wav"))
    audioclip_combined = CompositeAudioClip([audioclip, audioclip_instrumental])

    new_clip_with_audio = new_clip.set_audio(audioclip_combined) 
    new_clip_with_audio.write_videofile(file_name.replace(".mp4", f"_{target_language}.mp4"))

def generate_silent_wav(output_file, duration, device = "cpu"):
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

    if device == "cuda":
        command += ["-hwaccel", "cuda"]

    try:
        # Execute the command
        subprocess.run(command, check=True)
        print(f"Silent WAV file of {duration} seconds saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error while generating the silent WAV file: {e}")

def update_audio_file(file_path, device):
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

    if device == "cuda":
        command += ["-hwaccel", "cuda"]

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
i=0
def slow_down_video(input_video, start_time, end_time, slow_factor, remove_input_file = False):
    global i
    # Load the video
    video = VideoFileClip(input_video)

    print(start_time, end_time, i)
    # 1. Extract the first part (before the slow-motion segment)
    part1 = video.subclip(0, start_time)

    # 2. Extract the slow-motion part and apply the slow factor
    slow_part = video.subclip(start_time, end_time).fx(vfx.speedx, factor=1/slow_factor)

    # 3. Extract the third part (after the slow-motion segment)
    part3 = video.subclip(end_time, video.duration)

    # Ensure all clips have the same fps (to avoid stuck frames)
    part1 = part1.set_fps(video.fps)
    slow_part = slow_part.set_fps(video.fps)
    part3 = part3.set_fps(video.fps)

    # 4. Concatenate the parts together
    final_video = concatenate_videoclips([part1, slow_part, part3], method="compose")


     # 5. Write the result to a lossless format (intermediate step)
    lossless_output = f"intermediate_lossless_{i}.mkv"
    i+=1
    final_video.write_videofile(lossless_output, codec="ffv1", preset="ultrafast", audio=False, fps=video.fps, logger=None)

    if remove_input_file:
        os.remove(input_video)

    return lossless_output


def final_encode_lossless_to_final(intermediate_video, output_video, crf=18, bitrate="3000k"):
    # Load the intermediate lossless video
    lossless_clip = VideoFileClip(intermediate_video)

    # 1. Re-encode the lossless video to final output format (e.g., H.264)
    lossless_clip.write_videofile(output_video, audio=False, logger=None)

    return output_video

if __name__ == "__main__":
    merge(file_name="Making a smart closet with ML.mp4", target_language="hi")
    # slow_down_video("Making a smart closet with ML.mp4", "temp.mp4", 0, 10, 2)