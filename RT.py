import os
import time
import wave
from queue import Queue
from threading import Thread

import pyaudio
from colorama import Fore
from faster_whisper import WhisperModel

messages = Queue()
recordings = Queue()
p = pyaudio.PyAudio()

channels = 1
rate = 16000
chunksize = 3
formataudio = pyaudio.paInt16
saplesize = 2


def start_recording():
    messages.put(True)
    recording = Thread(target=record)
    recording.start()
    transcribe = Thread(target=speech_recognition)
    transcribe.start()


def stop_recording():
    messages.get()
    print(f"{Fore.LIGHTRED_EX}Recording stopped.{Fore.RESET}")


def speech_recognition():
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
        start = time.time()
        segments, info = model.transcribe(file)
        for segment in segments:
            print(f"{segment.text} --- {Fore.RED}{time.time() - start}{Fore.RESET}")

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
    print(f"{Fore.YELLOW}Press 'S' to start recording, or 'Q' to stop recording.{Fore.RESET}")

    try:
        while True:
            user_input = input()
            if user_input.lower() == 's':
                start_recording()
                print(f"{Fore.LIGHTGREEN_EX}Recording started...{Fore.RESET}")
            elif user_input.lower() == 'q':
                stop_recording()
                break
    except KeyboardInterrupt:
        print("\nExited recording.")


if __name__ == "__main__":
    main()
