import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import requests
import os
import tempfile
import wave

# Load API key securely from Streamlit secrets or environment variable
ASSEMBLYAI_API_KEY = st.secrets.get("auth_key") or os.getenv("ASSEMBLYAI_API_KEY")

# Set up UI
st.title("🎙️ Real-time Audio Transcription")
st.write("Allow microphone access and click 'Start' to begin recording.")

# Initialize session state
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = []

# Custom audio processor class to collect microphone input
class AudioProcessor:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().tobytes()
        st.session_state.audio_buffer.append(pcm)
        return frame

# Streamlit WebRTC setup
webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"audio": {"echoCancellation": True}, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    audio_processor_factory=AudioProcessor,
)

# Transcription logic
if st.button("🛑 Transcribe"):
    if len(st.session_state.audio_buffer) == 0:
        st.warning("No audio recorded. Make sure you clicked 'Start' and allowed mic access.")
    elif not ASSEMBLYAI_API_KEY:
        st.error("AssemblyAI API key not found. Please set it in Streamlit secrets.")
    else:
        st.info("Processing and sending audio to AssemblyAI...")

        # Write buffer to a temp .wav file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            with wave.open(f.name, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(16000)
                wf.writeframes(b"".join(st.session_state.audio_buffer))
            audio_file_path = f.name

        # Step 1: Upload audio
        headers = {"authorization": ASSEMBLYAI_API_KEY}
        with open(audio_file_path, "rb") as f:
            upload_response = requests.post(
                "https://api.assemblyai.com/v2/upload",
                headers=headers,
                files={"file": f}
            )
        audio_url = upload_response.json()["upload_url"]

        # Step 2: Request transcription
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

        # Step 3: Poll until transcription completes
        st.write("Transcribing...")
        polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        while True:
            polling_response = requests.get(polling_url, headers=headers).json()
            if polling_response["status"] == "completed":
                st.success("✅ Transcription complete!")
                st.subheader("📝 Transcript:")
                st.markdown(polling_response["text"])
                break
            elif polling_response["status"] == "error":
                st.error(f"Transcription failed: {polling_response['error']}")
                break
