import os

from util import MAX_AUDIO_SIZE_MB, LANGUAGES, \
    ALLOWED_AUDIO_EXTENSIONS, UPLOAD_FOLDER, APP_NAME, SECRET_KEY
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SubmitField, SelectField
from flask_bootstrap import Bootstrap

from google_cloud_stt import transcribe_file
from analyzer import GoogleCloudResultsAnalyzer as Analyzer


app = Flask(__name__)
app.config['MAX_FILE_CONTENT'] = MAX_AUDIO_SIZE_MB * 1024 * 1024
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    upload_form = AddAudioForm()
    upload_form.language.choices = LANGUAGES

    if upload_form.validate_on_submit():
        file_name = upload_form.file.data.filename
        if '.' not in file_name:
            upload_form.submit.errors.append('Файл не имеет расширения')
        else:
            file_ext = file_name.rsplit('.', 1)[1].lower()
            if file_ext not in ALLOWED_AUDIO_EXTENSIONS:
                upload_form.submit.errors.append(f'Неподдерживаемое расширение')
            else:
                file = request.files['file']
                file.save(os.path.join(UPLOAD_FOLDER, file_name))

                return redirect(url_for('analyze', filename=file_name, language=upload_form.language.data))

    return render_template('index.html', title=APP_NAME, upload_form=upload_form)


@app.route('/analyze/<filename>/<language>', methods=['GET'])
def analyze(filename='audio.mp3', language='en-US'):
    print(filename, language)
    results = transcribe_file(os.path.join(UPLOAD_FOLDER, filename), language)
    analyzer = Analyzer(results)
    text = analyzer.get_text()
    return f"<i>Confidence: {int(10000 * analyzer.average_confidence()) / 100}%</i>\n" \
           f"{text}".replace('\n', '<br><br>')


class AddAudioForm(FlaskForm):
    language = SelectField('Выберите язык', coerce=str)

    file = FileField("Выберите аудио", validators=[
        FileRequired('Загрузите аудиофайл'),
        FileAllowed(list(ALLOWED_AUDIO_EXTENSIONS), "Неподдерживаемое расширение")
    ])

    submit = SubmitField("Распознать текст")


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')