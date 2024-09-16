import whisper
import json
from translate import translate

def transcribe(file_name: str, target_language: str, device: str = "cuda"):
    model = whisper.load_model("medium", device=device, download_root="./whisper_model")
    result = model.transcribe(file_name)
    print("Audio Languge: " + result["language"])
    segments = result["segments"]

    model = None
    for segment in segments:
        segment[f'text_{target_language}'] = translate(segment['text'], target_language)
    
    with open("subtitles.json", "w") as file:
        json.dump(segments, file)
