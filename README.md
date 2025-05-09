# Speech to Text Converter

Simple Python backend application that converts speech from your microphone to text using the faster-whisper library (a faster implementation of OpenAI's Whisper model).

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the required dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

3. Run the script:
   ```
   python speech_to_text.py
   ```

   Or simply type:
   ```
   run
   ```

4. Start speaking into your microphone when you see "Listening... Speak now". The recording will automatically stop after you finish speaking (when it detects silence).

5. Press Ctrl+C to exit the program.

## Cursor Rules

This project uses Cursor rules to manage certain behaviors:

- **Virtual Environment**: All Python and pip commands automatically run in the virtual environment
- **Package Installation**: When installing new packages, they are automatically added to requirements.txt
- **Run Command**: Type `run`, `run speech`, or `speech` to automatically run the script with the virtual environment activated

## Notes

- The default language is set to English. You can change it by modifying the `language` parameter in the `model.transcribe` function.
- Make sure your microphone is properly connected and configured.
- The script uses Voice Activity Detection (VAD) to automatically stop recording when you pause speaking.
- You can adjust the voice detection sensitivity by modifying the `silence_threshold` parameter in the `record_audio_with_vad` function.
- The script will record for a maximum of 30 seconds or until silence is detected for 1 second (configurable).
- The script uses the "medium" Whisper model, which offers good accuracy. For faster performance or better accuracy, you can use "tiny", "base", "small", or "large" models by changing the model name.
- First-time execution will download the Whisper model, which may take some time depending on your internet connection.
- The default recording duration is 5 seconds. You can change this by modifying the `duration` parameter in the `record_audio` function. 