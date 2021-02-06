from time import time
from pydub import AudioSegment
import os


DEBUG = True

LANGUAGES = [
    ('en-US', 'English (US)'),
    ('en-UK', 'English (UK)'),
    ('ru-RU', 'Русский (RU)')
]

LANGUAGE_EN = 'en-US'
LANGUAGE_RU = 'ru-RU'
SAMPLE_RATE = 8000
READ_FRAMES = 2000
RECOGNITION_TIMEOUT = 120
MAX_AUDIO_SIZE_MB = 32
APP_NAME = 'hackatom2021'
UPLOAD_FOLDER = 'audio'
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3'}
DOT_DELTA_TIME = 0.7
PARAGRAPH_DELTA_TIME = 1.1
PARAGRAPH_EVERY_N_SENTENCES = 3

DENSITY = {
    'ru': {
        'dot': 0.05,
        'comma': 0.08,
        'paragraph': 0.02
    },
    'en': {
        'dot': 0.05,
        'comma': 0.04,
        'paragraph': 0.025
    }
}


def time_left(from_time):
    if DEBUG:
        print(int(time() - from_time), 'seconds left')


def convert_to_wav(file_path):
    sound = AudioSegment.from_file(file_path)
    dst = '.'.join(file_path.split('/')[-1].split('.')[:-1]) + '.wav'
    print(f'Converting {file_path} to {dst}...')
    sound.export(dst, format='wav', parameters=f'-ac 1 -ar {SAMPLE_RATE}'.split())
    print(f'File {file_path} was converted to {dst}')
    return dst
