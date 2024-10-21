import whisper
import json
import torch
import subprocess
from translate import translate
from translate import model as translate_model

import wave
import contextlib
from pyannote.audio import Pipeline, Audio
from pyannote.core import Segment
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd

from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding

from transformers.utils import logging

logging.set_verbosity_error()


def transcribe(file_name: str, target_language: str, num_speakers = 2, device: str = "cuda"):
    model = whisper.load_model("small", device=device, download_root="./whisper_model")
    segments, language = extract_speakers(model, file_name, num_speakers)
    print("Audio Languge: " + language)
    # segments = result["segments"]

    # for segment in segments:
    #     segment[f'text_{target_language}'] = translate(segment['text'], target_language, device)
    
    with open("subtitles.json", "w") as file:
        json.dump(segments, file)

def extract_speakers(model, path, num_speakers=2):
    """Do diarization with speaker names"""
    
    embedding_model = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cuda"))

    mono = 'mono.wav'
    cmd = 'ffmpeg -loglevel error -i "{}" -y -ac 1 mono.wav'.format(path)
    subprocess.check_output(cmd, shell=True)

    result = model.transcribe(mono, word_timestamps=True)
    language = result['language']
    segments = result["segments"]
    
    with contextlib.closing(wave.open(mono,'r')) as f:
      frames = f.getnframes()
      rate = f.getframerate()
      duration = frames / float(rate)
        
    audio = Audio()

    def segment_embedding(segment):
        start = segment["start"]
        # Whisper overshoots the end timestamp in the last segment
        end = min(duration, segment["end"])
        clip = Segment(start, end)
        waveform, sample_rate = audio.crop(mono, clip)
        return embedding_model(waveform[None])

    embeddings = np.zeros(shape=(len(segments), 192))
    for i, segment in enumerate(segments):
      embeddings[i] = segment_embedding(segment)
    embeddings = np.nan_to_num(embeddings)
    
    clustering = AgglomerativeClustering(num_speakers).fit(embeddings)
    labels = clustering.labels_
    for i in range(len(segments)):
      segments[i]["speaker"] = 'SPEAKER ' + str(labels[i] + 1)
    return segments, language

if __name__ == "__main__":
    transcribe("Introducing GPT-4o.mp4", "hi", 4, "cuda")