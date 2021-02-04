from time import time
from pydub import AudioSegment


DEBUG = False
LANGUAGE_EN = 'en-US'
LANGUAGE_RU = 'ru-RU'
BUCKET_NAME = 'korzina'
SAMPLE_RATE = 8000
RECOGNITION_TIMEOUT = 120


def time_left(from_time):
    if DEBUG:
        print(int(time() - from_time), 'seconds left')


def mp3_to_wav(file_path):
    sound = AudioSegment.from_mp3(file_path)
    dst = '.'.join(file_path.split('/')[-1].split('.')[:-1]) + '.wav'
    sound.export(dst, format='wav', parameters=f'-ac 1 -ar {SAMPLE_RATE}'.split())
    print(f'File {file_path} was converted to {dst}')
    return dst
