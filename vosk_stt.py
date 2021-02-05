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


words = []

q = open("output.txt", "w")


if not os.path.exists("model"):
    print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
    exit (1)

wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print ("Audio file must be WAV format mono PCM.")
    exit (1)

model = Model("model")
rec = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(2000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
        rc = json.loads(rec.Result())
        for i in rc['result']:
            word = Word()
            word.start = i['start']
            word.end = i['end']
            word.value = i['word']
            word.conf = i['conf']
            words.append(word)
            #print(word.start, word.end, word.value)
    else:
        pass#print(rec.PartialResult())
intervals = []
for i in range(1, len(words)):
    intervals.append(words[i].start - words[i - 1].end)
intervals.sort()
dots_count = int(len(words) * 0.05)
comma_count = int(len(words) * 0.08)
print(dots_count, comma_count)
dots_interval = intervals[-dots_count]
comma_interval = intervals[-(dots_count + comma_count)]
text = ''
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
text += words[-1].value

res = json.loads(rec.FinalResult())
print(res['text'])
q.write(text)
q.close()

#print(rec.FinalResult())
