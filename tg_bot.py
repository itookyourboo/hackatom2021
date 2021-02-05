import telepot
from telepot.loop import MessageLoop
from requests import get
from json import loads
from util import time
from vosk_stt import vosk
from analyzer import VoskResultsAnalyzer as Analyzer

TOKEN = '846229948:AAGQ6Ey8qX_yRYFzrjVnWp7_dp9h68J7JhY'
bot = telepot.Bot(TOKEN)
print(bot.getMe())


def get_file_path(token, file_id):
    get_path = get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(token, file_id))
    json_doc = loads(get_path.text)
    try:
        file_path = json_doc['result']['file_path']
    except Exception as e:  # Happens when the file size is bigger than the API condition
        print('Cannot download a file because the size is more than 20MB')
        return None

    return 'https://api.telegram.org/file/bot{}/{}'.format(token, file_path)


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'audio':
        audio = msg['audio']
        file_name, duration, file_id = audio['file_name'], audio['duration'], audio['file_id']
        path = get_file_path(TOKEN, file_id)
        bot.sendMessage(chat_id, 'Загружаю аудио...')
        file = get(path)

        with open(file_name, 'wb') as f:
            f.write(file.content)

        bot.sendMessage(chat_id, 'Аудио обрабатывается. Подождите несколько минут.')

        words = vosk(file_name, 'ru')
        send_results(chat_id, words, file_name)


def send_results(chat_id, words, file_name):
    analyzer = Analyzer(words)
    bot.sendMessage(chat_id, 'Конвертирую в docx...')
    with open(analyzer.to_docx(file_name), 'rb') as docx_file:
        bot.sendDocument(chat_id, docx_file,
                         caption=f'Готово!\nТочность составила {analyzer.get_confidence() * 100}%')

if __name__ == '__main__':
    MessageLoop(bot, handle).run_as_thread()

    while True:
        pass
