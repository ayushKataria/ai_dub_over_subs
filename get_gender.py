import os
import torch
import subprocess
import torch.nn.functional as F
import torchaudio
from transformers import AutoConfig, Wav2Vec2FeatureExtractor
from gender_classification_models.models import HubertForSpeechClassification
from transformers.utils import logging

logging.set_verbosity_error()

model_name_or_path = "m3hrdadfi/hubert-base-persian-speech-gender-recognition"
config = AutoConfig.from_pretrained(model_name_or_path)
feature_extractor = None
model = None


def speech_file_to_array_fn(path, sampling_rate):
    speech_array, _sampling_rate = torchaudio.load(path)
    resampler = torchaudio.transforms.Resample(_sampling_rate)
    speech = resampler(speech_array).squeeze().numpy()
    return speech


def predict(path: str, device: str):
    global sampling_rate, feature_extractor, model
    if feature_extractor == None:
        feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name_or_path, device_map = device)
    sampling_rate = feature_extractor.sampling_rate
    if model == None:
        model = HubertForSpeechClassification.from_pretrained(model_name_or_path).to(device)

    
    small_clip_path = get_smaller_clip(path, "small_clip.wav")

    speech = speech_file_to_array_fn(small_clip_path, sampling_rate)
    inputs = feature_extractor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
    inputs = {key: inputs[key].to(device) for key in inputs}

    with torch.no_grad():
        logits = model(**inputs).logits

    scores = F.softmax(logits, dim=1).detach().cpu().numpy()[0]
    outputs = [{"Label": config.id2label[i], "Score": f"{round(score * 100, 3):.1f}%"} for i, score in enumerate(scores)]

    os.remove(small_clip_path)

    if outputs[0]['Label'] == "F":
        return "Female"
    else:
        return "Male"

def get_smaller_clip(input_file: str, output_file: str):
    command = ["ffmpeg", "-loglevel", "error", "-ss", "0", "-t", "15", "-i", input_file, output_file]
    subprocess.call(command)
    return output_file
    