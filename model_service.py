from flask import Flask, request, jsonify
import mlflow.keras
from tensorflow.keras.applications.xception import preprocess_input
from PIL import Image
import numpy as np
import os
import time
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Установка трекингового URI
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))

# Инициализация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("model_service.log"),
        logging.StreamHandler()
    ]
)

# Загрузка модели из реестра MLflow
model_name = "XceptionModel"
model_version = 1  # Укажите актуальную версию модели

try:
    model = mlflow.keras.load_model(f"models:/{model_name}/{model_version}")
    logging.info(f"Модель '{model_name}' версии {model_version} успешно загружена из MLflow Model Registry")
except Exception as e:
    logging.error(f"Ошибка загрузки модели из MLflow: {e}")
    model = None

# Метки классов
labels = {
    0: 'dress',
    1: 'hat',
    2: 'longsleeve',
    3: 'outwear',
    4: 'pants',
    5: 'shirt',
    6: 'shoes',
    7: 'shorts',
    8: 'skirt',
    9: 't-shirt'
}

# Инициализация Flask приложения
app = Flask(__name__)

# Ограничение размера загружаемых файлов (например, до 5 МБ)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 МБ

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

@app.route('/predict', methods=['POST'])
def predict():
    # Проверка загрузки модели
    if model is None:
        logging.error("Модель не загружена")
        return jsonify({'error': 'Модель не загружена'}), 500

    start_time = time.time()

    # Проверка наличия файла в запросе
    if 'file' not in request.files:
        logging.warning("Файл не найден в запросе")
        return jsonify({'error': 'Нет файла для предсказания'}), 400

    file = request.files['file']

    # Логирование полученного файла
    logging.info(f"Получен файл: {file.filename}, MIME-тип: {file.content_type}")

    # Проверка пустого имени файла
    if file.filename == '':
        logging.warning("Пустое имя файла")
        return jsonify({'error': 'Файл не выбран'}), 400

    # Проверка MIME-типа файла
    if file.content_type not in ALLOWED_MIME_TYPES:
        logging.warning(f"Неподдерживаемый формат изображения: {file.content_type}")
        return jsonify({'error': 'Неподдерживаемый формат изображения'}), 400

    try:
        # Обработка изображения
        img = Image.open(file)

        # Конвертация изображения в RGB, если необходимо
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img = img.resize((299, 299))
        x = np.array(img)
        X = np.expand_dims(x, axis=0)
        X = preprocess_input(X)

        # Предсказание
        pred = model.predict(X)
        predicted_index = pred[0].argmax()
        predicted_label = labels.get(predicted_index, "Неизвестно")

        # Логирование
        response_time = f"{(time.time() - start_time) * 1000:.2f}ms"
        logging.info(f"Предсказание: {predicted_label} (индекс: {predicted_index}), время обработки: {response_time}")

        # Возврат результата
        return jsonify({'prediction': predicted_label})

    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        return jsonify({'error': 'Ошибка при обработке изображения'}), 500

# Обработка ошибок превышения размера файла
@app.errorhandler(413)
def request_entity_too_large(error):
    logging.warning("Размер загружаемого файла превышает допустимый лимит")
    return jsonify({'error': 'Размер файла превышает допустимый лимит (5 МБ)'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)