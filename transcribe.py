import whisper
import json
from translate import translate
from translate import model as translate_model

def transcribe(file_name: str, target_language: str, device: str = "cuda"):
    model = whisper.load_model("small", device=device, download_root="./whisper_model")
    result = model.transcribe(file_name, word_timestamps=True)
    print("Audio Languge: " + result["language"])
    segments = result["segments"]

    for segment in segments:
        segment[f'text_{target_language}'] = translate(segment['text'], target_language, device)
    
    with open("subtitles.json", "w") as file:
        json.dump(segments, file)