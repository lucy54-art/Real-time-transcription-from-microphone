# app.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import requests
import os
import tempfile

# AssemblyAI API key
ASSEMBLYAI_API_KEY = st.secrets.get("auth_key") or os.getenv("ASSEMBLYAI_API_KEY")

st.title("🎙️ Real-time Audio Transcription")

st.write("Click Start to begin recording your voice.")

# Use a buffer to collect audio chunks
audio_buffer = []

# Custom audio processor
class AudioProcessor:
    def __init__(self) -> None:
        self.recorded_data = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert audio frame to numpy array and store raw data
        pcm = frame.to_ndarray().flatten().tobytes()
        audio_buffer.append(pcm)
        return frame

# Streamlit WebRTC UI
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    audio_processor_factory=AudioProcessor,
)

# When recording is stopped
if st.button("🛑 Transcribe"):
    if len(audio_buffer) == 0:
        st.warning("No audio recorded.")
    else:
        st.info("Processing and sending to AssemblyAI...")

        # Write raw PCM data to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            import wave

            wf = wave.open(f.name, "wb")
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(16000)
            wf.writeframes(b"".join(audio_buffer))
            wf.close()
            audio_file_path = f.name

        # Upload to AssemblyAI
        headers = {"authorization": ASSEMBLYAI_API_KEY}
        with open(audio_file_path, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                files={"file": f},
            )
        audio_url = upload_response.json()["upload_url"]

        # Request transcription
        transcript_request = {
            "audio_url": audio_url,
            "language_code": "en_us"
        }
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json=transcript_request,
            headers=headers
        )

        transcript_id = transcript_response.json()["id"]

        # Poll for result
        transcript_text = ""
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        while True:
            polling_response = requests.get(polling_url, headers=headers).json()
            if polling_response["status"] == "completed":
                transcript_text = polling_response["text"]
                break
            elif polling_response["status"] == "error":
                st.error(f"Transcription failed: {polling_response['error']}")
                break

        st.subheader("📝 Transcription Result:")
        st.success(transcript_text)
