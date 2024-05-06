import os
import wave
from queue import Queue
from threading import Thread

import pyaudio
import streamlit as s
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel
from functools import lru_cache

messages = Queue()
recordings = Queue()
p = pyaudio.PyAudio()

channels = 1
rate = 16000
chunksize = 3
formataudio = pyaudio.paInt16
saplesize = 2

stream = None


class SessionState:
    def __init__(self):
        self._session_id = None
        self._app_closed = False

    def get_state(self):
        return self._app_closed

    def set_state(self, state):
        self._app_closed = state

    def get_session_id(self):
        return self._session_id

    def set_session_id(self, session_id):
        self._session_id = session_id

session_state = SessionState()

@lru_cache(maxsize=None)
def app_closer():
    stop_recording()
    session_id = s.report_thread.get_report_ctx().session_id
    if session_state.get_session_id() == session_id:
        session_state.set_state(True)
        

def start_recording(language):
    messages.put(True)
    recording = Thread(target=record)
    recording.start()
    transcribe = Thread(target=speech_recognition(language))
    transcribe.start()


def stop_recording():
    messages.get()
    if stream:
        stream.stop_stream()
        stream.close()
        p.terminate()


def speech_recognition(langauge):
    model = WhisperModel('tiny.en', device='cpu', compute_type='int8')
    while not messages.empty():

        file = "temp.wav"
        frames = recordings.get()

        wf = wave.open(file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        segments, info = model.transcribe(file)
        for segment in segments:
            translated = GoogleTranslator(source='en', target=langauge).translate(segment.text)
            s.title(translated)
        os.remove(file)


def record(chunk=1024):
    stream = p.open(format=formataudio, channels=channels, rate=rate, input=True, input_device_index=1,
                    frames_per_buffer=chunk)

    frames = []

    while not messages.empty():

        data = stream.read(chunk)
        frames.append(data)
        if len(frames) >= (rate * chunksize) / chunk:
            recordings.put(frames.copy())
            frames = []

    stream.stop_stream()
    stream.close()
    p.terminate()


def main():
    s.title("Choose a Language")

    stopper = s.button("Stop Recording")

    language = s.selectbox("Select Language", GoogleTranslator().get_supported_languages(as_dict=True))

    if language:
        start_recording(language)
    
    if stopper:
        stop_recording()
        app_closer()
        s.stop()

def mainsec():
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    print(langs_dict)


if __name__ == "__main__":
    main()
