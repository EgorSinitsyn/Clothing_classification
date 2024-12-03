from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import time
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
import requests

# Загружаем переменные окружения из .env файла
load_dotenv()

# Инициализация Flask приложения
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
def log_request(ip, method, path, status_code, response_time):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO logs (ip_address, method, path, status_code, response_time) 
                VALUES (%s, %s, %s, %s, %s)
            """, (ip, method, path, status_code, response_time))
            connection.commit()
            cursor.close()
        finally:
            connection.close()

# Функция для взаимодействия с микросервисом model_service.py
def get_prediction_from_microservice(filepath):
    url = 'http://localhost:5001/predict'  # Адрес вашего микросервиса
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        if response.status_code == 200:
            data = response.json()
            return data.get('prediction')
        else:
            print(f"Ошибка от микросервиса: {response.json().get('error')}")
            return None
    except Exception as e:
        print(f"Ошибка при подключении к микросервису: {e}")
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
            log_request(request.remote_addr, 'GET', f'/predict/{filename}', status_code,
                        f"{(time.time() - start_time) * 1000:.2f}ms")
            # Возврат результата
            return render_template('result.html', result=predicted_label)
        else:
            # Если предсказание не получено, возвращаем ошибку
            status_code = 500
            log_request(request.remote_addr, 'GET', f'/predict/{filename}', status_code,
                        f"{(time.time() - start_time) * 1000:.2f}ms")
            return "Ошибка при получении предсказания от микросервиса"
    except Exception as e:
        # Логирование ошибки
        status_code = 500
        log_request(request.remote_addr, 'GET', f'/predict/{filename}', status_code,
                    f"{(time.time() - start_time) * 1000:.2f}ms")
        return f"Ошибка при обработке запроса: {e}"

if __name__ == '__main__':
    clean_uploads_folder(max_age=3600)  # Удаление файлов старше 1 часа
    app.run(debug=True)