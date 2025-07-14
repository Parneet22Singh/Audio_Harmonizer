### Audio Harmonizer
Audio Harmonizer converts live recordable audio (in chunks) into multiple target languages while generating new audio that reflects the user’s chosen tone (wording)—informal, formal, or neutral. It preserves the original syntax and intent of the audio and applies a suitable accent along with repharsing the wording on the basis of desired tone.

Audio modification and generation: Powered by the ElevenLabs API.

Transcription and tone/language conversion: Handled by the Gemini API.

This tool enables seamless multilingual audio transformation with customizable tone and style.

## Live.py
It consists of the python code that records a 5 second chunk live and then moves forward with the further processing (currently hindi only), it is near real-time.
## main_harmonizer.py
It requires the user to specify the path to an audio (uploading an audio) for the processing.

### NOTE
- Since this is in development stages, CLI version is provided, UI based not available yet.
