import os
from groq import Groq

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe audio from bytes (from audio_recorder_streamlit)."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        result = client.audio.transcriptions.create(
            file=("recording.wav", audio_bytes, "audio/wav"),
            model="whisper-large-v3",
            language="ur",
            response_format="text",
            temperature=0.0,
        )
        return result.strip() if result else ""
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

def transcribe_audio(audio_file) -> str:
    """Transcribe audio from uploaded file."""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        audio_bytes = audio_file.read()
        audio_file.seek(0)
        filename = getattr(audio_file, 'name', 'audio.mp3')
        ext = filename.split('.')[-1].lower()
        mime_map = {'mp3':'audio/mpeg','wav':'audio/wav','m4a':'audio/mp4','ogg':'audio/ogg','webm':'audio/webm'}
        mime = mime_map.get(ext, 'audio/mpeg')
        result = client.audio.transcriptions.create(
            file=(filename, audio_bytes, mime),
            model="whisper-large-v3",
            language="ur",
            response_format="text",
            temperature=0.0,
        )
        return result.strip() if result else ""
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
