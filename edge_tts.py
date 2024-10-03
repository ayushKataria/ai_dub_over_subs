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
    if duration is not None:
        rate = get_expected_rate(file_name, duration)
    else:
        rate = "+0%"
    os.remove(file_name)
    communicate = edge_tts.Communicate(text, voice_to_use, rate=rate)
    file_name = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    await communicate.save(file_name)
    return file_name, voice_to_use

def get_expected_rate(wav_file: str, expected_duration: float):
    current_duration = librosa.get_duration(path=wav_file)
    speed = int((current_duration / expected_duration) * 100) - 100
    rate = ""
    if speed > 0:
        rate = "+"
    rate += str(speed) + "%"
    print(f"Rate: {rate}")

    return rate



if __name__ == "__main__":
    asyncio.run(atts("यदि आप इस ऐप को कैसे बनाया गया है के बारे में सभी विवरण चाहते हैं"))

