import os
from faster_whisper import WhisperModel
import pyaudio
from queue import Queue
from threading import Thread
import wave

messages = Queue()
recordings = Queue()
p = pyaudio.PyAudio()

channels = 1
rate = 16000
chunksize = 1
formataudio = pyaudio.paInt16
saplesize = 2


def start_recording():
    messages.put(True)
    print("Starting recording...")
    recording = Thread(target=record)
    recording.start()
    transcribe = Thread(target=speech_recognition)
    transcribe.start()


def stop_recording():
    print(messages.get())
    print("Stopped recording.")


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

        segments, info = model.transcribe(file)
        for segment in segments:
            print(segment.text)

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
    print("Press Enter to start recording")
    try:
        while True:
            input()
            start_recording()
            stop_key = input("Press Enter to stop recording")
            if stop_key:
                stop_recording()
    except KeyboardInterrupt:
        print("\nRecording stopped.")


if __name__ == "__main__":
    main()
