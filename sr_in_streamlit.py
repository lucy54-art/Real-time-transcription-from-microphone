import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av
import queue
import time
import numpy as np

# --- Streamlit App ---
def main():
    st.title("Streamlit Real-Time Audio Capture and Playback")
    st.write("Click 'Start' to capture audio from your microphone.")

    webrtc_ctx = webrtc_streamer(
        key="sample_audio_capture",
        mode=WebRtcMode.SENDONLY,
        media_stream_constraints={"video": False, "audio": True},
    )

    # Add a check for webrtc_ctx being None
    if webrtc_ctx:
        if webrtc_ctx.state.playing:
            st.success("Audio streaming started!")
            audio_receiver = webrtc_ctx.audio_receiver
            if audio_receiver:
                st.write("Audio receiver available.")
                audio_buffer = []

                # While streaming is active (state.playing is True)
                while webrtc_ctx.state.playing:
                    try:
                        audio_frames = audio_receiver.get_frames(timeout=1)
                        for audio_frame in audio_frames:
                            audio_array = audio_frame.to_ndarray()
                            audio_buffer.append(audio_array)

                    except queue.Empty:
                        time.sleep(0.1)
                        continue

                # When the loop finishes (because state.playing became False)
                if audio_buffer:
                    st.write(f"type(audio_frames) = {type(audio_frames)}")
                    st.write(f"audio_frames = {audio_frames}")
                    combined_audio = np.concatenate(audio_buffer, axis=0)
                    sample_rate = audio_frames.sample_rate if audio_frames else 44100
                    format_bytes = audio_frames.format.bytes if audio_frames else 2

                    audio_bytes = combined_audio.astype(np.int16).tobytes() if format_bytes == 2 else combined_audio.tobytes()

                    st.write("Recorded Audio:")
                    st.audio(audio_bytes, format='audio/wav', sample_rate=sample_rate)

        # Handle the case when streaming is stopped (state.playing is False)
        # after it was previously True
        elif not webrtc_ctx.state.playing:
            st.warning("Audio streaming stopped.")

    st.write("Additional app content goes here.")


if __name__ == "__main__":
    main()
