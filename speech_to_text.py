from faster_whisper import WhisperModel
import pyaudio
import wave
import numpy as np
import tempfile
import os
import time
import collections

def record_audio_with_vad(silence_threshold=500, silence_duration=3.0, max_duration=30, sample_rate=16000):
    """Record audio from microphone with voice activity detection (VAD)."""
    # Audio recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    CHUNK = 1024
    
    audio = pyaudio.PyAudio()
    
    print("Listening... Speak now (recording will stop after silence or max duration)")
    
    # Start recording
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=sample_rate,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    frames = []
    silent_chunks = 0
    voice_started = False
    silent_threshold_chunks = int(silence_duration * sample_rate / CHUNK)
    max_chunks = int(max_duration * sample_rate / CHUNK)
    
    # Use deque to store the last few RMS values for smoother detection
    rms_values = collections.deque(maxlen=10)
    
    for i in range(0, max_chunks):
        data = stream.read(CHUNK)
        frames.append(data)
        
        # Calculate audio level using numpy instead of audioop
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(audio_data, dtype=np.float64)))
        
        rms_values.append(rms)
        avg_rms = sum(rms_values) / len(rms_values)
        
        # Voice activity detection
        if avg_rms > silence_threshold:
            silent_chunks = 0
            voice_started = True
        elif voice_started:
            silent_chunks += 1
            
        # If silent for the defined period after voice was detected, stop recording
        if voice_started and silent_chunks > silent_threshold_chunks:
            break
    
    # Stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # If no voice was detected, return empty frames
    if not voice_started:
        return [], sample_rate
    
    return frames, sample_rate

def save_audio_to_file(frames, sample_rate):
    """Save recorded audio frames to a temporary WAV file."""
    if not frames:
        return None
        
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    wf = wave.open(temp_file.name, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return temp_file.name

def transcribe_speech():
    """Record speech from microphone and transcribe it using faster-whisper."""
    global model
    
    # Record audio from microphone with voice activity detection
    frames, sample_rate = record_audio_with_vad()
    
    if not frames:
        print("No speech detected")
        return None
    
    # Save audio to temporary file
    temp_file = save_audio_to_file(frames, sample_rate)
    
    if not temp_file:
        return None
    
    try:
        # Transcribe audio using faster-whisper with options to preserve filler words
        segments, info = model.transcribe(
            temp_file,
            language="en",                     # Use English language
            condition_on_previous_text=False,  # Don't filter based on context to keep filler words
            beam_size=5,                       # Consider more transcription paths, better for catching fillers
            best_of=5,                         # Generate more candidates before picking the best one
            temperature=0.0,                   # No randomness, exact logits for deterministic output
            word_timestamps=True,              # Track individual word timing
            vad_filter=False,                  # Don't remove non-speech parts like "um", "uh"
            no_speech_threshold=0.0,           # Don't filter out any audio segments, keep everything
            compression_ratio_threshold=2.4,   # Allow more repeated words like "like like like"
            log_prob_threshold=-1.0,           # Keep low probability words (fillers often have low probability)
            suppress_tokens=[-1]               # Only suppress the end token, nothing else
        )
        
        # Collect all segments into a single text
        text = " ".join([segment.text for segment in segments])
        
        # Print debug info
        print(f"Detected Language: {info.language} (probability: {info.language_probability:.2f})")
        print(f"You said: {text}")
        return text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    print("Speech to Text Conversion using faster-whisper")
    print("Loading Whisper model...")
    
    # Load the Whisper model (medium for better accuracy)
    model = WhisperModel("medium", device="cpu", compute_type="int8")
    
    print("Model loaded. Press Ctrl+C to exit")
    
    try:
        while True:
            transcribe_speech()
            # Add a small delay before the next recording
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting program...") 