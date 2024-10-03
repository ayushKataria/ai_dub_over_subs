import asyncio
import os
import librosa
import math

import uuid
from TTS.api import TTS
import soundfile as sf
from transformers.utils import logging

logging.set_verbosity_error()

async def axtts(text: str, reference_wav: str, language: str = "hi", duration: float = None, device: str = "cpu") -> tuple:
    # Check if the directory exists, if not, create it
    folder_path = "./tts_files"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Directory '{folder_path}' created.")
    else:
        print(f"Directory '{folder_path}' already exists.")

    text = str(text)

    if device == "cuda":
        gpu = True
    else:
        gpu = False

    # Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=gpu).to(device)
    file_name = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    # Text to speech to a file
    tts.tts_to_file(text=text, speaker_wav=reference_wav, language="hi", file_path=file_name)
    
    if duration is not None:
        file_name = speed_up_audio(file_name, duration, folder_path)
    return file_name

def speed_up_audio(wav_file: str, expected_duration: float, folder_path: str):
    current_duration = librosa.get_duration(path=wav_file)
    expected_duration = math.ceil(expected_duration)
    speed = current_duration / expected_duration
    print(f"Speed: {speed}")
    
    # Load the audio file
    y, sr = librosa.load(wav_file)

    # Use librosa's time-stretch function to change the speed without altering the pitch
    y_fast = librosa.effects.time_stretch(y, rate=speed)

    # Save the modified audio
    output_path = folder_path + "/" + str(uuid.uuid4()) + ".wav"
    sf.write(output_path, y_fast, sr)

    os.remove(wav_file)

    return output_path


if __name__ == "__main__":
    asyncio.run(axtts("यदि आप इस ऐप को कैसे बनाया गया है के बारे में सभी विवरण चाहते हैं"))


