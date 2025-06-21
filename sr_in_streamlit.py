from streamlit_webrtc import webrtc_streamer

webrtc_streamer(
    key="sample",
    media_stream_constraints={
        "video": False,
        "audio": True
    }
)
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import assemblyai as aai
import threading
import queue
import time
import os

# Set your AssemblyAI API key here (replace with your actual key or use environment variables)
# Remember to keep your API key secure!
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY") # Recommended: Use environment variable

# Ensure the API key is set
if not aai.settings.api_key:
    st.error("AssemblyAI API key not found. Please set the ASSEMBLYAI_API_KEY environment variable.")
    st.stop()

# Class to handle audio processing and sending to AssemblyAI
class AssemblyAIAudioProcessor:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._stop_event = threading.Event()
        self._transcription_placeholder = st.empty() # Placeholder for transcription results

    def _transcribe(self):
        def on_open(session_opened: aai.RealtimeSessionOpened):
            st.info(f"Session ID: {session_opened.session_id}")

        def on_error(error: aai.RealtimeError):
            st.error(f"An error occurred: {error}")

        def on_close():
            st.info("Closing Session")

        def on_data(transcript: aai.RealtimeTranscript):
            if not transcript.text:
                return

            if isinstance(transcript, aai.RealtimeFinalTranscript):
                # Add new line after final transcript
                self._transcription_placeholder.markdown(transcript.text, unsafe_allow_html=True)
            else:
                self._transcription_placeholder.markdown(transcript.text, unsafe_allow_html=True)

        transcriber = aai.RealtimeTranscriber(
            sample_rate=44100,  # Ensure this matches the expected sample rate
            on_data=on_data,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close,
        )

        try:
            transcriber.connect()
            st.info("Connected to AssemblyAI. Start speaking!")

            while not self._stop_event.is_set():
                try:
                    audio_frame = self._queue.get(timeout=1)
                    if audio_frame is None:  # Sentinel value to stop the thread
                        break
                    # Convert audio frame to bytes and send to AssemblyAI
                    audio_bytes = audio_frame.to_ndarray().tobytes()
                    transcriber.stream(audio_bytes)
                except queue.Empty:
                    time.sleep(0.01) # Avoid busy loop
        except Exception as e:
            st.error(f"Error during transcription: {e}")
        finally:
            transcriber.close()
            st.info("Disconnected from AssemblyAI.")

    def recv(self, frame):
        # This function receives audio frames from streamlit-webrtc
        self._queue.put(frame)

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._transcribe)
            self._thread.start()

        return frame # Return the frame to continue the stream if needed

    def stop(self):
        # Stop the transcription thread
        self._stop_event.set()
        self._queue.put(None)  # Put sentinel value to unblock the queue
        if self._thread and self._thread.is_alive():
            self._thread.join()

# Create an instance of the audio processor
audio_processor = AssemblyAIAudioProcessor()

# Configure webrtc_streamer to use the audio processor
webrtc_ctx = webrtc_streamer(
    key="assemblyai_transcription",
    mode=WebRtcMode.SENDONLY, # Send audio only
    media_stream_constraints={"video": False, "audio": True}, # Request audio permission
    audio_processor_factory=lambda: audio_processor
)

# Control transcription based on webrtc_streamer state
if webrtc_ctx.state.playing:
    st.info("Streaming started. Click Stop to end.")
    # You might want to add a button to explicitly stop the stream
    if st.button("Stop Transcription"):
        audio_processor.stop()
else:
    st.info("Click Start to begin transcription.")

# Ensure cleanup on script exit
if not webrtc_ctx.state.playing and webrtc_ctx.state.stopped:
    audio_processor.stop()
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import assemblyai as aai
import threading
import queue
import time
import os

# Set your AssemblyAI API key here (replace with your actual key or use environment variables)
# Remember to keep your API key secure!
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY") # Recommended: Use environment variable

# Ensure the API key is set
if not aai.settings.api_key:
    st.error("AssemblyAI API key not found. Please set the ASSEMBLYAI_API_KEY environment variable.")
    st.stop()

# Class to handle audio processing and sending to AssemblyAI
class AssemblyAIAudioProcessor:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = None
        self._stop_event = threading.Event()
        self._transcription_placeholder = st.empty() # Placeholder for transcription results

    def _transcribe(self):
        def on_open(session_opened: aai.RealtimeSessionOpened):
            st.info(f"Session ID: {session_opened.session_id}")

        def on_error(error: aai.RealtimeError):
            st.error(f"An error occurred: {error}")

        def on_close():
            st.info("Closing Session")

        def on_data(transcript: aai.RealtimeTranscript):
            if not transcript.text:
                return

            if isinstance(transcript, aai.RealtimeFinalTranscript):
                # Add new line after final transcript
                self._transcription_placeholder.markdown(transcript.text, unsafe_allow_html=True)
            else:
                self._transcription_placeholder.markdown(transcript.text, unsafe_allow_html=True)

        transcriber = aai.RealtimeTranscriber(
            sample_rate=44100,  # Ensure this matches the expected sample rate
            on_data=on_data,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close,
        )

        try:
            transcriber.connect()
            st.info("Connected to AssemblyAI. Start speaking!")

            while not self._stop_event.is_set():
                try:
                    audio_frame = self._queue.get(timeout=1)
                    if audio_frame is None:  # Sentinel value to stop the thread
                        break
                    # Convert audio frame to bytes and send to AssemblyAI
                    audio_bytes = audio_frame.to_ndarray().tobytes()
                    transcriber.stream(audio_bytes)
                except queue.Empty:
                    time.sleep(0.01) # Avoid busy loop
        except Exception as e:
            st.error(f"Error during transcription: {e}")
        finally:
            transcriber.close()
            st.info("Disconnected from AssemblyAI.")

    def recv(self, frame):
        # This function receives audio frames from streamlit-webrtc
        self._queue.put(frame)

        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._transcribe)
            self._thread.start()

        return frame # Return the frame to continue the stream if needed

    def stop(self):
        # Stop the transcription thread
        self._stop_event.set()
        self._queue.put(None)  # Put sentinel value to unblock the queue
        if self._thread and self._thread.is_alive():
            self._thread.join()

# Create an instance of the audio processor
audio_processor = AssemblyAIAudioProcessor()

# Configure webrtc_streamer to use the audio processor
webrtc_ctx = webrtc_streamer(
    key="assemblyai_transcription",
    mode=WebRtcMode.SENDONLY, # Send audio only
    media_stream_constraints={"video": False, "audio": True}, # Request audio permission
    audio_processor_factory=lambda: audio_processor
)

# Control transcription based on webrtc_streamer state
if webrtc_ctx.state.playing:
    st.info("Streaming started. Click Stop to end.")
    # You might want to add a button to explicitly stop the stream
    if st.button("Stop Transcription"):
        audio_processor.stop()
else:
    st.info("Click Start to begin transcription.")

# Ensure cleanup on script exit
if not webrtc_ctx.state.playing and webrtc_ctx.state.stopped:
    audio_processor.stop()
