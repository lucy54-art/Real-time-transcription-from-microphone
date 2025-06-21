import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Set up WebRTC configuration for audio only
# You can customize this configuration as needed
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

st.title("Audio Recording App")

# Use webrtc_streamer for audio input only
webrtc_ctx = webrtc_streamer(
    key="audio_recorder",
    mode=WebRtcMode.SENDONLY, # Send audio from the client to the server
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={"video": False, "audio": True}, # Request audio only
    async_processing=True,
)

if webrtc_ctx.state.playing:
    st.write("Recording...")

    # You can access the audio stream from webrtc_ctx.audio_receiver
    # For example, you can process the audio data in real-time or save it to a file
    # For demonstration purposes, let's just display a message

    if webrtc_ctx.audio_receiver:
        st.write("Audio stream received!")

