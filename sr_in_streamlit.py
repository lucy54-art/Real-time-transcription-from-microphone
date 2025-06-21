import streamlit as st
import streamlit_webrtc
import av
import io
import wave
import numpy as np

# Use session state to store recorded audio frames
if "audio_frames" not in st.session_state:
    st.session_state["audio_frames"] = []

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    """
    Callback function to process audio frames.
    Append the frame data to the session state.
    """
    st.session_state["audio_frames"].append(frame)
    return frame  # Return the frame unmodified

st.title("Microphone Recorder and Player")

st.write("Click 'START' to begin recording from your microphone.")
webrtc_ctx = streamlit_webrtc.webrtc_streamer(
    key="audio-recorder",
    mode=streamlit_webrtc.WebRtcMode.SENDONLY,  # We only need to send audio
    audio_receiver_size=1024,
    media_stream_constraints={"video": False, "audio": True},
    audio_frame_callback=audio_frame_callback,
)

# Playback the recorded audio when recording stops
if webrtc_ctx.state.playing:
    st.write("Recording...")
elif webrtc_ctx.state.stopped and st.session_state["audio_frames"]:
    st.write("Recording stopped.")

    # Convert the recorded frames to WAV format
    recorded_audio_bytes = b""
    try:
        # Use a BytesIO object to store the WAV data
        with io.BytesIO() as buffer:
            with wave.open(buffer, "wb") as wf:
                wf.setnchannels(st.session_state["audio_frames"][0].format.channels)
                wf.setsampwidth(st.session_state["audio_frames"][0].format.bytes)
                wf.setframerate(st.session_state["audio_frames"][0].rate)
                for frame in st.session_state["audio_frames"]:
                    wf.writeframes(frame.to_ndarray().tobytes())
            recorded_audio_bytes = buffer.getvalue()

    except Exception as e:
        st.error(f"Error processing audio frames: {e}")

    if recorded_audio_bytes:
        st.subheader("Recorded Audio:")
        st.audio(recorded_audio_bytes, format="audio/wav")

    # Clear the recorded frames
    st.session_state["audio_frames"] = []
