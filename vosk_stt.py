# Толя, твой выход
from vosk import Model, KaldiRecognizer, SetLogLevel
import sys
import os
import wave
import json
import difflib
import pymorphy2
import pymorphy2_dicts_ru

SetLogLevel(0)


class Word:
    start = None
    end = None
    value = None
    conf = None
    is_termin = 0
    coeff = 1


def vosk(file_name, model_language):
    model_file = None
    if (model_language.lower() == "russian"):
        model_file = "model_ru_extra"
    else:
        model_file = "model_en"
    words = []
    wf = wave.open(file_name, "rb")
    # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    #     print("Audio file must be WAV format mono PCM.")
    #     exit(1)
    model = Model(model_file)
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(2000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            # print(rec.Result())
            rc = json.loads(rec.Result())
            if (len(rc['text']) == 0):
                continue
            for i in rc['result']:
                word = Word()
                word.start = i['start']
                word.end = i['end']
                word.value = i['word']
                word.conf = i['conf']
                words.append(word)
    return words


def make_text(words):
    text = ''
    for i in words:
        text += i.value + ' '
    return text


def find_str(words):
    for i in transcriptions:
        transcriptions[i].append(float(1))
        w = list(transcriptions[i][-2].split())
        for j in range(len(words)):
            if (morph.parse(w[0])[0].normal_form == morph.parse(words[j].value)[0].normal_form):
                cnt = 1
                n = len(w)
                while (cnt < n and j + n < len(words) and morph.parse(w[cnt])[0].normal_form ==
                       morph.parse(words[j + cnt].value)[0].normal_form):
                    cnt += 1
                transcriptions[i][-1] = max(float(1 + 0.15 * cnt), transcriptions[i][-1])


def text_treatment(file_name, model_language):
    text = ''
    words = vosk(file_name, model_language)

    find_str(words)
    interrupt = 0
    for i in range(len(words)):
        if (interrupt):
            interrupt -= 1
            continue
        word = ''
        flag = 0
        if (words[i].value == None):
            continue
        cnt = 0
        for j in range(1, 7):
            if (i + j - 1 >= len(words)):
                break
            word += words[i + j - 1].value
            if (words[i + j - 1].value not in unions):
                cnt += 1
            for k in transcriptions:
                if (cnt != len(k)):
                    continue
                coeff = transcriptions[k][-1]
                for l in range(len(transcriptions[k]) - 1):
                    diff = difflib.SequenceMatcher(None, word, transcriptions[k][l])
                    accur = diff.ratio()
                    if (float(accur) * float(coeff) >= ACCURACY_CONST):
                        print(accur, word, k, transcriptions[k])
                        words[i + j - 1].value += '(' + k + ')'
                        flag = 1
                        break
                if (flag):
                    break
            if (flag):
                interrupt = j - 1
                break

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
unions = ['и', 'а', 'или', 'к', 'с', 'в', 'по']
ACCURACY_CONST = 0.9
morph = pymorphy2.MorphAnalyzer()
file_name = input()
model_language = input()
f_text = f.read()
transcriptions = json.loads(f_text)
text = text_treatment(file_name, model_language)
q.write(text)
q.close()
