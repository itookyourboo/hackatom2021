import telepot
from telepot.loop import MessageLoop
from requests import get
from json import loads
from util import time, TOKEN
from vosk_stt import vosk
from analyzer import VoskResultsAnalyzer as Analyzer


bot = telepot.Bot(TOKEN)
session = {}


def get_file_path(token, file_id):
    get_path = get('https://api.telegram.org/bot{}/getFile?file_id={}'.format(token, file_id))
    json_doc = loads(get_path.text)
    try:
        file_path = json_doc['result']['file_path']
    except Exception as e:  # Happens when the file size is bigger than the API condition
        print('Cannot download a file because the size is more than 20MB')
        return None

    return 'https://api.telegram.org/file/bot{}/{}'.format(token, file_path)


def get_language_from_caption(caption):
    if not caption:
        return None

    if any(token in caption.lower() for token in ['русский', 'российский', 'ру', 'ru', 'russian']):
        return 'ru'
    elif any(token in caption.lower() for token in ['английский', 'англ', 'en', 'english']):
        return 'en'

    return None


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if chat_id not in session:
        session[chat_id] = {
            'lang': 'ru',
            'speed': 1.0,
            'status': 'nothing'
        }
    user_state = session[chat_id]

    if content_type == 'audio':
        audio = msg['audio']
        caption = msg.get('caption')
        lang = get_language_from_caption(caption)
        if lang:
            user_state['lang'] = lang

        file_name, duration, file_id = audio['file_name'], audio['duration'], audio['file_id']
        path = get_file_path(TOKEN, file_id)
        bot.sendMessage(chat_id, f'Загружаю аудио...\n'
                                 f'Язык: {user_state["lang"]}')
        file = get(path)

        with open(file_name, 'wb') as f:
            f.write(file.content)

        bot.sendMessage(chat_id, 'Аудио обрабатывается. Подождите несколько минут.')

        words = vosk(file_name, user_state['lang'])
        send_results(chat_id, words, user_state['lang'], file_name)

    elif content_type == 'text':
        text = msg['text']
        if text == '/start':
            show_start_message(chat_id)

        lang = get_language_from_caption(text)
        if lang:
            user_state['lang'] = lang
            bot.sendMessage(chat_id, f'Выбран язык: {user_state["lang"]}')


def show_start_message(chat_id):
    bot.sendMessage(chat_id, 'Привет!\n'
                             'Чтобы перевести аудиозапись в текст, пришлите мне её документом.\n'
                             'Чтобы выбрать язык, напишите ru или en при отправке документа или заранее.')


def send_results(chat_id, words, lang, file_name):
    analyzer = Analyzer(words, lang)
    with open(analyzer.to_docx(file_name), 'rb') as docx_file:
        bot.sendDocument(chat_id, docx_file,
                         caption=f'Готово!\nТочность составила {analyzer.get_confidence_percent()}%')

if __name__ == '__main__':
    MessageLoop(bot, handle).run_forever()

    while True:
        pass
