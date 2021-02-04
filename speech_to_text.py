from pydub import AudioSegment
from google.cloud import storage, speech

BUCKET_NAME = 'korzina'
SAMPLE_RATE = 8000


def mp3_to_wav(file_path):
    sound = AudioSegment.from_mp3(file_path)
    dst = '.'.join(file_path.split('/')[-1].split('.')[:-1]) + '.wav'
    sound.export(dst, format='wav', parameters=f'-ac 1 -ar {SAMPLE_RATE}'.split())

    print(f'File {file_path} was converted to {dst}')
    return dst


def upload_to_cloud(source, blob_name):
    source_file_name = source
    destination_blob_name = blob_name

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f'File {source} was uploaded')
    return f'gs://{BUCKET_NAME}/{blob_name}'


def delete_blob(blob_name):
    storage_client = storage.Client()

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f'File {blob_name} was deleted')


def transcribe_file(file_path, language='en-US', debug=False):
    client = speech.SpeechClient()
    file_name = mp3_to_wav(file_path)
    gcs_uri = upload_to_cloud(file_name, file_name)
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=language,
    )
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=120)
    delete_blob(file_name)

    confidences = []
    transcripts = []

    if debug:
        print('========================')
        for result in response.results:
            if debug:
                transcripts.append([x.transcript for x in result.alternatives])
                print('Transcription', transcripts[-1])
                confidences.append([x.confidence for x in result.alternatives])
                print('Confidence', confidences[-1])
        print('========================')

    for result in response.results:
        print(result.alternatives[0].transcript)


transcribe_file('data/аудиозапись.mp3', language='ru-RU', debug=True)
