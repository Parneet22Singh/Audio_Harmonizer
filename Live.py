import os
import time
import sounddevice as sd
import soundfile as sf
import threading
from queue import Queue
from faster_whisper import WhisperModel
import google.generativeai as genai
from elevenlabs import ElevenLabs
import playsound

# Configurations
AUDIO_FILENAME = "live_input.wav"
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY", "Your-API-Key")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "Your-API-Key")

genai.configure(api_key=GENAI_API_KEY)
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # US English
model = WhisperModel("small", compute_type="int8")

# Queues for pipeline
transcript_queue = Queue()
adapted_queue = Queue()

# Step 1: Capture Audio

def record_audio(duration=5):
    samplerate = 44100
    print("🎙️ Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write(AUDIO_FILENAME, audio, samplerate)
    print("✅ Recording Done")

# Step 2: Transcribe

def transcribe_worker():
    while True:
        record_audio(5)
        segments, _ = model.transcribe(AUDIO_FILENAME)
        text = " ".join([s.text for s in segments])
        if text.strip():
            transcript_queue.put(text)
        time.sleep(1)

# Step 3: Adapt with Gemini

def adapt_worker(tone="formal", language="Hindi"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    while True:
        if not transcript_queue.empty():
            text = transcript_queue.get()
            prompt = (
                f"Translate and rewrite the following English sentence into {language} using a {tone} tone. "
                f"Preserve the message:{text} and make sure only the message is given as output nothing else."
            )
            print("🔄 Sending to Gemini...")
            try:
                response = model.generate_content(prompt)
                if response and response.candidates:
                    parts = response.candidates[0].content.parts
                    adapted_text = ''.join(part.text for part in parts if hasattr(part, "text"))
                    adapted_queue.put(adapted_text.strip())
                    print("✅ Adapted.")
            except Exception as e:
                print("❌ Gemini error:", e)
        time.sleep(1)

# Step 4: Generate Audio

def speak_worker():
    while True:
        if not adapted_queue.empty():
            text = adapted_queue.get()
            print(f"🔊 Speaking: {text}")
            audio = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100"
            )
            with open("output.mp3", "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            playsound.playsound("output.mp3")
        time.sleep(1)

# Main Orchestration

def start_realtime_pipeline():
    threading.Thread(target=transcribe_worker, daemon=True).start()
    threading.Thread(target=adapt_worker, daemon=True).start()
    threading.Thread(target=speak_worker, daemon=True).start()
    print("🚀 Real-time harmonizer running. Press Ctrl+C to stop.")
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    start_realtime_pipeline()
