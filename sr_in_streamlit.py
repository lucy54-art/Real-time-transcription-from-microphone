import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import numpy as np
import io
import wave

st.title("🎤 Simple Audio Recorder with Playback")

if "audio_frames" not in st.session_state:
    st.session_state.audio_frames = []

class AudioRecorder:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Convert audio frame to bytes and store in session_state
        pcm = frame.to_ndarray(format="s16").tobytes()
        st.session_state.audio_frames.append(pcm)
        return frame

webrtc_ctx = webrtc_streamer(
    key="audio-recorder",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioRecorder,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

# Button to stop and save recording
if st.button("🛑 Stop and Save Recording"):
    if len(st.session_state.audio_frames) == 0:
        st.warning("No audio recorded.")
    else:
        # Combine all audio frames
        audio_data = b"".join(st.session_state.audio_frames)
        st.session_state.audio_frames = []  # reset for next recording

        # Save to WAV in memory
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)  # mono audio
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(48000)  # sample rate used by streamlit-webrtc default
            wf.writeframes(audio_data)

        buffer.seek(0)
        st.audio(buffer, format="audio/wav")
