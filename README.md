# AI Dubs over Subs

AI Dubs over Subs is an experimental project that takes a video file and dubs it into a target language using AI. The project leverages several advanced AI models for transcription, translation, and text-to-speech synthesis, alongside tools for video and audio manipulation.

## How it Works
1. **Transcription**: The project uses OpenAI Whisper to transcribe the original audio into text.
2. **Translation**: The transcribed text is translated into the target language using the `alirezamsh/small100` translation model.
3. **Text-to-Speech (TTS)**: The translated text is converted into speech using `edge-tts`.
4. **Audio Manipulation**: Existing audio (speech) is removed from the video using [vocal-remover](https://github.com/tsurumeso/vocal-remover), and the newly generated dubbed audio is synced back into the video with the help of `ffmpeg`.

## Project Status
⚠️ **This project is currently in its early stages**. While functional, the dubbed audio sync is not perfect, and the translation & TTS quality could be improved by using better models. The current version is intended more as a proof of concept (POC) than a production-ready solution.

## Acknowledgements
This project has been built upon the work of several other open-source projects:
- **[OpenAI Whisper](https://github.com/openai/whisper)**: Used for automatic transcription of audio to text.
- **[alirezamsh/small100](https://huggingface.co/alirezamsh/small100)**: Used for translating the transcribed text into the target language.
- **[edge-tts](https://github.com/rany2/edge-tts)**: Used to convert the translated text into synthesized speech.
- **[m3hrdadfi/hubert-base-persian-speech-gender-recognition](https://github.com/m3hrdadfi/hubert-base-persian-speech-gender-recognition)**: Used to detect the gender of the speaker, helping to choose an appropriate TTS voice.
- **[tsurumeso/vocal-remover](https://github.com/tsurumeso/vocal-remover)**: Used to remove the existing speech from the video before applying the new dubbed audio.

## Setup

### 1. Install Dependencies
Ensure you have `ffmpeg` installed on your system, then install the required Python dependencies by running:

```bash
pip install -r requirements.txt
```
### 2. Run main.py
```python
python main.py -f file_name.mp4 -l language
```
Where:
    file_name.mp4: is the path to your input video file.
    language: is the target language you want the video to be dubbed in (e.g., en, es, fr, etc.).

### Future Improvements

- Audio Sync: Improve the timing between the dubbed audio and the video to create a more natural sync.
- Translation Models: Replace or enhance the translation model to improve accuracy.
- TTS Quality: Use more advanced TTS models to achieve more realistic and natural-sounding voices. Maybe use a model that is capable of mimicing the original speakers voice
- Multi Speaker Support: Identify multiple speakers in the video and dub them with different voices.
