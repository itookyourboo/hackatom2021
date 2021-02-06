from google.cloud import storage, speech

from analyzer import GoogleCloudResultsAnalyzer
from util import *


# Загрузка файла на облако, получение ссылки на файл в облаке
def upload_to_cloud(source, blob_name):
    source_file_name = source
    destination_blob_name = blob_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f'File {source} was uploaded')
    return f'gs://{BUCKET_NAME}/{blob_name}'


# Удаление файла с облака
def delete_blob(blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f'File {blob_name} was deleted')


# Обработка аудиофайла
def transcribe_file(file_path, language=LANGUAGE_RU):
    from_time = time()

    client = speech.SpeechClient()
    file_name = convert_to_wav(file_path)
    time_left(from_time)

    gcs_uri = upload_to_cloud(file_name, file_name)
    time_left(from_time)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=language,
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=RECOGNITION_TIMEOUT)
    time_left(from_time)

    delete_blob(file_name)
    time_left(from_time)

    return response.results


if __name__ == '__main__':
    file = 'data/аудиозапись.mp3'
    lang = LANGUAGE_RU

    results = transcribe_file(file, lang)
    analyzer = GoogleCloudResultsAnalyzer(results)
    if DEBUG:
        print(analyzer.get_debug_info())
    text = analyzer.get_text()
    file_name = file.split('/')[-1]
    with open(f'results/{file_name}.txt', 'w') as file:
        file.write(analyzer.get_formatted_text(text))
    print('Average confidence:', analyzer.average_confidence())
