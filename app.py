from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
import os
import time
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import requests
import logging
import mlflow

# Загружаем переменные окружения из .env файла
load_dotenv()

# Установка трекингового URI
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# Инициализация логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Инициализация Flask приложения
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Поддерживаемые MIME-типы
ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/pjpeg',
    'image/x-png',
    'image/gif',
    'image/webp'
}

# Функция проверки расширения файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Очистка папки uploads от старых файлов
def clean_uploads_folder(max_age=3600):  # max_age задаётся в секундах (1 час = 3600 секунд)
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        # Проверяем, файл ли это и не используется ли он прямо сейчас
        if os.path.isfile(filepath):
            file_age = time.time() - os.path.getmtime(filepath)
            if file_age > max_age:  # Если файл старше max_age
                os.remove(filepath)
                print(f"Удалён файл: {filepath}")


# Функция подключения к базе данных
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

# Логирование в базу данных
def log_request(ip, method, path, status_code, response_time, predicted_label=None, is_right_answer=None):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO logs (ip_address, method, path, status_code, response_time, model_predict, is_right_answer) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (ip, method, path, status_code, response_time, predicted_label, is_right_answer))
            connection.commit()
            cursor.close()
        finally:
            connection.close()


# Функция для взаимодействия с микросервисом model_service.py
def get_prediction_from_microservice(filepath):
    url = 'http://localhost:5001/predict'  # Адрес микросервиса
    try:
        with open(filepath, 'rb') as f:
            # Определение MIME-типа на основе расширения файла
            ext = filepath.rsplit('.', 1)[1].lower()
            mime_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'application/octet-stream')
            files = {'file': (os.path.basename(filepath), f, mime_type)}
            response = requests.post(url, files=files)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Получено предсказание от микросервиса: {data.get('prediction')}")
            return data.get('prediction')
        else:
            error_message = data.get('error', 'Неизвестная ошибка')
            logging.error(f"Ошибка от микросервиса: {error_message}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при подключении к микросервису: {e}")
        return None

# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    start_time = time.time()  # Время начала обработки запроса
    if request.method == 'POST':
        # Проверка наличия файла в запросе
        if 'file' not in request.files:
            return 'Нет файла для загрузки'
        file = request.files['file']
        if file.filename == '':
            return 'Файл не выбран'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Логирование
            status_code = 200
            log_request(request.remote_addr, 'POST', '/', status_code, f"{(time.time() - start_time) * 1000:.2f}ms")
            return render_template('index.html', filename=filename)
    # Логирование
    status_code = 200
    log_request(request.remote_addr, 'GET', '/', status_code, f"{(time.time() - start_time) * 1000:.2f}ms")
    return render_template('index.html')


# Маршрут для предсказания
@app.route('/predict/<filename>')
def predict(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    start_time = time.time()  # Время начала обработки запроса

    try:
        # Получаем предсказание от микросервиса
        predicted_label = get_prediction_from_microservice(filepath)

        if predicted_label:
            # Логирование
            status_code = 200
            log_request(
                ip=request.remote_addr,
                method="GET",
                path=f"/predict/{filename}",
                status_code=status_code,
                response_time=f"{(time.time() - start_time) * 1000:.2f}ms",
                predicted_label=predicted_label  # Передаём предсказанный класс
            )
            # Возврат результата
            return render_template('result.html', result=predicted_label)
        else:
            # Если предсказание не получено, возвращаем ошибку
            status_code = 500
            log_request(
                ip=request.remote_addr,
                method="GET",
                path=f"/predict/{filename}",
                status_code=status_code,
                response_time=f"{(time.time() - start_time) * 1000:.2f}ms",
                predicted_label=None  # В случае ошибки передаём None
            )
            return "Ошибка при получении предсказания от микросервиса"
    except Exception as e:
        # Логирование ошибки
        status_code = 500
        log_request(
            ip=request.remote_addr,
            method="GET",
            path=f"/predict/{filename}",
            status_code=status_code,
            response_time=f"{(time.time() - start_time) * 1000:.2f}ms",
            predicted_label=None
        )
        return f"Ошибка при обработке запроса: {e}"


@app.route('/feedback', methods=['POST'])
def feedback():
    start_time = time.time()  # Время начала обработки запроса

    # Получаем данные из формы
    predicted_label = request.form.get('predicted_label')
    is_right_answer = request.form.get('is_right_answer')  # Значение 1 (Да) или 0 (Нет)

    if is_right_answer is not None:
        try:
            # Преобразуем ответ в целое число
            is_right_answer = int(is_right_answer)

            # Логирование в базу данных
            log_request(
                ip=request.remote_addr,
                method="POST",
                path="/feedback",
                status_code=200,
                response_time=f"{(time.time() - start_time) * 1000:.2f}ms",
                predicted_label=predicted_label,
                is_right_answer=is_right_answer
            )
            return "Спасибо за ваш ответ!"
        except Exception as e:
            return f"Ошибка при записи в базу данных: {e}", 500
    else:
        return "Некорректный ответ", 400

if __name__ == '__main__':
    clean_uploads_folder(max_age=3600)  # Удаление файлов старше 1 часа
    app.run(debug=True)