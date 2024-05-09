from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View  
from django.http import StreamingHttpResponse
from . import translator
import os
import wave
from queue import Queue
import asyncio
import pyaudio
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel
from rest_framework.views import APIView

# Create your views here.

#request handler (request --> response)

#function is called in mainapp.urls.py to senf a response to the client

def test_request(request):
    return render(request, 'entrance.html', {'afrikaans': 'af', 'albanian': 'sq', 'amharic': 'am', 'arabic': 'ar', 'armenian': 'hy', 'assamese': 'as', 'aymara': 'ay', 'azerbaijani': 'az', 'bambara': 'bm', 'basque': 'eu', 'belarusian': 'be', 'bengali': 'bn', 'bhojpuri': 'bho', 'bosnian': 'bs', 'bulgarian': 'bg', 'catalan': 'ca', 'cebuano': 'ceb', 'chichewa': 'ny', 'chinese (simplified)': 'zh-CN', 'chinese (traditional)': 'zh-TW', 'corsican': 'co', 'croatian': 'hr', 'czech': 'cs', 'danish': 'da', 'dhivehi': 'dv', 'dogri': 'doi', 'dutch': 'nl', 'english': 'en', 'esperanto': 'eo', 'estonian': 'et', 'ewe': 'ee', 'filipino': 'tl', 'finnish': 'fi', 'french': 'fr', 'frisian': 'fy', 'galician': 'gl', 'georgian': 'ka', 'german': 'de', 'greek': 'el', 'guarani': 'gn', 'gujarati': 'gu', 'haitian creole': 'ht', 'hausa': 'ha', 'hawaiian': 'haw', 'hebrew': 'iw', 'hindi': 'hi', 'hmong': 'hmn', 'hungarian': 'hu', 'icelandic': 'is', 'igbo': 'ig', 'ilocano': 'ilo', 'indonesian': 'id', 'irish': 'ga', 'italian': 'it', 'japanese': 'ja', 'javanese': 'jw', 'kannada': 'kn', 'kazakh': 'kk', 'khmer': 'km', 'kinyarwanda': 'rw', 'konkani': 'gom', 'korean': 'ko', 'krio': 'kri', 'kurdish (kurmanji)': 'ku', 'kurdish (sorani)': 'ckb', 'kyrgyz': 'ky', 'lao': 'lo', 'latin': 'la', 'latvian': 'lv', 'lingala': 'ln', 'lithuanian': 'lt', 'luganda': 'lg', 'luxembourgish': 'lb', 'macedonian': 'mk', 'maithili': 'mai', 'malagasy': 'mg', 'malay': 'ms', 'malayalam': 'ml', 'maltese': 'mt', 'maori': 'mi', 'marathi': 'mr', 'meiteilon (manipuri)': 'mni-Mtei', 'mizo': 'lus', 'mongolian': 'mn', 'myanmar': 'my', 'nepali': 'ne', 'norwegian': 'no', 'odia (oriya)': 'or', 'oromo': 'om', 'pashto': 'ps', 'persian': 'fa', 'polish': 'pl', 'portuguese': 'pt', 'punjabi': 'pa', 'quechua': 'qu', 'romanian': 'ro', 'russian': 'ru', 'samoan': 'sm', 'sanskrit': 'sa', 'scots gaelic': 'gd', 'sepedi': 'nso', 'serbian': 'sr', 'sesotho': 'st', 'shona': 'sn', 'sindhi': 'sd', 'sinhala': 'si', 'slovak': 'sk', 'slovenian': 'sl', 'somali': 'so', 'spanish': 'es', 'sundanese': 'su', 'swahili': 'sw', 'swedish': 'sv', 'tajik': 'tg', 'tamil': 'ta', 'tatar': 'tt', 'telugu': 'te', 'thai': 'th', 'tigrinya': 'ti', 'tsonga': 'ts', 'turkish': 'tr', 'turkmen': 'tk', 'twi': 'ak', 'ukrainian': 'uk', 'urdu': 'ur', 'uyghur': 'ug', 'uzbek': 'uz', 'vietnamese': 'vi', 'welsh': 'cy', 'xhosa': 'xh', 'yiddish': 'yi', 'yoruba': 'yo', 'zulu': 'zu'}
)

class SpeechTranslator(APIView):
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
        await self.speech_recognition(language)

    #def stop_recording(self):
    #    self.messages.get()
    #    if self.stream:
    #        self.stream.stop_stream()
    #        self.stream.close()
    #        self.p.terminate()

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
                stream = StreamingHttpResponse(translated, status=200, content_type='text/event-stream')
                return stream
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


