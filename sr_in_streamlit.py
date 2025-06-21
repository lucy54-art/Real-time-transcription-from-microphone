import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import io
import wave

st.title("🎤 Simple Audio Recorder with Playback")

if "audio_frames" not in st.session_state:
    st.session_state.audio_frames = []
if "recording" not in st.session_state:
    st.session_state.recording = False

class AudioRecorder:
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray(format="s16").tobytes()
        st.session_state.audio_frames.append(pcm)
        return frame

# Control buttons
start = st.button("▶️ Start Recording")
stop = st.button("🛑 Stop Recording")

if start:
    st.session_state.audio_frames = []
    st.session_state.recording = True

if stop:
    st.session_state.recording = False

if st.session_state.recording:
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioRecorder,
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        async_processing=True,
    )
    st.write("Recording...")

if not st.session_state.recording and len(st.session_state.audio_frames) > 0:
    st.write(f"Recorded {len(st.session_state.audio_frames)} audio frames.")
    
    # Save and play audio
    audio_data = b"".join(st.session_state.audio_frames)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)  # streamlit-webrtc default sample rate
        wf.writeframes(audio_data)
    buffer.seek(0)

    st.audio(buffer, format="audio/wav")
