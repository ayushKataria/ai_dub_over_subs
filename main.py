import json
import os
import shutil
from transcribe import transcribe
from remove_vocals import remove_vocals
from tts import atts
import asyncio
import argparse
import filetype
from time import time
import gc
import torch

import get_gender
from merge_audio_files import merge

async def main(file_name: str, target_language: str, device: str):
    start = time()

    kind = filetype.guess(file_name)
    if kind.mime != "video/mp4":
        raise Exception("Invalid file type. It currently supports only mp4")

    print(file_name, target_language)
    # Generate subtitles
    print("Generating transciption and translating to target language")
    transcribe(file_name, target_language, device=device)

    # Removing model from memory
    if device == "cuda":
        gc.collect()
        torch.cuda.empty_cache()

    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)
        print(len(subtitles))

    # Generate instrumental track
    print("Removing existing vocals from video")
    remove_vocals(file_name, device)

    # Removing model from memory
    if device == "cuda":
        gc.collect()
        torch.cuda.empty_cache()

    # Get the gender of the speaker
    print("Predicting the gender of speaker for tts")
    gender = get_gender.predict(file_name.replace(".mp4", "_Instruments.wav"), device = device)
    # gender = "Female"

    # Removing model from memory
    if device == "cuda":
        gc.collect()
        torch.cuda.empty_cache()

    voice_to_use = None
    # Generate tts files
    print("Generating TTS files")
    for subtitle in subtitles:
        tts_file_name, voice_to_use = await atts(subtitle[f'text_{target_language}'], target_language, gender, voice_to_use, subtitle['end'] - subtitle['start'])
        subtitle['file_name'] = tts_file_name
    
    with open("subtitles.json", "w") as file:
        json.dump(subtitles, file)
    # Combine tts files
    print("Merging TTS audio files and video")
    merge(file_name=file_name, target_language=target_language, device=device)

    # Cleanup extra files generated
    print("Cleaning up intermediate files")
    cleanup(file_name=file_name)
    
    print(f"Time taken for Dub: {time() - start}")

def cleanup(file_name: str):
    files_to_remove = ["concat_file.txt", "output.wav", "output_new.wav", "subtitles.json", "silence.wav", file_name.replace(".mp4", "_Instruments.wav"), file_name.replace(".mp4", "_Vocals.wav")]
    folders_to_remove = ["tts_files"]
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    for folder_path in folders_to_remove:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AIDubsOverSubs',
                    description='It takes a path to a video file and dubs the audio to a given language')
    parser.add_argument("-f", "--file", required=True, help="Video file path")
    parser.add_argument("-l", "--language", required=True, help="Target language")
    parser.add_argument("-d", "--device", required=False, default=None, help="Device for all the model")
    args = parser.parse_args()

    device = args.device
    if torch.cuda.is_available(): 
        if args.device is None:
            device = "cuda"
    else:
        if args.device is None:
            device = "cpu"
        if args.device == "cuda":
            raise Exception("Cuda not available")
    
    print(f"Using device: {device}")
    
    asyncio.run(main(args.file, args.language, device))