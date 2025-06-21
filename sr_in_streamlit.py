from streamlit_webrtc import webrtc_streamer

webrtc_streamer(
    key="sample",
    media_stream_constraints={
        "video": False,
        "audio": True
    }
)
