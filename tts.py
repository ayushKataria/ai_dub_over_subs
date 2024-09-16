import asyncio
import os
import random
import librosa
import subprocess

import edge_tts
from edge_tts import VoicesManager
import uuid

async def atts(text: str, language: str = "hi", gender: str = "Male", voice_to_use: str = None, duration: float = None) -> None:
    # Check if the directory exists, if not, create it
    folder_path = "./tts_files"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Directory '{folder_path}' created.")
    else:
        print(f"Directory '{folder_path}' already exists.")

    if voice_to_use is None:
        voices = await VoicesManager.create()
        voice = voices.find(Gender=gender, Language=language)
        voice_to_use = random.choice(voice)["Name"]
    # Also supports Locales
    # voice = voices.find(Gender="Female", Locale="es-AR")
    text = str(text)
    print(voice_to_use)

    communicate = edge_tts.Communicate(text, voice_to_use)
    file_name = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    await communicate.save(file_name)
    if not(duration is None):
        file_name = update_wav_speed(file_name, duration, folder_path)
    return file_name, voice_to_use

def update_wav_speed(wav_file: str, expected_duration: float, folder_path: str = "./"):
    current_duration = librosa.get_duration(filename=wav_file)
    speed = min(max(round(current_duration / expected_duration, 1), 0.5), 100)
    print(f"Speed: {speed}")
    new_file_name = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    new_new_file_name = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    
    subprocess.call(["ffmpeg", "-y", "-i", wav_file, "-af", f"atempo={speed}", new_file_name])

    subprocess.call(["ffmpeg", "-i", new_file_name, "-f", "wav", "-bitexact", "-acodec", "pcm_s16le", new_new_file_name])

    os.remove(wav_file)
    os.remove(new_file_name)
    return new_new_file_name




if __name__ == "__main__":
    asyncio.run(atts("यदि आप इस ऐप को कैसे बनाया गया है के बारे में सभी विवरण चाहते हैं", duration = 8))

