import os
import wave
from queue import Queue
import asyncio

import pyaudio
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel

class SpeechTranslator:
    def __init__(self):
        self.messages = Queue()
        self.recordings = Queue()
        self.p = pyaudio.PyAudio()
        self.channels = 1
        self.rate = 16000
        self.chunksize = 3
        self.formataudio = pyaudio.paInt16
        self.stream = None
        self.model = WhisperModel('tiny.en', device='cpu', compute_type='int8')

    async def start_recording(self, language):
        self.messages.put(True)
        await self.record()

    def stop_recording(self):
        self.messages.get()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()

    async def speech_recognition(self, language):
        while not self.messages.empty():
            file = "temp.wav"
            frames = self.recordings.get()

            wf = wave.open(file, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))
            wf.close()

            segments, info = self.model.transcribe(file)
            for segment in segments:
                translated = GoogleTranslator(source='en', target=language).translate(segment.text)
                yield translated + '\n'
            os.remove(file)

    async def record(self, chunk=1024):
        self.stream = self.p.open(format=self.formataudio, channels=self.channels, rate=self.rate, input=True,
                                  input_device_index=1, frames_per_buffer=chunk)
        frames = []
        while not self.messages.empty():
            data = self.stream.read(chunk)
            frames.append(data)
            if len(frames) >= (self.rate * self.chunksize) / chunk:
                self.recordings.put(frames.copy())
                frames = []
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

async def main(language):
    translator = SpeechTranslator()
    await translator.start_recording(language)


