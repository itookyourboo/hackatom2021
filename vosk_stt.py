# Толя, твой выход
from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import json

SetLogLevel(0)



class Word:
    start = None
    end = None
    value = None
    conf = None



def vosk(file_name, model_language):
    model_file = None
    if (model_language.lower() == "russian"):
        model_file = "model_ru"
    else:
        model_file = "model_en"
    words = []
    wf = wave.open(file_name, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)
    model = Model(model_file)
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(2000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            rc = json.loads(rec.Result())
            for i in rc['result']:
                word = Word()
                word.start = i['start']
                word.end = i['end']
                word.value = i['word']
                word.conf = i['conf']
                words.append(word)
    return words



def text_treatment(file_name, model_language):
    text = ''
    words = vosk(file_name, model_language)


    intervals = []
    for i in range(1, len(words)):
        intervals.append(words[i].start - words[i - 1].end)
    intervals.sort()
    dots_count = int(len(words) * 0.05)
    comma_count = int(len(words) * 0.08)
    print(dots_count, comma_count)
    dots_interval = intervals[-dots_count]
    comma_interval = intervals[-(dots_count + comma_count)]
    flag = 1
    for i in range(1, len(words)):
        if (flag):
            words[i - 1].value = words[i - 1].value.capitalize()
            flag = 0
        text += words[i - 1].value
        if (dots_interval > words[i].start - words[i - 1].end >= comma_interval):
            text += ','
        elif (words[i].start - words[i - 1].end >= dots_interval):
            text += '.'
            flag = 1
        text += ' '
    text += words[-1].value + '.'
    return text


q = open("output.txt", "w")
f = open("transcription.txt", "r", encoding="utf-8")
file_name = input()
model_language = input()
transcriptions = json.loads(f.read())
text = text_treatment(file_name, model_language)
q.write(text)
q.close()