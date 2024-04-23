import os
import wave
from queue import Queue
from threading import Thread

import pyaudio
import streamlit as s
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel

messages = Queue()
recordings = Queue()
p = pyaudio.PyAudio()

channels = 1
rate = 16000
chunksize = 3
formataudio = pyaudio.paInt16
saplesize = 2


def start_recording(language):
    messages.put(True)
    recording = Thread(target=record)
    recording.start()
    transcribe = Thread(target=speech_recognition(language))
    transcribe.start()


def stop_recording():
    messages.get()


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

    language = s.selectbox("Select Language", GoogleTranslator().get_supported_languages(as_dict=True), format_func=lambda x: x, help="search")

    col1, col2 = s.columns(2)

    with col1:
        if s.button("Start Recording") and language:
            start_recording(language)

    with col2:
        if s.button("Stop Recording"):
            stop_recording()


def main2():
    langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
    print(langs_dict)


if __name__ == "__main__":
    main()
