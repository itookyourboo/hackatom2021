# Толя, твой выход
from vosk import Model, KaldiRecognizer
import wave
import json
from word import Word
from analyzer import VoskResultsAnalyzer as Analyzer
from util import convert_to_wav


def vosk(file_name, model_language):
    if file_name.split('.')[-1] != 'wav':
        file_name = convert_to_wav(file_name)

    model_file = f'model_{model_language}'
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


if __name__ == '__main__':
    file = 'аудиозапись.mp3'
    words = vosk(file, 'ru')

    analyzer = Analyzer(words)
    print(analyzer.to_plain_text())
    analyzer.to_docx(file)
