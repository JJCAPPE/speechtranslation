
from faster_whisper import WhisperModel

def main2():
    file = "try.m4a"
    model = WhisperModel('tiny.en', device='cpu', compute_type='int8')
    segments, info = model.transcribe(file)
    for segment in segments:
        print(segment.text)

if __name__ == "__main__":
    main2()
