import os
import pyaudio
import wave
from faster_whisper import WhisperModel


def record_chunk(p, stream, file_path, chunk_length=0.5):
    frames = []
    for _ in range(0, int(16000 / 1024 * chunk_length)):
        data = stream.read(1024)
        frames.append(data)
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()


def handle_exit(signum, frame):
    print("Stopping...")
    raise SystemExit


def main():
    print("Starting...")
    model_size = "medium.en"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    print("open")
    try:
        while True:
            chunk_file = "temp_chunk.wav"
            record_chunk(p, stream, chunk_file)
            segments, _ = model.transcribe(chunk_file, beam_size=5)
            segments = list(segments)
            for segment in segments:
                print(segment.text)
            os.remove(chunk_file)
    except SystemExit:
        pass
    finally:
        print("Terminated")
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    main()
