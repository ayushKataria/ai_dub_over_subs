import json
from transcribe import transcribe
from remove_vocals import remove_vocals
from tts import atts
import asyncio
import argparse

import get_gender
from merge_audio_files import merge

async def main(file_name: str, target_language: str):
    print(file_name, target_language)
    # Generate subtitles
    transcribe(file_name, target_language)

    with open("subtitles.json", "r") as file:
        subtitles = json.load(file)

    # Generate instrumental track
    remove_vocals(file_name)

    # Get the gender of the speaker
    gender = get_gender.predict(file_name.replace(".mp4", "_Instruments.wav"))
    # gender = "Female"

    voice_to_use = None
    # Generate tts files
    for subtitle in subtitles:
        file_name, voice_to_use = await atts(subtitle[f'text_{target_language}'], target_language, gender, voice_to_use, subtitle['end'] - subtitle['start'])
        subtitle['file_name'] = file_name
    
    with open("subtitles.json", "w") as file:
        json.dump(subtitles, file)
    # Combine tts files
    merge(folder_name=".\tts_files")
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='AIDubsOverSubs',
                    description='It takes a path to a video file and dubs the audio to a given language')
    parser.add_argument("-f", "--file", required=True, help="Video file path")
    parser.add_argument("-l", "--language", required=True, help="Target language")
    
    args = parser.parse_args()
    asyncio.run(main(args.file, args.language))